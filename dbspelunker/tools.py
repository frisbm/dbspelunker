import re
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    ColumnInfo,
    ColumnType,
    ConstraintInfo,
    ConstraintType,
    DatabaseOverview,
    DatabaseType,
    IndexInfo,
    IndexType,
    RelationshipInfo,
    SchemaInfo,
    StoredProcedureInfo,
    TableInfo,
    TriggerInfo,
)
from .prompt_builder import PromptBuilder, RenderOptions


class SQLSafetyValidator:
    FORBIDDEN_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        "MERGE",
    }

    @classmethod
    def validate_readonly_sql(cls, sql: str) -> bool:
        normalized = re.sub(r"\s+", " ", sql.upper().strip())
        words = normalized.split()

        if not words:
            return False

        first_word = words[0]
        if first_word not in {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH"}:
            return False

        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in words:
                return False

        return True


class DatabaseConnector:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._engine: Optional[Engine] = None

    def get_engine(self) -> Engine:
        if not self._engine:
            self._engine = create_engine(self.connection_string)
        return self._engine

    def execute_safe_sql(self, sql: str) -> List[Dict[str, Any]]:
        if not SQLSafetyValidator.validate_readonly_sql(sql):
            raise ValueError(f"SQL query is not safe for read-only execution: {sql}")

        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database query failed: {str(e)}")

    def get_database_type(self) -> DatabaseType:
        engine = self.get_engine()
        dialect_name = engine.dialect.name.lower()

        mapping = {
            "postgresql": DatabaseType.POSTGRESQL,
            "mysql": DatabaseType.MYSQL,
            "sqlite": DatabaseType.SQLITE,
            "mssql": DatabaseType.SQLSERVER,
            "oracle": DatabaseType.ORACLE,
        }

        return mapping.get(dialect_name, DatabaseType.POSTGRESQL)


def get_database_overview_tool(connection_string: str) -> DatabaseOverview:
    """Get high-level database metadata including schemas, tables, and basic statistics."""
    connector = DatabaseConnector(connection_string)
    engine = connector.get_engine()
    inspector = inspect(engine)

    db_type = connector.get_database_type()
    schema_names = inspector.get_schema_names() or ["public"]

    schemas = []
    total_tables = 0
    total_views = 0

    for schema_name in schema_names:
        if schema_name in [
            "information_schema",
            "pg_catalog",
            "mysql",
            "performance_schema",
        ]:
            continue

        table_names = inspector.get_table_names(schema=schema_name)
        view_names = inspector.get_view_names(schema=schema_name)

        total_tables += len(table_names)
        total_views += len(view_names)

        # Create basic table info objects for the overview
        basic_tables = [
            TableInfo(name=table_name, columns=[]) for table_name in table_names
        ]
        basic_views = [
            TableInfo(name=view_name, columns=[]) for view_name in view_names
        ]

        schemas.append(
            SchemaInfo(
                name=schema_name,
                tables=basic_tables,
                views=basic_views,
                stored_procedures=[],
                relationships=[],
            )
        )

    return DatabaseOverview(
        name=engine.url.database or "unknown",
        database_type=db_type,
        schemas=schemas,
        total_tables=total_tables,
        total_views=total_views,
        total_stored_procedures=0,
        total_triggers=0,
        total_indexes=0,
    )


def execute_readonly_sql_tool(connection_string: str, sql: str) -> List[Dict[str, Any]]:
    """Execute a READ-ONLY SQL query safely against the database."""
    connector = DatabaseConnector(connection_string)
    return connector.execute_safe_sql(sql)


def get_table_schema_tool(
    connection_string: str, table_name: str, schema_name: Optional[str] = None
) -> TableInfo:
    """Get detailed schema information for a specific table."""
    connector = DatabaseConnector(connection_string)
    engine = connector.get_engine()
    inspector = inspect(engine)

    columns_data = inspector.get_columns(table_name, schema=schema_name)
    pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
    foreign_keys = inspector.get_foreign_keys(table_name, schema=schema_name)
    indexes = inspector.get_indexes(table_name, schema=schema_name)

    pk_columns = set(pk_constraint.get("constrained_columns", []))
    fk_map = {
        fk["constrained_columns"][0]: (fk["referred_table"], fk["referred_columns"][0])
        for fk in foreign_keys
        if fk["constrained_columns"]
    }

    columns = []
    for col_data in columns_data:
        col_name = col_data["name"]
        columns.append(
            ColumnInfo(
                name=col_name,
                data_type=_map_column_type(str(col_data["type"])),
                is_nullable=col_data["nullable"],
                default_value=str(col_data["default"])
                if col_data["default"] is not None
                else None,
                is_primary_key=col_name in pk_columns,
                is_foreign_key=col_name in fk_map,
                foreign_key_table=fk_map.get(col_name, (None, None))[0],
                foreign_key_column=fk_map.get(col_name, (None, None))[1],
            )
        )

    constraints = []
    if pk_constraint["constrained_columns"]:
        constraints.append(
            ConstraintInfo(
                name=pk_constraint["name"] or f"{table_name}_pkey",
                type=ConstraintType.PRIMARY_KEY,
                columns=pk_constraint["constrained_columns"],
            )
        )

    for fk in foreign_keys:
        constraints.append(
            ConstraintInfo(
                name=fk["name"] or f"{table_name}_fk",
                type=ConstraintType.FOREIGN_KEY,
                columns=fk["constrained_columns"],
                referenced_table=fk["referred_table"],
                referenced_columns=fk["referred_columns"],
            )
        )

    index_info: List[IndexInfo] = []
    for idx in indexes:
        index_info.append(
            IndexInfo(
                name=idx["name"] or f"{table_name}_idx_{len(index_info)}",
                table_name=table_name,
                index_type=IndexType.UNIQUE if idx["unique"] else IndexType.INDEX,
                columns=[col for col in idx["column_names"] if col is not None],
                is_unique=idx["unique"],
                is_primary=False,
            )
        )

    # Get row count and size information
    row_count = None
    size_bytes = None

    try:
        db_type = connector.get_database_type()

        if db_type == DatabaseType.POSTGRESQL:
            # Get row count and size for PostgreSQL
            try:
                # Try to get row count with a simple estimate
                count_query = f"SELECT reltuples::bigint as row_count FROM pg_class WHERE relname = '{table_name}'"
                count_result = connector.execute_safe_sql(count_query)
                if count_result and count_result[0]["row_count"] is not None:
                    row_count = int(count_result[0]["row_count"])

                # Try to get table size
                full_table_name = (
                    f"{schema_name}.{table_name}" if schema_name else table_name
                )
                size_query = (
                    f"SELECT pg_total_relation_size('{full_table_name}') as size_bytes"
                )
                size_result = connector.execute_safe_sql(size_query)
                if size_result and size_result[0]["size_bytes"] is not None:
                    size_bytes = int(size_result[0]["size_bytes"])

            except Exception:
                pass  # These are optional

        elif db_type == DatabaseType.MYSQL:
            # Get row count and size for MySQL
            size_query = f"""
                SELECT 
                    data_length + index_length as size_bytes,
                    table_rows as row_count
                FROM information_schema.tables
                WHERE table_name = '{table_name}' 
                AND table_schema = '{schema_name or "DATABASE()"}'
            """
            try:
                result = connector.execute_safe_sql(size_query)
                if result:
                    size_bytes = result[0].get("size_bytes")
                    row_count = result[0].get("row_count")
            except Exception:
                pass

    except Exception:
        pass  # Size and row count are optional

    return TableInfo(
        name=table_name,
        schema_name=schema_name,
        columns=columns,
        constraints=constraints,
        indexes=index_info,
        triggers=get_triggers_tool(connection_string, table_name, schema_name),
        row_count=row_count,
        size_bytes=size_bytes,
    )


def analyze_relationships_tool(
    connection_string: str, schema_name: Optional[str] = None
) -> List[RelationshipInfo]:
    """Analyze foreign key relationships between tables."""
    connector = DatabaseConnector(connection_string)
    engine = connector.get_engine()
    inspector = inspect(engine)

    relationships = []
    table_names = inspector.get_table_names(schema=schema_name)

    for table_name in table_names:
        foreign_keys = inspector.get_foreign_keys(table_name, schema=schema_name)

        for fk in foreign_keys:
            if fk["constrained_columns"] and fk["referred_columns"]:
                relationships.append(
                    RelationshipInfo(
                        source_table=table_name,
                        source_column=fk["constrained_columns"][0],
                        target_table=fk["referred_table"],
                        target_column=fk["referred_columns"][0],
                        constraint_name=fk["name"] or f"{table_name}_fk",
                        on_delete=str(fk.get("ondelete"))
                        if fk.get("ondelete")
                        else None,
                        on_update=str(fk.get("onupdate"))
                        if fk.get("onupdate")
                        else None,
                    )
                )

    return relationships


def get_indexes_tool(
    connection_string: str, table_name: str, schema_name: Optional[str] = None
) -> List[IndexInfo]:
    """Get detailed index information for a table."""
    connector = DatabaseConnector(connection_string)
    engine = connector.get_engine()
    inspector = inspect(engine)

    indexes_data = inspector.get_indexes(table_name, schema=schema_name)

    indexes: List[IndexInfo] = []
    for idx_data in indexes_data:
        indexes.append(
            IndexInfo(
                name=idx_data["name"] or f"{table_name}_idx_{len(indexes)}",
                table_name=table_name,
                index_type=IndexType.UNIQUE if idx_data["unique"] else IndexType.INDEX,
                columns=[col for col in idx_data["column_names"] if col is not None],
                is_unique=idx_data["unique"],
                is_primary=False,
            )
        )

    return indexes


def get_triggers_tool(
    connection_string: str, table_name: str, schema_name: Optional[str] = None
) -> List[TriggerInfo]:
    """Get trigger information for a table (implementation varies by database type)."""
    connector = DatabaseConnector(connection_string)
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_triggers(connector, table_name, schema_name)
    elif db_type == DatabaseType.MYSQL:
        return _get_mysql_triggers(connector, table_name, schema_name)
    else:
        return []


def get_stored_procedures_tool(
    connection_string: str, schema_name: Optional[str] = None
) -> List[StoredProcedureInfo]:
    """Get stored procedure information (implementation varies by database type)."""
    connector = DatabaseConnector(connection_string)
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_functions(connector, schema_name)
    elif db_type == DatabaseType.MYSQL:
        return _get_mysql_procedures(connector, schema_name)
    else:
        return []


def _map_column_type(type_str: str) -> ColumnType:
    """Map database-specific column types to our enum."""
    type_lower = type_str.lower()

    if "int" in type_lower:
        if "bigint" in type_lower:
            return ColumnType.BIGINT
        elif "smallint" in type_lower:
            return ColumnType.SMALLINT
        return ColumnType.INTEGER
    elif any(t in type_lower for t in ["varchar", "char", "text", "string"]):
        if "text" in type_lower:
            return ColumnType.TEXT
        elif "char" in type_lower:
            return ColumnType.CHAR
        return ColumnType.VARCHAR
    elif any(t in type_lower for t in ["decimal", "numeric"]):
        return ColumnType.DECIMAL
    elif any(t in type_lower for t in ["float", "double", "real"]):
        return ColumnType.FLOAT
    elif any(t in type_lower for t in ["bool", "boolean"]):
        return ColumnType.BOOLEAN
    elif any(t in type_lower for t in ["date", "time", "timestamp"]):
        if "timestamp" in type_lower:
            return ColumnType.TIMESTAMP
        elif "time" in type_lower:
            return ColumnType.TIME
        return ColumnType.DATE
    elif "json" in type_lower:
        return ColumnType.JSON
    elif any(t in type_lower for t in ["blob", "binary"]):
        return ColumnType.BLOB
    elif "uuid" in type_lower:
        return ColumnType.UUID
    elif "array" in type_lower:
        return ColumnType.ARRAY

    return ColumnType.OTHER


def _get_postgresql_triggers(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[TriggerInfo]:
    """Get PostgreSQL triggers for a table."""
    schema_filter = f"AND schemaname = '{schema_name}'" if schema_name else ""
    sql = f"""
    SELECT trigger_name, event_manipulation, action_timing, action_statement
    FROM information_schema.triggers 
    WHERE table_name = '{table_name}' {schema_filter}
    """

    try:
        results = connector.execute_safe_sql(sql)
        triggers = []

        for row in results:
            triggers.append(
                TriggerInfo(
                    name=row["trigger_name"],
                    table_name=table_name,
                    event=row["event_manipulation"].lower(),
                    timing=row["action_timing"].lower(),
                    definition=row["action_statement"],
                )
            )

        return triggers
    except Exception:
        return []


def _get_mysql_triggers(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[TriggerInfo]:
    """Get MySQL triggers for a table."""
    sql = f"SHOW TRIGGERS LIKE '{table_name}'"

    try:
        results = connector.execute_safe_sql(sql)
        triggers = []

        for row in results:
            triggers.append(
                TriggerInfo(
                    name=row.get("Trigger", ""),
                    table_name=table_name,
                    event=row.get("Event", "").lower(),
                    timing=row.get("Timing", "").lower(),
                    definition=row.get("Statement", ""),
                )
            )

        return triggers
    except Exception:
        return []


def _get_postgresql_functions(
    connector: DatabaseConnector, schema_name: Optional[str]
) -> List[StoredProcedureInfo]:
    """Get PostgreSQL functions/procedures."""
    schema_filter = f"AND n.nspname = '{schema_name}'" if schema_name else ""
    sql = f"""
    SELECT p.proname as name, n.nspname as schema_name, pg_get_functiondef(p.oid) as definition
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast') {schema_filter}
    """

    try:
        results = connector.execute_safe_sql(sql)
        procedures = []

        for row in results:
            procedures.append(
                StoredProcedureInfo(
                    name=row["name"],
                    schema_name=row["schema_name"],
                    definition=row["definition"],
                    language="plpgsql",
                )
            )

        return procedures
    except Exception:
        return []


def _get_mysql_procedures(
    connector: DatabaseConnector, schema_name: Optional[str]
) -> List[StoredProcedureInfo]:
    """Get MySQL stored procedures."""
    schema_filter = f"AND ROUTINE_SCHEMA = '{schema_name}'" if schema_name else ""
    sql = f"""
    SELECT ROUTINE_NAME, ROUTINE_SCHEMA, ROUTINE_DEFINITION, ROUTINE_TYPE
    FROM information_schema.ROUTINES
    WHERE ROUTINE_TYPE IN ('PROCEDURE', 'FUNCTION') {schema_filter}
    """

    try:
        results = connector.execute_safe_sql(sql)
        procedures = []

        for row in results:
            procedures.append(
                StoredProcedureInfo(
                    name=row["ROUTINE_NAME"],
                    schema_name=row["ROUTINE_SCHEMA"],
                    definition=row["ROUTINE_DEFINITION"] or "",
                    language="sql",
                )
            )

        return procedures
    except Exception:
        return []


def generate_table_summary_prompt(
    table_info: TableInfo, relationships: List[RelationshipInfo]
) -> str:
    """Generate a prompt for AI to analyze what a table represents."""
    column_details = []
    for col in table_info.columns:
        detail = f"{col.name}: {col.data_type.value}"
        if col.is_primary_key:
            detail += " (PRIMARY KEY)"
        if col.is_foreign_key:
            detail += f" (FK to {col.foreign_key_table}.{col.foreign_key_column})"
        if not col.is_nullable:
            detail += " NOT NULL"
        column_details.append(detail)

    # Find relationships involving this table
    related_tables = set()
    table_relationships = []
    for rel in relationships:
        if rel.source_table == table_info.name:
            related_tables.add(rel.target_table)
            table_relationships.append(
                f"References {rel.target_table}.{rel.target_column} via {rel.source_column}"
            )
        elif rel.target_table == table_info.name:
            related_tables.add(rel.source_table)
            table_relationships.append(
                f"Referenced by {rel.source_table}.{rel.source_column} via {rel.target_column}"
            )

    constraint_info = []
    for constraint in table_info.constraints:
        constraint_info.append(
            f"{constraint.name}: {constraint.type.value} on {constraint.columns}"
        )

    index_info = []
    for index in table_info.indexes:
        index_info.append(f"{index.name}: {index.index_type.value} on {index.columns}")

    row_info = (
        f"Estimated rows: {table_info.row_count}"
        if table_info.row_count
        else "Row count unknown"
    )
    size_info = (
        f"Size: {table_info.size_bytes} bytes"
        if table_info.size_bytes
        else "Size unknown"
    )

    # Build table metadata
    table_metadata = f"""Table: {table_info.name}
Schema: {table_info.schema_name or "default"}
Type: {table_info.table_type}
{row_info}
{size_info}"""

    pb = (
        PromptBuilder()
        .with_title("Database Table Analysis and Business Purpose Summary")
        .extend_instructions(
            [
                "Analyze the provided database table structure and metadata",
                "Identify what type of business data this table likely stores",
                "Determine the table's role within the larger database system",
                "Focus on business purpose rather than technical implementation details",
                "Provide insights based on column names, types, and relationships",
            ]
        )
        .extend_rules(
            [
                "Base analysis solely on the provided table structure and relationships",
                "Keep the summary concise but informative (2-3 sentences)",
                "Explain relationships in business terms, not technical terms",
                "Avoid speculation beyond what can be reasonably inferred from column names",
                "Focus on functional purpose rather than technical details",
            ]
        )
        .set_output(
            """
Provide a concise analysis with:
1. A 2-3 sentence summary of what this table represents and stores
2. A brief explanation of how it relates to other tables in the system  
3. Any insights about its likely business purpose based on column names and structure

Keep the response focused on business/functional purpose rather than technical details.
            """.strip()
        )
        .add_supporting_info("Table Metadata", table_metadata, kind="text")
        .add_supporting_info(
            f"Columns ({len(table_info.columns)} total)",
            "\n".join(column_details),
            kind="text",
        )
        .add_supporting_info(
            f"Constraints ({len(table_info.constraints)} total)",
            "\n".join(constraint_info) if constraint_info else "None",
            kind="text",
        )
        .add_supporting_info(
            f"Indexes ({len(table_info.indexes)} total)",
            "\n".join(index_info) if index_info else "None",
            kind="text",
        )
        .add_supporting_info(
            "Relationships",
            "\n".join(table_relationships)
            if table_relationships
            else "No foreign key relationships",
            kind="text",
        )
        .add_supporting_info(
            "Related Tables",
            ", ".join(sorted(related_tables)) if related_tables else "None",
            kind="text",
        )
        .add_metadata("table_name", table_info.name)
        .add_metadata("analysis_type", "table_summary")
    )

    return pb.render(RenderOptions(include_toc=False))

import re
from typing import Any, Dict, List, Optional

import sqlparse
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


def format_sql(sql: str) -> str:
    """
    Format SQL code for better readability in documentation.

    Args:
        sql: Raw SQL string to format

    Returns:
        Formatted SQL string with proper indentation and capitalization
    """
    if not sql or not sql.strip():
        return sql

    try:
        # Use sqlparse to format the SQL with nice options
        formatted: str = sqlparse.format(  # type: ignore[no-untyped-call]
            sql,
            reindent=True,  # Add proper indentation
            keyword_case="upper",  # Uppercase SQL keywords
            identifier_case="lower",  # Lowercase identifiers
            strip_comments=False,  # Keep comments
            use_space_around_operators=True,  # Add spaces around operators
            indent_width=2,  # Use 2-space indentation
            indent_after_first=True,  # Indent after first line
            reindent_aligned=True,  # Align continued lines
        )

        # Clean up any excessive whitespace while preserving structure
        lines: List[str] = []
        for line in formatted.split("\n"):
            stripped = line.rstrip()
            if stripped:
                lines.append(stripped)

        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)

    except Exception:
        # If formatting fails, return original SQL
        return sql.strip()


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
    connector = DatabaseConnector(connection_string)
    engine = connector.get_engine()
    inspector = inspect(engine)

    db_type = connector.get_database_type()
    schema_names = inspector.get_schema_names() or ["public"]

    schemas = []
    total_tables = 0
    total_views = 0
    total_stored_procedures = 0
    total_triggers = 0
    total_indexes = 0

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

        # Get stored procedures for this schema
        stored_procedures = get_stored_procedures_tool(connection_string, schema_name)
        total_stored_procedures += len(stored_procedures)

        # Count triggers and indexes across all tables in this schema
        schema_triggers = 0
        schema_indexes = 0
        for table_name in table_names:
            # Get triggers for this table
            table_triggers = get_triggers_tool(
                connection_string, table_name, schema_name
            )
            schema_triggers += len(table_triggers)

            # Get indexes for this table
            table_indexes = inspector.get_indexes(table_name, schema=schema_name)
            schema_indexes += len(table_indexes)

        total_triggers += schema_triggers
        total_indexes += schema_indexes

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
                stored_procedures=stored_procedures,
                relationships=[],
            )
        )

    return DatabaseOverview(
        name=engine.url.database or "unknown",
        database_type=db_type,
        schemas=schemas,
        total_tables=total_tables,
        total_views=total_views,
        total_stored_procedures=total_stored_procedures,
        total_triggers=total_triggers,
        total_indexes=total_indexes,
    )


def get_table_schema_tool(
    connection_string: str, table_name: str, schema_name: Optional[str] = None
) -> TableInfo:
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
        type_str = str(col_data["type"])
        data_type, max_length, precision, scale = _extract_type_info(type_str)

        columns.append(
            ColumnInfo(
                name=col_name,
                data_type=data_type,
                max_length=max_length,
                precision=precision,
                scale=scale,
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

    # Get foreign key constraints with proper ON DELETE/UPDATE info
    fk_constraints = get_foreign_key_constraints_tool(
        connector, table_name, schema_name
    )
    constraints.extend(fk_constraints)

    # Add CHECK constraints
    check_constraints = get_check_constraints_tool(connector, table_name, schema_name)
    constraints.extend(check_constraints)

    index_info: List[IndexInfo] = []
    for idx in indexes:
        # Check if this index is the primary key index
        idx_columns = [col for col in idx["column_names"] if col is not None]
        is_primary_key_index = (
            idx["unique"]
            and set(idx_columns) == pk_columns
            and len(idx_columns) == len(pk_columns)
        )

        index_info.append(
            IndexInfo(
                name=idx["name"] or f"{table_name}_idx_{len(index_info)}",
                table_name=table_name,
                index_type=IndexType.PRIMARY
                if is_primary_key_index
                else (IndexType.UNIQUE if idx["unique"] else IndexType.INDEX),
                columns=idx_columns,
                is_unique=idx["unique"],
                is_primary=is_primary_key_index,
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
                # Use actual COUNT(*) for accurate row count
                full_table_name = (
                    f'"{schema_name}"."{table_name}"'
                    if schema_name
                    else f'"{table_name}"'
                )
                count_query = f"SELECT COUNT(*) as row_count FROM {full_table_name}"
                count_result = connector.execute_safe_sql(count_query)
                if count_result and count_result[0]["row_count"] is not None:
                    row_count = int(count_result[0]["row_count"])

                # Try to get table size
                size_query = (
                    f"SELECT pg_total_relation_size('{full_table_name}') as size_bytes"
                )
                size_result = connector.execute_safe_sql(size_query)
                if size_result and size_result[0]["size_bytes"] is not None:
                    size_bytes = int(size_result[0]["size_bytes"])

            except Exception:
                # Fallback to estimate if COUNT(*) fails (e.g., on very large tables)
                try:
                    estimate_query = f"SELECT reltuples::bigint as row_count FROM pg_class WHERE relname = '{table_name}'"
                    estimate_result = connector.execute_safe_sql(estimate_query)
                    if estimate_result and estimate_result[0]["row_count"] is not None:
                        row_count = max(
                            0, int(estimate_result[0]["row_count"])
                        )  # Ensure non-negative
                except Exception:
                    pass

        elif db_type == DatabaseType.MYSQL:
            # Get row count and size for MySQL
            try:
                # Use actual COUNT(*) for accurate row count
                full_table_name = (
                    f"`{schema_name}`.`{table_name}`"
                    if schema_name
                    else f"`{table_name}`"
                )
                count_query = f"SELECT COUNT(*) as row_count FROM {full_table_name}"
                count_result = connector.execute_safe_sql(count_query)
                if count_result and count_result[0]["row_count"] is not None:
                    row_count = int(count_result[0]["row_count"])

                # Get table size from information_schema
                size_query = f"""
                    SELECT 
                        data_length + index_length as size_bytes
                    FROM information_schema.tables
                    WHERE table_name = '{table_name}' 
                    AND table_schema = '{schema_name or "DATABASE()"}'
                """
                size_result = connector.execute_safe_sql(size_query)
                if size_result and size_result[0]["size_bytes"] is not None:
                    size_bytes = int(size_result[0]["size_bytes"])
            except Exception:
                # Fallback to information_schema estimate
                try:
                    estimate_query = f"""
                        SELECT table_rows as row_count
                        FROM information_schema.tables
                        WHERE table_name = '{table_name}' 
                        AND table_schema = '{schema_name or "DATABASE()"}'
                    """
                    estimate_result = connector.execute_safe_sql(estimate_query)
                    if estimate_result and estimate_result[0]["row_count"] is not None:
                        row_count = max(0, int(estimate_result[0]["row_count"]))
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
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_relationships(connector, schema_name)
    else:
        # Fallback to SQLAlchemy inspector for other databases
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


def _get_postgresql_relationships(
    connector: DatabaseConnector, schema_name: Optional[str] = None
) -> List[RelationshipInfo]:
    """Get foreign key relationships for PostgreSQL with proper ON DELETE/UPDATE detection."""
    schema_filter = f"AND n.nspname = '{schema_name}'" if schema_name else ""

    sql = f"""
    SELECT 
        tc.constraint_name,
        tc.table_name as source_table,
        kcu.column_name as source_column,
        ccu.table_name as target_table,
        ccu.column_name as target_column,
        rc.delete_rule as on_delete,
        rc.update_rule as on_update
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu 
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    JOIN information_schema.referential_constraints rc 
        ON tc.constraint_name = rc.constraint_name
        AND tc.table_schema = rc.constraint_schema
    JOIN pg_namespace n ON n.nspname = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
    {schema_filter}
    ORDER BY tc.table_name, tc.constraint_name
    """

    try:
        results = connector.execute_safe_sql(sql)
        relationships = []

        for row in results:
            # Convert SQL standard values to more readable format
            on_delete = None
            if row["on_delete"] and row["on_delete"] != "NO ACTION":
                on_delete = row["on_delete"]

            on_update = None
            if row["on_update"] and row["on_update"] != "NO ACTION":
                on_update = row["on_update"]

            relationships.append(
                RelationshipInfo(
                    source_table=row["source_table"],
                    source_column=row["source_column"],
                    target_table=row["target_table"],
                    target_column=row["target_column"],
                    constraint_name=row["constraint_name"],
                    on_delete=on_delete,
                    on_update=on_update,
                )
            )

        return relationships
    except Exception:
        # Fallback to original method if query fails
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
    pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
    pk_columns = set(pk_constraint.get("constrained_columns", []))

    indexes: List[IndexInfo] = []
    for idx_data in indexes_data:
        # Check if this index is the primary key index
        idx_columns = [col for col in idx_data["column_names"] if col is not None]
        is_primary_key_index = (
            idx_data["unique"]
            and set(idx_columns) == pk_columns
            and len(idx_columns) == len(pk_columns)
        )

        indexes.append(
            IndexInfo(
                name=idx_data["name"] or f"{table_name}_idx_{len(indexes)}",
                table_name=table_name,
                index_type=IndexType.PRIMARY
                if is_primary_key_index
                else (IndexType.UNIQUE if idx_data["unique"] else IndexType.INDEX),
                columns=idx_columns,
                is_unique=idx_data["unique"],
                is_primary=is_primary_key_index,
            )
        )

    return indexes


def get_triggers_tool(
    connection_string: str, table_name: str, schema_name: Optional[str] = None
) -> List[TriggerInfo]:
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
    connector = DatabaseConnector(connection_string)
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_functions(connector, schema_name)
    elif db_type == DatabaseType.MYSQL:
        return _get_mysql_procedures(connector, schema_name)
    else:
        return []


def get_check_constraints_tool(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str] = None
) -> List[ConstraintInfo]:
    """Get CHECK constraints for a table."""
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_check_constraints(connector, table_name, schema_name)
    elif db_type == DatabaseType.MYSQL:
        return _get_mysql_check_constraints(connector, table_name, schema_name)
    else:
        return []


def get_foreign_key_constraints_tool(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str] = None
) -> List[ConstraintInfo]:
    """Get foreign key constraints for a table with proper ON DELETE/UPDATE info."""
    db_type = connector.get_database_type()

    if db_type == DatabaseType.POSTGRESQL:
        return _get_postgresql_foreign_key_constraints(
            connector, table_name, schema_name
        )
    else:
        # Fallback to SQLAlchemy inspector for other databases
        engine = connector.get_engine()
        inspector = inspect(engine)
        foreign_keys = inspector.get_foreign_keys(table_name, schema=schema_name)

        constraints = []
        for fk in foreign_keys:
            constraints.append(
                ConstraintInfo(
                    name=fk["name"] or f"{table_name}_fk",
                    type=ConstraintType.FOREIGN_KEY,
                    columns=fk["constrained_columns"],
                    referenced_table=fk["referred_table"],
                    referenced_columns=fk["referred_columns"],
                    on_delete=str(fk.get("ondelete")) if fk.get("ondelete") else None,
                    on_update=str(fk.get("onupdate")) if fk.get("onupdate") else None,
                )
            )
        return constraints


def _get_postgresql_foreign_key_constraints(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[ConstraintInfo]:
    """Get foreign key constraints for PostgreSQL with proper ON DELETE/UPDATE detection."""
    schema_filter = f"AND tc.table_schema = '{schema_name}'" if schema_name else ""

    sql = f"""
    SELECT 
        tc.constraint_name,
        array_agg(kcu.column_name ORDER BY kcu.ordinal_position) as constrained_columns,
        ccu.table_name as referenced_table,
        array_agg(ccu.column_name ORDER BY kcu.ordinal_position) as referenced_columns,
        rc.delete_rule as on_delete,
        rc.update_rule as on_update
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu 
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    JOIN information_schema.referential_constraints rc 
        ON tc.constraint_name = rc.constraint_name
        AND tc.table_schema = rc.constraint_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = '{table_name}'
    {schema_filter}
    GROUP BY tc.constraint_name, ccu.table_name, rc.delete_rule, rc.update_rule
    ORDER BY tc.constraint_name
    """

    try:
        results = connector.execute_safe_sql(sql)
        constraints = []

        for row in results:
            # Convert SQL standard values to more readable format
            on_delete = None
            if row["on_delete"] and row["on_delete"] != "NO ACTION":
                on_delete = row["on_delete"]

            on_update = None
            if row["on_update"] and row["on_update"] != "NO ACTION":
                on_update = row["on_update"]

            # Handle column arrays
            constrained_columns = []
            if row["constrained_columns"]:
                if isinstance(row["constrained_columns"], list):
                    constrained_columns = row["constrained_columns"]
                else:
                    # Parse PostgreSQL array format
                    import re

                    col_match = re.findall(r"[^{},]+", str(row["constrained_columns"]))
                    constrained_columns = [
                        col.strip('"') for col in col_match if col.strip()
                    ]

            referenced_columns = []
            if row["referenced_columns"]:
                if isinstance(row["referenced_columns"], list):
                    referenced_columns = row["referenced_columns"]
                else:
                    # Parse PostgreSQL array format
                    import re

                    col_match = re.findall(r"[^{},]+", str(row["referenced_columns"]))
                    referenced_columns = [
                        col.strip('"') for col in col_match if col.strip()
                    ]

            constraints.append(
                ConstraintInfo(
                    name=row["constraint_name"],
                    type=ConstraintType.FOREIGN_KEY,
                    columns=constrained_columns,
                    referenced_table=row["referenced_table"],
                    referenced_columns=referenced_columns,
                    on_delete=on_delete,
                    on_update=on_update,
                )
            )

        return constraints
    except Exception:
        return []


def _get_postgresql_check_constraints(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[ConstraintInfo]:
    """Get CHECK constraints for PostgreSQL."""
    schema_filter = f"AND n.nspname = '{schema_name}'" if schema_name else ""

    sql = f"""
    SELECT 
        con.conname as constraint_name,
        pg_get_constraintdef(con.oid) as constraint_definition,
        ARRAY(
            SELECT attname 
            FROM pg_attribute 
            WHERE attrelid = con.conrelid 
            AND attnum = ANY(con.conkey)
        ) as constrained_columns
    FROM pg_constraint con
    JOIN pg_class c ON con.conrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE c.relname = '{table_name}'
    AND con.contype = 'c'  -- CHECK constraints
    {schema_filter}
    ORDER BY con.conname
    """

    try:
        results = connector.execute_safe_sql(sql)
        constraints = []

        for row in results:
            # Extract the CHECK clause from the constraint definition
            definition = row["constraint_definition"] or ""
            check_clause = None
            if definition.startswith("CHECK"):
                # Remove "CHECK " prefix and outer parentheses
                check_clause = definition[6:].strip()
                if check_clause.startswith("(") and check_clause.endswith(")"):
                    check_clause = check_clause[1:-1]

            # Handle column names array (PostgreSQL returns arrays as strings)
            columns = []
            col_array = row["constrained_columns"]
            if col_array:
                if isinstance(col_array, str):
                    # Parse PostgreSQL array format: {col1,col2}
                    import re

                    col_match = re.findall(r"[^{},]+", col_array)
                    columns = [col.strip('"') for col in col_match if col.strip()]
                elif isinstance(col_array, list):
                    columns = col_array

            constraints.append(
                ConstraintInfo(
                    name=row["constraint_name"],
                    type=ConstraintType.CHECK,
                    columns=columns,
                    check_clause=check_clause,
                )
            )

        return constraints
    except Exception:
        return []


def _get_mysql_check_constraints(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[ConstraintInfo]:
    """Get CHECK constraints for MySQL."""
    schema_filter = (
        f"AND table_schema = '{schema_name}'"
        if schema_name
        else "AND table_schema = DATABASE()"
    )

    sql = f"""
    SELECT 
        constraint_name,
        check_clause
    FROM information_schema.check_constraints
    WHERE table_name = '{table_name}'
    {schema_filter}
    ORDER BY constraint_name
    """

    try:
        results = connector.execute_safe_sql(sql)
        constraints = []

        for row in results:
            constraints.append(
                ConstraintInfo(
                    name=row["constraint_name"],
                    type=ConstraintType.CHECK,
                    columns=[],  # MySQL doesn't easily provide column info for CHECK constraints
                    check_clause=row["check_clause"],
                )
            )

        return constraints
    except Exception:
        return []


def _extract_type_info(
    type_str: str,
) -> tuple[ColumnType, Optional[int], Optional[int], Optional[int]]:
    """
    Extract type information including length, precision, and scale from type string.

    Returns:
        tuple: (data_type, max_length, precision, scale)
    """
    type_lower = type_str.lower()
    max_length = None
    precision = None
    scale = None

    # Extract numeric info from parentheses - handle patterns like VARCHAR(50), DECIMAL(10,2)
    import re

    params_match = re.search(r"\(([^)]+)\)", type_str)
    if params_match:
        params_str = params_match.group(1)
        if "," in params_str:
            # Precision and scale (e.g., DECIMAL(10,2))
            parts = params_str.split(",")
            try:
                precision = int(parts[0].strip())
                scale = int(parts[1].strip())
            except (ValueError, IndexError):
                pass
        else:
            # Single length parameter (e.g., VARCHAR(50))
            try:
                max_length = int(params_str.strip())
            except ValueError:
                pass

    # Determine the base type
    if "int" in type_lower:
        if "bigint" in type_lower:
            return ColumnType.BIGINT, max_length, precision, scale
        elif "smallint" in type_lower:
            return ColumnType.SMALLINT, max_length, precision, scale
        return ColumnType.INTEGER, max_length, precision, scale
    elif "varchar" in type_lower:
        return ColumnType.VARCHAR, max_length, precision, scale
    elif "char" in type_lower and "varchar" not in type_lower:
        # Pure CHAR type (not VARCHAR)
        return ColumnType.CHAR, max_length, precision, scale
    elif "text" in type_lower:
        return ColumnType.TEXT, max_length, precision, scale
    elif any(t in type_lower for t in ["decimal", "numeric"]):
        return ColumnType.DECIMAL, max_length, precision, scale
    elif any(t in type_lower for t in ["float", "double", "real"]):
        return ColumnType.FLOAT, max_length, precision, scale
    elif any(t in type_lower for t in ["bool", "boolean"]):
        return ColumnType.BOOLEAN, max_length, precision, scale
    elif "timestamp" in type_lower:
        return ColumnType.TIMESTAMP, max_length, precision, scale
    elif "time" in type_lower:
        return ColumnType.TIME, max_length, precision, scale
    elif "date" in type_lower:
        return ColumnType.DATE, max_length, precision, scale
    elif "json" in type_lower:
        return ColumnType.JSON, max_length, precision, scale
    elif any(t in type_lower for t in ["blob", "binary"]):
        return ColumnType.BLOB, max_length, precision, scale
    elif "uuid" in type_lower:
        return ColumnType.UUID, max_length, precision, scale
    elif "array" in type_lower:
        return ColumnType.ARRAY, max_length, precision, scale

    return ColumnType.OTHER, max_length, precision, scale


def _map_column_type(type_str: str) -> ColumnType:
    """Legacy function for backwards compatibility."""
    data_type, _, _, _ = _extract_type_info(type_str)
    return data_type


def _get_postgresql_triggers(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[TriggerInfo]:
    # Use a more comprehensive query that gets trigger details from pg_trigger
    schema_condition = f"AND n.nspname = '{schema_name}'" if schema_name else ""
    sql = f"""
    SELECT 
        t.tgname as trigger_name,
        c.relname as table_name,
        n.nspname as schema_name,
        p.proname as function_name,
        CASE 
            WHEN t.tgtype & 2 != 0 THEN 'before'
            WHEN t.tgtype & 64 != 0 THEN 'instead_of'
            ELSE 'after'
        END as timing,
        CASE 
            WHEN t.tgtype & 4 != 0 THEN 'insert'
            WHEN t.tgtype & 8 != 0 THEN 'delete'
            WHEN t.tgtype & 16 != 0 THEN 'update'
            WHEN t.tgtype & 32 != 0 THEN 'truncate'
            ELSE 'unknown'
        END as event,
        CASE t.tgenabled
            WHEN 'O' THEN true
            WHEN 'D' THEN false
            WHEN 'R' THEN true
            WHEN 'A' THEN true
            ELSE false
        END as is_enabled,
        pg_get_triggerdef(t.oid) as definition
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    WHERE c.relname = '{table_name}' 
    AND NOT t.tgisinternal
    {schema_condition}
    ORDER BY t.tgname
    """

    try:
        results = connector.execute_safe_sql(sql)
        triggers = []

        for row in results:
            # Import the enums at the function level to avoid circular imports
            from .models import TriggerEvent, TriggerTiming

            # Map event string to enum
            event_str = row["event"].lower()
            try:
                event = TriggerEvent(event_str)
            except ValueError:
                # Default to INSERT if we can't map the event
                event = TriggerEvent.INSERT

            # Map timing string to enum
            timing_str = row["timing"].lower()
            try:
                timing = TriggerTiming(timing_str)
            except ValueError:
                # Default to AFTER if we can't map the timing
                timing = TriggerTiming.AFTER

            triggers.append(
                TriggerInfo(
                    name=row["trigger_name"],
                    table_name=table_name,
                    event=event,
                    timing=timing,
                    definition=row["definition"] or "",
                    is_enabled=row["is_enabled"],
                    description=f"Trigger function: {row['function_name']}",
                )
            )

        return triggers
    except Exception:
        # Fall back to the information_schema approach if the pg_trigger query fails
        return _get_postgresql_triggers_fallback(connector, table_name, schema_name)


def _get_postgresql_triggers_fallback(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[TriggerInfo]:
    """Fallback to information_schema if pg_trigger query fails."""
    from .models import TriggerEvent, TriggerTiming

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
            # Map event string to enum with fallback
            event_str = row["event_manipulation"].lower()
            try:
                event = TriggerEvent(event_str)
            except ValueError:
                event = TriggerEvent.INSERT

            # Map timing string to enum with fallback
            timing_str = row["action_timing"].lower()
            try:
                timing = TriggerTiming(timing_str)
            except ValueError:
                timing = TriggerTiming.AFTER

            triggers.append(
                TriggerInfo(
                    name=row["trigger_name"],
                    table_name=table_name,
                    event=event,
                    timing=timing,
                    definition=row["action_statement"] or "",
                )
            )

        return triggers
    except Exception:
        return []


def _get_mysql_triggers(
    connector: DatabaseConnector, table_name: str, schema_name: Optional[str]
) -> List[TriggerInfo]:
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
    schema_filter = f"AND n.nspname = '{schema_name}'" if schema_name else ""
    sql = f"""
    SELECT 
        p.proname as name,
        n.nspname as schema_name,
        CASE p.prokind
            WHEN 'f' THEN 'function'
            WHEN 'p' THEN 'procedure'
            WHEN 'a' THEN 'aggregate'
            WHEN 'w' THEN 'window'
            ELSE 'function'
        END as routine_type,
        CASE 
            WHEN p.prorettype = 0 THEN 'void'
            ELSE format_type(p.prorettype, NULL)
        END as return_type,
        p.proargnames as arg_names,
        oidvectortypes(p.proargtypes) as arg_types,
        p.pronargs as arg_count,
        pg_get_functiondef(p.oid) as definition,
        l.lanname as language,
        p.proisstrict as is_strict,
        p.prosecdef as security_definer,
        CASE p.provolatile
            WHEN 'i' THEN true  -- immutable
            WHEN 's' THEN true  -- stable
            WHEN 'v' THEN false -- volatile
            ELSE false
        END as is_deterministic,
        obj_description(p.oid, 'pg_proc') as description
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    JOIN pg_language l ON p.prolang = l.oid
    WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1')
    AND p.prokind IN ('f', 'p')  -- functions and procedures only
    {schema_filter}
    ORDER BY n.nspname, p.proname
    """

    try:
        results = connector.execute_safe_sql(sql)
        procedures = []

        for row in results:
            # Parse parameters
            parameters = []
            if row["arg_names"] and row["arg_types"]:
                arg_names = row["arg_names"]
                arg_types = row["arg_types"].split(", ") if row["arg_types"] else []

                # Handle case where arg_names might be a PostgreSQL array string
                if (
                    isinstance(arg_names, str)
                    and arg_names.startswith("{")
                    and arg_names.endswith("}")
                ):
                    # Parse PostgreSQL array format like {arg1,arg2,arg3}
                    names = arg_names[1:-1].split(",") if len(arg_names) > 2 else []
                elif isinstance(arg_names, list):
                    names = arg_names
                else:
                    names = []

                # Create parameter list
                for i, arg_type in enumerate(arg_types):
                    param_name = (
                        names[i] if i < len(names) and names[i] else f"param_{i + 1}"
                    )
                    parameters.append(
                        {
                            "name": param_name,
                            "type": arg_type.strip(),
                            "mode": "IN",  # PostgreSQL default
                        }
                    )

            # Determine security type
            security_type = "DEFINER" if row.get("security_definer") else "INVOKER"

            procedures.append(
                StoredProcedureInfo(
                    name=row["name"],
                    schema_name=row["schema_name"],
                    parameters=parameters,
                    return_type=row["return_type"]
                    if row["return_type"] != "void"
                    else None,
                    definition=row["definition"] or "",
                    language=row["language"] or "sql",
                    is_deterministic=row.get("is_deterministic", False),
                    security_type=security_type,
                    description=row.get("description"),
                )
            )

        return procedures
    except Exception:
        # Fall back to basic query if the comprehensive one fails
        return _get_postgresql_functions_fallback(connector, schema_name)


def _get_postgresql_functions_fallback(
    connector: DatabaseConnector, schema_name: Optional[str]
) -> List[StoredProcedureInfo]:
    """Fallback to basic query if the comprehensive PostgreSQL functions query fails."""
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
                    definition=row["definition"] or "",
                    language="plpgsql",
                )
            )

        return procedures
    except Exception:
        return []


def _get_mysql_procedures(
    connector: DatabaseConnector, schema_name: Optional[str]
) -> List[StoredProcedureInfo]:
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


def generate_trigger_summary_prompt(
    trigger_info: TriggerInfo, table_info: TableInfo
) -> str:
    """Generate AI prompt for analyzing a database trigger."""

    # Extract trigger details
    trigger_metadata = f"""Trigger: {trigger_info.name}
Table: {trigger_info.table_name}
Event: {trigger_info.event.value.upper()}
Timing: {trigger_info.timing.value.upper()}
Enabled: {"Yes" if trigger_info.is_enabled else "No"}
Language: Detected from definition"""

    # Extract table context
    table_context = f"""Table: {table_info.name}
Schema: {table_info.schema_name or "default"}
Type: {table_info.table_type}
Columns: {len(table_info.columns)} total
Primary Keys: {[col.name for col in table_info.columns if col.is_primary_key]}
Foreign Keys: {[col.name for col in table_info.columns if col.is_foreign_key]}"""

    # Extract key columns for context
    key_columns = []
    for col in table_info.columns[:10]:  # Limit to first 10 columns
        detail = f"{col.name}: {col.data_type.value}"
        if col.is_primary_key:
            detail += " (PK)"
        if col.is_foreign_key:
            detail += " (FK)"
        if not col.is_nullable:
            detail += " NOT NULL"
        key_columns.append(detail)

    pb = (
        PromptBuilder()
        .with_title("Database Trigger Analysis and Business Purpose Summary")
        .extend_instructions(
            [
                "Analyze the provided database trigger and its context",
                "Identify the business purpose and logic of this trigger",
                "Determine what business rules or automation this trigger implements",
                "Explain the trigger's role in maintaining data integrity or business processes",
                "Focus on business value rather than technical implementation details",
            ]
        )
        .extend_rules(
            [
                "Base analysis solely on the trigger definition and table structure",
                "Keep the summary concise but informative (2-3 sentences)",
                "Explain the trigger's purpose in business terms",
                "Identify potential performance implications if relevant",
                "Avoid speculation beyond what can be reasonably inferred",
                "Focus on what the trigger accomplishes, not how it's coded",
            ]
        )
        .set_output(
            """
Provide a concise analysis with:
1. A 2-3 sentence summary of what this trigger does and why it exists
2. The business rule or process it implements
3. Any notable implications for data consistency, auditing, or performance

Keep the response focused on business purpose and impact rather than technical details.
            """.strip()
        )
        .add_supporting_info("Trigger Metadata", trigger_metadata, kind="text")
        .add_supporting_info("Table Context", table_context, kind="text")
        .add_supporting_info(
            f"Key Columns ({len(key_columns)} shown)",
            "\n".join(key_columns),
            kind="text",
        )
        .add_supporting_info(
            "Trigger Definition",
            format_sql(trigger_info.definition),
            kind="code",
        )
        .add_metadata("trigger_name", trigger_info.name)
        .add_metadata("table_name", trigger_info.table_name)
        .add_metadata("analysis_type", "trigger_summary")
    )

    return pb.render(RenderOptions(include_toc=False))


def generate_stored_procedure_summary_prompt(
    procedure_info: StoredProcedureInfo, schema_tables: List[TableInfo]
) -> str:
    """Generate AI prompt for analyzing a stored procedure."""

    # Extract procedure details
    parameters_text = []
    for param in procedure_info.parameters:
        param_detail = f"{param.get('name', 'unknown')}: {param.get('type', 'unknown')}"
        if param.get("mode"):
            param_detail += f" ({param['mode']})"
        parameters_text.append(param_detail)

    procedure_metadata = f"""Procedure: {procedure_info.name}
Schema: {procedure_info.schema_name or "default"}
Language: {procedure_info.language or "sql"}
Return Type: {procedure_info.return_type or "void"}
Parameters: {len(procedure_info.parameters)} total
Deterministic: {"Yes" if procedure_info.is_deterministic else "No"}
Security: {procedure_info.security_type or "INVOKER"}"""

    # Schema context - list of available tables
    schema_context = f"""Schema Tables ({len(schema_tables)} total):
{", ".join([table.name for table in schema_tables[:20]])}"""
    if len(schema_tables) > 20:
        schema_context += "..."

    pb = (
        PromptBuilder()
        .with_title("Database Stored Procedure Analysis and Business Purpose Summary")
        .extend_instructions(
            [
                "Analyze the provided stored procedure and its database context",
                "Identify the business function and purpose of this procedure",
                "Determine what business process or operation this procedure performs",
                "Explain the procedure's role in the application's business logic",
                "Focus on business value and functional purpose rather than code implementation",
            ]
        )
        .extend_rules(
            [
                "Base analysis solely on the procedure definition, parameters, and schema context",
                "Keep the summary concise but informative (2-3 sentences)",
                "Explain the procedure's business function in clear terms",
                "Identify the type of operation (data processing, reporting, validation, etc.)",
                "Avoid speculation beyond what can be reasonably inferred from the code",
                "Focus on what the procedure accomplishes for the business",
            ]
        )
        .set_output(
            """
Provide a concise analysis with:
1. A 2-3 sentence summary of what this procedure does and its business purpose
2. The type of operation it performs (e.g., data transformation, business calculation, reporting)
3. Any insights about its role in the application's business processes

Keep the response focused on business functionality rather than technical implementation.
            """.strip()
        )
        .add_supporting_info("Procedure Metadata", procedure_metadata, kind="text")
        .add_supporting_info("Schema Context", schema_context, kind="text")
        .add_supporting_info(
            f"Parameters ({len(procedure_info.parameters)} total)",
            "\n".join(parameters_text) if parameters_text else "None",
            kind="text",
        )
        .add_supporting_info(
            "Procedure Definition",
            format_sql(procedure_info.definition),
            kind="code",
        )
        .add_metadata("procedure_name", procedure_info.name)
        .add_metadata("schema_name", procedure_info.schema_name or "default")
        .add_metadata("analysis_type", "procedure_summary")
    )

    return pb.render(RenderOptions(include_toc=False))

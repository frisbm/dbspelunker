from typing import Any, Dict, List, Optional

from .models import DatabaseType


def format_table_size(size_bytes: Optional[int]) -> str:
    """Format table size in human-readable format."""
    if not size_bytes:
        return "Unknown"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes = int(size_bytes / 1024.0)
    return f"{size_bytes:.1f} PB"


def get_database_specific_queries(db_type: DatabaseType) -> Dict[str, str]:
    """Get database-specific SQL queries for metadata extraction."""
    queries = {
        DatabaseType.POSTGRESQL: {
            "table_sizes": """
                SELECT schemaname, tablename, 
                       pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                       pg_stat_get_tuples_estimate(oid) as row_count
                FROM pg_tables 
                JOIN pg_class ON relname = tablename
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            """,
            "database_size": "SELECT pg_database_size(current_database()) as size_bytes",
            "version": "SELECT version() as version",
        },
        DatabaseType.MYSQL: {
            "table_sizes": """
                SELECT table_schema, table_name,
                       data_length + index_length as size_bytes,
                       table_rows as row_count
                FROM information_schema.tables
                WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
            """,
            "database_size": """
                SELECT SUM(data_length + index_length) as size_bytes
                FROM information_schema.tables
                WHERE table_schema = database()
            """,
            "version": "SELECT version() as version",
        },
        DatabaseType.SQLITE: {
            "table_sizes": """
                SELECT name as table_name, 
                       0 as size_bytes,
                       0 as row_count
                FROM sqlite_master 
                WHERE type = 'table'
            """,
            "database_size": "SELECT 0 as size_bytes",
            "version": "SELECT sqlite_version() as version",
        },
    }

    return queries.get(db_type, queries[DatabaseType.POSTGRESQL])


def normalize_identifier(identifier: str) -> str:
    """Normalize database identifiers for consistent comparison."""
    return identifier.strip().lower()


def extract_constraint_info(constraint_def: str) -> Dict[str, Any]:
    """Extract structured information from constraint definitions."""
    info: Dict[str, Any] = {
        "type": "unknown",
        "columns": [],
        "referenced_table": None,
        "referenced_columns": [],
        "check_clause": None,
    }

    constraint_def = constraint_def.strip().upper()

    if "PRIMARY KEY" in constraint_def:
        info["type"] = "primary_key"
    elif "FOREIGN KEY" in constraint_def:
        info["type"] = "foreign_key"
    elif "UNIQUE" in constraint_def:
        info["type"] = "unique"
    elif "CHECK" in constraint_def:
        info["type"] = "check"
        info["check_clause"] = constraint_def

    return info


def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get nested dictionary values using dot notation."""
    keys = path.split(".")
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def deduplicate_preserving_order(items: List[Any]) -> List[Any]:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def group_by_schema(tables: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group tables by schema name."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for table in tables:
        schema = table.get("schema_name", "public")
        if schema not in grouped:
            grouped[schema] = []
        grouped[schema].append(table)

    return grouped


def calculate_relationship_cardinality(
    source_table: str, target_table: str, relationships: List[Dict[str, Any]]
) -> str:
    """Calculate the cardinality of relationships between tables."""
    source_to_target = sum(
        1
        for r in relationships
        if r["source_table"] == source_table and r["target_table"] == target_table
    )
    target_to_source = sum(
        1
        for r in relationships
        if r["source_table"] == target_table and r["target_table"] == source_table
    )

    if source_to_target > 0 and target_to_source > 0:
        return "many_to_many"
    elif source_to_target == 1 and target_to_source == 0:
        return "one_to_many"
    elif source_to_target == 0 and target_to_source == 1:
        return "many_to_one"
    else:
        return "one_to_one"

from datetime import datetime
from enum import StrEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DatabaseType(StrEnum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"


class ColumnType(StrEnum):
    INTEGER = "integer"
    BIGINT = "bigint"
    SMALLINT = "smallint"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    FLOAT = "float"
    DOUBLE = "double"
    REAL = "real"
    VARCHAR = "varchar"
    CHAR = "char"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    JSON = "json"
    BLOB = "blob"
    UUID = "uuid"
    ARRAY = "array"
    OTHER = "other"


class IndexType(StrEnum):
    PRIMARY = "primary"
    UNIQUE = "unique"
    INDEX = "index"
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    FULLTEXT = "fulltext"


class TriggerEvent(StrEnum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    TRUNCATE = "truncate"


class TriggerTiming(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    INSTEAD_OF = "instead_of"


class ConstraintType(StrEnum):
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    NOT_NULL = "not_null"
    DEFAULT = "default"


class ColumnInfo(BaseModel):
    name: str
    data_type: ColumnType
    is_nullable: bool
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    description: Optional[str] = None


class ConstraintInfo(BaseModel):
    name: str
    type: ConstraintType
    columns: List[str]
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
    check_clause: Optional[str] = None
    description: Optional[str] = None


class IndexInfo(BaseModel):
    name: str
    table_name: str
    index_type: IndexType
    columns: List[str]
    is_unique: bool
    is_primary: bool
    is_clustered: bool = False
    size_bytes: Optional[int] = None
    description: Optional[str] = None


class TriggerInfo(BaseModel):
    name: str
    table_name: str
    event: TriggerEvent
    timing: TriggerTiming
    definition: str
    is_enabled: bool = True
    description: Optional[str] = None


class StoredProcedureInfo(BaseModel):
    name: str
    schema_name: Optional[str] = None
    parameters: List[Dict[str, str]] = Field(default_factory=list)
    return_type: Optional[str] = None
    definition: str
    language: Optional[str] = None
    is_deterministic: bool = False
    security_type: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None


class TableInfo(BaseModel):
    name: str
    schema_name: Optional[str] = None
    table_type: str = "table"
    columns: List[ColumnInfo]
    constraints: List[ConstraintInfo] = Field(default_factory=list)
    indexes: List[IndexInfo] = Field(default_factory=list)
    triggers: List[TriggerInfo] = Field(default_factory=list)
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    relationship_summary: Optional[str] = None


class RelationshipInfo(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    constraint_name: str
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
    relationship_type: str = "one_to_many"


class SchemaInfo(BaseModel):
    name: str
    tables: List[TableInfo]
    views: List[TableInfo] = Field(default_factory=list)
    stored_procedures: List[StoredProcedureInfo] = Field(default_factory=list)
    relationships: List[RelationshipInfo] = Field(default_factory=list)
    description: Optional[str] = None


class DatabaseOverview(BaseModel):
    name: str
    database_type: DatabaseType
    version: Optional[str] = None
    schemas: List[SchemaInfo]
    total_tables: int
    total_views: int = 0
    total_stored_procedures: int = 0
    total_triggers: int = 0
    total_indexes: int = 0
    database_size_bytes: Optional[int] = None
    character_set: Optional[str] = None
    collation: Optional[str] = None
    connection_info: Dict[str, str] = Field(default_factory=dict)


class DocumentationSection(BaseModel):
    title: str
    content: str
    subsections: List["DocumentationSection"] = Field(default_factory=list)


class DocumentationReport(BaseModel):
    database_overview: DatabaseOverview
    executive_summary: str
    table_documentation: List[Dict[str, str]]
    relationship_analysis: str
    index_analysis: str
    performance_insights: List[str] = Field(default_factory=list)
    security_considerations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    sections: List[DocumentationSection] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    generation_metadata: Dict[str, str] = Field(default_factory=dict)


DocumentationSection.model_rebuild()

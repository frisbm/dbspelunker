"""
DBSpelunker - AI-powered database documentation and analysis system.

A multi-agent workflow using Pydantic AI to automatically generate comprehensive
database documentation by analyzing schemas, relationships, indexes, triggers,
and stored procedures.
"""

from .dbspelunker import DBSpelunker
from .genai import GeminiModel
from .models import (
    ColumnInfo,
    DatabaseOverview,
    DocumentationReport,
    IndexInfo,
    RelationshipInfo,
    SchemaInfo,
    StoredProcedureInfo,
    TableInfo,
    TriggerInfo,
)

__version__ = "1.0.0"
__author__ = "DBSpelunker Team"

__all__ = [
    "DBSpelunker",
    "DatabaseOverview",
    "DocumentationReport",
    "SchemaInfo",
    "TableInfo",
    "ColumnInfo",
    "RelationshipInfo",
    "IndexInfo",
    "TriggerInfo",
    "StoredProcedureInfo",
    "GeminiModel",
]

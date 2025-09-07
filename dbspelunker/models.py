from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Dict, List, Optional, Union

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

    def to_markdown(
        self,
        path: Optional[Union[str, Path]] = None,
        include_json_appendix: bool = False,
    ) -> str:
        """
        Render this DocumentationReport to a beautiful, well-structured Markdown document.

        Args:
            path: Optional file path. If provided, the Markdown is also written to this path.
            include_json_appendix: If True, appends a compact JSON snapshot of the model.

        Returns:
            The Markdown string.
        """

        # ----------------------------
        # Local helpers (markdown utils)
        # ----------------------------
        def _esc(v: Optional[str]) -> str:
            if v is None:
                return ""
            # Escape markdown table-breaking chars
            return (
                str(v)
                .replace("\\", "\\\\")
                .replace("|", "\\|")
                .replace("*", "\\*")
                .replace("_", "\\_")
                .replace("`", "\\`")
            )

        def _code(v: Optional[str]) -> str:
            return f"`{_esc(v)}`" if v is not None else ""

        def _slug(s: str) -> str:
            import re

            slug = re.sub(r"[^\w\- ]+", "", s, flags=re.UNICODE).strip().lower()
            slug = re.sub(r"\s+", "-", slug)
            return slug

        def _bytes(n: Optional[int]) -> str:
            if n is None:
                return ""
            step = 1024.0
            units = ["B", "KB", "MB", "GB", "TB", "PB"]
            idx = 0
            f = float(n)
            while f >= step and idx < len(units) - 1:
                f /= step
                idx += 1
            return f"{f:,.2f} {units[idx]}"

        def _dt(d: Optional[datetime]) -> str:
            if not d:
                return ""
            # ISO-like, readable; you can tweak timezone if desired
            return d.strftime("%Y-%m-%d %H:%M:%S")

        def _yn(b: Optional[bool]) -> str:
            return "Yes" if b else "No"

        def _kv_table(rows: List[tuple[str, str]]) -> str:
            # rows: List[(key, value)]
            out = ["| Key | Value |", "| --- | ----- |"]
            for k, v in rows:
                out.append(f"| {_esc(k)} | {_esc(v)} |")
            return "\n".join(out)

        def _md_table(headers: List[str], rows: List[List[str]]) -> str:
            out = [
                "| " + " | ".join(_esc(h) for h in headers) + " |",
                "| " + " | ".join("---" for _ in headers) + " |",
            ]
            for r in rows:
                out.append("| " + " | ".join(_esc(c) for c in r) + " |")
            return "\n".join(out)

        def _truncate_block(sql: str) -> str:
            if sql is None:
                return ""
            s = sql.strip()
            return f"```sql\n{s}\n```"

        def _h(level: int, text: str) -> str:
            return f"{'#' * level} {text}".strip()

        # ----------------------------
        # Begin building the document
        # ----------------------------
        lines: List[str] = []
        db = self.database_overview

        # Title
        title = f"Database Documentation: {db.name}"
        lines.append(_h(1, title))
        lines.append("")

        # Quick badges / meta
        badge = f"- Type: {_code(db.database_type.value)}"
        if db.version:
            badge += f" · Version: {_code(db.version)}"
        if db.character_set:
            badge += f" · Charset: {_code(db.character_set)}"
        if db.collation:
            badge += f" · Collation: {_code(db.collation)}"
        if self.generated_at:
            badge += f" · Generated: {_code(_dt(self.generated_at))}"
        lines.append(badge)
        lines.append("")

        # Optional executive summary
        if (self.executive_summary or "").strip():
            lines.append(_h(2, "Executive Summary"))
            lines.append("")
            lines.append(self.executive_summary.strip())
            lines.append("")

        # Database Overview
        lines.append(_h(2, "Database Overview"))
        lines.append("")
        kv_rows = [
            ("Name", db.name),
            ("Type", db.database_type.value),
            ("Version", db.version or ""),
            ("Total Tables", f"{db.total_tables:,}"),
            ("Total Views", f"{db.total_views:,}"),
            ("Stored Procedures", f"{db.total_stored_procedures:,}"),
            ("Indexes", f"{db.total_indexes:,}"),
            ("Triggers", f"{db.total_triggers:,}"),
            ("Database Size", _bytes(db.database_size_bytes)),
            ("Character Set", db.character_set or ""),
            ("Collation", db.collation or ""),
        ]
        lines.append(_kv_table(kv_rows))
        lines.append("")

        # Table of Contents (top-level)
        toc_sections = [
            "Database Overview",
            "Schemas",
            "Relationships",
            "Indexes",
            "Performance Insights",
            "Security Considerations",
            "Recommendations",
        ]
        if self.sections:
            toc_sections.append("Additional Sections")
        if self.table_documentation:
            toc_sections.append("Table Documentation")
        if db.total_stored_procedures:
            toc_sections.append("Stored Procedures")
        if include_json_appendix:
            toc_sections.append("Appendix: JSON Snapshot")

        lines.append(_h(2, "Table of Contents"))
        lines.append("")
        for sec in toc_sections:
            lines.append(f"- [{sec}](#{_slug(sec)})")
        lines.append("")

        # Schemas, Tables & Views
        lines.append(_h(2, "Schemas"))
        lines.append("")
        for schema in db.schemas:
            lines.append(_h(3, f"Schema: {schema.name}"))
            if (schema.description or "").strip():
                lines.append("")
                lines.append((schema.description or "").strip())
                lines.append("")
            # Quick counts
            lines.append(
                _kv_table(
                    [
                        ("Tables", str(len(schema.tables))),
                        ("Views", str(len(schema.views))),
                        ("Stored Procedures", str(len(schema.stored_procedures))),
                        ("Relationships", str(len(schema.relationships))),
                    ]
                )
            )
            lines.append("")

            # Tables
            if schema.tables:
                lines.append(_h(4, "Tables"))
                lines.append("")
                for t in schema.tables:
                    fq = (
                        f"{schema.name}.{t.name}"
                        if t.schema_name or schema.name
                        else t.name
                    )
                    lines.append(_h(5, f"Table: {fq}"))
                    meta_bits = []
                    if t.table_type:
                        meta_bits.append(f"Type: {_code(t.table_type)}")
                    if t.row_count is not None:
                        meta_bits.append(f"Rows: {_code(f'{t.row_count:,}')}")  # noqa
                    if t.size_bytes is not None:
                        meta_bits.append(f"Size: {_code(_bytes(t.size_bytes))}")
                    if t.created_at:
                        meta_bits.append(f"Created: {_code(_dt(t.created_at))}")
                    if t.modified_at:
                        meta_bits.append(f"Modified: {_code(_dt(t.modified_at))}")
                    if meta_bits:
                        lines.append("- " + " · ".join(meta_bits))
                    if (t.ai_summary or "").strip():
                        lines.append("")
                        lines.append(f"> {(t.ai_summary or '').strip()}")
                    if (t.description or "").strip():
                        lines.append("")
                        lines.append((t.description or "").strip())

                    # Columns
                    if t.columns:
                        lines.append("")
                        lines.append(_h(6, "Columns"))
                        col_headers = [
                            "Column",
                            "Type",
                            "Nullable",
                            "Default",
                            "PK",
                            "FK",
                            "Details",
                            "Description",
                        ]
                        col_rows = []
                        for c in t.columns:
                            details = []
                            if c.max_length is not None:
                                details.append(f"len={c.max_length}")
                            if c.precision is not None:
                                details.append(f"p={c.precision}")
                            if c.scale is not None:
                                details.append(f"s={c.scale}")
                            if c.is_foreign_key:
                                if c.foreign_key_table:
                                    fk = f"{c.foreign_key_table}"
                                    if c.foreign_key_column:
                                        fk += f"({c.foreign_key_column})"
                                    details.append(f"fk→{fk}")
                            col_rows.append(
                                [
                                    c.name,
                                    c.data_type.value,
                                    _yn(c.is_nullable),
                                    c.default_value or "",
                                    _yn(c.is_primary_key),
                                    _yn(c.is_foreign_key),
                                    ", ".join(details),
                                    c.description or "",
                                ]
                            )
                        lines.append(_md_table(col_headers, col_rows))

                    # Constraints
                    if t.constraints:
                        lines.append("")
                        lines.append(_h(6, "Constraints"))
                        cons_headers = [
                            "Name",
                            "Type",
                            "Columns",
                            "Details",
                            "Description",
                        ]
                        cons_rows = []
                        for cst in t.constraints:
                            details = []
                            if cst.referenced_table:
                                ref_cols = ", ".join(cst.referenced_columns or [])
                                details.append(
                                    f"ref {cst.referenced_table}({ref_cols})"
                                    if ref_cols
                                    else f"ref {cst.referenced_table}"
                                )
                            if cst.on_delete:
                                details.append(f"on_delete={cst.on_delete}")
                            if cst.on_update:
                                details.append(f"on_update={cst.on_update}")
                            if cst.check_clause:
                                details.append(f"check={cst.check_clause}")
                            cons_rows.append(
                                [
                                    cst.name,
                                    cst.type.value,
                                    ", ".join(cst.columns),
                                    "; ".join(details),
                                    cst.description or "",
                                ]
                            )
                        lines.append(_md_table(cons_headers, cons_rows))

                    # Indexes
                    if t.indexes:
                        lines.append("")
                        lines.append(_h(6, "Indexes"))
                        idx_headers = [
                            "Name",
                            "Type",
                            "Columns",
                            "Unique",
                            "Primary",
                            "Clustered",
                            "Size",
                            "Description",
                        ]
                        idx_rows = []
                        for idx in t.indexes:
                            idx_rows.append(
                                [
                                    idx.name,
                                    idx.index_type.value,
                                    ", ".join(idx.columns),
                                    _yn(idx.is_unique),
                                    _yn(idx.is_primary),
                                    _yn(idx.is_clustered),
                                    _bytes(idx.size_bytes),
                                    idx.description or "",
                                ]
                            )
                        lines.append(_md_table(idx_headers, idx_rows))

                    # Triggers
                    if t.triggers:
                        lines.append("")
                        lines.append(_h(6, "Triggers"))
                        trg_headers = [
                            "Name",
                            "Timing",
                            "Event",
                            "Enabled",
                            "Description",
                        ]
                        trg_rows = []
                        for trg in t.triggers:
                            trg_rows.append(
                                [
                                    trg.name,
                                    trg.timing.value,
                                    trg.event.value,
                                    _yn(trg.is_enabled),
                                    trg.description or "",
                                ]
                            )
                        lines.append(_md_table(trg_headers, trg_rows))
                        # Include (truncated) definitions below table for readability
                        for trg in t.triggers:
                            if trg.definition:
                                lines.append("")
                                lines.append(_h(7, f"Trigger Definition: {trg.name}"))
                                lines.append(_truncate_block(trg.definition))

                    # Relationships touching this table (from schema.relationships)
                    rels = [
                        r
                        for r in schema.relationships
                        if r.source_table == t.name or r.target_table == t.name
                    ]
                    if rels:
                        lines.append("")
                        lines.append(_h(6, "Related Tables"))
                        rel_headers = [
                            "From",
                            "Column",
                            "To",
                            "Column",
                            "Constraint",
                            "On Delete",
                            "On Update",
                            "Type",
                        ]
                        rel_rows = []
                        for r in rels:
                            rel_rows.append(
                                [
                                    r.source_table,
                                    r.source_column,
                                    r.target_table,
                                    r.target_column,
                                    r.constraint_name,
                                    r.on_delete or "",
                                    r.on_update or "",
                                    r.relationship_type,
                                ]
                            )
                        lines.append(_md_table(rel_headers, rel_rows))

                    # Relationship summary text
                    if (t.relationship_summary or "").strip():
                        lines.append("")
                        lines.append(_h(6, "Relationship Summary"))
                        lines.append((t.relationship_summary or "").strip())

                    lines.append("")  # spacing between tables

            # Views
            if schema.views:
                lines.append(_h(4, "Views"))
                lines.append("")
                for v in schema.views:
                    fq = (
                        f"{schema.name}.{v.name}"
                        if v.schema_name or schema.name
                        else v.name
                    )
                    lines.append(_h(5, f"View: {fq}"))
                    meta_bits = []
                    if v.row_count is not None:
                        meta_bits.append(f"Rows: {_code(f'{v.row_count:,}')}")
                    if v.size_bytes is not None:
                        meta_bits.append(f"Size: {_code(_bytes(v.size_bytes))}")
                    if v.created_at:
                        meta_bits.append(f"Created: {_code(_dt(v.created_at))}")
                    if v.modified_at:
                        meta_bits.append(f"Modified: {_code(_dt(v.modified_at))}")
                    if meta_bits:
                        lines.append("- " + " · ".join(meta_bits))
                    if (v.description or "").strip():
                        lines.append("")
                        lines.append((v.description or "").strip())
                    lines.append("")

            # Stored Procedures (within schema)
            if schema.stored_procedures:
                lines.append(_h(4, "Stored Procedures"))
                lines.append("")
                sp_headers = [
                    "Name",
                    "Returns",
                    "Language",
                    "Deterministic",
                    "Created",
                    "Modified",
                ]
                sp_rows = []
                for sp in schema.stored_procedures:
                    sp_rows.append(
                        [
                            sp.name,
                            sp.return_type or "",
                            sp.language or "",
                            _yn(sp.is_deterministic),
                            _dt(sp.created_at),
                            _dt(sp.modified_at),
                        ]
                    )
                lines.append(_md_table(sp_headers, sp_rows))
                # Definitions
                for sp in schema.stored_procedures:
                    if sp.definition:
                        lines.append("")
                        lines.append(_h(5, f"Procedure Definition: {sp.name}"))
                        lines.append(_truncate_block(sp.definition))
                        if (sp.description or "").strip():
                            lines.append("")
                            lines.append((sp.description or "").strip())
                lines.append("")

        # Relationships (global)
        lines.append(_h(2, "Relationships"))
        lines.append("")
        if (self.relationship_analysis or "").strip():
            lines.append(self.relationship_analysis.strip())
            lines.append("")
        all_rels: List[RelationshipInfo] = []
        for schema in db.schemas:
            all_rels.extend(schema.relationships)
        if all_rels:
            rel_headers = [
                "From",
                "Column",
                "To",
                "Column",
                "Constraint",
                "On Delete",
                "On Update",
                "Type",
            ]
            rel_rows = []
            for r in all_rels:
                rel_rows.append(
                    [
                        r.source_table,
                        r.source_column,
                        r.target_table,
                        r.target_column,
                        r.constraint_name,
                        r.on_delete or "",
                        r.on_update or "",
                        r.relationship_type,
                    ]
                )
            lines.append(_md_table(rel_headers, rel_rows))
            lines.append("")

        # Indexes (global)
        lines.append(_h(2, "Indexes"))
        lines.append("")
        if (self.index_analysis or "").strip():
            lines.append(self.index_analysis.strip())
            lines.append("")
        # Aggregate index stats across all tables
        from collections import Counter

        idx_counter: Counter[str] = Counter()
        unique_count = 0
        primary_count = 0
        clustered_count = 0
        size_total = 0
        for schema in db.schemas:
            for t in schema.tables:
                for ix in t.indexes:
                    idx_counter[ix.index_type.value] += 1
                    unique_count += 1 if ix.is_unique else 0
                    primary_count += 1 if ix.is_primary else 0
                    clustered_count += 1 if ix.is_clustered else 0
                    size_total += ix.size_bytes or 0
        if sum(idx_counter.values()) > 0:
            idx_rows = [[k, f"{v:,}"] for k, v in sorted(idx_counter.items())]
            lines.append(_md_table(["Index Type", "Count"], idx_rows))
            lines.append("")
            lines.append(
                _kv_table(
                    [
                        ("Unique Indexes", f"{unique_count:,}"),
                        ("Primary Indexes", f"{primary_count:,}"),
                        ("Clustered Indexes", f"{clustered_count:,}"),
                        ("Estimated Index Storage", _bytes(size_total)),
                    ]
                )
            )
            lines.append("")

        # Performance Insights
        lines.append(_h(2, "Performance Insights"))
        lines.append("")
        if self.performance_insights:
            for tip in self.performance_insights:
                lines.append(f"- {tip.strip()}")
        else:
            lines.append("_No specific performance insights were provided._")
        lines.append("")

        # Security Considerations
        lines.append(_h(2, "Security Considerations"))
        lines.append("")
        if self.security_considerations:
            for s in self.security_considerations:
                lines.append(f"- {s.strip()}")
        else:
            lines.append("_No security considerations were provided._")
        lines.append("")

        # Recommendations
        lines.append(_h(2, "Recommendations"))
        lines.append("")
        if self.recommendations:
            for recommendation in self.recommendations:
                # Render as task list to make follow-up easy in GitHub/Markdown
                lines.append(f"- [ ] {recommendation.strip()}")
        else:
            lines.append("_No recommendations were provided._")
        lines.append("")

        # Additional Sections (arbitrary nested sections)
        if self.sections:
            lines.append(_h(2, "Additional Sections"))
            lines.append("")

            def _render_section(sec: DocumentationSection, level: int = 3) -> None:
                lines.append(_h(level, sec.title))
                if (sec.content or "").strip():
                    lines.append("")
                    lines.append(sec.content.strip())
                for sub in sec.subsections or []:
                    lines.append("")
                    _render_section(sub, level=level + 1)

            for section in self.sections:
                _render_section(section, level=3)
                lines.append("")

        # Table Documentation (free-form per-table docs the caller may have supplied)
        if self.table_documentation:
            lines.append(_h(2, "Table Documentation"))
            lines.append("")
            for entry in self.table_documentation:
                # accept common keys
                title = entry.get("table_name") or "Untitled"
                content = (
                    entry.get("content")
                    or entry.get("documentation")
                    or entry.get("markdown")
                    or ""
                )
                lines.append(_h(3, str(title)))
                if content.strip():
                    lines.append("")
                    lines.append(content.strip())
                lines.append("")

        # Generation Metadata
        if self.generation_metadata:
            lines.append(_h(2, "Generation Metadata"))
            lines.append("")
            lines.append(_kv_table(list(self.generation_metadata.items())))
            lines.append("")

        # Optional JSON appendix
        if include_json_appendix:
            lines.append(_h(2, "Appendix: JSON Snapshot"))
            lines.append("")
            json_str = self.model_dump_json(exclude_none=True, indent=2)
            lines.append("```json")
            lines.append(json_str)
            lines.append("```")
            lines.append("")

        markdown = "\n".join(lines).rstrip() + "\n"

        # Optionally write to disk
        if path is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(markdown, encoding="utf-8")

        return markdown


DocumentationSection.model_rebuild()

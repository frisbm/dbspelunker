from datetime import datetime
from pathlib import Path

from config import load_config
from dbspelunker import DBSpelunker
from dbspelunker.genai import GeminiModel
from dbspelunker.models import DocumentationReport


def format_markdown_documentation(documentation: DocumentationReport) -> str:
    """Format documentation as markdown."""
    md_lines = []

    # Title and overview
    md_lines.append(f"# Database Documentation: {documentation.database_overview.name}")
    md_lines.append("")
    md_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_lines.append("")

    # Executive Summary
    md_lines.append("## Executive Summary")
    md_lines.append("")
    md_lines.append(documentation.executive_summary)
    md_lines.append("")

    # Database Statistics
    md_lines.append("## Database Statistics")
    md_lines.append("")
    md_lines.append(
        f"- **Database Type**: {documentation.database_overview.database_type.value}"
    )
    md_lines.append(
        f"- **Total Tables**: {documentation.database_overview.total_tables}"
    )
    md_lines.append(f"- **Total Views**: {documentation.database_overview.total_views}")
    md_lines.append(
        f"- **Total Stored Procedures**: {documentation.database_overview.total_stored_procedures}"
    )
    md_lines.append(
        f"- **Total Indexes**: {documentation.database_overview.total_indexes}"
    )
    md_lines.append(
        f"- **Total Triggers**: {documentation.database_overview.total_triggers}"
    )

    total_columns = sum(
        len(table.columns)
        for schema in documentation.database_overview.schemas
        for table in schema.tables
    )
    total_relationships = sum(
        len(schema.relationships) for schema in documentation.database_overview.schemas
    )

    md_lines.append(f"- **Total Columns**: {total_columns}")
    md_lines.append(f"- **Total Relationships**: {total_relationships}")
    md_lines.append("")

    # Schemas
    for schema in documentation.database_overview.schemas:
        md_lines.append(f"## Schema: {schema.name}")
        md_lines.append("")

        # Schema summary
        md_lines.append(f"- **Tables**: {len(schema.tables)}")
        md_lines.append(f"- **Views**: {len(schema.views)}")
        md_lines.append(f"- **Stored Procedures**: {len(schema.stored_procedures)}")
        md_lines.append(f"- **Relationships**: {len(schema.relationships)}")
        md_lines.append("")

        # Tables
        if schema.tables:
            md_lines.append("### Tables")
            md_lines.append("")

            for table in schema.tables:
                md_lines.append(f"#### {table.name}")
                md_lines.append("")

                # Basic info
                md_lines.append(f"**Type**: {table.table_type}")
                md_lines.append("")

                # AI Analysis
                if table.ai_summary:
                    md_lines.append("**AI Analysis**:")
                    md_lines.append("")
                    md_lines.append(table.ai_summary)
                    md_lines.append("")

                # Relationships
                if table.relationship_summary:
                    md_lines.append("**Relationships**:")
                    md_lines.append("")
                    md_lines.append(table.relationship_summary)
                    md_lines.append("")

                # Technical Details
                md_lines.append("**Technical Details**:")
                md_lines.append("")
                md_lines.append(f"- **Columns**: {len(table.columns)}")

                # Primary keys
                pk_columns = [col.name for col in table.columns if col.is_primary_key]
                if pk_columns:
                    md_lines.append(f"- **Primary Keys**: {', '.join(pk_columns)}")

                # Foreign keys
                fk_columns = [col.name for col in table.columns if col.is_foreign_key]
                if fk_columns:
                    md_lines.append(f"- **Foreign Keys**: {', '.join(fk_columns)}")

                md_lines.append(f"- **Constraints**: {len(table.constraints)}")
                md_lines.append(f"- **Indexes**: {len(table.indexes)}")
                md_lines.append(f"- **Triggers**: {len(table.triggers)}")

                if table.row_count is not None:
                    md_lines.append(f"- **Row Count**: {table.row_count:,}")

                if table.size_bytes is not None:
                    md_lines.append(f"- **Size**: {table.size_bytes:,} bytes")

                md_lines.append("")

                # Column Details
                if table.columns:
                    md_lines.append("**Columns**:")
                    md_lines.append("")
                    md_lines.append(
                        "| Name | Type | Nullable | Default | PK | FK | Description |"
                    )
                    md_lines.append(
                        "|------|------|----------|---------|----|----|-------------|"
                    )

                    for col in table.columns:
                        nullable = "Yes" if col.is_nullable else "No"
                        pk = "Yes" if col.is_primary_key else ""
                        fk = "Yes" if col.is_foreign_key else ""
                        default = col.default_value or ""
                        description = col.description or ""

                        md_lines.append(
                            f"| {col.name} | {col.data_type.value} | {nullable} | {default} | {pk} | {fk} | {description} |"
                        )

                    md_lines.append("")

                # Constraints
                if table.constraints:
                    md_lines.append("**Constraints**:")
                    md_lines.append("")
                    for constraint in table.constraints:
                        md_lines.append(
                            f"- **{constraint.name}** ({constraint.type.value}): {', '.join(constraint.columns)}"
                        )
                    md_lines.append("")

                # Indexes
                if table.indexes:
                    md_lines.append("**Indexes**:")
                    md_lines.append("")
                    for index in table.indexes:
                        md_lines.append(
                            f"- **{index.name}** ({index.index_type.value}): {', '.join(index.columns)}"
                        )
                        if index.is_unique:
                            md_lines.append("  - Unique index")
                    md_lines.append("")

                md_lines.append("---")
                md_lines.append("")

    # Relationship Analysis
    md_lines.append("## Relationship Analysis")
    md_lines.append("")
    md_lines.append(documentation.relationship_analysis)
    md_lines.append("")

    # Index Analysis
    md_lines.append("## Index Analysis")
    md_lines.append("")
    md_lines.append(documentation.index_analysis)
    md_lines.append("")

    # Performance Insights
    if documentation.performance_insights:
        md_lines.append("## Performance Insights")
        md_lines.append("")
        for insight in documentation.performance_insights:
            md_lines.append(f"- {insight}")
        md_lines.append("")

    return "\n".join(md_lines)


def main() -> None:
    """Generate comprehensive AI-powered documentation for the entire database."""
    try:
        config = load_config()
        gemini_model = GeminiModel(config)

        spelunker = DBSpelunker(
            gemini_model=gemini_model, db_connection_str=config.db_connection_string
        )

        print("DBSpelunker initialized successfully!")

        overview = spelunker.get_database_overview()
        print(f"Database: {overview.name} ({overview.database_type.value})")
        print(
            f"Found {overview.total_tables} tables across {len(overview.schemas)} schemas"
        )

        print("\nGenerating comprehensive AI-powered documentation...")
        print(
            "This may take several minutes as it analyzes all tables with AI summaries..."
        )

        # Generate full documentation with AI summaries
        documentation = spelunker.generate_full_documentation()

        # Format as markdown
        print("\nFormatting documentation as markdown...")
        markdown_content = format_markdown_documentation(documentation)

        Path("output").mkdir(parents=True, exist_ok=True)
        # Save to markdown file
        with open("output/database_documentation.md", "w") as f:
            f.write(markdown_content)

        print("\nComplete documentation generated successfully!")
        print(f"Database: {documentation.database_overview.name}")
        print(f"Total Tables: {documentation.database_overview.total_tables}")

        total_columns = sum(
            len(table.columns)
            for schema in documentation.database_overview.schemas
            for table in schema.tables
        )
        total_relationships = sum(
            len(schema.relationships)
            for schema in documentation.database_overview.schemas
        )

        print(f"Total Columns: {total_columns}")
        print(f"Total Relationships: {total_relationships}")
        print(f"Total Indexes: {documentation.database_overview.total_indexes}")
        print(f"Total Triggers: {documentation.database_overview.total_triggers}")

        print("\nExecutive Summary Preview:")
        print(documentation.executive_summary[:200] + "...")

        print("\nFull documentation saved to: database_documentation.md")

    except Exception as e:
        print(f"Failed to generate documentation: {str(e)}")
        print("Please check your configuration and database connection")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

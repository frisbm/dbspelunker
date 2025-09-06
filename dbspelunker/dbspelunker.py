import logging
from typing import Optional

from pydantic_ai import Agent

from .agents import (
    create_detail_analyzer_agent,
    create_documentation_agent,
    create_initiator_agent,
    create_schema_explorer_agent,
)
from .genai import GeminiModel
from .models import (
    DatabaseOverview,
    DocumentationReport,
    RelationshipInfo,
    SchemaInfo,
    TableInfo,
)
from .tools import (
    analyze_relationships_tool,
    generate_table_summary_prompt,
    get_database_overview_tool,
    get_table_schema_tool,
)


class DBSpelunker:
    """Main orchestrator for AI-driven database documentation and analysis."""

    def __init__(self, gemini_model: GeminiModel, db_connection_str: str):
        self.gemini_model = gemini_model
        self.db_connection_str = db_connection_str
        self.logger = logging.getLogger(__name__)

        self._validate_connection()

    def _validate_connection(self) -> None:
        """Validate that the database connection string is accessible."""
        try:
            overview = get_database_overview_tool(self.db_connection_str)
            self.logger.info(
                f"Successfully connected to {overview.database_type.value} database: {overview.name}"
            )
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")

    def get_database_overview(self) -> DatabaseOverview:
        """Get high-level database overview without full analysis."""
        return get_database_overview_tool(self.db_connection_str)

    def analyze_table(
        self, table_name: str, schema_name: Optional[str] = None
    ) -> TableInfo:
        """Analyze a specific table in detail."""
        return get_table_schema_tool(self.db_connection_str, table_name, schema_name)

    def generate_table_summary(
        self, table_info: TableInfo, relationships: list[RelationshipInfo]
    ) -> str:
        """Generate AI-powered summary for a table."""
        try:
            prompt = generate_table_summary_prompt(table_info, relationships)

            # Create a simple agent for text generation
            summary_agent = Agent(
                model=self.gemini_model.get_model(temperature=0.3), output_type=str
            )

            response = summary_agent.run_sync(prompt)
            return (
                str(response.output) if hasattr(response, "output") else str(response)
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to generate AI summary for table {table_info.name}: {str(e)}"
            )
            return f"Table {table_info.name} contains {len(table_info.columns)} columns and stores data related to the business domain."

    def analyze_schema(self, schema_name: str) -> SchemaInfo:
        """Analyze a complete database schema."""
        # For now, use direct tool calls to avoid async issues
        overview = get_database_overview_tool(self.db_connection_str)
        target_schema = next(
            (s for s in overview.schemas if s.name == schema_name), None
        )

        if not target_schema:
            raise ValueError(f"Schema '{schema_name}' not found in database")

        # Analyze each table in the schema
        analyzed_tables = []
        for table in target_schema.tables:
            table_info = get_table_schema_tool(
                self.db_connection_str, table.name, schema_name
            )
            analyzed_tables.append(table_info)

        # Get relationships for the schema
        relationships = analyze_relationships_tool(self.db_connection_str, schema_name)

        return SchemaInfo(
            name=schema_name,
            tables=analyzed_tables,
            views=target_schema.views,
            stored_procedures=target_schema.stored_procedures,
            relationships=relationships,
        )

    def generate_full_documentation(self) -> DocumentationReport:
        """Generate comprehensive documentation for the entire database."""
        self.logger.info("Starting full database documentation generation...")

        # Get basic overview for metadata
        basic_overview = self.get_database_overview()

        # Analyze each schema with full details and AI summaries
        all_schemas_info = []
        for schema in basic_overview.schemas:
            self.logger.info(f"Analyzing schema: {schema.name}")
            schema_info = self.analyze_schema(schema.name)

            # Generate AI summaries for each table
            self.logger.info(
                f"Generating AI summaries for {len(schema_info.tables)} tables..."
            )
            enhanced_tables = []
            for table in schema_info.tables:
                try:
                    # Generate AI summary
                    ai_summary = self.generate_table_summary(
                        table, schema_info.relationships
                    )

                    # Create enhanced table with AI summary
                    enhanced_table = TableInfo(
                        name=table.name,
                        schema_name=table.schema_name,
                        table_type=table.table_type,
                        columns=table.columns,
                        constraints=table.constraints,
                        indexes=table.indexes,
                        triggers=table.triggers,
                        row_count=table.row_count,
                        size_bytes=table.size_bytes,
                        created_at=table.created_at,
                        modified_at=table.modified_at,
                        description=table.description,
                        ai_summary=ai_summary,
                        relationship_summary=self._generate_relationship_summary(
                            table, schema_info.relationships
                        ),
                    )
                    enhanced_tables.append(enhanced_table)

                except Exception as e:
                    self.logger.warning(
                        f"Failed to enhance table {table.name}: {str(e)}"
                    )
                    enhanced_tables.append(table)

            # Update schema with enhanced tables
            enhanced_schema = SchemaInfo(
                name=schema_info.name,
                tables=enhanced_tables,
                views=schema_info.views,
                stored_procedures=schema_info.stored_procedures,
                relationships=schema_info.relationships,
                description=schema_info.description,
            )
            all_schemas_info.append(enhanced_schema)

        # Create updated overview with analyzed data
        from datetime import datetime

        updated_overview = DatabaseOverview(
            name=basic_overview.name,
            database_type=basic_overview.database_type,
            version=basic_overview.version,
            schemas=all_schemas_info,  # Use the analyzed schemas with full data
            total_tables=sum(len(schema.tables) for schema in all_schemas_info),
            total_views=sum(len(schema.views) for schema in all_schemas_info),
            total_stored_procedures=sum(
                len(schema.stored_procedures) for schema in all_schemas_info
            ),
            total_triggers=sum(
                sum(len(table.triggers) for table in schema.tables)
                for schema in all_schemas_info
            ),
            total_indexes=sum(
                sum(len(table.indexes) for table in schema.tables)
                for schema in all_schemas_info
            ),
            database_size_bytes=basic_overview.database_size_bytes,
            character_set=basic_overview.character_set,
            collation=basic_overview.collation,
            connection_info=basic_overview.connection_info,
        )

        # Generate executive summary
        total_relationships = sum(
            len(schema.relationships) for schema in all_schemas_info
        )
        total_columns = sum(
            sum(len(table.columns) for table in schema.tables)
            for schema in all_schemas_info
        )
        total_constraints = sum(
            sum(len(table.constraints) for table in schema.tables)
            for schema in all_schemas_info
        )

        executive_summary = f"""
Database Analysis Summary:
- Database: {updated_overview.name} ({updated_overview.database_type.value})
- Total Tables: {updated_overview.total_tables}
- Total Columns: {total_columns}
- Total Constraints: {total_constraints}
- Total Indexes: {updated_overview.total_indexes}
- Total Triggers: {updated_overview.total_triggers}
- Total Relationships: {total_relationships}
- Schemas Analyzed: {len(all_schemas_info)}

This database contains {updated_overview.total_tables} tables with {total_columns} columns across {len(all_schemas_info)} schema(s).
The analysis identified {total_relationships} foreign key relationships between tables.
        """.strip()

        # Generate detailed table documentation
        table_docs = []
        for schema in all_schemas_info:
            for table in schema.tables:
                # Create detailed documentation for each table
                pk_columns = [col.name for col in table.columns if col.is_primary_key]
                fk_columns = [col.name for col in table.columns if col.is_foreign_key]

                # Build documentation with AI insights
                doc_parts = [
                    f"Table: {table.name}",
                    f"Schema: {schema.name}",
                    f"Type: {table.table_type}",
                ]

                # Add AI summary if available
                if table.ai_summary:
                    doc_parts.extend(["", "AI Analysis:", table.ai_summary])

                # Add relationship summary if available
                if table.relationship_summary:
                    doc_parts.extend(["", "Relationships:", table.relationship_summary])

                # Add technical details
                doc_parts.extend(
                    [
                        "",
                        "Technical Details:",
                        f"Columns: {len(table.columns)} ({', '.join([f'{col.name}({col.data_type.value})' for col in table.columns[:5]])}{'...' if len(table.columns) > 5 else ''})",
                        f"Primary Keys: {', '.join(pk_columns) if pk_columns else 'None'}",
                        f"Foreign Keys: {', '.join(fk_columns) if fk_columns else 'None'}",
                        f"Constraints: {len(table.constraints)}",
                        f"Indexes: {len(table.indexes)}",
                        f"Triggers: {len(table.triggers)}",
                    ]
                )

                # Add size information if available
                if table.row_count is not None:
                    doc_parts.append(f"Row Count: {table.row_count:,}")
                if table.size_bytes is not None:
                    doc_parts.append(f"Size: {table.size_bytes:,} bytes")

                doc = "\n".join(doc_parts)

                table_docs.append({"table_name": table.name, "documentation": doc})

        # Generate relationship analysis
        relationship_details = []
        for schema in all_schemas_info:
            for rel in schema.relationships:
                relationship_details.append(
                    f"{rel.source_table}.{rel.source_column} → {rel.target_table}.{rel.target_column}"
                )

        relationship_analysis = f"""
Found {total_relationships} foreign key relationships:
{chr(10).join(relationship_details[:10])}
{"..." if len(relationship_details) > 10 else ""}
        """.strip()

        # Generate index analysis
        all_indexes = []
        for schema in all_schemas_info:
            for table in schema.tables:
                for index in table.indexes:
                    all_indexes.append(
                        f"{table.name}.{index.name} ({index.index_type.value})"
                    )

        index_analysis = f"""
Found {len(all_indexes)} indexes across all tables:
{chr(10).join(all_indexes[:10])}
{"..." if len(all_indexes) > 10 else ""}
        """.strip()

        result = DocumentationReport(
            database_overview=updated_overview,
            executive_summary=executive_summary,
            table_documentation=table_docs,
            relationship_analysis=relationship_analysis,
            index_analysis=index_analysis,
            performance_insights=[
                f"Database has {total_relationships} relationships indicating good normalization",
                f"Found {len(all_indexes)} indexes for query optimization",
                f"Average {total_columns / updated_overview.total_tables:.1f} columns per table",
            ],
            recommendations=[
                "Review tables with no indexes for potential performance improvements",
                "Consider adding descriptions to tables and columns for better documentation",
                "Monitor foreign key constraint performance on large tables",
            ],
            generated_at=datetime.now(),
        )

        self.logger.info("Database documentation generation completed")
        return result

    def create_initiator_agent(self) -> Agent:
        """Create the initiator agent for workflow orchestration."""
        return create_initiator_agent(
            model=self.gemini_model.get_model(temperature=0.3),
            connection_string=self.db_connection_str,
        )

    def create_schema_explorer_agent(self) -> Agent:
        """Create the schema explorer agent for detailed table analysis."""
        return create_schema_explorer_agent(
            model=self.gemini_model.get_model(temperature=0.2),
            connection_string=self.db_connection_str,
        )

    def create_detail_analyzer_agent(self) -> Agent:
        """Create the detail analyzer agent for advanced features."""
        return create_detail_analyzer_agent(
            model=self.gemini_model.get_model(temperature=0.2),
            connection_string=self.db_connection_str,
        )

    def create_documentation_agent(self) -> Agent:
        """Create the documentation generator agent."""
        return create_documentation_agent(
            model=self.gemini_model.get_model(temperature=0.1),
            connection_string=self.db_connection_str,
        )

    def _generate_relationship_summary(
        self, table: TableInfo, relationships: list[RelationshipInfo]
    ) -> str:
        """Generate a summary of table relationships."""
        incoming = []
        outgoing = []

        for rel in relationships:
            if rel.source_table == table.name:
                outgoing.append(f"references {rel.target_table}")
            elif rel.target_table == table.name:
                incoming.append(f"referenced by {rel.source_table}")

        parts = []
        if outgoing:
            parts.append(f"This table {', '.join(outgoing)}")
        if incoming:
            parts.append(f"and is {', '.join(incoming)}")

        if not parts:
            return "This table has no foreign key relationships."

        return ". ".join(parts) + "."

    def _get_database_name(self) -> str:
        """Extract database name from connection string or overview."""
        try:
            overview = self.get_database_overview()
            return overview.name
        except Exception:
            return "unknown_database"

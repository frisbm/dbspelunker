import asyncio
import logging
from typing import List, Optional

from pydantic_ai import Agent

from .genai import GeminiModel
from .models import (
    DatabaseOverview,
    DocumentationReport,
    RelationshipInfo,
    SchemaInfo,
    StoredProcedureInfo,
    TableInfo,
    TriggerInfo,
)
from .tools import (
    analyze_relationships_tool,
    generate_table_summary_prompt,
    get_database_overview_tool,
    get_table_schema_tool,
)


class DBSpelunker:
    def __init__(self, gemini_model: GeminiModel, db_connection_str: str):
        self.gemini_model = gemini_model
        self.db_connection_str = db_connection_str
        self.logger = logging.getLogger(__name__)

        self._validate_connection()

    def _validate_connection(self) -> None:
        try:
            overview = get_database_overview_tool(self.db_connection_str)
            self.logger.info(
                f"Successfully connected to {overview.database_type.value} database: {overview.name}"
            )
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")

    def get_database_overview(self) -> DatabaseOverview:
        return get_database_overview_tool(self.db_connection_str)

    def analyze_table(
        self, table_name: str, schema_name: Optional[str] = None
    ) -> TableInfo:
        return get_table_schema_tool(self.db_connection_str, table_name, schema_name)

    async def generate_table_summary_async(
        self, table_info: TableInfo, relationships: list[RelationshipInfo]
    ) -> str:
        try:
            prompt = generate_table_summary_prompt(table_info, relationships)

            # Create a simple agent for text generation
            summary_agent = Agent(
                model=self.gemini_model.get_model(temperature=0.3), output_type=str
            )

            response = await summary_agent.run(prompt)
            return (
                str(response.output) if hasattr(response, "output") else str(response)
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to generate AI summary for table {table_info.name}: {str(e)}"
            )
            return f"Table {table_info.name} contains {len(table_info.columns)} columns and stores data related to the business domain."

    async def generate_trigger_summary_async(
        self, trigger_info: TriggerInfo, table_info: TableInfo
    ) -> str:
        try:
            from .tools import generate_trigger_summary_prompt

            prompt = generate_trigger_summary_prompt(trigger_info, table_info)

            # Create a simple agent for text generation
            summary_agent = Agent(
                model=self.gemini_model.get_model(temperature=0.3), output_type=str
            )

            response = await summary_agent.run(prompt)
            return (
                str(response.output) if hasattr(response, "output") else str(response)
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to generate AI summary for trigger {trigger_info.name}: {str(e)}"
            )
            return f"Trigger {trigger_info.name} implements {trigger_info.timing.value} {trigger_info.event.value} logic for {trigger_info.table_name}."

    async def generate_stored_procedure_summary_async(
        self, procedure_info: StoredProcedureInfo, schema_tables: List[TableInfo]
    ) -> str:
        try:
            from .tools import generate_stored_procedure_summary_prompt

            prompt = generate_stored_procedure_summary_prompt(
                procedure_info, schema_tables
            )

            # Create a simple agent for text generation
            summary_agent = Agent(
                model=self.gemini_model.get_model(temperature=0.3), output_type=str
            )

            response = await summary_agent.run(prompt)
            return (
                str(response.output) if hasattr(response, "output") else str(response)
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to generate AI summary for procedure {procedure_info.name}: {str(e)}"
            )
            return f"Procedure {procedure_info.name} performs {procedure_info.language or 'SQL'} operations with {len(procedure_info.parameters)} parameters."

    def analyze_schema(self, schema_name: str) -> SchemaInfo:
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

        # Get stored procedures for the schema (this is already done in overview,
        # but we want to make sure we have the most up-to-date data)
        from .tools import get_stored_procedures_tool

        stored_procedures = get_stored_procedures_tool(
            self.db_connection_str, schema_name
        )

        return SchemaInfo(
            name=schema_name,
            tables=analyzed_tables,
            views=target_schema.views,
            stored_procedures=stored_procedures,
            relationships=relationships,
        )

    def generate_full_documentation(self) -> DocumentationReport:
        self.logger.info("Starting full database documentation generation...")

        # Get basic overview for metadata
        basic_overview = self.get_database_overview()

        # Analyze each schema with full details and AI summaries
        all_schemas_info = []
        for schema in basic_overview.schemas:
            self.logger.info(f"Analyzing schema: {schema.name}")
            schema_info = self.analyze_schema(schema.name)

            # Generate AI summaries for tables and stored procedures asynchronously
            self.logger.info(
                f"Generating AI summaries for {len(schema_info.tables)} tables and {len(schema_info.stored_procedures)} procedures concurrently..."
            )

            # Run both table and procedure enhancements concurrently
            async def run_enhancements() -> tuple[
                List[TableInfo], List[StoredProcedureInfo]
            ]:
                return await asyncio.gather(
                    self._generate_enhanced_tables_async(
                        schema_info.tables, schema_info.relationships
                    ),
                    self._generate_enhanced_stored_procedures_async(
                        schema_info.stored_procedures, schema_info.tables
                    ),
                )

            enhanced_tables, enhanced_procedures = asyncio.run(run_enhancements())

            # Update schema with enhanced tables and procedures
            enhanced_schema = SchemaInfo(
                name=schema_info.name,
                tables=enhanced_tables,
                views=schema_info.views,
                stored_procedures=enhanced_procedures,
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

        # Sort table documentation alphabetically by table name
        table_docs.sort(key=lambda x: x["table_name"])

        # Generate relationship analysis
        relationship_details = []
        for schema in all_schemas_info:
            for rel in schema.relationships:
                relationship_details.append(
                    f"{rel.source_table}.{rel.source_column} → {rel.target_table}.{rel.target_column}"
                )

        # Sort relationships alphabetically by source table, then target table
        relationship_details.sort()

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

        # Sort indexes alphabetically by table name, then index name
        all_indexes.sort()

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

    def _generate_relationship_summary(
        self, table: TableInfo, relationships: list[RelationshipInfo]
    ) -> str:
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

    async def _generate_enhanced_tables_async(
        self, tables: list[TableInfo], relationships: list[RelationshipInfo]
    ) -> list[TableInfo]:
        async def enhance_single_table(table: TableInfo) -> TableInfo:
            try:
                # Generate AI summary asynchronously
                ai_summary = await self.generate_table_summary_async(
                    table, relationships
                )

                # Enhance triggers with AI summaries
                enhanced_triggers = await self._generate_enhanced_triggers_async(
                    table.triggers, table
                )

                # Create enhanced table with AI summary and enhanced triggers
                return TableInfo(
                    name=table.name,
                    schema_name=table.schema_name,
                    table_type=table.table_type,
                    columns=table.columns,
                    constraints=table.constraints,
                    indexes=table.indexes,
                    triggers=enhanced_triggers,
                    row_count=table.row_count,
                    size_bytes=table.size_bytes,
                    created_at=table.created_at,
                    modified_at=table.modified_at,
                    description=table.description,
                    ai_summary=ai_summary,
                    relationship_summary=self._generate_relationship_summary(
                        table, relationships
                    ),
                )

            except Exception as e:
                self.logger.warning(f"Failed to enhance table {table.name}: {str(e)}")
                return table

        # Process all tables concurrently
        enhanced_tables = await asyncio.gather(
            *[enhance_single_table(table) for table in tables], return_exceptions=False
        )

        return list(enhanced_tables)

    async def _generate_enhanced_triggers_async(
        self, triggers: list[TriggerInfo], table_info: TableInfo
    ) -> list[TriggerInfo]:
        """Generate AI summaries for triggers asynchronously."""

        async def enhance_single_trigger(trigger: TriggerInfo) -> TriggerInfo:
            try:
                # Generate AI summary for the trigger
                ai_summary = await self.generate_trigger_summary_async(
                    trigger, table_info
                )

                # Create enhanced trigger with AI summary
                return TriggerInfo(
                    name=trigger.name,
                    table_name=trigger.table_name,
                    event=trigger.event,
                    timing=trigger.timing,
                    definition=trigger.definition,
                    is_enabled=trigger.is_enabled,
                    description=trigger.description,
                    ai_summary=ai_summary,
                )

            except Exception as e:
                self.logger.warning(
                    f"Failed to enhance trigger {trigger.name}: {str(e)}"
                )
                return trigger

        if not triggers:
            return []

        # Process all triggers concurrently
        enhanced_triggers = await asyncio.gather(
            *[enhance_single_trigger(trigger) for trigger in triggers],
            return_exceptions=False,
        )

        return list(enhanced_triggers)

    async def _generate_enhanced_stored_procedures_async(
        self, procedures: list[StoredProcedureInfo], schema_tables: list[TableInfo]
    ) -> list[StoredProcedureInfo]:
        """Generate AI summaries for stored procedures asynchronously."""

        async def enhance_single_procedure(
            procedure: StoredProcedureInfo,
        ) -> StoredProcedureInfo:
            try:
                # Generate AI summary for the procedure
                ai_summary = await self.generate_stored_procedure_summary_async(
                    procedure, schema_tables
                )

                # Create enhanced procedure with AI summary
                return StoredProcedureInfo(
                    name=procedure.name,
                    schema_name=procedure.schema_name,
                    parameters=procedure.parameters,
                    return_type=procedure.return_type,
                    definition=procedure.definition,
                    language=procedure.language,
                    is_deterministic=procedure.is_deterministic,
                    security_type=procedure.security_type,
                    created_at=procedure.created_at,
                    modified_at=procedure.modified_at,
                    description=procedure.description,
                    ai_summary=ai_summary,
                )

            except Exception as e:
                self.logger.warning(
                    f"Failed to enhance procedure {procedure.name}: {str(e)}"
                )
                return procedure

        if not procedures:
            return []

        # Process all procedures concurrently
        enhanced_procedures = await asyncio.gather(
            *[enhance_single_procedure(procedure) for procedure in procedures],
            return_exceptions=False,
        )

        return list(enhanced_procedures)

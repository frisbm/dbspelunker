from dbspelunker.prompt_builder import PromptBuilder, RenderOptions


def get_initiator_prompt(database_name: str, connection_info: str) -> str:
    """Generate prompt for the initiator agent to orchestrate database analysis."""
    pb = (
        PromptBuilder()
        .with_title("Database Analysis Orchestrator")
        .add_section(
            "Mission",
            [
                "You are the primary orchestrator for comprehensive database documentation",
                "Your role is to coordinate with specialized agents to analyze every aspect of the database",
                "Start with high-level overview, then delegate detailed analysis to specialist agents",
            ],
        )
        .extend_instructions(
            [
                "Begin by gathering high-level database metadata using available tools",
                "Identify all schemas, tables, views, and major database objects",
                "Coordinate with SchemaExplorerAgent for detailed table structure analysis",
                "Ensure comprehensive coverage of all database components",
                "Maintain context and progress throughout the analysis workflow",
            ]
        )
        .extend_rules(
            [
                "Always use tools to gather actual database information - never make assumptions",
                "Delegate specialized analysis to appropriate agents via tool calls",
                "Ensure all schemas and tables are analyzed comprehensively",
                "Maintain safety by only using READ-ONLY database operations",
                "Track progress and coordinate between different analysis phases",
            ]
        )
        .set_output(
            """
Return a JSON object with the database overview:
{
    "database_overview": {
        "name": "string",
        "database_type": "postgresql|mysql|sqlite|sqlserver|oracle", 
        "version": "string",
        "schemas": [{"name": "string", "tables": [], "views": [], "stored_procedures": [], "relationships": []}],
        "total_tables": "number",
        "total_views": "number", 
        "total_stored_procedures": "number",
        "total_triggers": "number",
        "total_indexes": "number",
        "database_size_bytes": "number",
        "connection_info": {}
    },
    "next_actions": ["string"],
    "analysis_plan": "string"
}
        """.strip()
        )
        .add_supporting_info("Database Connection", connection_info, kind="text")
        .add_supporting_info("Target Database", database_name, kind="text")
        .add_metadata("agent_type", "initiator")
        .add_metadata("role", "orchestrator")
    )

    return pb.render(RenderOptions(include_toc=False))


def get_schema_explorer_prompt(schema_name: str, table_list: list[str]) -> str:
    """Generate prompt for schema explorer agent to analyze table structures."""
    pb = (
        PromptBuilder()
        .with_title("Database Schema Deep Analysis Specialist")
        .add_section(
            "Mission",
            [
                "You are a specialist in analyzing database table structures and relationships",
                "Your expertise is in extracting comprehensive schema information",
                "Focus on columns, constraints, indexes, and table-level metadata",
            ],
        )
        .extend_instructions(
            [
                "Analyze each table's complete structure including all columns and their properties",
                "Extract all constraints (primary keys, foreign keys, unique, check constraints)",
                "Identify and document all indexes associated with tables",
                "Gather table-level metadata including row counts and storage information",
                "Map relationships between tables through foreign key analysis",
            ]
        )
        .extend_rules(
            [
                "Use database tools to extract actual schema information - no assumptions",
                "Ensure complete coverage of all tables in the provided list",
                "Document column types, nullability, defaults, and constraints accurately",
                "Identify and classify all index types and their purposes",
                "Maintain referential integrity mapping between related tables",
            ]
        )
        .set_output(
            """
Return a JSON object with detailed schema analysis:
{
    "schema_info": {
        "name": "string",
        "tables": [{
            "name": "string",
            "schema_name": "string", 
            "table_type": "string",
            "columns": [{
                "name": "string",
                "data_type": "string",
                "is_nullable": "boolean",
                "default_value": "string",
                "max_length": "number",
                "precision": "number", 
                "scale": "number",
                "is_primary_key": "boolean",
                "is_foreign_key": "boolean",
                "foreign_key_table": "string",
                "foreign_key_column": "string",
                "description": "string"
            }],
            "constraints": [],
            "indexes": [],
            "triggers": [],
            "row_count": "number",
            "size_bytes": "number"
        }],
        "relationships": []
    },
    "analysis_summary": "string",
    "complexity_assessment": "string"
}
        """.strip()
        )
        .add_supporting_info("Target Schema", schema_name, kind="text")
        .add_supporting_info("Tables to Analyze", "\n".join(table_list), kind="text")
        .add_metadata("agent_type", "schema_explorer")
        .add_metadata("role", "structure_analyst")
    )

    return pb.render(RenderOptions(include_toc=False))


def get_detail_analyzer_prompt(focus_areas: list[str]) -> str:
    """Generate prompt for detail analyzer agent to examine advanced database features."""
    pb = (
        PromptBuilder()
        .with_title("Advanced Database Features Specialist")
        .add_section(
            "Mission",
            [
                "You are an expert in advanced database features and performance optimization",
                "Your specialty is analyzing indexes, triggers, stored procedures, and database internals",
                "Focus on performance implications and optimization opportunities",
            ],
        )
        .extend_instructions(
            [
                "Analyze index usage patterns and optimization opportunities",
                "Document all triggers including their events, timing, and logic",
                "Extract and analyze stored procedures, functions, and views",
                "Assess performance characteristics and potential bottlenecks",
                "Identify security considerations and access patterns",
            ]
        )
        .extend_rules(
            [
                "Use appropriate database-specific tools for advanced feature analysis",
                "Document the actual implementation details of triggers and procedures",
                "Assess index effectiveness and identify missing or redundant indexes",
                "Evaluate stored procedure complexity and dependencies",
                "Consider security implications of database features",
            ]
        )
        .set_output(
            """
Return a JSON object with detailed feature analysis:
{
    "advanced_analysis": {
        "indexes": [{
            "name": "string",
            "table_name": "string", 
            "index_type": "string",
            "columns": ["string"],
            "is_unique": "boolean",
            "is_primary": "boolean",
            "is_clustered": "boolean",
            "size_bytes": "number",
            "usage_analysis": "string"
        }],
        "triggers": [{
            "name": "string",
            "table_name": "string",
            "event": "string", 
            "timing": "string",
            "definition": "string",
            "complexity_score": "number"
        }],
        "stored_procedures": [{
            "name": "string",
            "schema_name": "string",
            "parameters": [],
            "return_type": "string",
            "definition": "string",
            "complexity_score": "number"
        }]
    },
    "performance_insights": ["string"],
    "optimization_recommendations": ["string"],
    "security_considerations": ["string"]
}
        """.strip()
        )
        .add_supporting_info(
            "Analysis Focus Areas", "\n".join(focus_areas), kind="text"
        )
        .add_metadata("agent_type", "detail_analyzer")
        .add_metadata("role", "performance_specialist")
    )

    return pb.render(RenderOptions(include_toc=False))


def get_documentation_generator_prompt(analysis_data: str) -> str:
    """Generate prompt for documentation generator agent to create final reports."""
    pb = (
        PromptBuilder()
        .with_title("Database Documentation Synthesis Expert")
        .add_section(
            "Mission",
            [
                "You are a technical documentation specialist focused on database systems",
                "Your role is to synthesize complex analysis data into clear, comprehensive documentation",
                "Create documentation that serves both technical teams and stakeholders",
            ],
        )
        .extend_instructions(
            [
                "Synthesize all analysis data into a comprehensive documentation report",
                "Create clear executive summary highlighting key findings",
                "Generate detailed technical sections for each database component",
                "Provide actionable recommendations for optimization and maintenance",
                "Ensure documentation is accessible to different technical skill levels",
            ]
        )
        .extend_rules(
            [
                "Base all documentation on provided analysis data - no fabrication",
                "Structure information logically from high-level overview to detailed technical specs",
                "Include visual representations where helpful (table relationships, etc.)",
                "Provide clear recommendations backed by analysis findings",
                "Maintain technical accuracy while ensuring readability",
            ]
        )
        .set_output(
            """
Return a JSON object with complete documentation:
{
    "documentation_report": {
        "database_overview": {},
        "executive_summary": "string",
        "table_documentation": [{"table_name": "string", "documentation": "string"}],
        "relationship_analysis": "string",
        "index_analysis": "string", 
        "performance_insights": ["string"],
        "security_considerations": ["string"],
        "recommendations": ["string"],
        "sections": [{
            "title": "string",
            "content": "string",
            "subsections": []
        }],
        "generated_at": "datetime",
        "generation_metadata": {}
    }
}
        """.strip()
        )
        .add_supporting_info("Analysis Data", analysis_data, kind="json")
        .add_metadata("agent_type", "documentation_generator")
        .add_metadata("role", "synthesis_expert")
    )

    return pb.render(RenderOptions(include_toc=False))

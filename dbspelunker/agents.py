from typing import Any, Dict, List, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel

from .models import (
    DatabaseOverview,
    DocumentationReport,
    RelationshipInfo,
    SchemaInfo,
    StoredProcedureInfo,
    TableInfo,
    TriggerInfo,
)
from .prompts import (
    get_detail_analyzer_prompt,
    get_documentation_generator_prompt,
    get_initiator_prompt,
    get_schema_explorer_prompt,
)
from .tools import (
    analyze_relationships_tool,
    execute_readonly_sql_tool,
    get_database_overview_tool,
    get_indexes_tool,
    get_stored_procedures_tool,
    get_table_schema_tool,
    get_triggers_tool,
)


class DatabaseAnalysisContext:
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.analysis_results: Dict[str, Any] = {}


def create_initiator_agent(model: GoogleModel, connection_string: str) -> Agent:
    """Create the initiator agent responsible for orchestrating the analysis workflow."""

    def get_database_overview(
        ctx: RunContext[DatabaseAnalysisContext],
    ) -> DatabaseOverview:
        """Get high-level database overview and metadata."""
        return get_database_overview_tool(ctx.deps.connection_string)

    def execute_sql_query(
        ctx: RunContext[DatabaseAnalysisContext], sql: str
    ) -> List[Dict[str, Any]]:
        """Execute a READ-ONLY SQL query against the database."""
        return execute_readonly_sql_tool(ctx.deps.connection_string, sql)

    def call_schema_explorer(
        ctx: RunContext[DatabaseAnalysisContext], schema_name: str, tables: List[str]
    ) -> SchemaInfo:
        """Delegate detailed schema analysis to the schema explorer agent."""
        schema_agent = create_schema_explorer_agent(model, ctx.deps.connection_string)
        prompt = get_schema_explorer_prompt(schema_name, tables)

        schema_ctx = DatabaseAnalysisContext(
            ctx.deps.connection_string, ctx.deps.database_name
        )
        result = schema_agent.run_sync(prompt, deps=schema_ctx)  # type: ignore
        return result.output  # type: ignore

    return Agent(  # type: ignore
        model=model,
        output_type=DatabaseOverview,
        system_prompt=lambda ctx: get_initiator_prompt(
            ctx.deps.database_name, ctx.deps.connection_string
        ),
        tools=[get_database_overview, execute_sql_query, call_schema_explorer],
    )


def create_schema_explorer_agent(model: GoogleModel, connection_string: str) -> Agent:
    """Create the schema explorer agent for detailed table structure analysis."""

    def get_table_details(
        ctx: RunContext[DatabaseAnalysisContext],
        table_name: str,
        schema_name: Optional[str] = None,
    ) -> TableInfo:
        """Get comprehensive table schema information."""
        return get_table_schema_tool(
            ctx.deps.connection_string, table_name, schema_name
        )

    def analyze_table_relationships(
        ctx: RunContext[DatabaseAnalysisContext], schema_name: Optional[str] = None
    ) -> List[RelationshipInfo]:
        """Analyze relationships between tables in the schema."""
        return analyze_relationships_tool(ctx.deps.connection_string, schema_name)

    def execute_sql_query(
        ctx: RunContext[DatabaseAnalysisContext], sql: str
    ) -> List[Dict[str, Any]]:
        """Execute a READ-ONLY SQL query for additional schema information."""
        return execute_readonly_sql_tool(ctx.deps.connection_string, sql)

    def call_detail_analyzer(
        ctx: RunContext[DatabaseAnalysisContext], focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Delegate advanced feature analysis to the detail analyzer agent."""
        detail_agent = create_detail_analyzer_agent(model, ctx.deps.connection_string)
        prompt = get_detail_analyzer_prompt(focus_areas)

        detail_ctx = DatabaseAnalysisContext(
            ctx.deps.connection_string, ctx.deps.database_name
        )
        result = detail_agent.run_sync(prompt, deps=detail_ctx)  # type: ignore
        return result.output  # type: ignore

    return Agent(
        model=model,
        output_type=SchemaInfo,  # type: ignore[arg-type]
        tools=[
            get_table_details,
            analyze_table_relationships,
            execute_sql_query,
            call_detail_analyzer,
        ],
    )


def create_detail_analyzer_agent(model: GoogleModel, connection_string: str) -> Agent:
    """Create the detail analyzer agent for advanced database features."""

    def get_table_indexes(
        ctx: RunContext[DatabaseAnalysisContext],
        table_name: str,
        schema_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get detailed index information for a table."""
        indexes = get_indexes_tool(ctx.deps.connection_string, table_name, schema_name)
        return [index.model_dump() for index in indexes]

    def get_table_triggers(
        ctx: RunContext[DatabaseAnalysisContext],
        table_name: str,
        schema_name: Optional[str] = None,
    ) -> List[TriggerInfo]:
        """Get trigger information for a table."""
        return get_triggers_tool(ctx.deps.connection_string, table_name, schema_name)

    def get_stored_procedures(
        ctx: RunContext[DatabaseAnalysisContext], schema_name: Optional[str] = None
    ) -> List[StoredProcedureInfo]:
        """Get stored procedure information for the schema."""
        return get_stored_procedures_tool(ctx.deps.connection_string, schema_name)

    def execute_sql_query(
        ctx: RunContext[DatabaseAnalysisContext], sql: str
    ) -> List[Dict[str, Any]]:
        """Execute a READ-ONLY SQL query for performance analysis."""
        return execute_readonly_sql_tool(ctx.deps.connection_string, sql)

    def call_documentation_generator(
        ctx: RunContext[DatabaseAnalysisContext], analysis_data: str
    ) -> DocumentationReport:
        """Delegate final documentation generation to the documentation agent."""
        doc_agent = create_documentation_agent(model, ctx.deps.connection_string)
        prompt = get_documentation_generator_prompt(analysis_data)

        doc_ctx = DatabaseAnalysisContext(
            ctx.deps.connection_string, ctx.deps.database_name
        )
        result = doc_agent.run_sync(prompt, deps=doc_ctx)  # type: ignore
        return result.output  # type: ignore

    return Agent(
        model=model,
        output_type=dict,  # type: ignore[arg-type]
        tools=[
            get_table_indexes,
            get_table_triggers,
            get_stored_procedures,
            execute_sql_query,
            call_documentation_generator,
        ],
    )


def create_documentation_agent(model: GoogleModel, connection_string: str) -> Agent:
    """Create the documentation generator agent for final report synthesis."""

    def execute_sql_query(
        ctx: RunContext[DatabaseAnalysisContext], sql: str
    ) -> List[Dict[str, Any]]:
        """Execute a READ-ONLY SQL query for additional documentation context."""
        return execute_readonly_sql_tool(ctx.deps.connection_string, sql)

    def get_database_overview(
        ctx: RunContext[DatabaseAnalysisContext],
    ) -> DatabaseOverview:
        """Get database overview for documentation context."""
        return get_database_overview_tool(ctx.deps.connection_string)

    return Agent(
        model=model,
        output_type=DocumentationReport,  # type: ignore[arg-type]
        tools=[execute_sql_query, get_database_overview],
    )


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow for database analysis."""

    def __init__(self, model: GoogleModel, connection_string: str, database_name: str):
        self.model = model
        self.connection_string = connection_string
        self.database_name = database_name
        self.context = DatabaseAnalysisContext(connection_string, database_name)

    def run_full_analysis(self) -> DocumentationReport:
        """Run the complete database analysis workflow."""
        initiator = create_initiator_agent(self.model, self.connection_string)

        result = initiator.run_sync(
            "Begin comprehensive database analysis and documentation generation",
            deps=self.context,  # type: ignore
        )

        if isinstance(result.output, DatabaseOverview):
            doc_agent = create_documentation_agent(self.model, self.connection_string)

            doc_result = doc_agent.run_sync(
                f"Generate comprehensive documentation based on analysis: {result.output.model_dump_json()}",
                deps=self.context,  # type: ignore
            )

            return doc_result.output  # type: ignore[no-any-return]

        raise RuntimeError("Failed to complete database analysis workflow")

    def run_schema_analysis(self, schema_name: str) -> SchemaInfo:
        """Run analysis for a specific schema."""
        overview = get_database_overview_tool(self.connection_string)

        target_schema = next(
            (s for s in overview.schemas if s.name == schema_name), None
        )
        if not target_schema:
            raise ValueError(f"Schema '{schema_name}' not found in database")

        table_names = [table.name for table in target_schema.tables]

        schema_agent = create_schema_explorer_agent(self.model, self.connection_string)
        prompt = get_schema_explorer_prompt(schema_name, table_names)

        result = schema_agent.run_sync(prompt, deps=self.context)  # type: ignore
        return result.output  # type: ignore

    def run_table_analysis(
        self, table_name: str, schema_name: Optional[str] = None
    ) -> TableInfo:
        """Run detailed analysis for a specific table."""
        return get_table_schema_tool(self.connection_string, table_name, schema_name)

from pathlib import Path

from config import load_config
from dbspelunker import DBSpelunker
from dbspelunker.genai import GeminiModel


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
        documentation.to_markdown(
            path=Path("output/database_documentation.md"), include_json_appendix=False
        )

        print("Documentation generated successfully!")
        print("Output saved to output/database_documentation.md")

    except Exception as e:
        print(f"Failed to generate documentation: {str(e)}")
        print("Please check your configuration and database connection")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

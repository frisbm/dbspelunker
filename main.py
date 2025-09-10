import argparse
from pathlib import Path

from config import load_config
from dbspelunker import DBSpelunker
from dbspelunker.genai import GeminiModel


def main() -> None:
    """Generate comprehensive AI-powered documentation for the entire database."""
    parser = argparse.ArgumentParser(
        description="Generate AI-powered documentation for a database"
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="output/database_documentation.md",
        help="Output file path for the documentation (default: output/database_documentation.md)",
    )

    args = parser.parse_args()
    output_path = Path(args.output_file)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        config = load_config()
        gemini = GeminiModel(config)

        spelunker = DBSpelunker(gemini=gemini, db_connection_str=config.database_url)

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
        documentation.to_markdown(path=output_path, include_json_appendix=False)

        print("Documentation generated successfully!")
        print(f"Output saved to {output_path}")

    except Exception as e:
        print(f"Failed to generate documentation: {str(e)}")
        print("Please check your configuration and database connection")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

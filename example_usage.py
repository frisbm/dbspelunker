#!/usr/bin/env python3
"""
Example usage of the DBSpelunker multi-agent database documentation system.
"""

import json
import logging
from pathlib import Path
from typing import Any

from config import load_config
from dbspelunker import DBSpelunker
from dbspelunker.genai import GeminiModel


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("dbspelunker.log"), logging.StreamHandler()],
    )


def save_report(report: Any, filename: str) -> None:
    """Save documentation report to a JSON file."""
    output_path = Path(filename)
    with open(output_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2, default=str)
    print(f"Report saved to: {output_path.absolute()}")


def main() -> None:
    """Main example demonstrating DBSpelunker usage."""
    setup_logging()

    try:
        config = load_config()
        print(f"Loaded configuration for project: {config.project_id}")

        gemini_model = GeminiModel(config)
        print(f"Initialized Gemini model: {config.model}")

        spelunker = DBSpelunker(
            gemini_model=gemini_model, db_connection_str=config.db_connection_string
        )
        print("DBSpelunker initialized successfully!")

        print("\n=== Database Overview ===")
        overview = spelunker.get_database_overview()
        print(f"Database: {overview.name} ({overview.database_type.value})")
        print(f"Total tables: {overview.total_tables}")
        print(f"Total schemas: {len(overview.schemas)}")

        if overview.schemas:
            schema_name = overview.schemas[0].name
            print(f"\n=== Analyzing Schema: {schema_name} ===")

            try:
                schema_info = spelunker.analyze_schema(schema_name)
                print(f"Schema analysis completed for: {schema_info.name}")
                print(f"Tables analyzed: {len(schema_info.tables)}")
                print(f"Relationships found: {len(schema_info.relationships)}")

                save_report(schema_info, f"schema_{schema_name}_analysis.json")

            except Exception as e:
                print(f"Schema analysis failed: {str(e)}")

        print("\n=== Single Table Analysis ===")
        if overview.schemas and overview.schemas[0].tables:
            table_name = (
                overview.schemas[0].tables[0].name
                if overview.schemas[0].tables
                else None
            )

            if table_name:
                try:
                    table_info = spelunker.analyze_table(table_name, schema_name)
                    print(f"Table analysis completed for: {table_info.name}")
                    print(f"Columns: {len(table_info.columns)}")
                    print(f"Constraints: {len(table_info.constraints)}")
                    print(f"Indexes: {len(table_info.indexes)}")

                    save_report(table_info, f"table_{table_name}_analysis.json")

                except Exception as e:
                    print(f"Table analysis failed: {str(e)}")
            else:
                print("No tables found for analysis")

        print("\n=== Full Documentation Generation ===")
        try:
            print("Starting comprehensive documentation generation...")
            print("This may take several minutes depending on database size...")

            documentation = spelunker.generate_full_documentation()

            print("Documentation generation completed!")
            print(
                f"Executive summary length: {len(documentation.executive_summary)} characters"
            )
            print(f"Performance insights: {len(documentation.performance_insights)}")
            print(f"Recommendations: {len(documentation.recommendations)}")

            save_report(documentation, "complete_database_documentation.json")

            print("\n=== Sample Executive Summary ===")
            print(
                documentation.executive_summary[:500] + "..."
                if len(documentation.executive_summary) > 500
                else documentation.executive_summary
            )

        except Exception as e:
            print(f"Full documentation generation failed: {str(e)}")
            print(
                "You can still use individual analysis methods for specific schemas or tables"
            )

    except Exception as e:
        print(f"Application failed to start: {str(e)}")
        print("Please check your configuration and database connection")


if __name__ == "__main__":
    main()

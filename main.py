import json
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

        print("🔍 DBSpelunker initialized successfully!")

        overview = spelunker.get_database_overview()
        print(f"📊 Database: {overview.name} ({overview.database_type.value})")
        print(
            f"📋 Found {overview.total_tables} tables across {len(overview.schemas)} schemas"
        )

        print("\n🤖 Generating comprehensive AI-powered documentation...")
        print("⚠️  This may take several minutes as it analyzes all tables with AI summaries...")
        
        # Generate full documentation with AI summaries
        documentation = spelunker.generate_full_documentation()
        
        # Save to output.json
        print("\n💾 Saving comprehensive documentation to output.json...")
        with open("output.json", "w") as f:
            json.dump(documentation.model_dump(), f, indent=2, default=str)
        
        print(f"\n✅ Complete documentation generated successfully!")
        print(f"📄 Database: {documentation.database_overview.name}")
        print(f"📊 Total Tables: {documentation.database_overview.total_tables}")
        print(f"📈 Total Columns: {sum(len(table.columns) for schema in documentation.database_overview.schemas for table in schema.tables)}")
        print(f"🔗 Total Relationships: {sum(len(schema.relationships) for schema in documentation.database_overview.schemas)}")
        print(f"📋 Total Indexes: {documentation.database_overview.total_indexes}")
        print(f"⚡ Total Triggers: {documentation.database_overview.total_triggers}")
        
        print(f"\n🎯 Executive Summary Preview:")
        print(documentation.executive_summary[:200] + "...")
        
        print(f"\n📁 Full documentation saved to: output.json")
        print(f"🕒 Generated at: {documentation.generated_at}")

    except Exception as e:
        print(f"❌ Failed to generate documentation: {str(e)}")
        print("Please check your configuration and database connection")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

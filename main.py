from config import load_config
from dbspelunker import DBSpelunker
from dbspelunker.genai import GeminiModel


def main() -> None:
    """Simple example of using DBSpelunker."""
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

        print("\n🚀 Ready to spelunk your database!")
        print("See example_usage.py for more comprehensive examples")

    except Exception as e:
        print(f"❌ Failed to initialize DBSpelunker: {str(e)}")
        print("Please check your configuration and database connection")


if __name__ == "__main__":
    main()

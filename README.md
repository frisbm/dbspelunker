# DBSpelunker

A simple tool that uses AI to automatically generate documentation for your database.

## What it does

DBSpelunker connects to your database, analyzes all the tables and relationships, and creates a comprehensive markdown document explaining what everything is for. It uses AI to understand what each table represents based on column names and structure.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create a `config.json` file:
```json
{
  "database_url": "postgresql://user:password@localhost:5432/database_name",
  "project_id": "your-google-cloud-project-id",
  "location": "us-east1",
  "model": "gemini-2.5-flash",
  "token_limit": 1048576,
  "thinking_budget": 32768,
  "maximum_remote_calls": 10,
  "max_concurrent_requests": 65535,
  "max_output_tokens": 65535,
  "top_p": 0.5
}
```

3. Run the tool:
```bash
uv run python main.py
```

## Output

The tool creates a `database_documentation.md` file with:
- Database overview and statistics
- Detailed table descriptions with AI analysis
- Relationship mappings
- Index analysis
- Performance insights

## Requirements

- Python 3.13+
- Google Cloud AI API access
- Database connection (PostgreSQL, MySQL, SQLite, SQL Server, Oracle)
# SQLite MCP Server

A Model Context Protocol (MCP) server implementation for SQLite databases. This server enables AI assistants to interact with SQLite databases through a standardized protocol, providing schema inspection, query execution, and data analysis capabilities.

## 🎯 Features

This MCP server implements the core MCP concepts:

### 📦 Resources
- **Database Schema**: Access complete database schema information including tables, columns, types, and constraints

### 🛠️ Tools
- **list_tables**: List all tables in a SQLite database
- **get_table_schema**: Get detailed schema information for a specific table
- **execute_query**: Execute SELECT queries safely with parameterization support
- **count_rows**: Count rows in a table with optional WHERE clauses

### 💬 Prompts
- **analyze_table_prompt**: Generate comprehensive table analysis prompts
- **query_builder_prompt**: Help build SQL queries based on user intent

## 📋 Requirements

- Python 3.12+
- fastmcp >= 0.1.0

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/patrijam/mcp-sqlite-server.git
cd mcp-sqlite-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a sample database for testing:
```bash
python create_sample_db.py
```

## 🎮 Usage

### With VS Code Copilot

The repository includes a pre-configured `.vscode/mcp.json` file. To use:

1. Ensure you have VS Code with GitHub Copilot and MCP support enabled
2. Open this repository in VS Code
3. The SQLite MCP Server will be automatically available to Copilot

### With MCP Inspector

Test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

Configuration:
- **Transport Type**: STDIO
- **Command**: `python3`
- **Arguments**: `sqlite_server.py`
- **Working Directory**: Path to this repository

### Standalone

Run the server directly:
```bash
python sqlite_server.py
```

## 📖 Example Usage

Once connected through an MCP client (like VS Code Copilot or Claude Desktop), you can:

1. **List all tables**:
   - Use the `list_tables` tool with the database path

2. **Get table schema**:
   - Use the `get_table_schema` tool to see column information

3. **Execute queries**:
   ```python
   execute_query(
       db_path="sample_database.db",
       query="SELECT * FROM customers WHERE country = ?",
       params=["Switzerland"]
   )
   ```

4. **Count rows**:
   ```python
   count_rows(
       db_path="sample_database.db",
       table_name="customers",
       where_clause="country = 'Switzerland'"
   )
   ```

## 🗂️ Sample Database

The included `sample_database.db` contains:
- **customers**: Customer information (8 records)
- **products**: Product catalog (10 records)
- **orders**: Order history (8 records)
- **order_items**: Order line items (14 records)

This sample database is perfect for testing queries like:
- "Show me all customers from Switzerland"
- "What products are in the Electronics category?"
- "List all completed orders"

## 🔒 Security

- Only SELECT queries are allowed by default for safety
- All queries support parameterization to prevent SQL injection
- Database connections use `check_same_thread=False` for thread safety

## 🏗️ Architecture

This implementation follows the Model Context Protocol specification:

```
┌─────────────────┐
│   MCP Client    │
│ (VS Code, etc)  │
└────────┬────────┘
         │
         │ MCP Protocol
         │
┌────────▼────────┐
│  SQLite MCP     │
│     Server      │
├─────────────────┤
│ • Resources     │
│ • Tools         │
│ • Prompts       │
└────────┬────────┘
         │
         │ SQLite API
         │
┌────────▼────────┐
│ SQLite Database │
└─────────────────┘
```

## 📚 Related Exercises

This server is part of Exercise 5 in the Agentic AI course. See `exercise.md` for the complete exercise series, including:
- Exercise 1-3: Setting up MCP servers (Brave Search, PubMed)
- Exercise 4: Designing the SQLite MCP Server
- Exercise 5: Implementing the SQLite MCP Server (this project)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://gofastmcp.com)
- Follows the [Model Context Protocol](https://modelcontextprotocol.io) specification
- Part of the ZHAW Agentic AI course exercises

# Testing Guide for SQLite MCP Server

This guide explains how to test the SQLite MCP Server using various methods.

## Method 1: Unit Tests (Quickest)

Run the included test suite:

```bash
python3 test_server.py
```

This tests all tools, resources, and prompts without requiring MCP protocol setup.

## Method 2: MCP Inspector (Recommended)

The MCP Inspector provides a web UI to test your MCP server.

### Setup:

1. Install the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2. When the inspector opens in your browser, configure:
   - **Transport Type**: `STDIO`
   - **Command**: `python3`
   - **Arguments**: `sqlite_server.py`
   - **Working Directory**: (path to this repository)

3. Click "Connect"

### Testing:

Once connected, you can:

1. **Browse Resources**:
   - Look for `sqlite://sample_database.db/schema`
   - Click to view the full database schema

2. **Call Tools**:
   - `list_tables`: 
     ```json
     {"db_path": "sample_database.db"}
     ```
   
   - `get_table_schema`:
     ```json
     {"db_path": "sample_database.db", "table_name": "customers"}
     ```
   
   - `execute_query`:
     ```json
     {
       "db_path": "sample_database.db",
       "query": "SELECT * FROM customers WHERE country = ?",
       "params": ["Switzerland"]
     }
     ```
   
   - `count_rows`:
     ```json
     {
       "db_path": "sample_database.db",
       "table_name": "customers",
       "where_clause": "country = 'Switzerland'"
     }
     ```

3. **Use Prompts**:
   - `analyze_table_prompt`:
     ```json
     {"db_path": "sample_database.db", "table_name": "products"}
     ```
   
   - `query_builder_prompt`:
     ```json
     {
       "db_path": "sample_database.db",
       "table_name": "orders",
       "user_intent": "Show me all completed orders sorted by date"
     }
     ```

## Method 3: VS Code Copilot

If you have VS Code with GitHub Copilot and MCP support:

1. Open this repository in VS Code
2. The `.vscode/mcp.json` configuration will automatically load the server
3. In Copilot, you can ask questions like:
   - "List all tables in the sample database"
   - "Show me customers from Switzerland"
   - "What's the schema of the products table?"
   - "Count how many orders are in completed status"

## Method 4: Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "python3",
      "args": [
        "/full/path/to/sqlite_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop and the tools will be available.

## Example Queries to Test

Once connected via any method, try these example queries:

1. **Simple query**:
   ```sql
   SELECT * FROM customers LIMIT 5
   ```

2. **Filtered query**:
   ```sql
   SELECT * FROM products WHERE category = 'Electronics' ORDER BY price DESC
   ```

3. **Join query**:
   ```sql
   SELECT 
     c.first_name || ' ' || c.last_name AS customer_name,
     o.order_date,
     o.total_amount,
     o.status
   FROM customers c
   JOIN orders o ON c.customer_id = o.customer_id
   WHERE c.country = 'Switzerland'
   ORDER BY o.order_date DESC
   ```

4. **Aggregation query**:
   ```sql
   SELECT 
     category,
     COUNT(*) as product_count,
     AVG(price) as avg_price,
     SUM(stock_quantity) as total_stock
   FROM products
   GROUP BY category
   ```

## Troubleshooting

### Server won't start
- Ensure Python 3.12+ is installed: `python3 --version`
- Install dependencies: `pip install -r requirements.txt`
- Check that `sample_database.db` exists: `ls -la sample_database.db`

### Connection refused in MCP Inspector
- Verify the working directory is set correctly
- Check that the command path is absolute or in PATH
- Look at the console/logs for error messages

### Tools not appearing in VS Code
- Restart VS Code completely
- Check `.vscode/mcp.json` has correct path to python3
- Enable MCP debugging in VS Code settings
- Check Output panel → GitHub Copilot → MCP for logs

## Expected Test Results

When testing with the sample database, you should see:

- **4 tables**: customers, products, orders, order_items
- **8 customers** (5 from Switzerland)
- **10 products** (in 3 categories)
- **8 orders** (with various statuses)
- **14 order items** (linking orders to products)

All SELECT queries should work, while non-SELECT queries should be blocked for security.

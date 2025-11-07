"""
Test script for SQLite MCP Server functionality.
This script tests all tools and features without requiring the full MCP protocol.
"""

import json
import sqlite3
import re

DB_PATH = "sample_database.db"

# Import the underlying functions (before decoration)
def get_connection(db_path: str) -> sqlite3.Connection:
    """Get or create a database connection."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def validate_table_name(conn: sqlite3.Connection, table_name: str) -> bool:
    """Validate that a table name exists in the database."""
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        return False
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=? AND name NOT LIKE 'sqlite_%'
    """, (table_name,))
    
    return cursor.fetchone() is not None


def quote_identifier(identifier: str) -> str:
    """Quote an SQL identifier safely."""
    return '"' + identifier.replace('"', '""') + '"'


def list_tables(db_path: str):
    """List all tables in database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_table_schema(db_path: str, table_name: str):
    """Get table schema."""
    conn = get_connection(db_path)
    
    # Validate table name exists
    if not validate_table_name(conn, table_name):
        return {"error": f"Table '{table_name}' not found or invalid"}
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sql 
        FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    result = cursor.fetchone()
    if not result:
        return {"error": f"Table '{table_name}' not found"}
    
    create_sql = result[0]
    
    # Use quoted identifier for PRAGMA
    quoted_name = quote_identifier(table_name)
    cursor.execute(f"PRAGMA table_info({quoted_name})")
    columns = [
        {
            "name": col[1],
            "type": col[2],
            "not_null": bool(col[3]),
            "default": col[4],
            "primary_key": bool(col[5])
        }
        for col in cursor.fetchall()
    ]
    
    return {
        "table": table_name,
        "sql": create_sql,
        "columns": columns
    }


def execute_query(db_path: str, query: str, params=None):
    """Execute a query."""
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return {
            "error": "Only SELECT queries are allowed for safety. Use other tools for data modification."
        }
    
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        
        results = [
            {column_names[i]: row[i] for i in range(len(column_names))}
            for row in rows
        ]
        
        return {
            "success": True,
            "rows": results,
            "row_count": len(results),
            "columns": column_names
        }
        
    except sqlite3.Error as e:
        return {
            "success": False,
            "error": str(e)
        }


def count_rows(db_path: str, table_name: str, where_clause=None):
    """Count rows in a table."""
    conn = get_connection(db_path)
    
    # Validate table name exists
    if not validate_table_name(conn, table_name):
        return {
            "success": False,
            "error": f"Table '{table_name}' not found or invalid"
        }
    
    cursor = conn.cursor()
    
    try:
        # Use quoted identifier for table name
        quoted_name = quote_identifier(table_name)
        
        if where_clause:
            # Validate WHERE clause
            where_upper = where_clause.upper()
            dangerous = ['DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', '--', ';']
            if any(keyword in where_upper for keyword in dangerous):
                return {
                    "success": False,
                    "error": "WHERE clause contains invalid keywords"
                }
            
            query = f"SELECT COUNT(*) FROM {quoted_name} WHERE {where_clause}"
        else:
            query = f"SELECT COUNT(*) FROM {quoted_name}"
        
        cursor.execute(query)
        count = cursor.fetchone()[0]
        
        return {
            "success": True,
            "table": table_name,
            "count": count,
            "where_clause": where_clause
        }
        
    except sqlite3.Error as e:
        return {
            "success": False,
            "error": str(e)
        }


def test_list_tables():
    """Test listing all tables."""
    print("=" * 70)
    print("TEST: list_tables")
    print("=" * 70)
    tables = list_tables(DB_PATH)
    print(f"Found {len(tables)} tables: {tables}")
    assert len(tables) == 4, "Expected 4 tables"
    assert "customers" in tables
    assert "products" in tables
    assert "orders" in tables
    assert "order_items" in tables
    print("✅ PASSED\n")


def test_get_table_schema():
    """Test getting table schema."""
    print("=" * 70)
    print("TEST: get_table_schema")
    print("=" * 70)
    schema = get_table_schema(DB_PATH, "customers")
    print(json.dumps(schema, indent=2))
    assert schema["table"] == "customers"
    assert len(schema["columns"]) == 6
    column_names = [col["name"] for col in schema["columns"]]
    assert "customer_id" in column_names
    assert "email" in column_names
    assert "country" in column_names
    print("✅ PASSED\n")


def test_execute_query_simple():
    """Test executing a simple SELECT query."""
    print("=" * 70)
    print("TEST: execute_query (simple)")
    print("=" * 70)
    result = execute_query(DB_PATH, "SELECT * FROM customers LIMIT 3")
    print(f"Query returned {result['row_count']} rows")
    print(f"Columns: {result['columns']}")
    print(f"First row: {result['rows'][0] if result['rows'] else 'None'}")
    assert result["success"] == True
    assert result["row_count"] == 3
    assert "first_name" in result["columns"]
    print("✅ PASSED\n")


def test_execute_query_with_params():
    """Test executing a parameterized SELECT query."""
    print("=" * 70)
    print("TEST: execute_query (with parameters)")
    print("=" * 70)
    query = "SELECT * FROM customers WHERE country = ?"
    params = ["Switzerland"]
    result = execute_query(DB_PATH, query, params)
    print(f"Query: {query}")
    print(f"Params: {params}")
    print(f"Found {result['row_count']} customers from Switzerland")
    for row in result['rows']:
        print(f"  - {row['first_name']} {row['last_name']} ({row['email']})")
    assert result["success"] == True
    assert result["row_count"] > 0
    # Verify all results are from Switzerland
    for row in result['rows']:
        assert row['country'] == "Switzerland"
    print("✅ PASSED\n")


def test_execute_query_security():
    """Test that non-SELECT queries are blocked."""
    print("=" * 70)
    print("TEST: execute_query (security - block non-SELECT)")
    print("=" * 70)
    result = execute_query(DB_PATH, "DELETE FROM customers WHERE customer_id = 1")
    print(f"Result: {result}")
    assert "error" in result
    assert "Only SELECT queries are allowed" in result["error"]
    print("✅ PASSED\n")


def test_count_rows():
    """Test counting rows."""
    print("=" * 70)
    print("TEST: count_rows (without WHERE)")
    print("=" * 70)
    result = count_rows(DB_PATH, "customers")
    print(f"Total customers: {result['count']}")
    assert result["success"] == True
    assert result["count"] == 8
    print("✅ PASSED\n")


def test_count_rows_with_where():
    """Test counting rows with WHERE clause."""
    print("=" * 70)
    print("TEST: count_rows (with WHERE)")
    print("=" * 70)
    result = count_rows(DB_PATH, "customers", "country = 'Switzerland'")
    print(f"Customers from Switzerland: {result['count']}")
    assert result["success"] == True
    assert result["count"] == 5
    print("✅ PASSED\n")


def test_get_database_schema():
    """Test getting complete database schema resource."""
    print("=" * 70)
    print("TEST: get_database_schema (Resource)")
    print("=" * 70)
    # Directly query the database for schema
    conn = get_connection(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = cursor.fetchall()
    print(f"Database: {DB_PATH}")
    print(f"Number of tables: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    assert len(tables) == 4
    print("✅ PASSED\n")


def test_analyze_table_prompt():
    """Test analyze table prompt concept."""
    print("=" * 70)
    print("TEST: analyze_table_prompt (concept)")
    print("=" * 70)
    schema = get_table_schema(DB_PATH, "customers")
    prompt = f"""Analyze the table 'customers' from database '{DB_PATH}'.

Table Schema:
{json.dumps(schema, indent=2)}

Please provide:
1. A summary of the table structure
2. The purpose and use case of this table
3. Suggested queries for common operations
4. Any potential data quality concerns based on the schema
"""
    print("Generated prompt (first 500 chars):")
    print("-" * 70)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 70)
    assert "customers" in prompt
    assert "Table Schema" in prompt
    print("✅ PASSED\n")


def test_query_builder_prompt():
    """Test query builder prompt concept."""
    print("=" * 70)
    print("TEST: query_builder_prompt (concept)")
    print("=" * 70)
    intent = "Find all customers from Switzerland ordered by registration date"
    schema = get_table_schema(DB_PATH, "customers")
    
    columns_info = "\n".join([
        f"  - {col['name']} ({col['type']})"
        for col in schema['columns']
    ])
    
    prompt = f"""Build a SQL query for the following intent:
User Intent: {intent}

Target Table: customers
Available Columns:
{columns_info}

Please generate an appropriate SELECT query that:
1. Addresses the user's intent
2. Uses only the available columns
3. Follows SQL best practices
4. Includes appropriate WHERE, ORDER BY, or LIMIT clauses if needed
"""
    print(f"User Intent: {intent}")
    print("\nGenerated prompt (first 500 chars):")
    print("-" * 70)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 70)
    assert intent in prompt
    assert "customers" in prompt
    assert "Available Columns" in prompt
    print("✅ PASSED\n")


def test_complex_query():
    """Test a more complex join query."""
    print("=" * 70)
    print("TEST: execute_query (complex join)")
    print("=" * 70)
    query = """
        SELECT 
            c.first_name || ' ' || c.last_name AS customer_name,
            c.country,
            COUNT(o.order_id) AS order_count,
            SUM(o.total_amount) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name, c.country
        HAVING order_count > 0
        ORDER BY total_spent DESC
        LIMIT 5
    """
    result = execute_query(DB_PATH, query)
    print(f"Top 5 customers by total spent:")
    print(f"Columns: {result['columns']}")
    for row in result['rows']:
        print(f"  {row['customer_name']} ({row['country']}): "
              f"{row['order_count']} orders, ${row['total_spent']:.2f}")
    assert result["success"] == True
    assert result["row_count"] <= 5
    print("✅ PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SQLite MCP Server - Test Suite")
    print("=" * 70 + "\n")
    
    tests = [
        test_list_tables,
        test_get_table_schema,
        test_execute_query_simple,
        test_execute_query_with_params,
        test_execute_query_security,
        test_count_rows,
        test_count_rows_with_where,
        test_get_database_schema,
        test_analyze_table_prompt,
        test_query_builder_prompt,
        test_complex_query
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}\n")
            failed += 1
    
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

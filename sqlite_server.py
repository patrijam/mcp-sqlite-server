"""
SQLite MCP Server - Exercise 5 Implementation

This MCP server provides access to SQLite databases through the Model Context Protocol.
It implements Resources, Tools, and Prompts as per MCP Server concepts.

Resources: SQLite databases and tables
Tools: Query execution, table listing, schema inspection  
Prompts: Predefined interactions for common queries
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Optional
from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("SQLite MCP Server")

# Database connection cache
_db_connections: dict[str, sqlite3.Connection] = {}


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get or create a database connection."""
    if db_path not in _db_connections:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        _db_connections[db_path] = conn
    return _db_connections[db_path]


@mcp.resource("sqlite://{db_path}/schema")
def get_database_schema(db_path: str) -> str:
    """
    Resource: Get the complete schema of a SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        JSON string with database schema information
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = []
    for row in cursor.fetchall():
        table_name = row[0]
        create_sql = row[1]
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
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
        
        tables.append({
            "name": table_name,
            "sql": create_sql,
            "columns": columns
        })
    
    schema = {
        "database": db_path,
        "tables": tables
    }
    
    return json.dumps(schema, indent=2)


@mcp.tool()
def list_tables(db_path: str) -> list[str]:
    """
    Tool: List all tables in a SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        List of table names
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    return [row[0] for row in cursor.fetchall()]


@mcp.tool()
def get_table_schema(db_path: str, table_name: str) -> dict[str, Any]:
    """
    Tool: Get the schema of a specific table.
    
    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table
        
    Returns:
        Dictionary with table schema information
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Get table creation SQL
    cursor.execute("""
        SELECT sql 
        FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    result = cursor.fetchone()
    if not result:
        return {"error": f"Table '{table_name}' not found"}
    
    create_sql = result[0]
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
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


@mcp.tool()
def execute_query(db_path: str, query: str, params: Optional[list] = None) -> dict[str, Any]:
    """
    Tool: Execute a SQL query on the database.
    
    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute (SELECT statements only for safety)
        params: Optional list of parameters for parameterized queries
        
    Returns:
        Dictionary with query results and metadata
    """
    # Safety check - only allow SELECT queries
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
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        
        # Convert rows to list of dictionaries
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


@mcp.tool()
def count_rows(db_path: str, table_name: str, where_clause: Optional[str] = None) -> dict[str, Any]:
    """
    Tool: Count rows in a table, optionally with a WHERE clause.
    
    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table
        where_clause: Optional WHERE clause (without the WHERE keyword)
        
    Returns:
        Dictionary with count result
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        if where_clause:
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
        else:
            query = f"SELECT COUNT(*) FROM {table_name}"
        
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


@mcp.prompt()
def analyze_table_prompt(db_path: str, table_name: str) -> str:
    """
    Prompt: Generate a comprehensive analysis prompt for a table.
    
    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table to analyze
        
    Returns:
        Formatted prompt string
    """
    schema = get_table_schema(db_path, table_name)
    
    if "error" in schema:
        return f"Error: {schema['error']}"
    
    prompt = f"""Analyze the table '{table_name}' from database '{db_path}'.

Table Schema:
{json.dumps(schema, indent=2)}

Please provide:
1. A summary of the table structure
2. The purpose and use case of this table
3. Suggested queries for common operations
4. Any potential data quality concerns based on the schema
"""
    
    return prompt


@mcp.prompt()
def query_builder_prompt(db_path: str, table_name: str, user_intent: str) -> str:
    """
    Prompt: Help build SQL queries based on user intent.
    
    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the table
        user_intent: What the user wants to achieve
        
    Returns:
        Formatted prompt string for query building
    """
    schema = get_table_schema(db_path, table_name)
    
    if "error" in schema:
        return f"Error: {schema['error']}"
    
    columns_info = "\n".join([
        f"  - {col['name']} ({col['type']})"
        for col in schema['columns']
    ])
    
    prompt = f"""Build a SQL query for the following intent:
User Intent: {user_intent}

Target Table: {table_name}
Available Columns:
{columns_info}

Please generate an appropriate SELECT query that:
1. Addresses the user's intent
2. Uses only the available columns
3. Follows SQL best practices
4. Includes appropriate WHERE, ORDER BY, or LIMIT clauses if needed
"""
    
    return prompt


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

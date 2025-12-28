"""
Database schema upgrade script.
Adds missing columns to services table.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "control-center.db"

def upgrade_database():
    """Add missing columns to services table."""
    print(f"Upgrading database at {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(services)")
        columns = {row[1]: row for row in cursor.fetchall()}
        print(f"Current columns: {list(columns.keys())}")

        # Add missing columns
        columns_to_add = []

        if 'description' not in columns:
            columns_to_add.append(("description", "VARCHAR(500)"))

        if 'health' not in columns:
            columns_to_add.append(("health", "VARCHAR(20)", "unknown"))

        if 'cwd' not in columns:
            columns_to_add.append(("cwd", "VARCHAR(500)"))

        if 'is_system' not in columns:
            columns_to_add.append(("is_system", "BOOLEAN", "0"))

        # Execute ALTER TABLE statements
        for col_info in columns_to_add:
            col_name = col_info[0]
            col_type = col_info[1]
            default = col_info[2] if len(col_info) > 2 else None

            if default:
                sql = f"ALTER TABLE services ADD COLUMN {col_name} {col_type} DEFAULT '{default}'"
            else:
                sql = f"ALTER TABLE services ADD COLUMN {col_name} {col_type}"

            print(f"Executing: {sql}")
            cursor.execute(sql)

        conn.commit()
        print("✓ Database upgraded successfully")

        # Show final schema
        cursor.execute("PRAGMA table_info(services)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"Final columns: {final_columns}")

    except Exception as e:
        print(f"✗ Error upgrading database: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_database()

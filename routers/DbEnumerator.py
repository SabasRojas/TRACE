from fastapi import APIRouter, Form
import mysql.connector
from typing import List, Dict, Any
from services.DbEnumerator_service import store_db_enumeration_results

router = APIRouter(prefix="/tools/db-enumerator", tags=["db_enumerator"])

PII_KEYWORDS = ["user", "email", "name", "ssn", "dob", "address", "phone", "credit", "card"]

@router.post("/")
def enumerate_database(
    host: str = Form(...),
    port: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    project_id: str = Form(...)
):
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Fetch MySQL server version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]

        # List all databases
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall() if db[0] not in ["information_schema", "performance_schema", "mysql", "sys"]]

        result_summary: List[Dict[str, Any]] = []

        for db in databases:
            cursor.execute(f"USE `{db}`")
            cursor.execute("SHOW TABLES")
            tables = [t[0] for t in cursor.fetchall()]

            pii_tables = []
            table_details = []

            for table in tables:
                # Optional: Use table structure to identify possible PII (column names)
                cursor.execute(f"DESCRIBE `{table}`")
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]

                if any(any(kw in col.lower() for kw in PII_KEYWORDS) for col in column_names):
                    pii_tables.append(table)

                table_details.append({
                    "name": table,
                    "columns": column_names
                })

            result_summary.append({
                "database": db,
                "total_tables": len(tables),
                "pii_tables": pii_tables,
                "tables": table_details
            })

        final_result = {
            "status": "success",
            "version": version,
            "databases": result_summary
        }

        store_db_enumeration_results(project_id, final_result)

        return final_result

    except mysql.connector.Error as e:
        return {"status": "error", "message": f"MySQL Error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected Error: {str(e)}"}

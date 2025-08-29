from neo4j import GraphDatabase
import json
from typing import Dict, Any, List

from services.neo4j_driver import driver  # assumes you already initialized it in neo4j_driver.py

def store_db_enumeration_results(project_id: str, enumeration: Dict[str, Any]):
    """
    Stores DB enumeration results under a Project node in Neo4j.

    Arguments:
        project_id (str): ID of the project node to link the data to
        enumeration (dict): Output dict containing version and database info
    """
    if "databases" not in enumeration:
        raise ValueError("Invalid enumeration result format")

    with driver.session() as session:
        for db in enumeration["databases"]:
            db_name = db["database"]
            tables: List[str] = db.get("tables", [])
            pii_tables: List[str] = db.get("pii_tables", [])

            # Create or update the Database node and relationship to Project
            session.run("""
                MATCH (p:Project {id: $project_id})
                MERGE (d:Database {name: $db_name})
                MERGE (p)-[:ENUMERATED]->(d)
                SET d.totalTables = $total_tables,
                    d.piiTables = $pii_tables
            """, project_id=project_id,
                 db_name=db_name,
                 total_tables=len(tables),
                 pii_tables=json.dumps(pii_tables))

            # Create relationships from Database -> Table nodes
            for table in tables:
                session.run("""
                    MATCH (d:Database {name: $db_name})
                    MERGE (t:Table {name: $table_name})
                    MERGE (d)-[:CONTAINS]->(t)
                """, db_name=db_name, table_name=table)

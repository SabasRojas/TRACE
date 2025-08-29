import logging
from neo4j import GraphDatabase, basic_auth

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Neo4j connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
DEFAULT_DATABASE = "neo4j"

# Create a single global driver instance
driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

import logging
from neo4j import GraphDatabase, basic_auth

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Neo4j connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
DEFAULT_DATABASE = "neo4j"

# Create a single global driver instance
driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))


def create_database_if_not_exists(db_name: str):
    """Creates the specified Neo4j database if it does not already exist."""
    """Creates the specified Neo4j database if it does not already exist."""
    with driver.session(database="system") as session:
        def create_db(tx, db_name):
            result = tx.run("SHOW DATABASES")
            existing_dbs = [record["name"] for record in result]
            if db_name not in existing_dbs:
                existing_dbs = [record["name"] for record in result]
            if db_name not in existing_dbs:
                tx.run("CREATE DATABASE $dbName", dbName=db_name)
                logger.info(f"Database '{db_name}' created.")
                logger.info(f"Database '{db_name}' created.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
                logger.info(f"Database '{db_name}' already exists.")

        session.execute_write(create_db, db_name)


def test_connection(database_name: str = DEFAULT_DATABASE):
    """Tests connectivity to the database."""
    try:
        with driver.session(database=database_name) as session:
            result = session.run("RETURN 'Connection successful!' AS message")
            for record in result:
                logger.info(record["message"])
    except Exception as e:
        logger.error(f"Connection test failed: {e}")


def get_driver(no_init_error: bool = False):
    """Returns the Neo4j driver instance."""
    try:
        return driver
    except Exception as e:
        if no_init_error:
            logger.warning("Driver access failed, returning None")
            return None
        raise e


def close_driver():
    """Closes the global driver instance (typically used during shutdown)."""
    if driver:
        driver.close()
        logger.info("Neo4j driver closed.")


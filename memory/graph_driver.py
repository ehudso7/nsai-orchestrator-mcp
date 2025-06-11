from neo4j import GraphDatabase
import os
import logging

logger = logging.getLogger(__name__)

class GraphMemory:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, user, password]):
            logger.warning("Neo4j credentials not provided. GraphMemory will run in mock mode.")
            self.driver = None
        else:
            try:
                logger.info(f"[GraphMemory] Connecting to Neo4j at: {uri}")
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def insert_context(self, node_id: str, label: str, content: str):
        if not self.driver:
            logger.debug(f"Mock GraphMemory: Would insert context {node_id} with label {label}")
            return
            
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n.content = $content
        """
        try:
            with self.driver.session() as session:
                session.run(query, id=node_id, content=content)
        except Exception as e:
            logger.error(f"Failed to insert context: {e}")

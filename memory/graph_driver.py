from neo4j import GraphDatabase

class GraphMemory:
    def __init__(self):
        uri = "bolt://neo4j:7687"
        user = "neo4j"
        password = "password"
        print(f"[GraphMemory] CONNECTING TO: {uri}")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_context(self, node_id: str, label: str, content: str):
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n.content = $content
        """
        with self.driver.session() as session:
            session.run(query, id=node_id, content=content)

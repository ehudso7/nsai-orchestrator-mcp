"""Enhanced memory system with Redis cache and Neo4j graph storage."""

import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta

import aioredis
from neo4j import AsyncGraphDatabase
import structlog

from config import get_settings
from core.logging import performance_logger
from core.metrics import metrics_collector
from schemas import MemoryNode, MemoryEdge, MemoryGraph, MemoryQuery

logger = structlog.get_logger()
settings = get_settings()


class EnhancedMemorySystem:
    """Enhanced memory system with intelligent caching and graph storage."""
    
    def __init__(self):
        self.redis_pool = None
        self.neo4j_driver = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "deletes": 0
        }
        self.node_count = 0
        self.edge_count = 0
    
    async def initialize(self):
        """Initialize Redis and Neo4j connections."""
        try:
            # Initialize Redis connection pool
            self.redis_pool = aioredis.ConnectionPool.from_url(
                f"redis://{settings.database.redis_host}:{settings.database.redis_port}",
                password=settings.database.redis_password,
                db=settings.database.redis_db,
                max_connections=settings.database.redis_max_connections,
                decode_responses=True
            )
            
            # Test Redis connection
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            await redis.ping()
            logger.info("Redis connection established")
            
            # Initialize Neo4j driver
            self.neo4j_driver = AsyncGraphDatabase.driver(
                settings.database.neo4j_uri,
                auth=(settings.database.neo4j_user, settings.database.neo4j_password),
                max_connection_lifetime=settings.database.neo4j_max_connection_lifetime,
                max_connection_pool_size=settings.database.neo4j_max_connection_pool_size
            )
            
            # Test Neo4j connection
            await self.neo4j_driver.verify_connectivity()
            logger.info("Neo4j connection established")
            
            # Initialize database schema
            await self._initialize_schema()
            
            # Load initial statistics
            await self._update_statistics()
            
            logger.info("Enhanced memory system initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize memory system", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup connections."""
        try:
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            if self.neo4j_driver:
                await self.neo4j_driver.close()
            
            logger.info("Memory system cleanup completed")
            
        except Exception as e:
            logger.error("Error during memory system cleanup", error=str(e))
    
    async def _initialize_schema(self):
        """Initialize Neo4j schema and constraints."""
        async with self.neo4j_driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT memory_node_id IF NOT EXISTS FOR (n:MemoryNode) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT agent_result_id IF NOT EXISTS FOR (n:AgentResult) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (n:Task) REQUIRE n.id IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    # Constraint might already exist
                    logger.debug("Constraint creation skipped", constraint=constraint, error=str(e))
            
            # Create indexes
            indexes = [
                "CREATE INDEX memory_node_session_id IF NOT EXISTS FOR (n:MemoryNode) ON (n.session_id)",
                "CREATE INDEX memory_node_created_at IF NOT EXISTS FOR (n:MemoryNode) ON (n.created_at)",
                "CREATE INDEX memory_node_tags IF NOT EXISTS FOR (n:MemoryNode) ON (n.tags)"
            ]
            
            for index in indexes:
                try:
                    await session.run(index)
                except Exception as e:
                    logger.debug("Index creation skipped", index=index, error=str(e))
    
    async def insert_node(self, node: MemoryNode) -> bool:
        """Insert a memory node with Redis caching and Neo4j persistence."""
        start_time = time.time()
        
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Store in Redis cache
            cache_key = f"node:{node.id}"
            node_data = {
                "id": node.id,
                "label": node.label,
                "content": node.content,
                "created_at": node.created_at.isoformat(),
                "session_id": node.session_id,
                "tags": node.tags,
                "ttl": node.ttl
            }
            
            # Set TTL if specified
            ttl = node.ttl or settings.app.memory_ttl_seconds
            await redis.setex(cache_key, ttl, json.dumps(node_data))
            
            # Store in Neo4j
            async with self.neo4j_driver.session() as session:
                query = """
                MERGE (n:MemoryNode {id: $id})
                SET n.label = $label,
                    n.content = $content,
                    n.created_at = datetime($created_at),
                    n.session_id = $session_id,
                    n.tags = $tags,
                    n.ttl = $ttl
                RETURN n
                """
                
                await session.run(query, **node_data)
            
            # Update statistics
            self.cache_stats["writes"] += 1
            self.node_count += 1
            
            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_memory_operation("insert", "both")
            performance_logger.memory_operation("insert", duration_ms)
            
            logger.info("Memory node inserted", node_id=node.id, duration_ms=duration_ms)
            
            return True
            
        except Exception as e:
            logger.error("Failed to insert memory node", node_id=node.id, error=str(e))
            return False
    
    async def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get a memory node with Redis fallback to Neo4j."""
        start_time = time.time()
        
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            cache_key = f"node:{node_id}"
            
            # Try Redis first
            cached_data = await redis.get(cache_key)
            if cached_data:
                self.cache_stats["hits"] += 1
                metrics_collector.record_cache_hit("redis")
                
                node_data = json.loads(cached_data)
                return MemoryNode(
                    id=node_data["id"],
                    label=node_data["label"],
                    content=node_data["content"],
                    created_at=datetime.fromisoformat(node_data["created_at"]),
                    session_id=node_data.get("session_id"),
                    tags=node_data.get("tags", []),
                    ttl=node_data.get("ttl")
                )
            
            # Fallback to Neo4j
            self.cache_stats["misses"] += 1
            metrics_collector.record_cache_miss("redis")
            
            async with self.neo4j_driver.session() as session:
                query = """
                MATCH (n:MemoryNode {id: $node_id})
                RETURN n.id as id, n.label as label, n.content as content,
                       n.created_at as created_at, n.session_id as session_id,
                       n.tags as tags, n.ttl as ttl
                """
                
                result = await session.run(query, node_id=node_id)
                record = await result.single()
                
                if record:
                    node_data = dict(record)
                    
                    # Cache in Redis for future access
                    ttl = node_data.get("ttl") or settings.app.memory_ttl_seconds
                    await redis.setex(cache_key, ttl, json.dumps({
                        **node_data,
                        "created_at": node_data["created_at"].isoformat()
                    }))
                    
                    duration_ms = (time.time() - start_time) * 1000
                    performance_logger.memory_operation("get", duration_ms, cache_hit=False)
                    
                    return MemoryNode(
                        id=node_data["id"],
                        label=node_data["label"],
                        content=node_data["content"],
                        created_at=node_data["created_at"],
                        session_id=node_data.get("session_id"),
                        tags=node_data.get("tags", []),
                        ttl=node_data.get("ttl")
                    )
            
            return None
            
        except Exception as e:
            logger.error("Failed to get memory node", node_id=node_id, error=str(e))
            return None
    
    async def insert_edge(self, edge: MemoryEdge) -> bool:
        """Insert a memory edge (relationship)."""
        start_time = time.time()
        
        try:
            async with self.neo4j_driver.session() as session:
                query = """
                MATCH (source:MemoryNode {id: $source_id})
                MATCH (target:MemoryNode {id: $target_id})
                MERGE (source)-[r:RELATES {type: $relationship}]->(target)
                SET r.weight = $weight,
                    r.properties = $properties,
                    r.created_at = datetime()
                RETURN r
                """
                
                await session.run(
                    query,
                    source_id=edge.source,
                    target_id=edge.target,
                    relationship=edge.relationship,
                    weight=edge.weight,
                    properties=edge.properties
                )
            
            self.edge_count += 1
            
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_memory_operation("insert_edge", "neo4j")
            performance_logger.memory_operation("insert_edge", duration_ms)
            
            return True
            
        except Exception as e:
            logger.error("Failed to insert memory edge", edge=edge.dict(), error=str(e))
            return False
    
    async def query(self, query: MemoryQuery) -> Dict[str, Any]:
        """Execute a memory query."""
        start_time = time.time()
        
        try:
            if query.query_type == "search":
                result = await self._search_nodes(query.filters, query.limit, query.offset)
            elif query.query_type == "neighbors":
                result = await self._get_neighbors(query.filters, query.limit)
            elif query.query_type == "path":
                result = await self._find_path(query.filters)
            elif query.query_type == "subgraph":
                result = await self._get_subgraph(query.filters, query.limit)
            else:
                raise ValueError(f"Unknown query type: {query.query_type}")
            
            duration_ms = (time.time() - start_time) * 1000
            performance_logger.memory_operation(f"query_{query.query_type}", duration_ms)
            
            return result
            
        except Exception as e:
            logger.error("Memory query failed", query=query.dict(), error=str(e))
            raise
    
    async def _search_nodes(self, filters: Dict[str, Any], limit: int, offset: int) -> Dict[str, Any]:
        """Search for nodes based on filters."""
        async with self.neo4j_driver.session() as session:
            # Build dynamic query based on filters
            conditions = []
            params = {"limit": limit, "offset": offset}
            
            if "label" in filters:
                conditions.append("n.label = $label")
                params["label"] = filters["label"]
            
            if "session_id" in filters:
                conditions.append("n.session_id = $session_id")
                params["session_id"] = filters["session_id"]
            
            if "tags" in filters:
                conditions.append("ANY(tag IN $tags WHERE tag IN n.tags)")
                params["tags"] = filters["tags"]
            
            if "content_contains" in filters:
                conditions.append("n.content CONTAINS $content_contains")
                params["content_contains"] = filters["content_contains"]
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            query = f"""
            MATCH (n:MemoryNode)
            {where_clause}
            RETURN n
            ORDER BY n.created_at DESC
            SKIP $offset
            LIMIT $limit
            """
            
            result = await session.run(query, **params)
            nodes = []
            
            async for record in result:
                node_data = dict(record["n"])
                nodes.append({
                    "id": node_data["id"],
                    "label": node_data["label"],
                    "content": node_data["content"],
                    "created_at": node_data["created_at"].isoformat(),
                    "session_id": node_data.get("session_id"),
                    "tags": node_data.get("tags", [])
                })
            
            return {"nodes": nodes, "total": len(nodes)}
    
    async def _get_neighbors(self, filters: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Get neighboring nodes."""
        node_id = filters.get("node_id")
        if not node_id:
            raise ValueError("node_id is required for neighbors query")
        
        async with self.neo4j_driver.session() as session:
            query = """
            MATCH (n:MemoryNode {id: $node_id})-[r]-(neighbor:MemoryNode)
            RETURN neighbor, r
            LIMIT $limit
            """
            
            result = await session.run(query, node_id=node_id, limit=limit)
            neighbors = []
            
            async for record in result:
                neighbor_data = dict(record["neighbor"])
                relationship_data = dict(record["r"])
                
                neighbors.append({
                    "node": {
                        "id": neighbor_data["id"],
                        "label": neighbor_data["label"],
                        "content": neighbor_data["content"]
                    },
                    "relationship": {
                        "type": relationship_data.get("type"),
                        "weight": relationship_data.get("weight", 1.0)
                    }
                })
            
            return {"neighbors": neighbors}
    
    async def _find_path(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Find path between two nodes."""
        source_id = filters.get("source_id")
        target_id = filters.get("target_id")
        
        if not source_id or not target_id:
            raise ValueError("source_id and target_id are required for path query")
        
        async with self.neo4j_driver.session() as session:
            query = """
            MATCH path = shortestPath((source:MemoryNode {id: $source_id})-[*]-(target:MemoryNode {id: $target_id}))
            RETURN path
            """
            
            result = await session.run(query, source_id=source_id, target_id=target_id)
            record = await result.single()
            
            if record:
                # Process path data
                return {"path_found": True, "path": "path_data"}  # Simplified for now
            else:
                return {"path_found": False}
    
    async def _get_subgraph(self, filters: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Get subgraph around a node."""
        node_id = filters.get("node_id")
        depth = filters.get("depth", 2)
        
        if not node_id:
            raise ValueError("node_id is required for subgraph query")
        
        async with self.neo4j_driver.session() as session:
            query = f"""
            MATCH path = (center:MemoryNode {{id: $node_id}})-[*1..{depth}]-(connected:MemoryNode)
            RETURN path
            LIMIT $limit
            """
            
            result = await session.run(query, node_id=node_id, limit=limit)
            
            # Process subgraph data
            nodes = set()
            edges = []
            
            async for record in result:
                # Extract nodes and relationships from path
                pass  # Simplified for now
            
            return {"subgraph": {"nodes": list(nodes), "edges": edges}}
    
    async def get_graph(self, filters: Optional[Dict[str, Any]] = None) -> MemoryGraph:
        """Get memory graph for visualization."""
        try:
            async with self.neo4j_driver.session() as session:
                # Get nodes
                node_query = "MATCH (n:MemoryNode) RETURN n LIMIT 100"
                node_result = await session.run(node_query)
                
                nodes = []
                async for record in node_result:
                    node_data = dict(record["n"])
                    nodes.append(MemoryNode(
                        id=node_data["id"],
                        label=node_data["label"],
                        content=node_data["content"],
                        created_at=node_data["created_at"],
                        session_id=node_data.get("session_id"),
                        tags=node_data.get("tags", [])
                    ))
                
                # Get edges
                edge_query = """
                MATCH (source:MemoryNode)-[r:RELATES]->(target:MemoryNode)
                RETURN source.id as source, target.id as target, r.type as relationship,
                       r.weight as weight, r.properties as properties
                LIMIT 100
                """
                edge_result = await session.run(edge_query)
                
                edges = []
                async for record in edge_result:
                    edges.append(MemoryEdge(
                        source=record["source"],
                        target=record["target"],
                        relationship=record["relationship"],
                        weight=record.get("weight", 1.0),
                        properties=record.get("properties", {})
                    ))
                
                return MemoryGraph(
                    nodes=nodes,
                    edges=edges,
                    metadata={
                        "total_nodes": len(nodes),
                        "total_edges": len(edges),
                        "generated_at": datetime.utcnow().isoformat()
                    }
                )
                
        except Exception as e:
            logger.error("Failed to get memory graph", error=str(e))
            raise
    
    async def maintenance(self):
        """Perform memory system maintenance."""
        try:
            # Clean up expired cache entries
            await self._cleanup_expired_cache()
            
            # Clean up old nodes based on TTL
            await self._cleanup_expired_nodes()
            
            # Update statistics
            await self._update_statistics()
            
            logger.info("Memory maintenance completed")
            
        except Exception as e:
            logger.error("Memory maintenance failed", error=str(e))
    
    async def _cleanup_expired_cache(self):
        """Clean up expired Redis cache entries."""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        # Redis automatically handles TTL, but we can clean up any orphaned keys
        pattern = "node:*"
        async for key in redis.scan_iter(match=pattern):
            ttl = await redis.ttl(key)
            if ttl == -1:  # Key exists but has no TTL
                await redis.expire(key, settings.app.memory_ttl_seconds)
    
    async def _cleanup_expired_nodes(self):
        """Clean up expired nodes from Neo4j."""
        async with self.neo4j_driver.session() as session:
            query = """
            MATCH (n:MemoryNode)
            WHERE n.ttl IS NOT NULL 
            AND datetime() > n.created_at + duration({seconds: n.ttl})
            DELETE n
            RETURN count(n) as deleted_count
            """
            
            result = await session.run(query)
            record = await result.single()
            deleted_count = record["deleted_count"] if record else 0
            
            if deleted_count > 0:
                logger.info("Cleaned up expired nodes", count=deleted_count)
    
    async def _update_statistics(self):
        """Update memory system statistics."""
        try:
            async with self.neo4j_driver.session() as session:
                # Count nodes
                node_result = await session.run("MATCH (n:MemoryNode) RETURN count(n) as count")
                node_record = await node_result.single()
                self.node_count = node_record["count"] if node_record else 0
                
                # Count edges
                edge_result = await session.run("MATCH ()-[r:RELATES]->() RETURN count(r) as count")
                edge_record = await edge_result.single()
                self.edge_count = edge_record["count"] if edge_record else 0
                
        except Exception as e:
            logger.warning("Failed to update statistics", error=str(e))
    
    def get_node_count(self) -> int:
        """Get current node count."""
        return self.node_count
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return self.cache_stats.copy()
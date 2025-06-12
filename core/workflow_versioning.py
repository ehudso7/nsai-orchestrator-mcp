import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from core.models import Workflow, WorkflowExecution, WorkflowStatus
from core.database import SessionLocal
import difflib
import logging

logger = logging.getLogger(__name__)

class WorkflowVersionManager:
    """Manages workflow versions with Git-like functionality"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_version(self, workflow_id: int, message: str = "", author_id: int = None) -> Workflow:
        """Create a new version of a workflow"""
        
        # Get current workflow
        current = self.db.query(Workflow).filter_by(id=workflow_id).first()
        if not current:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create new version
        new_version = Workflow(
            name=f"{current.name} (v{current.version + 1})",
            description=current.description,
            owner_id=current.owner_id,
            status=WorkflowStatus.DRAFT,
            nodes=current.nodes.copy(),
            edges=current.edges.copy(),
            config=current.config.copy(),
            version=current.version + 1,
            parent_workflow_id=workflow_id,
            tags=current.tags.copy(),
            category=current.category
        )
        
        # Add version metadata
        new_version.config["version_info"] = {
            "message": message,
            "author_id": author_id or current.owner_id,
            "created_at": datetime.utcnow().isoformat(),
            "parent_version": current.version,
            "changes": self._calculate_changes(current, new_version)
        }
        
        self.db.add(new_version)
        self.db.commit()
        
        logger.info(f"Created version {new_version.version} of workflow {workflow_id}")
        return new_version
    
    def get_version_history(self, workflow_id: int) -> List[Dict[str, Any]]:
        """Get complete version history of a workflow"""
        
        history = []
        current_id = workflow_id
        
        while current_id:
            workflow = self.db.query(Workflow).filter_by(id=current_id).first()
            if not workflow:
                break
            
            version_info = workflow.config.get("version_info", {})
            history.append({
                "id": workflow.id,
                "version": workflow.version,
                "name": workflow.name,
                "created_at": workflow.created_at.isoformat(),
                "message": version_info.get("message", ""),
                "author_id": version_info.get("author_id"),
                "changes": version_info.get("changes", {})
            })
            
            current_id = workflow.parent_workflow_id
        
        return history
    
    def rollback_to_version(self, workflow_id: int, target_version: int) -> Workflow:
        """Rollback workflow to a specific version"""
        
        # Find target version
        target = self._find_version(workflow_id, target_version)
        if not target:
            raise ValueError(f"Version {target_version} not found for workflow {workflow_id}")
        
        # Create new version that's a copy of the target
        current = self.db.query(Workflow).filter_by(id=workflow_id).first()
        
        rollback = Workflow(
            name=f"{current.name} (Rollback to v{target_version})",
            description=target.description,
            owner_id=current.owner_id,
            status=current.status,
            nodes=target.nodes.copy(),
            edges=target.edges.copy(),
            config=target.config.copy(),
            version=current.version + 1,
            parent_workflow_id=workflow_id,
            tags=target.tags.copy(),
            category=target.category
        )
        
        rollback.config["version_info"] = {
            "message": f"Rollback to version {target_version}",
            "author_id": current.owner_id,
            "created_at": datetime.utcnow().isoformat(),
            "parent_version": current.version,
            "rollback_from": target_version
        }
        
        self.db.add(rollback)
        self.db.commit()
        
        logger.info(f"Rolled back workflow {workflow_id} to version {target_version}")
        return rollback
    
    def diff_versions(self, workflow_id: int, version1: int, version2: int) -> Dict[str, Any]:
        """Calculate differences between two versions"""
        
        v1 = self._find_version(workflow_id, version1)
        v2 = self._find_version(workflow_id, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        return {
            "nodes": self._diff_lists(v1.nodes, v2.nodes),
            "edges": self._diff_lists(v1.edges, v2.edges),
            "config": self._diff_dicts(v1.config, v2.config),
            "summary": self._calculate_changes(v1, v2)
        }
    
    def merge_workflows(self, source_id: int, target_id: int, 
                       strategy: str = "manual") -> Dict[str, Any]:
        """Merge changes from source workflow into target"""
        
        source = self.db.query(Workflow).filter_by(id=source_id).first()
        target = self.db.query(Workflow).filter_by(id=target_id).first()
        
        if not source or not target:
            raise ValueError("Source or target workflow not found")
        
        # Find common ancestor
        common_ancestor = self._find_common_ancestor(source, target)
        
        if strategy == "auto":
            # Automatic merge if no conflicts
            conflicts = self._detect_conflicts(source, target, common_ancestor)
            if conflicts:
                return {
                    "status": "conflict",
                    "conflicts": conflicts,
                    "message": "Manual resolution required"
                }
            
            # Perform automatic merge
            merged = self._auto_merge(source, target, common_ancestor)
        else:
            # Manual merge - return conflict information
            return {
                "status": "manual",
                "source": self._workflow_to_dict(source),
                "target": self._workflow_to_dict(target),
                "common_ancestor": self._workflow_to_dict(common_ancestor) if common_ancestor else None,
                "conflicts": self._detect_conflicts(source, target, common_ancestor)
            }
        
        return merged
    
    def branch_workflow(self, workflow_id: int, branch_name: str) -> Workflow:
        """Create a branch (copy) of a workflow"""
        
        original = self.db.query(Workflow).filter_by(id=workflow_id).first()
        if not original:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        branch = Workflow(
            name=f"{original.name} - {branch_name}",
            description=f"Branch of {original.name}",
            owner_id=original.owner_id,
            status=WorkflowStatus.DRAFT,
            nodes=original.nodes.copy(),
            edges=original.edges.copy(),
            config=original.config.copy(),
            version=1,  # New branch starts at version 1
            parent_workflow_id=None,  # Branches are independent
            tags=original.tags.copy() + ["branch"],
            category=original.category
        )
        
        branch.config["branch_info"] = {
            "branched_from": workflow_id,
            "branched_at": datetime.utcnow().isoformat(),
            "branch_name": branch_name
        }
        
        self.db.add(branch)
        self.db.commit()
        
        logger.info(f"Created branch '{branch_name}' from workflow {workflow_id}")
        return branch
    
    def tag_version(self, workflow_id: int, tag_name: str, message: str = ""):
        """Tag a specific version of a workflow"""
        
        workflow = self.db.query(Workflow).filter_by(id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if "version_tags" not in workflow.config:
            workflow.config["version_tags"] = {}
        
        workflow.config["version_tags"][tag_name] = {
            "version": workflow.version,
            "created_at": datetime.utcnow().isoformat(),
            "message": message
        }
        
        self.db.commit()
        logger.info(f"Tagged workflow {workflow_id} v{workflow.version} as '{tag_name}'")
    
    def _find_version(self, workflow_id: int, version: int) -> Optional[Workflow]:
        """Find a specific version in the workflow history"""
        
        current_id = workflow_id
        while current_id:
            workflow = self.db.query(Workflow).filter_by(id=current_id).first()
            if not workflow:
                break
            
            if workflow.version == version:
                return workflow
            
            current_id = workflow.parent_workflow_id
        
        return None
    
    def _calculate_changes(self, old: Workflow, new: Workflow) -> Dict[str, Any]:
        """Calculate what changed between versions"""
        
        changes = {
            "nodes_added": 0,
            "nodes_removed": 0,
            "nodes_modified": 0,
            "edges_added": 0,
            "edges_removed": 0,
            "config_changes": []
        }
        
        # Compare nodes
        old_node_ids = {n["id"] for n in old.nodes}
        new_node_ids = {n["id"] for n in new.nodes}
        
        changes["nodes_added"] = len(new_node_ids - old_node_ids)
        changes["nodes_removed"] = len(old_node_ids - new_node_ids)
        
        # Check for modified nodes
        for node_id in old_node_ids & new_node_ids:
            old_node = next(n for n in old.nodes if n["id"] == node_id)
            new_node = next(n for n in new.nodes if n["id"] == node_id)
            if old_node != new_node:
                changes["nodes_modified"] += 1
        
        # Compare edges
        old_edge_ids = {e["id"] for e in old.edges}
        new_edge_ids = {e["id"] for e in new.edges}
        
        changes["edges_added"] = len(new_edge_ids - old_edge_ids)
        changes["edges_removed"] = len(old_edge_ids - new_edge_ids)
        
        return changes
    
    def _diff_lists(self, list1: List[Any], list2: List[Any]) -> Dict[str, Any]:
        """Calculate differences between two lists"""
        
        # Convert to strings for comparison
        str1 = json.dumps(list1, sort_keys=True, indent=2)
        str2 = json.dumps(list2, sort_keys=True, indent=2)
        
        diff = list(difflib.unified_diff(
            str1.splitlines(keepends=True),
            str2.splitlines(keepends=True),
            fromfile="version1",
            tofile="version2"
        ))
        
        return {
            "has_changes": len(diff) > 0,
            "diff": "".join(diff),
            "added": len(list2) - len(list1),
            "removed": len(list1) - len(list2)
        }
    
    def _diff_dicts(self, dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[str, Any]:
        """Calculate differences between two dictionaries"""
        
        added = set(dict2.keys()) - set(dict1.keys())
        removed = set(dict1.keys()) - set(dict2.keys())
        modified = {k for k in dict1.keys() & dict2.keys() if dict1[k] != dict2[k]}
        
        return {
            "added": list(added),
            "removed": list(removed),
            "modified": list(modified),
            "changes": {
                k: {"old": dict1.get(k), "new": dict2.get(k)}
                for k in added | removed | modified
            }
        }
    
    def _find_common_ancestor(self, workflow1: Workflow, workflow2: Workflow) -> Optional[Workflow]:
        """Find common ancestor of two workflows"""
        
        # Get ancestry chains
        ancestors1 = set()
        current = workflow1
        while current:
            ancestors1.add(current.id)
            if current.parent_workflow_id:
                current = self.db.query(Workflow).filter_by(id=current.parent_workflow_id).first()
            else:
                break
        
        # Find first common ancestor
        current = workflow2
        while current:
            if current.id in ancestors1:
                return current
            if current.parent_workflow_id:
                current = self.db.query(Workflow).filter_by(id=current.parent_workflow_id).first()
            else:
                break
        
        return None
    
    def _detect_conflicts(self, source: Workflow, target: Workflow, 
                         ancestor: Optional[Workflow]) -> List[Dict[str, Any]]:
        """Detect merge conflicts between workflows"""
        
        conflicts = []
        
        if not ancestor:
            # No common ancestor - everything is a potential conflict
            return [{
                "type": "no_common_ancestor",
                "message": "Workflows have no common history"
            }]
        
        # Check for conflicting node modifications
        for node in ancestor.nodes:
            source_node = next((n for n in source.nodes if n["id"] == node["id"]), None)
            target_node = next((n for n in target.nodes if n["id"] == node["id"]), None)
            
            if source_node and target_node and source_node != target_node and source_node != node:
                conflicts.append({
                    "type": "node_conflict",
                    "node_id": node["id"],
                    "ancestor": node,
                    "source": source_node,
                    "target": target_node
                })
        
        return conflicts
    
    def _auto_merge(self, source: Workflow, target: Workflow, 
                   ancestor: Optional[Workflow]) -> Dict[str, Any]:
        """Automatically merge non-conflicting changes"""
        
        # This is a simplified auto-merge
        # In practice, you'd want more sophisticated merging
        
        merged_nodes = target.nodes.copy()
        merged_edges = target.edges.copy()
        
        # Add new nodes from source
        target_node_ids = {n["id"] for n in target.nodes}
        for node in source.nodes:
            if node["id"] not in target_node_ids:
                merged_nodes.append(node)
        
        # Add new edges from source
        target_edge_ids = {e["id"] for e in target.edges}
        for edge in source.edges:
            if edge["id"] not in target_edge_ids:
                merged_edges.append(edge)
        
        return {
            "status": "success",
            "merged": {
                "nodes": merged_nodes,
                "edges": merged_edges
            }
        }
    
    def _workflow_to_dict(self, workflow: Workflow) -> Dict[str, Any]:
        """Convert workflow to dictionary for comparison"""
        
        return {
            "id": workflow.id,
            "version": workflow.version,
            "nodes": workflow.nodes,
            "edges": workflow.edges,
            "config": workflow.config
        }

def get_version_manager(db: Session = None) -> WorkflowVersionManager:
    """Get workflow version manager instance"""
    
    if db is None:
        db = SessionLocal()
    
    return WorkflowVersionManager(db)
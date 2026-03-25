import time
from typing import Dict, List, Optional
import threading
import logging

class ResourceManager:
    def __init__(self):
        self.available_resources = {}
        self.allocated_resources = {}
        self.lock = threading.Lock()

class Orchestrator:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.tasks: Dict[str, dict] = {}
        self.resource_manager = ResourceManager()
        self.health_check_interval = 30
        self._running = False
        self._health_thread: Optional[threading.Thread] = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def register_node(self, node_id: str, capabilities: dict) -> bool:
        """Register a new node with its capabilities"""
        with self.resource_manager.lock:
            if node_id in self.nodes:
                return False
            
            self.nodes[node_id] = {
                'capabilities': capabilities,
                'status': 'available',
                'last_heartbeat': time.time(),
                'current_load': 0.0
            }
            
            self.resource_manager.available_resources[node_id] = capabilities.copy()
            self.logger.info(f'Node {node_id} registered with capabilities: {capabilities}')
            return True

    def allocate_resources(self, task_id: str, requirements: dict) -> Optional[str]:
        """Allocate resources for a task based on requirements"""
        with self.resource_manager.lock:
            best_node = None
            min_load = float('inf')
            
            for node_id, node in self.nodes.items():
                if node['status'] != 'available':
                    continue
                
                available = self.resource_manager.available_resources[node_id]
                if self._can_satisfy_requirements(available, requirements):
                    if node['current_load'] < min_load:
                        min_load = node['current_load']
                        best_node = node_id
            
            if best_node:
                self._allocate_to_node(best_node, task_id, requirements)
                return best_node
            return None

    def _can_satisfy_requirements(self, available: dict, required: dict) -> bool:
        """Check if available resources can satisfy requirements"""
        for resource, amount in required.items():
            if resource not in available or available[resource] < amount:
                return False
        return True

    def _allocate_to_node(self, node_id: str, task_id: str, requirements: dict):
        """Allocate resources on a specific node"""
        available = self.resource_manager.available_resources[node_id]
        for resource, amount in requirements.items():
            available[resource] -= amount
        
        self.resource_manager.allocated_resources[task_id] = {
            'node_id': node_id,
            'resources': requirements
        }
        
        self.nodes[node_id]['current_load'] += sum(requirements.values())
        self.logger.info(f'Task {task_id} allocated to node {node_id}')

    def release_resources(self, task_id: str):
        """Release resources allocated to a task"""
        with self.resource_manager.lock:
            if task_id not in self.resource_manager.allocated_resources:
                return
            
            allocation = self.resource_manager.allocated_resources[task_id]
            node_id = allocation['node_id']
            
            available = self.resource_manager.available_resources[node_id]
            for resource, amount in allocation['resources'].items():
                available[resource] += amount
            
            self.nodes[node_id]['current_load'] -= sum(allocation['resources'].values())
            del self.resource_manager.allocated_resources[task_id]
            self.logger.info(f'Resources released for task {task_id}')

    def start_health_monitoring(self):
        """Start monitoring node health"""
        self._running = True
        self._health_thread = threading.Thread(target=self._health_check_loop)
        self._health_thread.daemon = True
        self._health_thread.start()

    def stop_health_monitoring(self):
        """Stop health monitoring"""
        self._running = False
        if self._health_thread:
            self._health_thread.join()

    def _health_check_loop(self):
        """Continuous health checking loop"""
        while self._running:
            self._check_node_health()
            time.sleep(self.health_check_interval)

    def _check_node_health(self):
        """Check health status of all nodes"""
        current_time = time.time()
        with self.resource_manager.lock:
            for node_id, node in list(self.nodes.items()):
                if current_time - node['last_heartbeat'] > self.health_check_interval * 2:
                    self._handle_node_failure(node_id)

    def _handle_node_failure(self, node_id: str):
        """Handle node failure and resource reallocation"""
        self.logger.warning(f'Node {node_id} has failed')
        affected_tasks = [
            task_id for task_id, alloc in self.resource_manager.allocated_resources.items()
            if alloc['node_id'] == node_id
        ]
        
        del self.nodes[node_id]
        del self.resource_manager.available_resources[node_id]
        
        for task_id in affected_tasks:
            self.release_resources(task_id)
            # Trigger task rescheduling logic here
            self.logger.info(f'Task {task_id} needs rescheduling due to node failure')

    def update_node_heartbeat(self, node_id: str):
        """Update node's last heartbeat time"""
        if node_id in self.nodes:
            self.nodes[node_id]['last_heartbeat'] = time.time()

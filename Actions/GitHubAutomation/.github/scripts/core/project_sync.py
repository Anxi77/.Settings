"""Board synchronization with issues."""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .api_client import APIClient


class TaskStatus(Enum):
    """Task status enumeration."""
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"
    BLOCKED = "Blocked"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class TaskItem:
    """Task item representation."""
    issue: Dict[str, Any]
    status: TaskStatus
    priority: TaskPriority
    category: Optional[str] = None
    assignee: Optional[str] = None
    board_item: Optional[Any] = None


class BoardSync:
    """Synchronize board with issues and todos."""
    
    def __init__(self, api_client: APIClient, config: Dict[str, Any]):
        """Initialize board synchronizer.
        
        Args:
            api_client: API client
            config: Configuration dictionary
        """
        self.api = api_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration with defaults
        self.board_number = config.get('board_number', 1)
        self.status_field = config.get('status_field_name', 'Status')
        self.priority_field = config.get('priority_field_name', 'Priority')
        self.category_field = config.get('category_field_name', 'Category')
        
        # Label mappings
        self.status_labels = config.get('status_labels', {
            'todo': TaskStatus.TODO,
            'in-progress': TaskStatus.IN_PROGRESS,
            'in-review': TaskStatus.IN_REVIEW,
            'done': TaskStatus.DONE,
            'blocked': TaskStatus.BLOCKED
        })
        
        self.priority_labels = config.get('priority_labels', {
            'priority:low': TaskPriority.LOW,
            'priority:medium': TaskPriority.MEDIUM,
            'priority:high': TaskPriority.HIGH,
            'priority:critical': TaskPriority.CRITICAL
        })
    
    def sync_board(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Synchronize board with repository issues.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Sync results summary
        """
        self.logger.info(f"Starting board sync for {repo_owner}/{repo_name}")
        
        # Use efficient single-query board fetch
        try:
            result = self.api.get_board_with_items(repo_owner, self.board_number)
            board = result.get('organization', {}).get('projectV2') if result else None
        except Exception as e:
            self.logger.error(f"Failed to get board #{self.board_number}: {e}")
            return {'error': str(e)}
        
        # Get current board items (included in query response)
        if board and 'items' in board:
            board_items = self.api.get_board_items(board)
            self.logger.info(f"Fetched {len(board_items)} board items in single query")
        else:
            self.logger.warning("No board data found")
            return {'error': 'Board not found'}
        
        # Get repository issues
        issues = self.api.get_issues(repo_owner, repo_name, state='OPEN')
        task_issues = self._filter_task_issues(issues)
        
        # Create task items mapping
        task_items = self._create_task_items_optimized(task_issues, board_items, board)
        
        # Batch sync status updates
        sync_results = {
            'updated': 0,
            'created': 0,
            'errors': []
        }
        
        # Separate items needing updates vs creation
        items_to_update = []
        items_to_create = []
        
        for task_item in task_items:
            if hasattr(task_item, 'board_item') and task_item.board_item:
                items_to_update.append(task_item)
            else:
                items_to_create.append(task_item)
        
        # Batch update existing items
        if items_to_update:
            try:
                batch_updates = []
                for task_item in items_to_update:
                    field_id = self.api.get_field_id_by_name(repo_owner, self.board_number, self.status_field)
                    if field_id:
                        batch_updates.append({
                            'board_id': board['id'],
                            'item_id': task_item.board_item.get('id') if isinstance(task_item.board_item, dict) else None,
                            'field_id': field_id,
                            'value': task_item.status.value
                        })
                
                if batch_updates:
                    results = self.api.batch_update_items(batch_updates)
                    sync_results['updated'] = len([r for r in results if r])
                        
            except Exception as e:
                error_msg = f"Batch update failed: {e}"
                self.logger.error(error_msg)
                sync_results['errors'].append(error_msg)
        
        # Handle individual operations for items needing creation
        for task_item in items_to_create:
            try:
                created = self._create_project_item(board, task_item)
                if created:
                    sync_results['created'] += 1
            except Exception as e:
                error_msg = f"Failed to create item for issue #{task_item.issue.get('number', 'unknown')}: {e}"
                self.logger.error(error_msg)
                sync_results['errors'].append(error_msg)
        
        # Update board metrics
        self._update_board_metrics(board, task_items)
        
        self.logger.info(f"Board sync completed: {sync_results}")
        return sync_results
    
    def update_task_status(self, repo_owner: str, repo_name: str, issue_number: int, 
                          new_status: TaskStatus) -> bool:
        """Update task status in project board using GraphQL.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            issue_number: Issue number
            new_status: New task status
            
        Returns:
            True if updated successfully
        """
        try:
            # Get project board with items
            board = self.api.get_board_with_items(repo_owner, self.board_number)
            if not board:
                self.logger.error(f"Failed to get project board #{self.board_number}")
                return False
            
            # Find project item for this issue
            board_items = board.get('items', {}).get('nodes', [])
            target_item = None
            
            for item in board_items:
                content = item.get('content', {})
                if content and content.get('number') == issue_number:
                    target_item = item
                    break
            
            if not target_item:
                self.logger.warning(f"Project item not found for issue #{issue_number}")
                
                # Add issue to project board
                try:
                    # Get issue information first
                    issues = self.api.get_issues(repo_owner, repo_name, state='OPEN')
                    target_issue = None
                    for issue in issues:
                        if issue.get('number') == issue_number:
                            target_issue = issue
                            break
                    
                    if not target_issue:
                        self.logger.error(f"Issue #{issue_number} not found")
                        return False
                    
                    # Add issue to board
                    result = self.api.add_item_to_board(board['id'], target_issue['id'])
                    if result and 'addProjectV2ItemById' in result:
                        item_data = result['addProjectV2ItemById']['item']
                        self.logger.info(f"Added issue #{issue_number} to project board")
                        target_item = item_data
                    else:
                        self.logger.error(f"Failed to add issue #{issue_number} to board")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Failed to add issue to board: {e}")
                    return False
            
            # Update status field using GraphQL API
            field_id = self.api.get_field_id_by_name(repo_owner, self.board_number, self.status_field)
            if not field_id:
                self.logger.error(f"Status field '{self.status_field}' not found")
                return False
            
            updated = self.api.update_item_field(
                board['id'],
                target_item['id'],
                field_id,
                new_status.value
            )
            
            if updated:
                self.logger.info(f"Updated task #{issue_number} status to {new_status.value}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update task status: {e}")
            return False
    
    def get_project_statistics(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Get project board statistics.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Project statistics dictionary
        """
        try:
            board = self.api.get_board_with_items(repo_owner, self.board_number)
            if not board or 'items' not in board:
                return {'error': 'Board not found'}
            
            board_items = board.get('items', {}).get('nodes', [])
            
            # Count by status
            status_counts = {status.value: 0 for status in TaskStatus}
            priority_counts = {priority.value: 0 for priority in TaskPriority}
            
            total_items = len(board_items)
            
            # Get issues for analysis
            issues = self.api.get_issues(repo_owner, repo_name, state='OPEN')
            
            for item in board_items:
                # Find corresponding issue data
                if 'content' in item and item['content']:
                    issue_number = item['content'].get('number')
                    issue_data = next((issue for issue in issues if issue.get('number') == issue_number), None)
                    
                    if issue_data:
                        # Extract status and priority from labels
                        status = self._extract_status_from_labels(issue_data)
                        priority = self._extract_priority_from_labels(issue_data)
                        
                        status_counts[status.value] += 1
                        priority_counts[priority.value] += 1
                    else:
                        # Default counts for items without issue data
                        status_counts[TaskStatus.TODO.value] += 1
                        priority_counts[TaskPriority.MEDIUM.value] += 1
            
            return {
                'total_tasks': total_items,
                'status_breakdown': status_counts,
                'priority_breakdown': priority_counts,
                'completion_rate': (
                    status_counts[TaskStatus.DONE.value] / max(total_items, 1) * 100
                )
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project statistics: {e}")
            return {'error': str(e)}
    
    def _filter_task_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter issues that should be tracked as tasks.
        
        Args:
            issues: List of all issues
            
        Returns:
            Filtered list of task issues
        """
        task_issues = []
        
        # Exclusion criteria
        excluded_labels = self.config.get('excluded_labels', ['DSR', 'documentation'])
        excluded_prefixes = self.config.get('excluded_title_prefixes', ['.github/workflows/'])
        
        for issue in issues:
            # Skip if has excluded labels
            issue_labels = [label.get('name', '') for label in issue.get('labels', {}).get('nodes', [])]
            if any(label in excluded_labels for label in issue_labels):
                continue
            
            # Skip if title starts with excluded prefix
            if any(issue.get('title', '').startswith(prefix) for prefix in excluded_prefixes):
                continue
            
            # Skip if created by automation (would need additional query for author info)
            # For now, simplified filtering
            
            task_issues.append(issue)
        
        return task_issues
    
    def _create_task_items(self, issues: List[Dict[str, Any]], 
                          board_items: List) -> List[TaskItem]:
        """Create TaskItem objects from issues and board items.
        
        Args:
            issues: List of repository issues
            board_items: List of board items
            
        Returns:
            List of TaskItem objects
        """
        task_items = []
        
        # Create mapping of issue number to board item
        board_item_map = {}
        for item in board_items:
            content_number = item.get('content', {}).get('number')
            if content_number:
                board_item_map[content_number] = item
        
        for issue in issues:
            # Extract status from labels
            status = self._extract_status_from_labels(issue)
            
            # Extract priority from labels
            priority = self._extract_priority_from_labels(issue)
            
            # Extract category (optional)
            category = self._extract_category_from_labels(issue)
            
            # Get assignee
            assignees = issue.get('assignees', {}).get('nodes', [])
            assignee = assignees[0].get('login') if assignees else None
            
            # Get corresponding board item
            board_item = board_item_map.get(issue.get('number'))
            
            task_item = TaskItem(
                issue=issue,
                status=status,
                priority=priority,
                category=category,
                assignee=assignee,
                board_item=board_item
            )
            
            task_items.append(task_item)
        
        return task_items
    
    def _create_task_items_optimized(self, issues: List[Dict[str, Any]], 
                                    board_items: List, board: Dict[str, Any]) -> List[TaskItem]:
        """Create TaskItem objects with optimization.
        
        Args:
            issues: List of repository issue data dictionaries
            board_items: List of board item objects
            board: Board data for operations
            
        Returns:
            List of TaskItem objects
        """
        task_items = []
        
        # Create mapping of issue number to board item
        board_item_map = {}
        for item in board_items:
            content_number = item.get('content', {}).get('number') if isinstance(item, dict) else None
            if content_number:
                board_item_map[content_number] = item
        
        for issue in issues:
            # Extract status from labels
            status = self._extract_status_from_labels(issue)
            
            # Extract priority from labels
            priority = self._extract_priority_from_labels(issue)
            
            # Extract category (optional)
            category = self._extract_category_from_labels(issue)
            
            # Get assignee
            assignees = issue.get('assignees', {}).get('nodes', [])
            assignee = assignees[0].get('login') if assignees else None
            
            # Get corresponding board item
            board_item = board_item_map.get(issue.get('number'))
            
            # Check for field value conflicts between labels and board
            if board_item and hasattr(board_item, 'field_values'):
                # Priority: Board field values over issue labels
                board_status = board_item.field_values.get(self.status_field)
                board_priority = board_item.field_values.get(self.priority_field)
                
                if board_status:
                    # Map board status back to enum
                    for label, enum_status in self.status_labels.items():
                        if enum_status.value == board_status:
                            status = enum_status
                            break
                
                if board_priority:
                    # Map board priority back to enum
                    for label, enum_priority in self.priority_labels.items():
                        if enum_priority.value == board_priority:
                            priority = enum_priority
                            break
            
            task_item = TaskItem(
                issue=issue,
                status=status,
                priority=priority,
                category=category,
                assignee=assignee,
                board_item=board_item
            )
            
            task_items.append(task_item)
        
        return task_items
    
    def _extract_status_from_labels(self, issue: Dict[str, Any]) -> TaskStatus:
        """Extract task status from issue labels.
        
        Args:
            issue: Issue data dictionary
            
        Returns:
            TaskStatus enum value
        """
        labels = issue.get('labels', {}).get('nodes', [])
        for label in labels:
            label_name = label.get('name', '')
            if label_name in self.status_labels:
                return self.status_labels[label_name]
        
        # Default status
        return TaskStatus.TODO
    
    def _extract_priority_from_labels(self, issue: Dict[str, Any]) -> TaskPriority:
        """Extract task priority from issue labels.
        
        Args:
            issue: Issue data dictionary
            
        Returns:
            TaskPriority enum value
        """
        labels = issue.get('labels', {}).get('nodes', [])
        for label in labels:
            label_name = label.get('name', '')
            if label_name in self.priority_labels:
                return self.priority_labels[label_name]
        
        # Default priority
        return TaskPriority.MEDIUM
    
    def _extract_category_from_labels(self, issue: Dict[str, Any]) -> Optional[str]:
        """Extract task category from issue labels.
        
        Args:
            issue: Issue data dictionary
            
        Returns:
            Category string or None
        """
        category_prefix = self.config.get('category_label_prefix', 'category:')
        
        labels = issue.get('labels', {}).get('nodes', [])
        for label in labels:
            label_name = label.get('name', '')
            if label_name.startswith(category_prefix):
                return label_name[len(category_prefix):]
        
        return None
    
    def _update_project_item(self, project: Dict[str, Any], task_item: TaskItem) -> bool:
        """Update existing project item.
        
        Args:
            project: Project data dictionary
            task_item: TaskItem to update
            
        Returns:
            True if updated
        """
        try:
            if not task_item.board_item:
                self.logger.warning("No board item to update")
                return False
                
            board_item_id = task_item.board_item.get('id') if isinstance(task_item.board_item, dict) else task_item.board_item
            if not board_item_id:
                self.logger.error("Board item has no ID")
                return False
            
            success_count = 0
            
            # Update status field
            if hasattr(task_item, 'status'):
                status_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.status_field)
                if status_field_id:
                    result = self.api.update_item_field(
                        project['id'], board_item_id, status_field_id, task_item.status.value
                    )
                    if result:
                        success_count += 1
                        self.logger.debug(f"Updated status to {task_item.status.value}")
            
            # Update priority field
            if hasattr(task_item, 'priority'):
                priority_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.priority_field)
                if priority_field_id:
                    result = self.api.update_item_field(
                        project['id'], board_item_id, priority_field_id, task_item.priority.value
                    )
                    if result:
                        success_count += 1
                        self.logger.debug(f"Updated priority to {task_item.priority.value}")
            
            # Update category field if present
            if task_item.category:
                category_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.category_field)
                if category_field_id:
                    result = self.api.update_item_field(
                        project['id'], board_item_id, category_field_id, task_item.category
                    )
                    if result:
                        success_count += 1
                        self.logger.debug(f"Updated category to {task_item.category}")
            
            self.logger.info(f"Updated {success_count} fields for project item")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update project item: {e}")
            return False
    
    def _create_project_item(self, project: Dict[str, Any], task_item: TaskItem) -> bool:
        """Create new project item.
        
        Args:
            project: Project data dictionary
            task_item: TaskItem to create
            
        Returns:
            True if created
        """
        try:
            # Add issue to project board
            issue_id = task_item.issue.get('id')
            if not issue_id:
                self.logger.error(f"Issue #{task_item.issue.get('number', 'unknown')} has no ID")
                return False
                
            result = self.api.add_item_to_board(project['id'], issue_id)
            if not result or 'addProjectV2ItemById' not in result:
                self.logger.error(f"Failed to add issue #{task_item.issue.get('number', 'unknown')} to board")
                return False
            
            # Get the created item
            created_item = result['addProjectV2ItemById']['item']
            item_id = created_item.get('id')
            
            if not item_id:
                self.logger.error("Created item has no ID")
                return False
                
            self.logger.info(f"Created project item for issue #{task_item.issue.get('number', 'unknown')}")
            
            # Update fields on the newly created item
            success_count = 0
            
            # Update status field
            status_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.status_field)
            if status_field_id:
                result = self.api.update_item_field(
                    project['id'], item_id, status_field_id, task_item.status.value
                )
                if result:
                    success_count += 1
            
            # Update priority field
            priority_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.priority_field)
            if priority_field_id:
                result = self.api.update_item_field(
                    project['id'], item_id, priority_field_id, task_item.priority.value
                )
                if result:
                    success_count += 1
            
            # Update category field if present
            if task_item.category:
                category_field_id = self.api.get_field_id_by_name(project.get('owner', ''), self.board_number, self.category_field)
                if category_field_id:
                    result = self.api.update_item_field(
                        project['id'], item_id, category_field_id, task_item.category
                    )
                    if result:
                        success_count += 1
            
            self.logger.info(f"Updated {success_count} fields on new project item")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create project item: {e}")
            return False
    
    def _update_issue_labels(self, repo_owner: str, repo_name: str, issue: Dict[str, Any], new_status: TaskStatus):
        """Update issue labels to reflect new status.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            issue: Issue data dictionary
            new_status: New task status
        """
        try:
            issue_id = issue.get('id')
            if not issue_id:
                self.logger.error("Issue has no ID for label update")
                return
            
            labels = issue.get('labels', {}).get('nodes', [])
            current_label_names = [label.get('name', '') for label in labels]
            
            # Find old status labels to remove
            old_status_label_ids = []
            for label_name in current_label_names:
                if label_name in self.status_labels:
                    label_id = self.api.get_label_id_by_name(repo_owner, repo_name, label_name)
                    if label_id:
                        old_status_label_ids.append(label_id)
            
            # Remove old status labels if any
            if old_status_label_ids:
                self.api.remove_labels_from_issue(issue_id, old_status_label_ids)
                self.logger.debug(f"Removed old status labels from issue #{issue.get('number')}")
            
            # Find new status label to add
            new_status_label = None
            for label_name, status in self.status_labels.items():
                if status == new_status:
                    new_status_label = label_name
                    break
            
            if new_status_label:
                new_label_id = self.api.get_label_id_by_name(repo_owner, repo_name, new_status_label)
                if new_label_id:
                    self.api.add_labels_to_issue(issue_id, [new_label_id])
                    self.logger.info(f"Updated issue #{issue.get('number')} label to: {new_status_label}")
                else:
                    self.logger.warning(f"Status label '{new_status_label}' not found in repository")
            else:
                self.logger.warning(f"No label mapping found for status: {new_status}")
                
        except Exception as e:
            self.logger.error(f"Failed to update issue labels: {e}")
    
    def _update_project_metrics(self, project: Dict[str, Any], task_items: List[TaskItem]):
        """Update project-level metrics and summaries.
        
        Args:
            project: Project data dictionary
            task_items: List of task items
        """
        # This would update project description or README with current metrics
        # Implementation depends on specific requirements
        total_tasks = len(task_items)
        completed_tasks = sum(1 for item in task_items if item.status == TaskStatus.DONE)
        
        self.logger.info(f"Project metrics: {completed_tasks}/{total_tasks} tasks completed")

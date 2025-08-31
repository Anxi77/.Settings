"""Daily Status Report (DSR) generator and manager."""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .api_client import APIClient
from .commit_parser import CommitParser, CommitData


@dataclass
class TodoItem:
    """Todo item structure."""
    category: str
    task: str
    completed: bool = False
    issue_ref: Optional[str] = None


@dataclass
class BranchSummary:
    """Branch activity summary."""
    name: str
    commits: List[CommitData]
    files_changed: int
    insertions: int
    deletions: int


class DailyReporter:
    """Generate and manage Daily Status Report issues."""
    
    def __init__(self, api_client: APIClient, config: Dict[str, Any]):
        """Initialize daily reporter.
        
        Args:
            api_client: API client
            config: Configuration dictionary
        """
        self.api = api_client
        self.config = config
        self.parser = CommitParser()
        self.logger = logging.getLogger(__name__)
        
        # Configuration with defaults
        self.timezone = config.get('timezone', 'UTC')
        self.issue_prefix = config.get('issue_prefix', '📅')
        self.dsr_label = config.get('dsr_label', 'DSR')
        self.branch_label_prefix = config.get('branch_label_prefix', 'branch:')
        
    def generate_dsr(self, repo_owner: str, repo_name: str, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate or update Daily Status Report for specified date.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            target_date: Target date (defaults to today)
            
        Returns:
            Created or updated issue data dictionary
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        
        date_str = target_date.strftime('%Y-%m-%d')
        clean_repo_name = repo_name.lstrip('.')
        
        issue_title = f"{self.issue_prefix} Development Status Report ({date_str})"
        if repo_name:
            issue_title += f" - {repo_name}"
        
        self.logger.info(f"Generating DSR: {issue_title}")
        
        # Get repository information
        repo_info = self.api.get_repository(repo_owner, repo_name)
        if not repo_info:
            self.logger.error(f"Repository {repo_owner}/{repo_name} not found")
            return None
        
        repo_id = repo_info['id']
        
        # Get today's commits
        branch_summaries = self._get_branch_summaries(repo_owner, repo_name, target_date)
        
        if not branch_summaries:
            self.logger.info("No commits found for today")
            return None
        
        # Find existing DSR issue
        existing_issue = self._find_dsr_issue(repo_owner, repo_name, issue_title)
        
        # Get previous todos if creating new issue
        previous_todos = []
        if not existing_issue:
            previous_todos = self._get_previous_dsr_todos(repo_owner, repo_name, date_str)
        else:
            previous_todos = self._parse_existing_todos(existing_issue.get('body', ''))
        
        # Process new todos from commits
        all_todos = self._process_commit_todos(branch_summaries, previous_todos)
        
        # Generate report content
        report_body = self._generate_report_body(
            issue_title, branch_summaries, all_todos
        )
        
        # Create or update issue
        if existing_issue:
            updated_issue = self.api.update_issue(existing_issue['id'], body=report_body)
            self.logger.info(f"Updated DSR issue #{existing_issue.get('number', 'unknown')}")
            return updated_issue or existing_issue
        else:
            labels = [self.dsr_label]
            # Add branch label if single branch
            if len(branch_summaries) == 1:
                labels.append(f"{self.branch_label_prefix}{branch_summaries[0].name}")
            
            new_issue = self.api.create_issue(
                repo_id, issue_title, report_body, labels
            )
            self.logger.info(f"Created DSR issue #{new_issue.get('number', 'unknown') if new_issue else 'failed'}")
            return new_issue
    
    def _get_branch_summaries(self, repo_owner: str, repo_name: str, target_date: datetime) -> List[BranchSummary]:
        """Get branch activity summaries for target date.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            target_date: Target date
            
        Returns:
            List of BranchSummary objects
        """
        # Get commits from target date
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        commits = self.api.get_commits(
            repo_owner,
            repo_name,
            since=start_of_day.isoformat(),
            until=end_of_day.isoformat()
        )
        
        # Group commits by branch
        branch_commits = {}
        for commit in commits:
            # Parse commit message from GraphQL response
            try:
                commit_message = commit.get('message', '')
                commit_data = self.parser.parse(commit_message)
                
                # Skip certain commit types if configured
                excluded_types = self.config.get('excluded_commit_types', [])
                if commit_data.type in excluded_types:
                    continue
                
                # Group by branch (simplified - in real scenario would need API calls)
                branch_name = 'main'  # Default branch
                
                if branch_name not in branch_commits:
                    branch_commits[branch_name] = []
                
                branch_commits[branch_name].append(commit_data)
                
            except ValueError as e:
                commit_oid = commit.get('oid', 'unknown')
                self.logger.warning(f"Failed to parse commit {commit_oid[:7]}: {e}")
                continue
        
        # Create branch summaries
        summaries = []
        for branch_name, commits in branch_commits.items():
            # Calculate stats (simplified)
            total_files = sum(len(commit.body) for commit in commits)  # Approximation
            
            summary = BranchSummary(
                name=branch_name,
                commits=commits,
                files_changed=total_files,
                insertions=0,  # Would need detailed commit stats
                deletions=0
            )
            summaries.append(summary)
        
        return summaries
    
    def _find_dsr_issue(self, repo_owner: str, repo_name: str, title: str) -> Optional[Dict[str, Any]]:
        """Find existing DSR issue by title.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            title: Issue title to search for
            
        Returns:
            Issue data dictionary if found, None otherwise
        """
        issues = self.api.get_issues(repo_owner, repo_name, state='OPEN', labels=[self.dsr_label])
        
        for issue in issues:
            if issue.get('title') == title:
                return issue
        
        return None
    
    def _get_previous_dsr_todos(self, repo_owner: str, repo_name: str, current_date: str) -> List[TodoItem]:
        """Get uncompleted todos from previous DSR issues.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            current_date: Current date string (YYYY-MM-DD)
            
        Returns:
            List of uncompleted TodoItem objects
        """
        issues = self.api.get_issues(repo_owner, repo_name, state='OPEN', labels=[self.dsr_label])
        
        # Sort by creation date (newest first)
        sorted_issues = sorted(
            [i for i in issues if 'Development Status Report' in i.get('title', '')],
            key=lambda x: x.get('createdAt', ''),
            reverse=True
        )
        
        todos = []
        for issue in sorted_issues:
            if current_date in issue.get('title', ''):
                continue  # Skip current date issue
            
            # Parse todos from previous issue
            previous_todos = self._parse_existing_todos(issue.get('body', ''))
            
            # Only get uncompleted items
            for todo in previous_todos:
                if not todo.completed:
                    todos.append(todo)
            
            # Close previous issue
            self.api.update_issue(issue['id'], state='CLOSED')
            self.logger.info(f"Closed previous DSR issue #{issue.get('number', 'unknown')}")
            
            break  # Only process most recent previous issue
        
        return todos
    
    def _parse_existing_todos(self, issue_body: str) -> List[TodoItem]:
        """Parse existing todos from issue body.
        
        Args:
            issue_body: Issue body content
            
        Returns:
            List of TodoItem objects
        """
        todos = []
        current_category = 'General'
        in_todo_section = False
        
        if not issue_body:
            return todos
        
        for line in issue_body.split('\n'):
            line = line.strip()
            
            # Detect todo section start
            if '## 📝 Todo' in line or '[Todo]' in line:
                in_todo_section = True
                continue
            
            # Detect section end
            if in_todo_section and line.startswith('##') and '📝 Todo' not in line:
                in_todo_section = False
                continue
            
            if not in_todo_section:
                continue
            
            # Parse category headers
            if line.startswith('@'):
                current_category = line[1:].strip()
                continue
            
            # Parse todo items
            if line.startswith('- ['):
                completed = line[3] == 'x'
                task = line[6:].strip()
                
                # Extract issue reference if present
                issue_ref = None
                if task.startswith('#'):
                    issue_ref = task.split()[0]
                
                todos.append(TodoItem(
                    category=current_category,
                    task=task,
                    completed=completed,
                    issue_ref=issue_ref
                ))
        
        return todos
    
    def _process_commit_todos(self, branch_summaries: List[BranchSummary], 
                            existing_todos: List[TodoItem]) -> List[TodoItem]:
        """Process todos from commits and merge with existing.
        
        Args:
            branch_summaries: List of branch summaries
            existing_todos: Existing todo items
            
        Returns:
            Merged list of TodoItem objects
        """
        # Start with existing todos
        all_todos = existing_todos.copy()
        
        # Add new todos from commits
        for summary in branch_summaries:
            for commit in summary.commits:
                for category, task in commit.todos:
                    # Check if todo already exists
                    exists = any(
                        todo.category == category and todo.task == task
                        for todo in all_todos
                    )
                    
                    if not exists:
                        all_todos.append(TodoItem(
                            category=category,
                            task=task,
                            completed=False
                        ))
        
        # Sort todos by category
        all_todos.sort(key=lambda x: (x.category, x.task))
        
        return all_todos
    
    def _generate_report_body(self, title: str, branch_summaries: List[BranchSummary], 
                            todos: List[TodoItem]) -> str:
        """Generate DSR issue body content.
        
        Args:
            title: Issue title
            branch_summaries: Branch activity summaries
            todos: Todo items
            
        Returns:
            Formatted issue body
        """
        lines = [f"# {title}", "", "<div align=\"center\">", "", "## 📊 Branch Summary", "", "</div>", ""]
        
        # Add branch sections
        for summary in branch_summaries:
            lines.extend(self._format_branch_section(summary))
            lines.append("")
        
        # Add todo section
        lines.extend(["<div align=\"center\">", "", "## 📝 Todo", "", "</div>", ""])
        lines.extend(self._format_todo_section(todos))
        
        return '\n'.join(lines)
    
    def _format_branch_section(self, summary: BranchSummary) -> List[str]:
        """Format branch summary section.
        
        Args:
            summary: BranchSummary object
            
        Returns:
            List of formatted lines
        """
        lines = [f"### 🌿 {summary.name}", ""]
        
        if summary.commits:
            lines.append("**Commits:**")
            for commit in summary.commits:
                commit_line = f"- [{commit.type}] {commit.title}"
                if commit.scope:
                    commit_line = f"- [{commit.type}({commit.scope})] {commit.title}"
                lines.append(commit_line)
                
                # Add body if present
                if commit.body:
                    for body_line in commit.body:
                        lines.append(f"  - {body_line}")
            
            lines.append("")
        
        # Add stats
        lines.append(f"**Changes:** {summary.files_changed} files")
        
        return lines
    
    def _format_todo_section(self, todos: List[TodoItem]) -> List[str]:
        """Format todo section.
        
        Args:
            todos: List of TodoItem objects
            
        Returns:
            List of formatted lines
        """
        if not todos:
            return ["No todos at this time."]
        
        lines = []
        current_category = None
        
        for todo in todos:
            if todo.category != current_category:
                if current_category is not None:
                    lines.append("")
                lines.append(f"### @{todo.category}")
                current_category = todo.category
            
            checkbox = "[x]" if todo.completed else "[ ]"
            lines.append(f"- {checkbox} {todo.task}")
        
        return lines
    
    def close_previous_dsr_issues(self, repo_owner: str, repo_name: str, keep_days: int = 7):
        """Close old DSR issues.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            keep_days: Number of days to keep issues open
        """
        cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - keep_days)
        
        issues = self.api.get_issues(repo_owner, repo_name, state='OPEN', labels=[self.dsr_label])
        
        for issue in issues:
            created_at = issue.get('createdAt', '')
            if created_at and created_at < cutoff_date.isoformat():
                issue_id = issue.get('id')
                if issue_id:
                    self.api.update_issue(issue_id, state='CLOSED')
                    self.logger.info(f"Closed old DSR issue #{issue.get('number', 'unknown')}")

"""Daily Status Report (DSR) generator and manager."""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from infrastructure.api_client import APIClient
from domains.commits.parser import CommitParser, CommitData
from domains.issues.manager import TodoIssueManager, TodoIssueInfo
from domains.projects.sync import BoardSync

@dataclass
class TodoItem:
    """Todo item structure."""
    category: str
    task: str
    completed: bool = False
    issue_ref: Optional[str] = None
    issue_number: Optional[int] = None
    issue_url: Optional[str] = None

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

        # Initialize TODO issue manager
        self.todo_manager = TodoIssueManager(api_client, config.get('todo_issues', {}))

        # Initialize project board sync (will be set per repository)
        self.board_sync = None

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

        # Initialize board sync for this repository
        if not self.board_sync:
            self.board_sync = BoardSync(self.api, self.config.get('project_sync', {}), repo_owner, repo_name)
            self.board_sync.initialize_project()

        # Process new todos from commits (create individual issues)
        all_todos = self._process_commit_todos(
            branch_summaries,
            previous_todos,
            repo_owner,
            repo_name,
            dsr_issue_number=None  # Will be set after DSR creation for subsequent runs
        )

        # Generate report content
        report_body = self._generate_report_body(
            issue_title, branch_summaries, all_todos, repo_owner, repo_name
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

            # Ensure labels exist before creating issue
            label_ids = self._ensure_dsr_labels_exist(repo_owner, repo_name, labels)

            new_issue = self.api.create_issue(
                repo_id, issue_title, report_body, label_ids
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

                # Extract additional commit metadata
                commit_data.author = commit.get('author', {}).get('name', 'Unknown')
                commit_data.hash = commit.get('oid', 'unknown')
                
                # Format timestamp for display
                commit_timestamp = commit.get('authoredDate') or commit.get('committedDate')
                if commit_timestamp:
                    try:
                        # Parse ISO timestamp and convert to time string
                        dt = datetime.fromisoformat(commit_timestamp.replace('Z', '+00:00'))
                        commit_data.timestamp = commit_timestamp
                        commit_data.time = dt.strftime('%H:%M:%S')
                    except Exception:
                        commit_data.time = 'Unknown'
                else:
                    commit_data.time = 'Unknown'

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
                issue_number = None

                # Look for issue reference in format "(#123)" at the end
                import re
                issue_match = re.search(r'\(#(\d+)\)\s*$', task)
                if issue_match:
                    issue_number = int(issue_match.group(1))
                    issue_ref = f"#{issue_number}"
                    # Remove issue reference from task text
                    task = re.sub(r'\s*\(#\d+\)\s*$', '', task).strip()
                elif task.startswith('#'):
                    # Legacy format: task starting with #
                    issue_ref = task.split()[0]

                todos.append(TodoItem(
                    category=current_category,
                    task=task,
                    completed=completed,
                    issue_ref=issue_ref,
                    issue_number=issue_number
                ))

        return todos

    def _process_commit_todos(self, branch_summaries: List[BranchSummary],
                            existing_todos: List[TodoItem],
                            repo_owner: str, repo_name: str,
                            dsr_issue_number: Optional[int] = None) -> List[TodoItem]:
        """Process todos from commits and merge with existing.

        Args:
            branch_summaries: List of branch summaries
            existing_todos: Existing todo items
            repo_owner: Repository owner
            repo_name: Repository name
            dsr_issue_number: DSR issue number for linking

        Returns:
            Merged list of TodoItem objects with issue links
        """
        # Start with existing todos
        all_todos = existing_todos.copy()

        # Collect new todos and their commit context
        new_todos = []
        commit_authors = {}

        for summary in branch_summaries:
            for commit in summary.commits:
                for category, task in commit.todos:
                    # Check if todo already exists
                    exists = any(
                        todo.category == category and todo.task == task
                        for todo in all_todos
                    )

                    if not exists:
                        new_todos.append((category, task))
                        # Store commit author for issue assignment
                        commit_authors[(category, task)] = getattr(commit, 'author', None)

        if new_todos:
            self.logger.info(f"Creating individual issues for {len(new_todos)} new TODO items")

            # Create individual issues for new todos
            for category, task in new_todos:
                commit_author = commit_authors.get((category, task))

                # Get the commit data for context
                commit_data = None
                for summary in branch_summaries:
                    for commit in summary.commits:
                        if (category, task) in commit.todos:
                            commit_data = commit
                            break
                    if commit_data:
                        break

                try:
                    # Create individual issue
                    created_issues = self.todo_manager.create_issues_from_todos(
                        repo_owner=repo_owner,
                        repo_name=repo_name,
                        todos=[(category, task)],
                        commit_data=commit_data,
                        dsr_issue_number=dsr_issue_number,
                        commit_author=commit_author
                    )

                    if created_issues:
                        issue_info = created_issues[0]  # Should be only one

                        # Create TodoItem with issue information
                        todo_item = TodoItem(
                            category=category,
                            task=task,
                            completed=False,
                            issue_number=issue_info.issue_number,
                            issue_url=issue_info.issue_url,
                            issue_ref=f"#{issue_info.issue_number}"
                        )
                        all_todos.append(todo_item)

                        self.logger.info(f"Created issue #{issue_info.issue_number} for TODO: {task[:50]}...")
                    else:
                        # Fallback: create TodoItem without issue
                        self.logger.warning(f"Failed to create issue for TODO: {task[:50]}...")
                        all_todos.append(TodoItem(
                            category=category,
                            task=task,
                            completed=False
                        ))

                except Exception as e:
                    self.logger.error(f"Failed to create TODO issue for '{task}': {e}")
                    # Fallback: create TodoItem without issue
                    all_todos.append(TodoItem(
                        category=category,
                        task=task,
                        completed=False
                    ))

        # Sort todos by category
        all_todos.sort(key=lambda x: (x.category, x.task))

        return all_todos

    def _generate_report_body(self, title: str, branch_summaries: List[BranchSummary],
                            todos: List[TodoItem], repo_owner: str, repo_name: str) -> str:
        """Generate DSR issue body content with modern collapsible author-grouped format.

        Args:
            title: Issue title
            branch_summaries: Branch activity summaries
            todos: Todo items
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Formatted issue body
        """
        lines = [f"# {title}", "", "<div align=\"center\">", "", "## 📊 Branch Summary", "", "</div>", ""]

        # Group commits by author instead of branch
        author_commits = self._group_commits_by_author(branch_summaries)
        
        # Add author sections with modern formatting
        for author, commits in author_commits.items():
            lines.extend(self._format_author_section(author, commits))
            lines.append("")

        # Add closing div for branch summary
        lines.extend(["<div align=\"center\">", ""])
        
        # Add todo section
        lines.extend(["## 📝 Todo", "", "</div>", ""])
        lines.extend(self._format_todo_section(todos, repo_owner, repo_name))

        return '\n'.join(lines)

    def _group_commits_by_author(self, branch_summaries: List[BranchSummary]) -> Dict[str, List[CommitData]]:
        """Group all commits by author across branches.

        Args:
            branch_summaries: List of BranchSummary objects

        Returns:
            Dictionary mapping author names to their commits (sorted by time)
        """
        author_commits = {}
        
        for summary in branch_summaries:
            for commit in summary.commits:
                # Extract author name from commit (assuming it's available in title or we need to fetch it)
                author = getattr(commit, 'author', 'Unknown')
                if not author or author == 'Unknown':
                    # Fallback: extract from commit data or use a default
                    author = 'Unknown'
                
                if author not in author_commits:
                    author_commits[author] = []
                
                author_commits[author].append(commit)
        
        # Sort commits by timestamp for each author (newest first)
        for author in author_commits:
            author_commits[author].sort(key=lambda x: x.timestamp or '', reverse=True)
        
        return author_commits

    def _format_author_section(self, author: str, commits: List[CommitData]) -> List[str]:
        """Format author section with modern collapsible format based on Docs/format.md.

        Args:
            author: Author name
            commits: List of CommitData objects for this author

        Returns:
            List of formatted lines
        """
        commit_count = len(commits)
        lines = [
            f"<details>",
            f"<summary><h3 style=\"display: inline;\">✨ Author_{author}</h3></summary>",
            ""
        ]

        for commit in commits:
            # Extract time from commit
            time_str = commit.time or 'Unknown'
            
            # Get commit type description
            type_desc = self._get_commit_type_description(commit.type)
            
            # Get short commit hash
            commit_hash = commit.hash[:7] if commit.hash and commit.hash != 'unknown' else 'unknown'
            
            lines.extend([
                "> <details>",
                f"> <summary>💫 {time_str} - {commit.title}</summary>",
                ">",
                f"> Type: {commit.type} ({type_desc})",
                f"> Commit: {commit_hash}",
                f"> Author: {author}",
                ">"
            ])
            
            # Add body content if present
            if commit.body:
                for body_line in commit.body:
                    if body_line.strip():
                        lines.append(f"> • {body_line.strip()}")
                lines.append(">")
            else:
                lines.extend(["> No additional details provided.", ">"])
            
            lines.extend(["> </details>", ""])

        lines.append("</details>")
        return lines

    def _get_commit_type_description(self, commit_type: str) -> str:
        """Get human-readable description for commit type."""
        type_descriptions = {
            'feat': 'New Feature',
            'fix': 'Bug Fix',
            'docs': 'Documentation',
            'style': 'Code Style',
            'refactor': 'Code Refactoring',
            'test': 'Testing',
            'chore': 'Maintenance',
            'design': 'Design Changes',
            'comment': 'Comments',
            'rename': 'Rename/Move',
            'remove': 'File Removal',
            '!BREAKING CHANGE': 'Breaking Change',
            '!HOTFIX': 'Hotfix'
        }
        return type_descriptions.get(commit_type, commit_type.title())

    def _format_branch_section(self, summary: BranchSummary) -> List[str]:
        """Format branch summary section with collapsible commits.

        Args:
            summary: BranchSummary object

        Returns:
            List of formatted lines
        """
        commit_count = len(summary.commits) if summary.commits else 0
        lines = [
            f"<details>",
            f"<summary><strong>🌿 {summary.name}</strong> ({commit_count} commits, {summary.files_changed} files changed)</summary>",
            ""
        ]

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
                        # Check if line already starts with a dash/bullet
                        if body_line.strip().startswith('-'):
                            lines.append(f"  {body_line}")
                        else:
                            lines.append(f"  - {body_line}")

            lines.append("")
        else:
            lines.append("No commits in this branch.")
            lines.append("")

        lines.extend(["", "</details>", ""])

        return lines

    def _format_todo_section(self, todos: List[TodoItem], repo_owner: str, repo_name: str) -> List[str]:
        """Format todo section with collapsible categories.

        Args:
            todos: List of TodoItem objects
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            List of formatted lines
        """
        if not todos:
            return ["No todos at this time."]

        # Group todos by category
        category_todos = {}
        for todo in todos:
            if todo.category not in category_todos:
                category_todos[todo.category] = []
            category_todos[todo.category].append(todo)

        lines = []

        for category, category_items in category_todos.items():
            item_count = len(category_items)
            completed_count = sum(1 for item in category_items if item.completed)

            lines.extend([
                f"<details>",
                f"<summary><strong>@{category}</strong> ({completed_count}/{item_count} completed)</summary>",
                ""
            ])

            for todo in category_items:
                checkbox = "[x]" if todo.completed else "[ ]"

                # Add issue link if available
                task_line = f"- {checkbox} {todo.task}"
                if todo.issue_number:
                    task_line += f" ([#{todo.issue_number}](https://github.com/{repo_owner}/{repo_name}/issues/{todo.issue_number}))"
                elif todo.issue_ref:
                    task_line += f" ({todo.issue_ref})"

                lines.append(task_line)

            lines.extend(["", "</details>", ""])

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

    def _ensure_dsr_labels_exist(self, repo_owner: str, repo_name: str, label_names: List[str]) -> List[str]:
        """Ensure DSR-related labels exist in the repository, creating them if necessary.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            label_names: List of label names to ensure exist

        Returns:
            List of label IDs for existing/created labels
        """
        label_ids = []

        # Define default colors and descriptions for DSR labels
        label_defaults = {
            'DSR': {'color': 'D73A49', 'description': 'Daily Status Report'},
        }

        for label_name in label_names:
            # Get or create the label
            if label_name.startswith('branch:'):
                # Branch labels
                defaults = {
                    'color': '0052CC',
                    'description': f'Branch: {label_name.split(":")[1]}'
                }
            else:
                defaults = label_defaults.get(label_name, {'color': '0969da', 'description': f'DSR label: {label_name}'})

            label_id = self.api.get_or_create_label(
                repo_owner,
                repo_name,
                label_name,
                defaults['color'],
                defaults['description']
            )

            if label_id:
                label_ids.append(label_id)
            else:
                self.logger.warning(f"Failed to get or create DSR label: {label_name}")

        return label_ids


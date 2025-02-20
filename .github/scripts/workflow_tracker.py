import os
import re
from datetime import datetime
import pytz
from github import Github
import logging
from typing import Dict, List, Tuple, Optional
from github.Repository import Repository
from github.Issue import Issue

class WorkflowLogger:
    def __init__(self):
        self.logger = logging.getLogger('workflow_tracker')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('=== %(message)s ===')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def section(self, title: str, message: str = '') -> None:
        """섹션 헤더와 메시지를 출력합니다."""
        self.logger.info(f"{title}")
        if message:
            print(f"{message}")
    
    def commit(self, action: str, sha: str, message: str, extra: str = '') -> None:
        """커밋 관련 로그를 출력합니다."""
        print(f"{action}: [{sha[:7]}] {message}{' - ' + extra if extra else ''}")
    
    def todo(self, status: str, text: str) -> None:
        """TODO 항목 관련 로그를 출력합니다."""
        print(f"{status}: {text}")
    
    def debug(self, message: str) -> None:
        """디버그 메시지를 출력합니다."""
        print(f"DEBUG: {message}")

logger = WorkflowLogger()

COMMIT_TYPES = {
    'feat': {'emoji': '✨', 'label': 'feature', 'description': 'New Feature'},
    'fix': {'emoji': '🐛', 'label': 'bug', 'description': 'Bug Fix'},
    'refactor': {'emoji': '♻️', 'label': 'refactor', 'description': 'Code Refactoring'},
    'docs': {'emoji': '📝', 'label': 'documentation', 'description': 'Documentation Update'},
    'test': {'emoji': '✅', 'label': 'test', 'description': 'Test Update'},
    'chore': {'emoji': '🔧', 'label': 'chore', 'description': 'Build/Config Update'},
    'style': {'emoji': '💄', 'label': 'style', 'description': 'Code Style Update'},
    'perf': {'emoji': '⚡️', 'label': 'performance', 'description': 'Performance Improvement'},
}

def is_merge_commit_message(message):
    """Check if the message is a merge commit message"""
    return message.startswith('Merge')

class CommitMessage:
    def __init__(self, type_: str, title: str, body: str = '', todo: str = '', footer: str = ''):
        self.type = type_
        self.title = title
        self.body = body
        self.todo = todo
        self.footer = footer
        self.type_info = COMMIT_TYPES.get(type_.lower(), {'emoji': '🔍', 'label': 'other', 'description': 'Other'})

    @classmethod
    def parse(cls, message: str) -> Optional['CommitMessage']:
        """Parse commit message into structured format"""
        sections = {'title': '', 'body': '', 'todo': '', 'footer': ''}
        current_section = 'title'
        lines = []

        for line in message.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                if lines:
                    sections[current_section] = '\n'.join(lines)
                current_section = line[1:-1].lower()
                lines = []
            else:
                lines.append(line)

        if lines:
            sections[current_section] = '\n'.join(lines)

        # Parse type and title
        title_match = re.match(r'\[(.*?)\]\s*(.*)', sections.get('title', ''))
        if not title_match:
            return None

        return cls(
            type_=title_match.group(1),
            title=title_match.group(2),
            body=sections.get('body', ''),
            todo=sections.get('todo', ''),
            footer=sections.get('footer', '')
        )

def parse_commit_message(message: str) -> Optional[Dict]:
    """Parse commit message using CommitMessage class"""
    commit = CommitMessage.parse(message)
    if not commit:
        return None

    return {
        'type': commit.type,
        'type_info': commit.type_info,
        'title': commit.title,
        'body': commit.body,
        'todo': commit.todo,
        'footer': commit.footer
    }

class CategoryManager:
    def __init__(self):
        self._categories = {}
        self._current = 'General'
        self.add_category('General')  # 기본 카테고리 초기화
    
    def add_category(self, category):
        """카테고리 추가 또는 기존 카테고리 반환"""
        if not category:
            return self._categories['General']
            
        category = category.strip()
        if category not in self._categories:
            self._categories[category] = []
        return category
    
    def add_todo(self, category, todo_item):
        """카테고리에 TODO 항목 추가"""
        category = self.add_category(category)
        if todo_item not in self._categories[category]:
            self._categories[category].append(todo_item)
    
    def get_todos(self, category=None):
        """특정 카테고리 또는 전체 TODO 항목 반환"""
        if category:
            return self._categories.get(category, [])
        return self._categories
    
    def set_current(self, category):
        """현재 카테고리 설정"""
        self._current = self.add_category(category)
    
    @property
    def current(self):
        """현재 카테고리 반환"""
        return self._current

    @property
    def categories(self):
        """모든 카테고리 반환"""
        return list(self._categories.keys())

def parse_categorized_todos(text):
    """Parse todos with categories"""
    if not text:
        logger.debug("DEBUG: No todo text provided")
        return {}
    
    logger.section("Parsing TODOs")
    logger.debug(f"Raw todo text:\n{text}")
    
    categories = {}
    current_category = 'General'
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        logger.debug(f"Processing line: {line}")
        
        if line.startswith('@'):
            current_category = line[1:].strip()
            if current_category not in categories:
                categories[current_category] = []
            logger.debug(f"Found category: {current_category}")
            continue
            
        if line.startswith(('-', '*')):
            if current_category not in categories:
                categories[current_category] = []
            
            item = line[1:].strip()
            categories[current_category].append(item)
            logger.debug(f"Added todo item to {current_category}: {item}")
    
    return categories

def create_commit_section(commit_data, branch, commit_sha, author, time_string, repo):
    """Create commit section with details tag"""
    logger.section("Creating Commit Section")
    logger.debug(f"Commit SHA: {commit_sha[:7]}")
    logger.debug(f"Author: {author}")
    logger.debug(f"Time: {time_string}")
    
    # Handle None values in commit data
    body = commit_data.get('body', '').strip() if commit_data.get('body') else ''
    footer = commit_data.get('footer', '').strip() if commit_data.get('footer') else ''

    # Format body with bullet points
    body_lines = []
    if body:
        logger.debug("\nProcessing commit body:")
        for line in body.split('\n'):
            line = line.strip()
            if line:
                if line.startswith('-'):
                    line = line[1:].strip()
                body_lines.append(f"> • {line}")
                logger.debug(f"Added body line: {line}")
    quoted_body = '\n'.join(body_lines)
    
    # 현재 DSR 이슈 찾기
    current_date = datetime.now(pytz.timezone(os.environ.get('TIMEZONE', 'Asia/Seoul'))).strftime('%Y-%m-%d')
    dsr_issues = repo.get_issues(state='open', labels=[os.environ.get('ISSUE_LABEL', 'dsr')])
    current_dsr = None
    
    for issue in dsr_issues:
        if f"Daily Development Log ({current_date})" in issue.title:
            current_dsr = issue
            break
    
    # Extract issue numbers from entire commit message
    full_message = f"{commit_data['title']}\n{body}\n{footer}"
    issue_numbers = set(re.findall(r'#(\d+)', full_message))
    
    # Add current DSR issue number if found
    if current_dsr:
        issue_numbers.add(str(current_dsr.number))
    
    # Add comments to referenced issues and prepare related issues section
    related_issues = []
    
    # Process referenced issues
    if issue_numbers:
        logger.debug(f"\nProcessing referenced issues: {issue_numbers}")
        for issue_num in issue_numbers:
            try:
                issue = repo.get_issue(int(issue_num))
                # DSR 이슈인 경우 다른 메시지 사용
                if str(issue.number) == str(current_dsr.number):
                    issue.create_comment(f"커밋이 추가되었습니다: {commit_sha[:7]}\n\n```\n{commit_data['title']}\n```")
                else:
                    issue.create_comment(f"Referenced in commit {commit_sha[:7]}\n\nCommit message:\n```\n{commit_data['title']}\n```")
                related_issues.append(f"Related to #{issue_num}")
                logger.debug(f"Added reference to issue #{issue_num}")
            except Exception as e:
                logger.debug(f"Failed to add comment to issue #{issue_num}: {str(e)}")
    
    # Add related issues section
    if related_issues:
        quoted_body += "\n> \n> Related Issues:\n> " + "\n> ".join(related_issues)
    
    section = f'''> <details>
> <summary>💫 {time_string} - {commit_data['title'].strip()}</summary>
>
> Type: {commit_data['type']} ({commit_data['type_info']['description']})
> Commit: {commit_sha[:7]}
> Author: {author}
>
{quoted_body}
> </details>'''

    logger.debug("\nCreated commit section:")
    logger.debug(section)
    return section

def create_section(title, content):
    """Create collapsible section"""
    if not content:
        return ''
    
    return f'''<details>
<summary>{title}</summary>

{content}
</details>'''

def parse_existing_issue(body):
    """Parse existing issue body to extract branch commits and todos"""
    logger.section("Parsing Issue Body")
    # Initialize result structure
    result = {
        'branches': {},
        'todos': []
    }
    
    # Parse branch section
    logger.section("Parsing Branch Summary")
    print("\n=== Parsing Branch Summary ===")
    branch_pattern = r'<details>\s*<summary><h3 style="display: inline;">✨\s*(\w+)</h3></summary>(.*?)</details>'
    branch_blocks = re.finditer(branch_pattern, body, re.DOTALL)
    
    for block in branch_blocks:
        branch_name = block.group(1)
        branch_content = block.group(2).strip()
        print(f"\nFound branch: {branch_name}")
        
        commits = []
        lines = branch_content.split('\n')
        current_commit = []
        in_commit_block = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '> <details>' in line:
                if in_commit_block:
                    # save previous commit block
                    commits.append('\n'.join(current_commit))
                in_commit_block = True
                current_commit = [line]
                print(f"Starting new commit block: {line}")
            elif in_commit_block:
                current_commit.append(line)
                if '> </details>' in line:
                    commits.append('\n'.join(current_commit))
                    print(f"Completed commit block: {current_commit[0]}")
                    in_commit_block = False
                    current_commit = []
        
        # handle the last commit block
        if in_commit_block and current_commit:
            commits.append('\n'.join(current_commit))
        
        if commits:
            result['branches'][branch_name] = '\n\n'.join(commits)
            print(f"Parsed {len(commits)} commits from {branch_name}")
            print("Commits found:")
            for commit in commits:
                print(f"- {commit.split('\n')[0]}")
        else:
            print(f"No commits found in branch {branch_name}")
    
    print("\nParsed branches:", list(result['branches'].keys()))
    
    # Parse Todo section
    todo_pattern = r'## 📝 Todo\s*\n\n(.*?)(?=\n\n<div align="center">|$)'
    todo_match = re.search(todo_pattern, body, re.DOTALL)
    if todo_match:
        todo_section = todo_match.group(1).strip()
        print(f"\nFound TODO section:\n{todo_section}")
        if todo_section:
            current_category = 'General'
            for line in todo_section.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # skip details tags 
                if '<details>' in line:
                    print(f"Skipping details tag: {line}")
                    continue
                if '</details>' in line:
                    continue
                if '⚫' in line:
                    continue
                    
                # process category header - extract category name and ignore statistics
                if '<summary>' in line:
                    category_match = re.match(r'<summary>(?:<h3[^>]*>)?📑\s*([^()]+?)(?:\s*\(\d+/\d+\))?(?:</h3>)?</summary>', line)
                    if category_match:
                        current_category = category_match.group(1).strip()
                        print(f"\nFound category: {current_category}")
                        result['todos'].append((False, f"@{current_category}"))
                    continue
                
                # process todo items
                checkbox_match = re.match(r'-\s*\[([ xX])\]\s*(.*)', line)
                if checkbox_match:
                    is_checked = checkbox_match.group(1).lower() == 'x'
                    todo_text = checkbox_match.group(2).strip()
                    print(f"Found TODO item: [{is_checked}] {todo_text}")
                    result['todos'].append((is_checked, todo_text))
    
    print("\nParsed TODOs:")
    for checked, text in result['todos']:
        print(f"- [{'x' if checked else ' '}] {text}")
    
    return result

class TodoItem:
    def __init__(self, text: str, checked: bool = False, category: str = 'General'):
        self.text = text.strip()
        self.checked = checked
        self.category = category

    @property
    def is_issue(self) -> bool:
        return self.text.startswith('(issue)')

    def __str__(self) -> str:
        checkbox = '[x]' if self.checked else '[ ]'
        return f"- {checkbox} {self.text}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, TodoItem):
            return False
        return self.text == other.text and self.category == other.category

class TodoManager:
    def __init__(self):
        self.categories: Dict[str, List[TodoItem]] = {'General': []}
        self._current_category = 'General'

    @property
    def current_category(self) -> str:
        return self._current_category

    def set_category(self, category: str) -> None:
        """Set current category and ensure it exists"""
        category = category.strip() if category else 'General'
        self._current_category = category
        if category not in self.categories:
            self.categories[category] = []
        logger.debug(f"Category set to: {category}")

    def add_todo(self, text: str, checked: bool = False, category: str = None) -> None:
        """Add a new todo item"""
        use_category = category if category else self.current_category
        self.set_category(use_category)
        
        todo = TodoItem(text, checked, use_category)
        if todo not in self.categories[use_category]:
            self.categories[use_category].append(todo)
            logger.debug(f"Added todo to category '{use_category}': {text}")

    def get_all_todos(self) -> List[Tuple[bool, str]]:
        """Get all todos in format compatible with existing code"""
        result = []
        # 먼저 General 카테고리 처리
        if self.categories.get('General'):
            result.append((False, "@General"))
            for todo in self.categories['General']:
                result.append((todo.checked, todo.text))
        
        # 나머지 카테고리 처리 (알파벳 순)
        for category in sorted(cat for cat in self.categories if cat != 'General'):
            if self.categories[category]:
                result.append((False, f"@{category}"))
                for todo in self.categories[category]:
                    result.append((todo.checked, todo.text))
        return result

def convert_to_checkbox_list(text: str) -> str:
    """Convert text to checkbox list using TodoManager"""
    if not text:
        logger.debug("No text to convert to checkbox list")
        return ''

    logger.section("Converting to Checkbox List")
    logger.debug(f"Input text:\n{text}")

    todo_manager = TodoManager()
    current_category = None
    result = []  # 결과 리스트 초기화
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('@'):
            current_category = line[1:].strip()
            todo_manager.set_category(current_category)
            logger.debug(f"Setting category to: {current_category}")
            result.append(line)  # 카테고리 라인 추가
        elif line.startswith(('-', '*')):
            todo_text = line[1:].strip()
            if not (todo_text.startswith('[ ]') or todo_text.startswith('[x]')):
                todo_text = f"[ ] {todo_text}"
            todo_manager.add_todo(todo_text, category=current_category)
            logger.debug(f"Adding todo to category '{current_category}': {todo_text}")
        else:
            if not (line.startswith('[ ]') or line.startswith('[x]')):
                line = f"[ ] {line}"
            todo_manager.add_todo(line, category=current_category)
            logger.debug(f"Adding todo to category '{current_category}': {line}")

    todos = todo_manager.get_all_todos()
    result = []  # 최종 결과 리스트 초기화
    
    for checked, text in todos:
        if text.startswith('@'):
            result.append(text)
        else:
            result.append(f"- {text}")
    
    final_result = '\n'.join(result)
    logger.debug(f"Converted result:\n{final_result}")
    return final_result

def merge_todos(existing_todos: List[Tuple[bool, str]], new_todos: List[Tuple[bool, str]]) -> List[Tuple[bool, str]]:
    """Merge two lists of todos using TodoManager"""
    todo_manager = TodoManager()
    current_category = 'General'

    def process_todos(todos: List[Tuple[bool, str]], update_existing: bool = False) -> None:
        nonlocal current_category
        for checked, text in todos:
            if text.startswith('@'):
                current_category = text[1:].strip()
                todo_manager.set_category(current_category)
            else:
                if update_existing and checked:
                    # Update existing todo's checked status
                    for todos in todo_manager.categories.values():
                        for todo in todos:
                            if todo.text == text:
                                todo.checked = checked
                                break
                else:
                    todo_manager.add_todo(text, checked, current_category)

    # Process existing todos first
    process_todos(existing_todos, True)
    # Then process new todos
    process_todos(new_todos)

    return todo_manager.get_all_todos()

def normalize_category(category):
    """Normalize category name"""
    if not category:
        return 'General'
    return category.strip().replace(' ', '_')

def create_todo_section(todos: List[Tuple[bool, str]]) -> str:
    """Create todo section using TodoManager"""
    if not todos:
        return ''

    todo_manager = TodoManager()
    current_category = 'General'

    # Process all todos
    for checked, text in todos:
        if text.startswith('@'):
            current_category = text[1:].strip()
            todo_manager.set_category(current_category)
        else:
            todo_manager.add_todo(text, checked, current_category)

    # Create sections for each category
    sections = []
    for category in ['General'] + sorted(cat for cat in todo_manager.categories if cat != 'General'):
        todos = todo_manager.categories[category]
        if not todos:
            continue

        completed = sum(1 for todo in todos if todo.checked)
        total = len(todos)

        section = f'''<details>
<summary><h3 style="display: inline;">📑 {category} ({completed}/{total})</h3></summary>

{'\n'.join(str(todo) for todo in todos)}

⚫
</details>'''
        sections.append(section)

    return '\n\n'.join(sections)

def get_previous_day_todos(repo, issue_label, current_date):
    """Get unchecked todos from the previous day's issue"""
    # Find previous day's issue
    previous_issues = repo.get_issues(state='open', labels=[issue_label])
    previous_todos = []
    previous_issue = None
    
    for issue in previous_issues:
        if issue.title.startswith('📅 Daily Development Log') and issue.title != f'📅 Daily Development Log ({current_date})':
            previous_issue = issue
            # Parse todos from previous issue
            existing_content = parse_existing_issue(issue.body)
            # Get only unchecked todos
            previous_todos = [(False, todo[1]) for todo in existing_content['todos'] if not todo[0]]
            # Close previous issue
            issue.edit(state='closed')
            break
    
    return previous_todos

def is_commit_already_logged(commit_message, existing_content):
    """check if the commit is already logged"""
    # extract the title part of the commit message
    commit_title = commit_message.split('\n')[0].strip()
    
    print(f"\n=== Checking for duplicate commit ===")
    print(f"Checking commit: {commit_title}")
    
    # check if the commit is already logged
    for branch_content in existing_content['branches'].values():
        commit_blocks = branch_content.split('\n\n')
        for block in commit_blocks:
            if '> <summary>' in block:
                block_title = block.split('> <summary>')[1].split('</summary>')[0].strip()
                if commit_title in block_title:
                    print(f"Found matching commit: {block_title}")
                    return True
    
    print(f"No matching commit found")
    return False

def get_merge_commits(repo, merge_commit):
    """get the child commits of the merge commit"""
    if len(merge_commit.parents) != 2:  # not a merge commit
        print("Not a merge commit - skipping")
        return []
    
    parent1 = merge_commit.parents[0]
    parent2 = merge_commit.parents[1]
    
    print(f"\n=== Merge Commit Analysis ===")
    print(f"Merge commit SHA: {merge_commit.sha}")
    print(f"Parent1 SHA: {parent1.sha}")
    print(f"Parent2 SHA: {parent2.sha}")
    
    try:
        # get the commits from each parent
        comparison1 = repo.compare(parent1.sha, merge_commit.sha)
        comparison2 = repo.compare(parent2.sha, merge_commit.sha)
        
        commits1 = list(comparison1.commits)
        commits2 = list(comparison2.commits)
        
        print(f"\n=== Commit Analysis ===")
        print(f"Parent1 commits count: {len(commits1)}")
        print("Parent1 commits:")
        for c in commits1:
            print(f"- [{c.sha[:7]}] {c.commit.message.split('\n')[0]}")
        
        print(f"\nParent2 commits count: {len(commits2)}")
        print("Parent2 commits:")
        for c in commits2:
            print(f"- [{c.sha[:7]}] {c.commit.message.split('\n')[0]}")
        
        # remove duplicate commits and merge commits
        unique_commits = []
        seen_messages = set()
        
        for commit_list in [commits1, commits2]:
            for commit in commit_list:
                msg = commit.commit.message.strip()
                if not is_merge_commit_message(msg) and msg not in seen_messages:  # Exclude merge commits
                    seen_messages.add(msg)
                    unique_commits.append(commit)
        
        print(f"\nUnique commits found: {len(unique_commits)}")
        for c in unique_commits:
            print(f"- [{c.sha[:7]}] {c.commit.message.split('\n')[0]}")
        
        return unique_commits
        
    except Exception as e:
        print(f"\n=== Error in merge commit analysis ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return []

def get_commit_summary(commit):
    """Get a formatted commit summary"""
    sha = commit.sha[:7]
    msg = commit.commit.message.strip().split('\n')[0]
    return f"[{sha}] {msg}"

def log_commit_status(commit, status, extra_info=''):
    """Log commit status with consistent format"""
    summary = get_commit_summary(commit)
    print(f"{status}: {summary}{' - ' + extra_info if extra_info else ''}")

def is_daily_log_issue(issue_title):
    """Check if an issue is a DSR"""
    return issue_title.startswith('📅 Development Status Report')

def is_issue_todo(todo_text):
    """Check if todo item should be created as an issue"""
    return todo_text.strip().startswith('(issue)')

def create_issue_from_todo(repo, todo_text, category, parent_issue_number=None):
    """Create a new issue from todo item"""
    # Remove '(issue)' prefix and strip whitespace
    title = todo_text.replace('(issue)', '', 1).strip()
    
    # Create issue title with category
    issue_title = f"[{category}] {title}"
    
    # Create issue body with daily log reference
    body = f"""## 📌 Task Description
{title}

## 🏷 Category
{category}

## 🔗 References
- Created from Daily Log: #{parent_issue_number}
"""
    
    # Create labels
    labels = ['todo-generated', f'category:{category}']
    
    try:
        new_issue = repo.create_issue(
            title=issue_title,
            body=body,
            labels=labels
        )
        print(f"Created new issue #{new_issue.number}: {issue_title}")
        
        # Add reference comment to the parent issue
        if parent_issue_number:
            parent_issue = repo.get_issue(parent_issue_number)
            parent_issue.create_comment(f"Created issue #{new_issue.number} from todo item")
        
        return new_issue
    except Exception as e:
        print(f"Failed to create issue for todo: {title}")
        print(f"Error: {str(e)}")
        return None

def process_todo_items(repo, todos, parent_issue_number):
    """Process todo items and create issues for marked items"""
    processed_todos = []
    created_issues = []
    
    current_category = 'General'
    for checked, text in todos:
        if text.startswith('@'):
            current_category = text[1:].strip()
            processed_todos.append((checked, text))
            continue
            
        if is_issue_todo(text):
            # Create new issue
            new_issue = create_issue_from_todo(repo, text, current_category, parent_issue_number)
            if new_issue:
                created_issues.append(new_issue)
                # Add only the issue number as a todo item
                processed_todos.append((checked, f"#{new_issue.number}"))
        else:
            processed_todos.append((checked, text))
    
    return processed_todos, created_issues

def get_todays_commits(repo, branch, timezone):
    """Get all commits from today for the specified branch"""
    tz = pytz.timezone(timezone)
    today = datetime.now(tz).date()
    
    print(f"\n=== Getting Today's Commits for {branch} ===")
    
    try:
        # get commits of the branch
        commits = repo.get_commits(sha=branch)
        todays_commits = []
        
        for commit in commits:
            # GitHub API returns UTC time, so convert to specified timezone
            commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(tz).date()
            commit_time = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if commit_date == today:
                if not is_merge_commit_message(commit.commit.message):
                    todays_commits.append((commit_time, commit))
                    print(f"Found commit: [{commit.sha[:7]}] {commit.commit.message.split('\n')[0]} at {commit_time.strftime('%H:%M:%S')}")
            elif commit_date < today:
                break
        
        # sort by time (latest first)
        todays_commits.sort(key=lambda x: x[0], reverse=True)
        sorted_commits = [commit for _, commit in todays_commits]
        
        print(f"\nFound {len(sorted_commits)} commits for today")
        return sorted_commits
        
    except Exception as e:
        print(f"Error getting commits: {str(e)}")
        return []

def update_readme_with_daily_log(repo, issue_number, issue_title):
    """Update README.md with the latest daily log link"""
    try:
        # Get README content
        readme = repo.get_contents("README.md")
        content = readme.decoded_content.decode('utf-8')
        
        # Prepare new daily log section
        daily_log_section = f'''## 📌 Latest Development Status Report
[{issue_title}](../../issues/{issue_number})
'''
        
        # Check if daily log section exists
        daily_log_pattern = r'## 📌 Latest Development Status Report\n\[.*?\]\(.*?\)\n'
        if re.search(daily_log_pattern, content):
            # Update existing section
            new_content = re.sub(daily_log_pattern, daily_log_section, content)
        else:
            # Add new section at the top after the first heading
            first_heading_end = content.find('\n', content.find('#'))
            if first_heading_end == -1:
                new_content = daily_log_section + '\n' + content
            else:
                new_content = content[:first_heading_end + 1] + '\n' + daily_log_section + content[first_heading_end + 1:]
        
        # Update README
        repo.update_file(
            path="README.md",
            message=f"docs: Update DSR link to #{issue_number}",
            content=new_content,
            sha=readme.sha
        )
        print(f"Updated README.md with DSR #{issue_number}")
        
    except Exception as e:
        print(f"Failed to update README: {str(e)}")

def find_active_dsr_issue(repo: Repository, date_string: str, issue_title: str) -> Optional[Issue]:
    """Find active DSR issue for the given date"""
    logger.section("Searching for Active DSR Issue")
    
    # DSR 라벨로 검색
    dsr_issues = repo.get_issues(state='open', labels=['DSR'])
    
    for issue in dsr_issues:
        logger.debug(f"Checking issue #{issue.number}: {issue.title}")
        # 정확한 제목 매칭으로 오늘의 DSR 이슈 찾기
        if issue.title == issue_title:
            logger.debug(f"Found today's DSR issue: #{issue.number}")
            return issue
    
    logger.debug("No active DSR issue found for today")
    return None

def main():
    # Initialize GitHub token and environment variables
    github_token = os.environ['GITHUB_TOKEN']
    timezone = os.environ.get('TIMEZONE', 'Asia/Seoul')
    issue_prefix = os.environ.get('ISSUE_PREFIX', '📅')
    excluded_pattern = os.environ.get('EXCLUDED_COMMITS', '^(chore|docs|style):')

    # Initialize GitHub API client
    g = Github(github_token)
    
    # Get repository and branch information
    repository = os.environ['GITHUB_REPOSITORY']
    repo = g.get_repo(repository)
    branch = os.environ['GITHUB_REF'].replace('refs/heads/', '')
    
    # Get current time in specified timezone
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    date_string = now.strftime('%Y-%m-%d')
    time_string = now.strftime('%H:%M:%S')

    # Get repository name from full path
    repo_name = repository.split('/')[-1]
    if repo_name.startswith('.'):
        repo_name = repo_name[1:]

    # Create consistent issue title format
    issue_title = f"{issue_prefix} Development Status Report ({date_string})"
    if repo_name:
        issue_title += f" - {repo_name}"
    
    logger.section("Issue Title Format")
    logger.debug(f"Using title format: {issue_title}")

    # Get today's commits and sort by time
    commits_to_process = get_todays_commits(repo, branch, timezone)
    
    if not commits_to_process:
        logger.debug("No commits found for today")
        return

    # Find today's DSR issue
    today_issue = find_active_dsr_issue(repo, date_string, issue_title)
    previous_todos = []
    existing_content = {'branches': {}}

    if today_issue:
        existing_content = parse_existing_issue(today_issue.body)
        if existing_content['todos']:
            logger.section("Current Issue's TODO List")
            for todo in existing_content['todos']:
                status = "✅ Completed" if todo[0] else "⬜ Pending"
                logger.todo(status, todo[1])

    # Find and process previous DSR issues
    previous_issues = repo.get_issues(state='open', labels=['DSR'])
    for issue in previous_issues:
        if issue != today_issue and issue.title.startswith(f"{issue_prefix} Development Status Report"):
            logger.section(f"Processing Previous Issue #{issue.number}")
            prev_content = parse_existing_issue(issue.body)
            
            logger.debug("Filtering unchecked TODOs:")
            unchecked_todos = []
            current_category = None
            
            for checked, text in prev_content['todos']:
                if text.startswith('@'):
                    current_category = text[1:]
                    logger.debug(f"Found category: {current_category}")
                    unchecked_todos.append((False, text))
                elif not checked: 
                    logger.debug(f"Adding unchecked item: {text}")
                    unchecked_todos.append((False, text))
                else:
                    logger.debug(f"Skipping checked item: {text}")
            
            if unchecked_todos:
                logger.section(f"Found {len(unchecked_todos)} unchecked TODOs")
                for _, todo_text in unchecked_todos:
                    logger.todo("⬜", todo_text)
                previous_todos = unchecked_todos 
            else:
                logger.debug("No unchecked TODOs found to migrate")
                
            issue.edit(state='closed')
            logger.debug(f"Closed previous issue #{issue.number}")

    # process commits
    print("\n=== Filtering commits ===")
    filtered_commits = []
    seen_messages = set()
    
    for commit_to_process in commits_to_process:
        msg = commit_to_process.commit.message.strip()
        
        if is_merge_commit_message(msg):
            log_commit_status(commit_to_process, "Skipping merge commit")
            if len(commit_to_process.parents) == 2:
                print("Processing child commits from merge...")
                child_commits = get_merge_commits(repo, commit_to_process)
                commits_to_process.extend(child_commits)
            continue
            
        if msg not in seen_messages and not is_commit_already_logged(msg, existing_content):
            seen_messages.add(msg)
            filtered_commits.append(commit_to_process)
            log_commit_status(commit_to_process, "Adding commit")
        else:
            log_commit_status(commit_to_process, "Skipping duplicate commit")
    
    commits_to_process = filtered_commits
    
    if not commits_to_process:
        print("No new commits to process after filtering")
        return

    # Get current time in specified timezone
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    date_string = now.strftime('%Y-%m-%d')
    time_string = now.strftime('%H:%M:%S')

    # Get repository name from full path
    repo_name = repository.split('/')[-1]
    if repo_name.startswith('.'):
        repo_name = repo_name[1:]

    # Create issue title
    issue_title = f"{issue_prefix} Development Status Report ({date_string}) - {repo_name}"

    # Create commit sections
    commit_sections = []
    for commit_to_process in commits_to_process:
        # Parse commit message
        commit_data = parse_commit_message(commit_to_process.commit.message)
        if not commit_data:
            continue

        # Get commit time in local timezone
        commit_time = commit_to_process.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(tz)
        commit_time_string = commit_time.strftime('%H:%M:%S')
        
        commit_details = create_commit_section(
            commit_data,
            branch,
            commit_to_process.sha,
            commit_to_process.commit.author.name,
            commit_time_string,
            repo
        )
        commit_sections.append(commit_details)

    # Join all commit sections
    branch_content = '\n\n'.join(commit_sections)

    if today_issue:
        # Parse existing issue
        logger.section("Current Issue's TODO Statistics")
        print(f"Current TODOs in issue: {len(existing_content['todos'])} items")
        
        # Maintain existing todos while adding new ones
        all_todos = existing_content['todos']
        
        # Add todos from current commit
        current_commit = repo.get_commit(os.environ['GITHUB_SHA'])
        commit_data = parse_commit_message(current_commit.commit.message)
        if commit_data and commit_data['todo']:
            logger.section("Processing TODOs from Current Commit")
            print(f"Todo section from commit:\n{commit_data['todo']}")
            
            new_todos = []
            todo_lines = convert_to_checkbox_list(commit_data['todo']).split('\n')
            print(f"Converted todo lines: {todo_lines}")
            
            for line in todo_lines:
                if line.startswith('@'):
                    new_todos.append((False, line))
                elif line.startswith('-'):
                    new_todos.append((False, line[2:].strip()))
            
            logger.debug("Parsed new todos from current commit:")
            for checked, text in new_todos:
                print(f"- [{checked}] {text}")
            
            # Merge new todos only
            all_todos = merge_todos(all_todos, new_todos)
        
        # Merge previous todos
        if previous_todos:
            logger.section("TODOs Migrated from Previous Day")
            for _, todo_text in previous_todos:
                print(f"⬜ {todo_text}")
            all_todos = merge_todos(all_todos, previous_todos)
        
        # Process todos and create issues for marked items
        processed_todos, created_issues = process_todo_items(repo, all_todos, today_issue.number)
        
        logger.section("Created new issues from todos")
        for issue in created_issues:
            print(f"#{issue.number}: {issue.title}")
        
        logger.section("Final Result")
        print(f"Total TODOs: {len(processed_todos)} items")
        
        # Create updated body with processed todos
        branch_section = f'''<details>
<summary><h3 style="display: inline;">✨ {branch.title()}</h3></summary>

{branch_content}
</details>'''

        updated_body = f'''# {issue_title}

<div align="center">

## 📊 Branch Summary

</div>

{branch_section}

<div align="center">

## 📝 Todo

{create_todo_section(processed_todos)}'''

        today_issue.edit(body=updated_body)
        print(f"Updated issue #{today_issue.number}")
        update_readme_with_daily_log(repo, today_issue.number, issue_title)
    else:
        # create new issue
        all_todos = []
        
        # add TODOs from the current commit
        current_commit = repo.get_commit(os.environ['GITHUB_SHA'])
        commit_data = parse_commit_message(current_commit.commit.message)
        if commit_data and commit_data['todo']:
            todo_lines = convert_to_checkbox_list(commit_data['todo']).split('\n')
            for line in todo_lines:
                if line.startswith('-'):
                    all_todos.append((False, line[2:].strip()))
        
        # merge unchecked TODOs from the previous day
        if previous_todos:
            all_todos = merge_todos(all_todos, previous_todos)
        
        # Create initial body with commit at the top
        body = f'''# {issue_title}

<div align="center">

## 📊 Branch Summary

</div>

<details>
<summary><h3 style="display: inline;">✨ {branch.title()}</h3></summary>

{branch_content}
</details>

<div align="center">

## 📝 Todo

{create_todo_section(all_todos)}'''

        # Create new issue with initial content
        new_issue = repo.create_issue(
            title=issue_title,
            body=body,
            labels=[os.environ.get('ISSUE_LABEL', 'dsr'), f"branch:{branch}"]
        )
        print(f"Created new issue #{new_issue.number}")
        update_readme_with_daily_log(repo, new_issue.number, issue_title)

if __name__ == '__main__':
    main()
import os
import re
from datetime import datetime
import pytz
from github import Github

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

def parse_commit_message(message):
    """Parse commit message"""
    pattern = r'(?i)\[(.*?)\] (.*?)(?:\s*\n\s*\[body\](.*?))?(?:\s*\n\s*\[todo\](.*?))?(?:\s*\n\s*\[footer\](.*?))?$'
    match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"Failed to parse commit message: {message.split('\n')[0]}")
        return None
    
    commit_type = match.group(1).lower()
    type_info = COMMIT_TYPES.get(commit_type, {'emoji': '🔍', 'label': 'other', 'description': 'Other'})
    
    return {
        'type': commit_type,
        'type_info': type_info,
        'title': match.group(2),
        'body': match.group(3),
        'todo': match.group(4),
        'footer': match.group(5)
    }

class CategoryManager:
    def __init__(self):
        self._categories = {'general': 'General'}  # lowercase -> original case mapping
        self._current = 'General'
    
    def add_category(self, category):
        """Add a new category or get existing one"""
        if not category:
            return self._categories['general']
            
        category = category.strip()
        category_lower = category.lower()
        
        if category_lower not in self._categories:
            self._categories[category_lower] = category
        
        return self._categories[category_lower]
    
    def get_category(self, category):
        """Get original case of category"""
        if not category:
            return self._categories['general']
            
        category_lower = category.lower()
        return self._categories.get(category_lower, category)
    
    def set_current(self, category):
        """Set current category"""
        if not category:
            self._current = self._categories['general']
        else:
            self._current = self.add_category(category)
    
    @property
    def current(self):
        """Get current category"""
        return self._current

def parse_categorized_todos(text):
    """Parse todos with categories"""
    if not text:
        print("DEBUG: No todo text provided")
        return {}
    
    print("\n=== Parsing TODOs ===")
    print(f"Raw todo text:\n{text}")
    
    categories = {}
    category_manager = CategoryManager()
    current_category = 'General'
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        print(f"Processing line: {line}")
        
        if line.startswith('@'):
            current_category = line[1:].strip()
            if current_category not in categories:
                categories[current_category] = []
            print(f"Found category: {current_category}")
            continue
            
        if line.startswith(('-', '*')):
            if current_category not in categories:
                categories[current_category] = []
            
            item = line[1:].strip()
            categories[current_category].append(item)
            print(f"Added todo item to {current_category}: {item}")
    
    return categories

def create_commit_section(commit_data, branch, commit_sha, author, time_string, repo):
    """Create commit section with details tag"""
    # Handle None values in commit data
    body = commit_data.get('body', '').strip() if commit_data.get('body') else ''
    footer = commit_data.get('footer', '').strip() if commit_data.get('footer') else ''
    
    # Format body with bullet points
    body_lines = []
    if body:
        for line in body.split('\n'):
            line = line.strip()
            if line:
                body_lines.append(f"> • {line}")
    quoted_body = '\n'.join(body_lines)
    
    # Extract issue numbers from entire commit message
    full_message = f"{commit_data['title']}\n{body}\n{footer}"
    issue_numbers = set(re.findall(r'#(\d+)', full_message))
    
    # Add comments to referenced issues and prepare related issues section
    related_issues = []
    
    # Always add reference to current daily log
    try:
        issues = repo.get_issues(state='open', labels=['daily-log'])
        for issue in issues:
            if issue.title.startswith('📅 Daily Development Log'):
                related_issues.append(f"Daily Development Log: #{issue.number}")
                break
    except Exception as e:
        print(f"Failed to find current daily log issue: {str(e)}")
    
    # Process other referenced issues
    for issue_num in issue_numbers:
        try:
            issue = repo.get_issue(int(issue_num))
            issue.create_comment(f"Referenced in commit {commit_sha[:7]}\n\nCommit message:\n```\n{commit_data['title']}\n```")
            related_issues.append(f"Related to #{issue_num}")
        except Exception as e:
            print(f"Failed to add comment to issue #{issue_num}: {str(e)}")
    
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
    # Initialize result structure
    result = {
        'branches': {},
        'todos': []
    }
    
    # Parse branch section
    branch_pattern = r'<details>\s*<summary><h3 style="display: inline;">✨\s*(\w+)</h3></summary>(.*?)</details>'
    branch_blocks = re.finditer(branch_pattern, body, re.DOTALL)
    
    for block in branch_blocks:
        branch_name = block.group(1)
        branch_content = block.group(2).strip()
        result['branches'][branch_name] = branch_content
    
    # Parse Todo section
    todo_pattern = r'## 📝 Todo\s*\n\n(.*?)(?=\n\n<div align="center">|$)'
    todo_match = re.search(todo_pattern, body, re.DOTALL)
    if todo_match:
        todo_section = todo_match.group(1).strip()
        if todo_section:
            current_category = 'General'
            for line in todo_section.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # skip details tags 
                if '<details>' in line:
                    continue
                if '</details>' in line:
                    continue
                    
                # process category header
                if '<summary>📑' in line:
                    current_category = line.split('📑')[1].split('</summary>')[0].strip()
                    result['todos'].append((False, f"@{current_category}"))
                    continue
                
                # process todo items
                checkbox_match = re.match(r'- \[([ x])\] (.*)', line)
                if checkbox_match:
                    is_checked = checkbox_match.group(1) == 'x'
                    todo_text = checkbox_match.group(2)
                    result['todos'].append((is_checked, todo_text))
    
    return result

def merge_todos(existing_todos, new_todos):
    """Merge two lists of todos, avoiding duplicates and preserving order and state"""
    result = []
    todo_map = {}
    category_manager = CategoryManager()
    processed_categories = set()  # Track processed categories
    
    # Process existing todos
    current_category = 'General'  # Set default category as General
    for checked, text in existing_todos:
        if text.startswith('@'):
            current_category = text[1:].strip()
            if current_category.lower() not in processed_categories:  # Only add if not processed
                result.append((False, f"@{current_category}"))
                processed_categories.add(current_category.lower())
            continue
            
        todo_map[text] = len(result)
        result.append((checked, text))
    
    # Process new todos
    # Add General category if there are uncategorized items and not already added
    if not any(t[1].startswith('@') for t in new_todos) and 'general' not in processed_categories:
        result.insert(0, (False, "@General"))
        processed_categories.add('general')
        
    for checked, text in new_todos:
        if text.startswith('@'):
            current_category = text[1:].strip()
            # Add category marker if not exists
            if current_category.lower() not in processed_categories:
                result.append((False, f"@{current_category}"))
                processed_categories.add(current_category.lower())
            continue
            
        # Add General category marker for uncategorized items if not already added
        if current_category == 'General' and 'general' not in processed_categories:
            result.insert(0, (False, "@General"))
            processed_categories.add('general')
            
        # Find the appropriate category section
        category_index = next((i for i, (_, t) in enumerate(result) 
                            if t.startswith('@') and t[1:].strip().lower() == current_category.lower()), None)
        
        if category_index is not None:
            # Find the next category marker or end of list
            next_category_index = next((i for i, (_, t) in enumerate(result[category_index + 1:], 
                                    start=category_index + 1) if t.startswith('@')), len(result))
            
            if text not in todo_map:
                # Insert the new todo just before the next category
                result.insert(next_category_index, (checked, text))
                # Update indices in todo_map
                for t, idx in todo_map.items():
                    if idx >= next_category_index:
                        todo_map[t] = idx + 1
                todo_map[text] = next_category_index
                print(f"Added new todo to {current_category}: {text}")
            else:
                idx = todo_map[text]
                if checked and not result[idx][0]:
                    result[idx] = (True, text)
                    print(f"Updated existing todo in {current_category}: {text}")
    
    return result

def create_todo_section(todos):
    """Create todo section with categories"""
    if not todos:
        return ''
    
    print("\n=== Creating Todo Section ===")
    
    # process categorized todos
    categorized = {}
    category_manager = CategoryManager()
    general_todos = []
    
    for checked, todo_text in todos:
        print(f"Processing todo: {todo_text}")
        
        if todo_text.startswith('@'):
            category = todo_text[1:].strip()
            category = category_manager.add_category(category)
            category_manager.set_current(category)
            print(f"Found category: {category}")
            continue
            
        category = category_manager.current
        category_lower = category.lower()
        
        # Collect General todos separately
        if category == 'General':
            general_todos.append((checked, todo_text))
            print(f"Added to General category: {todo_text}")
            continue
            
        if category_lower not in categorized:
            categorized[category_lower] = {
                'name': category,
                'todos': []
            }
        categorized[category_lower]['todos'].append((checked, todo_text))
        print(f"Added to category '{category}': {todo_text}")
    
    # process categorized todos
    sections = []
    processed_categories = set()  # Track processed categories
    
    # Add General category first if it has items
    if general_todos:
        completed = sum(1 for checked, _ in general_todos if checked)
        total = len(general_todos)
        section = f'''<details>
<summary>📑 General ({completed}/{total})</summary>

{'\n'.join(f"- {'[x]' if checked else '[ ]'} {text}" for checked, text in general_todos)}
</details>'''
        sections.append(section)
        processed_categories.add('general')
        print(f"\nProcessing category: General")
        print(f"Items in category: {total} (Completed: {completed})")
    
    # Process other categories
    for category_lower, data in categorized.items():
        if not data['todos'] or category_lower in processed_categories:  # Skip empty or already processed categories
            continue
            
        category = data['name']
        completed = sum(1 for checked, _ in data['todos'] if checked)
        total = len(data['todos'])
        print(f"\nProcessing category: {category}")
        print(f"Items in category: {total} (Completed: {completed})")
        
        todo_lines = []
        for checked, text in data['todos']:
            checkbox = '[x]' if checked else '[ ]'
            todo_lines.append(f'- {checkbox} {text}')
            print(f"Added todo line: {text}")
        
        section = f'''<details>
<summary>📑 {category} ({completed}/{total})</summary>

{'\n'.join(todo_lines)}
</details>'''
        sections.append(section)
        processed_categories.add(category_lower)
        print(f"Created details section for {category}")
    
    # Add extra newline between sections for better readability
    result = '\n\n'.join(sections)
    print("\nFinal todo section:")
    print(result)
    return result

def convert_to_checkbox_list(text):
    """Convert text to checkbox list with categories"""
    if not text:
        print("DEBUG: No text to convert to checkbox list")
        return ''
    
    print("\n=== Converting to Checkbox List ===")
    print(f"Input text:\n{text}")
    
    lines = []
    current_category = None
    
    # Process each line
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('@'):
            current_category = line
            lines.append(current_category)
            print(f"Found category: {current_category}")
        elif line.startswith(('-', '*')):
            if current_category is None:
                if not any(l.startswith('@General') for l in lines):
                    lines.insert(0, '@General')
                    current_category = '@General'
                    print("Created General category for uncategorized items")
            
            todo_text = line[1:].strip()
            lines.append(f"- {todo_text}")
            print(f"Added todo item to {current_category}: {todo_text}")
    
    result = '\n'.join(lines)
    print(f"\nConverted result:\n{result}")
    return result

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
    commit_body = '\n'.join(commit_message.split('\n')[1:]).strip()
    
    print(f"\n=== Checking for duplicate commit ===")
    print(f"Checking commit: {commit_title}")
    
    # check if the commit is already logged
    for branch_content in existing_content['branches'].values():
        # filter the commit by title
        if commit_title in branch_content:
            print(f"Found matching title in existing content")
            
            # compare the body content (optional)
            if commit_body and commit_body in branch_content:
                print(f"Found matching body content - considering as duplicate")
                return True
            elif not commit_body:
                print(f"No body content to compare - considering as duplicate based on title")
                return True
            else:
                print(f"Body content differs - not a duplicate")
    
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
        
        # remove duplicate commits
        unique_commits = []
        seen_messages = set()
        
        for commit_list in [commits1, commits2]:
            for commit in commit_list:
                msg = commit.commit.message.strip()
                if msg not in seen_messages:
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
    """Check if an issue is a daily log"""
    return issue_title.startswith('📅 Daily Development Log')

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

def main():
    # Initialize GitHub token and environment variables
    github_token = os.environ['GITHUB_TOKEN']
    timezone = os.environ.get('TIMEZONE', 'Asia/Seoul')
    issue_prefix = os.environ.get('ISSUE_PREFIX', '📅')
    issue_label = os.environ.get('ISSUE_LABEL', 'daily-log')
    excluded_pattern = os.environ.get('EXCLUDED_COMMITS', '^(chore|docs|style):')

    # Initialize GitHub API client
    g = Github(github_token)
    
    # Get commit information from environment variables
    repository = os.environ['GITHUB_REPOSITORY']
    repo = g.get_repo(repository)
    commit_sha = os.environ['GITHUB_SHA']
    commit = repo.get_commit(commit_sha)
    branch = os.environ['GITHUB_REF'].replace('refs/heads/', '')
    
    # Check for excluded commit types
    if re.match(excluded_pattern, commit.commit.message):
        print(f"Excluded commit type: {commit.commit.message}")
        return
        
    # if the commit is a merge commit, process the child commits
    commits_to_process = []
    if len(commit.parents) == 2:  # merge commit
        print("Merge commit detected - processing child commits...")
        commits_to_process = get_merge_commits(repo, commit)

    if not commits_to_process:  # not a merge commit or failed to get child commits
        commits_to_process = [commit]

    # Search for existing issues
    issues = repo.get_issues(state='open', labels=[issue_label])
    today_issue = None
    previous_todos = []
    existing_content = {'branches': {}}

    # find today's issue
    for issue in issues:
        if f"Daily Development Log ({datetime.now(pytz.timezone(timezone)).strftime('%Y-%m-%d')})" in issue.title:
            today_issue = issue
            existing_content = parse_existing_issue(issue.body)
            # TODO list is printed only once
            if existing_content['todos']:
                print(f"\n=== Current Issue's TODO List ===")
                for todo in existing_content['todos']:
                    status = "✅ Completed" if todo[0] else "⬜ Pending"
                    print(f"{status}: {todo[1]}")
            break

    # find previous issues
    for issue in issues:
        if issue != today_issue and is_daily_log_issue(issue.title):
            print(f"\n=== Processing Previous Issue #{issue.number} ===")
            prev_content = parse_existing_issue(issue.body)
            unchecked_todos = [(False, todo[1]) for todo in prev_content['todos'] if not todo[0]]
            if unchecked_todos:
                print(f"Found {len(unchecked_todos)} unchecked TODOs")
                for _, todo_text in unchecked_todos:
                    print(f"⬜ Migrating: {todo_text}")
                previous_todos.extend(unchecked_todos)
            issue.edit(state='closed')
            print(f"Closed previous issue #{issue.number}")

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
    issue_title = f"{issue_prefix} Daily Development Log ({date_string}) - {repo_name}"

    # Process each commit
    for commit_to_process in commits_to_process:
        # Parse commit message
        commit_data = parse_commit_message(commit_to_process.commit.message)
        if not commit_data:
            continue

        # Create commit section
        commit_details = create_commit_section(
            commit_data,
            branch,
            commit_to_process.sha,
            commit_to_process.commit.author.name,
            time_string,
            repo
        )

        # Create todo section and merge with previous todos
        if today_issue:
            # Parse existing issue
            print(f"\n=== TODO Statistics ===")
            print(f"Current TODOs in issue: {len(existing_content['todos'])} items")
            
            # Add new commit to branch section
            branch_title = branch.title()
            if branch_title in existing_content['branches']:
                existing_content['branches'][branch_title] = f"{existing_content['branches'][branch_title]}\n\n{commit_details}"
            else:
                existing_content['branches'][branch_title] = commit_details
            
            # Convert new todos from commit message
            new_todos = []
            if commit_data['todo']:
                print(f"\n=== Processing TODOs from Commit ===")
                print(f"Todo section from commit:\n{commit_data['todo']}")
                
                todo_lines = convert_to_checkbox_list(commit_data['todo']).split('\n')
                print(f"Converted todo lines: {todo_lines}")
                
                for line in todo_lines:
                    if line.startswith('@'):
                        new_todos.append((False, line))
                    elif line.startswith('-'):
                        new_todos.append((False, line[2:].strip()))
            
            print(f"\nParsed new todos:")
            for checked, text in new_todos:
                print(f"- [{checked}] {text}")
            
            # Maintain existing todos while adding new ones
            all_todos = merge_todos(existing_content['todos'], new_todos)
            if previous_todos:
                print(f"\n=== TODOs Migrated from Previous Day ===")
                for _, todo_text in previous_todos:
                    print(f"⬜ {todo_text}")
                all_todos = merge_todos(all_todos, previous_todos)
            
            # Process todos and create issues for marked items
            processed_todos, created_issues = process_todo_items(repo, all_todos, today_issue.number)
            
            print(f"\n=== Created {len(created_issues)} new issues from todos ===")
            for issue in created_issues:
                print(f"#{issue.number}: {issue.title}")
            
            print(f"\n=== Final Result ===")
            print(f"Total TODOs: {len(processed_todos)} items")
            
            # Create updated body with processed todos
            branch_sections = []
            for branch_name, branch_content in existing_content['branches'].items():
                branch_sections.append(f'''<details>
<summary><h3 style="display: inline;">✨ {branch_name}</h3></summary>

{branch_content}
</details>''')
            
            updated_body = f'''# {issue_title}

<div align="center">

## 📊 Branch Summary

</div>

{''.join(branch_sections)}

<div align="center">

## 📝 Todo

</div>

{create_todo_section(processed_todos)}'''
            
            today_issue.edit(body=updated_body)
            print(f"Updated issue #{today_issue.number}")
        else:
            # For new issue, merge previous todos with new ones
            new_todos = []
            if commit_data['todo']:
                todo_lines = convert_to_checkbox_list(commit_data['todo']).split('\n')
                new_todos = [(False, line[2:].strip()) for line in todo_lines if line.startswith('-')]
            
            # Merge all todos
            all_todos = merge_todos(new_todos, previous_todos)
            
            # Create initial body
            body = f'''# {issue_title}

<div align="center">

## 📊 Branch Summary

</div>

<details>
<summary><h3 style="display: inline;">✨ {branch.title()}</h3></summary>

{commit_details}
</details>

<div align="center">

## 📝 Todo

</div>

{create_todo_section(all_todos)}'''

            # Create new issue with initial content
            new_issue = repo.create_issue(
                title=issue_title,
                body=body,
                labels=[issue_label, f"branch:{branch}", f"type:{commit_data['type_info']['label']}"]
            )
            print(f"Created new issue #{new_issue.number}")

if __name__ == '__main__':
    main()
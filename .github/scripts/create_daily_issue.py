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
    # Skip merge commits
    if is_merge_commit_message(message):
        print(f"Skipping merge commit message: {message.split('\n')[0]}")
        return None
        
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

def parse_categorized_todos(text):
    """Parse todos with categories"""
    if not text:
        print("DEBUG: No todo text provided")
        return {}
    
    print("\n=== Parsing TODOs ===")
    print(f"Raw todo text:\n{text}")
    
    categories = {}
    current_category = 'General'
    category_case_map = {}  # 카테고리 대소문자 원본 보존
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        print(f"Processing line: {line}")
        
        # check if the line is a category header
        if line.startswith('@'):
            original_category = line[1:].split(':')[0].strip()
            current_category = original_category.lower()  # 소문자로 저장
            category_case_map[current_category] = original_category  # 원본 대소문자 보존
            print(f"Found category: {original_category}")
            continue
            
        # process todo items
        if line.startswith(('-', '*')):
            if current_category not in categories:
                categories[current_category] = []
            item = line[1:].strip()
            categories[current_category].append(item)
            print(f"Added todo item to {category_case_map.get(current_category, current_category)}: {item}")
    
    # 결과 반환 시 원본 대소문자로 변환
    result = {}
    for category, items in categories.items():
        original_case = category_case_map.get(category, category)
        result[original_case] = items
    
    print("\nParsed categories:")
    for category, items in result.items():
        print(f"{category}: {len(items)} items")
        for item in items:
            print(f"  - {item}")
    
    return result

def create_commit_section(commit_data, branch, commit_sha, author, time_string):
    """Create commit section with details tag"""
    # Apply blockquote to each line of the body
    body_lines = [f"> {line}" for line in commit_data['body'].strip().split('\n')]
    quoted_body = '\n'.join(body_lines)
    
    # Apply blockquote to related issues if they exist
    related_issues = f"\n> **Related Issues:**\n> {commit_data['footer'].strip()}" if commit_data['footer'] else ''
    
    section = f'''> <details>
> <summary>💫 {time_string} - {commit_data['title'].strip()}</summary>
>
> Type: {commit_data['type']} ({commit_data['type_info']['description']})
> Commit: `{commit_sha}`
> Author: {author}
>
{quoted_body}{related_issues}
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
    current_category = 'General'
    seen_categories = set()  # 대소문자 구분 없이 카테고리 추적
    
    print("\n=== Merging TODOs ===")
    
    # process existing todos
    for checked, text in existing_todos:
        if text.startswith('@'):
            category = text[1:].strip()
            current_category = category
            category_lower = category.lower()
            if category_lower not in seen_categories:
                seen_categories.add(category_lower)
                result.append((False, text))
                print(f"Found existing category: {category}")
            continue
            
        todo_map[text] = len(result)
        result.append((checked, text))
        print(f"Added existing todo to {current_category}: {text}")
    
    # process new todos
    current_category = 'General'
    for checked, text in new_todos:
        if text.startswith('@'):
            category = text[1:].strip()
            current_category = category
            category_lower = category.lower()
            if category_lower not in seen_categories:
                seen_categories.add(category_lower)
                result.append((False, text))
                print(f"Found new category: {category}")
            else:
                print(f"Skipping duplicate category (case-insensitive): {category}")
            continue
            
        if text not in todo_map:
            result.append((checked, text))
            todo_map[text] = len(result) - 1
            print(f"Added new todo to {current_category}: {text}")
        else:
            idx = todo_map[text]
            if checked and not result[idx][0]:
                result[idx] = (True, text)
                print(f"Updated existing todo: {text}")
    
    return result

def create_todo_section(todos):
    """Create todo section with categories"""
    if not todos:
        return ''
    
    print("\n=== Creating Todo Section ===")
    
    # process categorized todos
    categorized = {}
    current_category = 'General'
    
    for checked, todo_text in todos:
        print(f"Processing todo: {todo_text}")
        
        # check if the todo is a category header
        if todo_text.startswith('@'):
            current_category = todo_text[1:].strip()
            print(f"Found category: {current_category}")
            continue
            
        if current_category not in categorized:
            categorized[current_category] = []
        categorized[current_category].append((checked, todo_text))
        print(f"Added to category '{current_category}': {todo_text}")
    
    # process categorized todos
    sections = []
    for category, category_todos in categorized.items():
        if not category_todos:  # skip empty categories
            continue
            
        print(f"\nProcessing category: {category}")
        print(f"Items in category: {len(category_todos)}")
        
        todo_lines = []
        for checked, text in category_todos:
            checkbox = '[x]' if checked else '[ ]'
            todo_lines.append(f'- {checkbox} {text}')
            print(f"Added todo line: {text}")
        
        if category == 'General':
            # General category is displayed directly
            sections.append('\n'.join(todo_lines))
        else:
            # other categories are wrapped in details
            section = f'''<details>
<summary>📑 {category}</summary>

{'\n'.join(todo_lines)}
</details>'''
            sections.append(section)
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
    
    categories = parse_categorized_todos(text)
    lines = []
    
    # process categories in order, preserving original case
    for category, todos in categories.items():
        if category != 'General':
            # Preserve the original category case from the commit message
            original_case = next(line[1:].strip() for line in text.split('\n') 
                              if line.strip().startswith('@') 
                              and line[1:].strip().lower() == category.lower())
            lines.append(f'@{original_case}')  # add category marker with original case
        for todo in todos:
            lines.append(f'- {todo}')
    
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
        if issue != today_issue and issue.title.startswith('📅 Daily Development Log'):
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

    # process commits which are not logged in the issue
    filtered_commits = []
    seen_messages = set()
    
    print("\n=== Filtering commits ===")
    for commit_to_process in commits_to_process:
        msg = commit_to_process.commit.message.strip()
        # skip merge commit messages
        if is_merge_commit_message(msg):
            print(f"Skipping merge commit: [{commit_to_process.sha[:7]}] {msg.split('\n')[0]}")
            continue
            
        if msg not in seen_messages and not is_commit_already_logged(msg, existing_content):
            seen_messages.add(msg)
            filtered_commits.append(commit_to_process)
            print(f"Adding commit: [{commit_to_process.sha[:7]}] {msg.split('\n')[0]}")
        else:
            print(f"Skipping duplicate commit: [{commit_to_process.sha[:7]}] {msg.split('\n')[0]}")
    
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
            time_string
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
                
                current_category = 'General'
                for line in todo_lines:
                    if line.startswith('@'):
                        # keep the category marker
                        new_todos.append((False, line))
                        current_category = line[1:].strip()
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
            
            print(f"\n=== Final Result ===")
            print(f"Total TODOs: {len(all_todos)} items")
            
            # Create updated body
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

{create_todo_section(all_todos)}'''
            
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
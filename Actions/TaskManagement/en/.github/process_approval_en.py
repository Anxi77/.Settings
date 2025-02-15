import os
from github import Github
from datetime import datetime
import re

# Task category definitions
TASK_CATEGORIES = {
    "🔧 Development": {
        "emoji": "🔧",
        "name": "Development",
        "description": "Core functionality implementation and development tasks"
    },
    "🎨 UI/UX": {
        "emoji": "🎨",
        "name": "UI/UX",
        "description": "User interface and experience related tasks"
    },
    "🔍 QA/Testing": {
        "emoji": "🔍",
        "name": "QA/Testing",
        "description": "Quality assurance and testing related tasks"
    },
    "📚 Documentation": {
        "emoji": "📚",
        "name": "Documentation",
        "description": "Documentation writing and management tasks"
    },
    "🛠️ Maintenance": {
        "emoji": "🛠️",
        "name": "Maintenance",
        "description": "Bug fixes and performance improvement tasks"
    }
}

def find_report_issue(repo, project_name):
    """Finds the project's report issue."""
    report_title = f"[{project_name}] Project Progress Report"
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if issue.title == report_title:
            return issue
    return None

def get_assignees_string(issue):
    """Returns a string of assignees from the issue."""
    return ', '.join([assignee.login for assignee in issue.assignees]) if issue.assignees else 'TBD'

def get_task_duration(task_issue):
    """Calculates the expected duration of the task."""
    body_lines = task_issue.body.split('\n')
    total_days = 0
    
    # Parse Mermaid gantt chart
    in_gantt = False
    for line in body_lines:
        line = line.strip()
        if 'gantt' in line:
            in_gantt = True
            continue
        if in_gantt and line and not line.startswith('```') and not line.startswith('title') and not line.startswith('dateFormat') and not line.startswith('section'):
            # Parse task line (e.g., "Design draft :2024-02-15, 3d")
            if ':' in line and 'd' in line:
                duration = line.split(',')[-1].strip()
                if duration.endswith('d'):
                    days = int(duration[:-1])
                    total_days += days
    
    return f"{total_days}d"

def parse_time_spent(todo_text):
    """Extracts time spent from a TODO item."""
    spent_match = re.search(r'\(spent:\s*(\d+)h\)', todo_text)
    if spent_match:
        return f"{spent_match.group(1)}h"
    return None

def update_task_status(repo, task_number, todo_text):
    """Updates the task status in the report."""
    # Find report issue
    project_name = repo.name
    report_issue = find_report_issue(repo, project_name)
    if not report_issue:
        return
        
    # Extract time spent
    spent_time = parse_time_spent(todo_text)
    if not spent_time:
        return
        
    # Update report content
    body = report_issue.body
    task_pattern = rf"\|\s*\[TSK-{task_number}\].*?\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|\s*-\s*\|\s*🟡\s*In Progress\s*\|\s*-\s*\|"
    
    def replace_task(match):
        return match.group(0).replace("| - | 🟡 In Progress |", f"| {spent_time} | ✅ Completed |")
    
    updated_body = re.sub(task_pattern, replace_task, body)
    if updated_body != body:
        report_issue.edit(body=updated_body)
        report_issue.create_comment(f"✅ Task TSK-{task_number} has been completed. (Time spent: {spent_time})")

def process_todo_completion(repo, todo_text):
    """Processes a completed TODO item."""
    # Extract TSK number
    task_match = re.search(r'\[TSK-(\d+)\]', todo_text)
    if not task_match:
        return
        
    task_number = task_match.group(1)
    update_task_status(repo, task_number, todo_text)

def create_task_entry(task_issue):
    """Creates a task entry for the report."""
    assignees = get_assignees_string(task_issue)
    title_parts = task_issue.title.strip('[]').split('] ')
    task_name = title_parts[1]
    issue_url = task_issue.html_url
    expected_time = get_task_duration(task_issue)
    return f"| [TSK-{task_issue.number}]({issue_url}) | {task_name} | {assignees} | {expected_time} | - | 🟡 In Progress | - |"

def get_category_from_labels(issue_labels):
    """Determines the task category based on issue labels."""
    for label in issue_labels:
        category_key = label.name
        if category_key in TASK_CATEGORIES:
            return category_key
    return "🔧 Development"  # Default category

def create_category_sections():
    """Creates all category sections."""
    sections = []
    for category_key, category_info in TASK_CATEGORIES.items():
        section = f"""<details>
<summary><h3>{category_key}</h3></summary>

| Task ID | Task Name | Assignee | Expected Time | Actual Time | Status | Priority |
| ------- | --------- | -------- | ------------- | ----------- | ------ | -------- |

</details>"""
        sections.append(section)
    return "\n\n".join(sections)

def update_report_content(old_content, new_task_entry, category_key):
    """Updates the report content."""
    print(f"\n=== Updating Report Content ===")
    print(f"Category: {category_key}")
    
    # Find category section
    category_start = old_content.find(f"<h3>{category_key}</h3>")
    if category_start == -1:
        print("Category section not found.")
        return old_content
    
    # Find category table
    table_header = "| Task ID | Task Name | Assignee | Expected Time | Actual Time | Status | Priority |"
    header_pos = old_content.find(table_header, category_start)
    if header_pos == -1:
        print("Table header not found.")
        return old_content
    
    # Find table end
    table_end = old_content.find("</details>", header_pos)
    if table_end == -1:
        print("Table end not found.")
        return old_content
    
    # Get current table content
    table_content = old_content[header_pos:table_end].strip()
    print("\nCurrent table content:")
    print(table_content)
    
    # Split table into lines
    lines = table_content.split('\n')
    
    # Check if task already exists
    task_number = re.search(r'TSK-(\d+)', new_task_entry).group(1)
    task_exists = False
    
    print(f"\nChecking task TSK-{task_number}...")
    
    for i, line in enumerate(lines):
        if f"TSK-{task_number}" in line:
            print(f"Existing task found: {line}")
            task_exists = True
            lines[i] = new_task_entry  # Update existing entry
            break
    
    if not task_exists:
        print("Adding new task")
        if len(lines) > 2:  # If header and separator exist
            lines.append(new_task_entry)
        else:  # First entry
            lines = [table_header, "| ------- | --------- | -------- | ------------- | ----------- | ------ | -------- |", new_task_entry]
    
    # Create new table
    new_table = '\n'.join(lines)
    print("\nUpdated table:")
    print(new_table)
    
    # Return updated content
    updated_content = f"{old_content[:header_pos]}{new_table}\n\n{old_content[table_end:]}"
    return updated_content

def calculate_progress_stats(body):
    """Calculates task progress statistics from report content."""
    print("\n=== Calculating Progress Stats ===")
    completed = 0
    in_progress = 0
    total = 0
    
    # Check all task statuses
    for line in body.split('\n'):
        if '| TSK-' in line or '|[TSK-' in line:
            total += 1
            if '✅ Completed' in line:
                completed += 1
            elif '🟡 In Progress' in line:
                in_progress += 1
    
    print(f"Completed: {completed}, In Progress: {in_progress}, Total: {total}")
    return completed, in_progress, total

def create_progress_section(completed, in_progress, total):
    """Creates the progress section."""
    if total == 0:
        return """### Overall Progress

```mermaid
pie title Task Progress Status
    "In Progress" : 0
    "Completed" : 0
```"""
    
    completed_percent = (completed / total) * 100
    in_progress_percent = (in_progress / total) * 100
    
    return f"""### Overall Progress

Progress Status: {completed}/{total} completed ({completed_percent:.1f}%)

```mermaid
pie title Task Progress Status
    "Completed" : {completed_percent}
    "In Progress" : {in_progress_percent}
```"""

def update_progress_section(body):
    """Updates the progress section in the report."""
    print("\n=== Updating Progress Section ===")
    
    # Calculate progress stats
    completed, in_progress, total = calculate_progress_stats(body)
    
    # Create new progress section
    new_progress_section = create_progress_section(completed, in_progress, total)
    
    # Update progress section
    progress_start = body.find("### Overall Progress")
    if progress_start == -1:
        print("Progress section not found.")
        return body
        
    progress_end = body.find("## 📝 Issues", progress_start)
    if progress_end == -1:
        print("Next section not found.")
        return body
    
    return f"{body[:progress_start]}{new_progress_section}\n\n{body[progress_end:]}"

def create_report_body(project_name):
    """Creates the project report template."""
    # Create category sections
    category_sections = create_category_sections()
    
    # Create initial progress section
    initial_progress = create_progress_section(0, 0, 0)
    
    return f"""<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=Project%20Report&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=Project%20Progress%20Report&descSize=25&descAlignY=75)

# 📊 Project Progress Report

</div>

## 📌 Basic Information

**Project Name**: {project_name}  
**Report Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Report Period**: {datetime.now().strftime('%Y-%m-%d')} ~ Ongoing

## 📋 Task Details

{category_sections}

## 📊 Progress Summary

{initial_progress}

## 📝 Issues and Risks

| Type | Content | Mitigation Plan |
| ---- | ------- | --------------- |
| - | - | - |

## 📈 Next Steps

1. Initial Setup and Environment Configuration
2. Define Detailed Work Items
3. Regular Progress Updates

---
> This report is automatically generated and will be continuously updated by the assignee.
"""

def sanitize_project_name(name):
    """Removes special characters from project name and converts to proper format."""
    print(f"\n=== Sanitizing Project Name ===")
    print(f"Original name: {name}")
    
    # Remove leading dots
    while name.startswith('.'):
        name = name[1:]
    
    # Convert special characters to spaces
    sanitized = re.sub(r'[^\w\s-]', ' ', name)
    
    # Convert multiple spaces to single space and trim
    sanitized = ' '.join(sanitized.split())
    
    print(f"Sanitized name: {sanitized}")
    return sanitized

def find_daily_log_issue(repo, project_name):
    """Finds the most recent Daily Log issue."""
    project_name = sanitize_project_name(project_name)  # Sanitize project name
    print(f"\n=== Searching Daily Log Issue ===")
    print(f"Project name: {project_name}")
    
    daily_issues = repo.get_issues(state='open', labels=['daily-log'])
    for issue in daily_issues:
        print(f"Checking issue: {issue.title}")
        # Compare project name from issue title
        issue_parts = issue.title.split(' - ')
        if len(issue_parts) == 2:
            issue_project = sanitize_project_name(issue_parts[1])
            if issue_project == project_name:
                print(f"Daily log issue found: #{issue.number}")
                return issue
            
    print("Daily log issue not found.")
    return None

def create_task_todo(task_issue):
    """Creates a TODO item for task start."""
    title_parts = task_issue.title.strip('[]').split('] ')
    task_name = title_parts[1]
    category_key = get_category_from_labels(task_issue.labels)
    
    print(f"\n=== Creating TODO Item ===")
    print(f"Task name: {task_name}")
    print(f"Category: {category_key}")
    
    # Create category header and task item
    todo_text = f"""@{TASK_CATEGORIES[category_key]['name']}
- [ ] #{task_issue.number}"""
    print(f"Generated TODO text:\n{todo_text}")
    return todo_text

def parse_existing_issue(body):
    """Parses existing TODO items from issue body."""
    print(f"\n=== Parsing Issue Body ===")
    todos = []
    in_todo_section = False
    
    for line in body.split('\n'):
        if '## 📝 Todo' in line:
            print("TODO section start")
            in_todo_section = True
            continue
        elif in_todo_section and line.strip() and line.startswith('##'):
            print("TODO section end")
            break
        elif in_todo_section and line.strip():
            if line.startswith('- [ ]'):
                todos.append((False, line[6:].strip()))
                print(f"Incomplete TODO added: {line[6:].strip()}")
            elif line.startswith('- [x]'):
                todos.append((True, line[6:].strip()))
                print(f"Completed TODO added: {line[6:].strip()}")
            elif line.startswith('@'):
                todos.append((None, line.strip()))
                print(f"Category added: {line.strip()}")
    
    print(f"Total {len(todos)} TODO items found.")
    return {
        'todos': todos
    }

def merge_todos(existing_todos, new_todos):
    """Merges existing and new TODO items."""
    print(f"\n=== Merging TODO Items ===")
    print(f"Existing TODO count: {len(existing_todos)}")
    print(f"New TODO count: {len(new_todos)}")
    
    all_todos = existing_todos.copy()
    
    # Add new TODO items
    for completed, text in new_todos:
        if text.startswith('@'):
            # Add category header without duplicates
            if text not in [t[1] for t in all_todos]:
                all_todos.append((None, text))
                print(f"New category added: {text}")
        else:
            # Add regular TODO items after duplicate check
            if text not in [t[1] for t in all_todos]:
                all_todos.append((completed, text))
                print(f"New TODO item added: {text}")
            else:
                print(f"Duplicate TODO item ignored: {text}")
    
    print(f"Total TODO items after merge: {len(all_todos)}")
    return all_todos

def create_todo_section(todos):
    """Creates the TODO section."""
    print(f"\n=== Creating TODO Section ===")
    
    # Group TODO items by category
    categories = {}
    current_category = "General"
    uncategorized_todos = []
    
    for completed, text in todos:
        print(f"Processing item: {text}")
        if completed is None and text.startswith('@'):
            current_category = text[1:]  # Remove @
            print(f"New category start: {current_category}")
            continue
            
        # Clean up items that already have checkbox format
        if text.startswith('- [ ]') or text.startswith('- [x]'):
            text = text.replace('- [ ]', '').replace('- [x]', '').strip()
            
        if current_category not in categories:
            categories[current_category] = []
            
        categories[current_category].append((completed, text))
        print(f"Item added to '{current_category}' category: {text}")
    
    # Create category sections
    sections = []
    for category, category_todos in categories.items():
        if not category_todos:  # Skip empty categories
            continue
            
        completed_count = sum(1 for completed, _ in category_todos if completed)
        total_count = len(category_todos)
        
        section = f"""<details>
<summary><h3 style="display: inline;">📑 {category} ({completed_count}/{total_count})</h3></summary>

"""
        # Add TODO items
        for completed, text in category_todos:
            checkbox = '[x]' if completed else '[ ]'
            if text.startswith('#'):  # Task reference
                section += f"- {checkbox} {text}\n"
            else:
                section += f"- {checkbox} {text}\n"
        
        section += "\n⚫\n</details>\n"
        sections.append(section)
    
    result = '\n'.join(sections)
    print(f"\nGenerated TODO section:\n{result}")
    return result

def process_approval(issue, repo):
    """Processes issue approval based on labels."""
    print(f"\n=== Starting Approval Process ===")
    print(f"Issue number: #{issue.number}")
    print(f"Issue title: {issue.title}")
    
    labels = [label.name for label in issue.labels]
    print(f"Issue labels: {labels}")
    
    # Extract project name and task name from title
    title_parts = issue.title.strip('[]').split('] ')
    project_name = repo.name  # Use repository name as project name
    print(f"Project name: {project_name}")
    
    if '✅ Approved' in labels:
        print("\nStarting approval process")
        # Determine task category
        category_key = get_category_from_labels(issue.labels)
        print(f"Task category: {category_key}")
        
        # Find existing report issue
        report_issue = find_report_issue(repo, project_name)
        
        if report_issue:
            print(f"\nReport issue found: #{report_issue.number}")
            # Update existing report
            task_entry = create_task_entry(issue)
            print(f"Generated task entry:\n{task_entry}")
            
            # Update task entry
            updated_body = update_report_content(report_issue.body, task_entry, category_key)
            
            # Update progress section
            updated_body = update_progress_section(updated_body)
            
            report_issue.edit(body=updated_body)
            report_issue.create_comment(f"✅ Task #{issue.number} has been added to the {category_key} category.")
            print("Report update completed")
            
            # Find and update Daily Log issue
            daily_issue = find_daily_log_issue(repo, project_name)
            if daily_issue:
                print(f"\nDaily log issue found: #{daily_issue.number}")
                # Create TODO item
                todo_text = create_task_todo(issue)
                
                # Parse current issue body
                existing_content = parse_existing_issue(daily_issue.body)
                
                # Add new TODO items
                new_todos = [(False, line) for line in todo_text.split('\n')]
                all_todos = merge_todos(existing_content['todos'], new_todos)
                
                # Update TODO section
                todo_section = create_todo_section(all_todos)
                
                # Update issue body
                print("\nStarting issue body update")
                body_parts = daily_issue.body.split('## 📝 Todo')
                updated_body = f"{body_parts[0]}## 📝 Todo\n\n{todo_section}"
                
                daily_issue.edit(body=updated_body)
                daily_issue.create_comment(f"New task has been added:\n\n{todo_text}")
                print("Daily log update completed")
            else:
                print(f"Today's Daily Log issue not found: {datetime.now().strftime('%Y-%m-%d')}")
        else:
            # Create new report issue
            report_body = create_report_body(project_name)
            report_issue = repo.create_issue(
                title=f"[{project_name}] Project Progress Report",
                body=report_body,
                labels=['📊 In Progress']
            )
            # Add first task
            task_entry = create_task_entry(issue)
            updated_body = update_report_content(report_body, task_entry, category_key)
            report_issue.edit(body=updated_body)
        
        # Add approval message
        issue.create_comment("✅ Task has been approved and added to the report.")
        
    elif '❌ Rejected' in labels:
        issue.create_comment("❌ Task has been rejected. Please revise and resubmit.")
        
    elif '⏸️ On Hold' in labels:
        issue.create_comment("⏸️ Task has been put on hold. Further discussion needed.")

def main():
    # Initialize GitHub client
    github_token = os.getenv('GITHUB_TOKEN')
    github = Github(github_token)
    
    # Get repository information
    repo_name = os.getenv('GITHUB_REPOSITORY')
    repo = github.get_repo(repo_name)
    
    # Get event information
    event_name = os.getenv('GITHUB_EVENT_NAME')
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if event_name == 'issues':
        # Get issue number
        with open(event_path, 'r') as f:
            import json
            event_data = json.load(f)
            issue_number = event_data['issue']['number']
            
            # Process issue
            issue = repo.get_issue(issue_number)
            
            # Process TODO completion for Daily Log
            if 'daily-log' in [label.name for label in issue.labels]:
                body = issue.body
                for line in body.split('\n'):
                    if '[x]' in line and 'TSK-' in line and 'spent:' in line:
                        process_todo_completion(repo, line)
            else:
                process_approval(issue, repo)

if __name__ == '__main__':
    main() 
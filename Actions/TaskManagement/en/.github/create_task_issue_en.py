import os
from github import Github
from pathlib import Path
import re

def convert_schedule_to_mermaid(schedule_data):
    """Converts CSV format schedule data to Mermaid gantt chart format."""
    tasks = []
    for line in schedule_data.split('\n'):
        if line.strip():
            task, date, duration = [part.strip() for part in line.split(',')]
            tasks.append(f"    {task} :{date}, {duration}")
    return '\n'.join(tasks)

def read_csv_data(file_path):
    """Reads task data from CSV file."""
    data = {}
    current_section = None
    section_content = []
    
    # Try different encodings
    encodings = ['utf-8', 'euc-kr']
    
    for encoding in encodings:
        try:
            print(f"\n=== Attempting to read CSV file ({encoding}) ===")
            print(f"File path: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                
            print(f"File read successful (encoding: {encoding})")
            
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                if line.startswith('[') and line.endswith(']'):  # New section start
                    if current_section and section_content:
                        data[current_section] = '\n'.join(section_content)
                        section_content = []
                    current_section = line
                    print(f"New section found: {current_section}")
                    continue
                    
                if current_section:  # Collect section content
                    section_content.append(line)
                    print(f"Section content added: {line[:50]}...")
                else:  # Process header information
                    if ',' in line:
                        key, value = line.split(',', 1)
                        data[key] = value.strip()
                        print(f"Header info added: {key} = {value.strip()}")
                
            # Process last section
            if current_section and section_content:
                data[current_section] = '\n'.join(section_content)
                
            print(f"\nTotal {len(data)} sections read.")
            return data
            
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding")
            continue
    
    # All encoding attempts failed
    raise UnicodeDecodeError(f"Could not read file with supported encodings ({', '.join(encodings)})")

def create_issue_body(data, project_name):
    """Creates issue body in task proposal template format."""
    # Convert schedule data to Mermaid format
    schedule_mermaid = convert_schedule_to_mermaid(data['[Schedule]'])
    
    body = f"""# Project Task Proposal

## 1. Proposal Overview

**Project Name**: {project_name}  
**Task Name**: {data['[Task Name]']}  
**Proposer**: {data['Proposer']}  
**Proposal Date**: {data['Proposal Date']}  
**Target Date**: {data['Target Date']}

## 2. Task Summary

### 2.1 Purpose

{data['[Task Purpose]']}

### 2.2 Scope

{data['[Task Scope]']}

## 3. Details

### Required Features

{data['[Required Features]']}

### Optional Features

{data['[Optional Features]']}

## 4. Approval Process

Please add one of the following labels to approve this task:
- `✅ Approved`: Task is approved and ready to start.
- `❌ Rejected`: Task is rejected and needs revision.
- `⏸️ On Hold`: Task is on hold and needs further discussion.

## 5. Schedule

```mermaid
gantt
    title Task Implementation Schedule
    dateFormat YYYY-MM-DD
    section Development
{schedule_mermaid}
```
"""
    return body

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

def main():
    # Initialize GitHub client
    github_token = os.getenv('GITHUB_TOKEN')
    github = Github(github_token)
    
    # Get repository information
    repo_name = os.getenv('GITHUB_REPOSITORY')
    repo = github.get_repo(repo_name)
    project_name = sanitize_project_name(repo.name)  # Clean repository name
    
    print(f"\n=== Repository Information ===")
    print(f"Original repository name: {repo.name}")
    print(f"Cleaned project name: {project_name}")
    
    # Find CSV files
    csv_dir = Path('TaskProposals')
    print(f"\n=== Searching CSV Files ===")
    print(f"Search directory: {csv_dir.absolute()}")
    
    for csv_file in csv_dir.glob('*.csv'):
        if csv_file.is_file():
            print(f"\nFound CSV file: {csv_file}")
            # Read CSV data
            data = read_csv_data(csv_file)
            
            # Create issue
            issue_title = f"[{project_name}] {data['[Task Name]']}"
            print(f"Creating issue with title: {issue_title}")
            
            issue_body = create_issue_body(data, project_name)
            
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=['⌛ Pending Review']
            )
            print(f"Issue created: #{issue.number}")
            
            # Remove processed CSV file
            os.remove(csv_file)
            print(f"CSV file deleted: {csv_file}")

if __name__ == '__main__':
    main() 
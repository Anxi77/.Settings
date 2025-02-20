import os
import json
from github import Github

def process_task_and_todo():
    github_token = os.environ["GITHUB_TOKEN"]
    g = Github(github_token)
    
    # GitHub 컨텍스트 정보 가져오기
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
    project_name = repo.name
    
    if "issue" in event:
        issue = event["issue"]
        
        # 태스크 라벨 확인
        if any(label["name"].startswith("task:") for label in issue["labels"]):
            process_task(repo, issue, project_name)
        
        # Todo 라벨 확인
        if any(label["name"] == "todo" for label in issue["labels"]):
            process_todo(repo, issue)

def process_task(repo, issue, project_name):
    """태스크 이슈 처리"""
    # 태스크 프로젝트 칼럼에 추가
    project = get_or_create_project(repo, project_name)
    task_column = get_column_by_name(project, "Tasks")
    
    # 이슈를 프로젝트 칼럼에 추가
    if task_column:
        task_column.create_card(content_id=issue["id"], content_type="Issue")

def process_todo(repo, issue):
    """Todo 이슈 처리"""
    # 관련된 태스크 찾기
    body = issue["body"]
    task_references = [line for line in body.split("\n") if "task:" in line.lower()]
    
    for ref in task_references:
        task_number = extract_task_number(ref)
        if task_number:
            link_todo_to_task(repo, issue["number"], task_number)

def get_or_create_project(repo, name):
    """프로젝트 보드 가져오기 또는 생성"""
    for project in repo.get_projects():
        if project.name == name:
            return project
    return repo.create_project(name, body="Task and Todo Tracking")

def get_column_by_name(project, name):
    """프로젝트 칼럼 가져오기"""
    for column in project.get_columns():
        if column.name == name:
            return column
    return project.create_column(name)

def extract_task_number(text):
    """태스크 번호 추출"""
    import re
    match = re.search(r"#(\d+)", text)
    return int(match.group(1)) if match else None

def link_todo_to_task(repo, todo_number, task_number):
    """Todo를 태스크에 연결"""
    todo_issue = repo.get_issue(todo_number)
    task_issue = repo.get_issue(task_number)
    
    # Todo 이슈에 태스크 참조 추가
    todo_issue.create_comment(f"Linked to task #{task_number}")
    
    # 태스크 이슈에 Todo 참조 추가
    task_issue.create_comment(f"Todo #{todo_number} has been linked to this task")

if __name__ == "__main__":
    process_task_and_todo() 
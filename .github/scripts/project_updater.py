import os
import json
from github import Github

def update_project_board():
    github_token = os.environ["GITHUB_TOKEN"]
    g = Github(github_token)
    
    # GitHub 컨텍스트 정보 가져오기
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
    project_name = repo.name
    project = get_project(repo, project_name)
    
    if not project:
        return
    
    # 프로젝트 칼럼 구성
    columns = {
        "To Do": get_or_create_column(project, "To Do"),
        "In Progress": get_or_create_column(project, "In Progress"),
        "Done": get_or_create_column(project, "Done")
    }
    
    # 카드 이동 이벤트 처리
    if "project_card" in event:
        handle_card_movement(event["project_card"], columns, repo)
    
    # 이슈 상태 변경 처리
    if "issue" in event:
        handle_issue_status(event["issue"], columns)

def get_project(repo, name):
    """프로젝트 가져오기"""
    for project in repo.get_projects():
        if project.name == name:
            return project
    return None

def get_or_create_column(project, name):
    """칼럼 가져오기 또는 생성"""
    for column in project.get_columns():
        if column.name == name:
            return column
    return project.create_column(name)

def handle_card_movement(card_event, columns, repo):
    """카드 이동 처리"""
    if card_event["column_id"]:
        # 카드가 이동된 경우 관련 이슈 상태 업데이트
        issue = get_issue_from_card(card_event, repo)
        if issue:
            update_issue_status(issue, card_event["column_id"], columns)

def handle_issue_status(issue, columns):
    """이슈 상태 변경 처리"""
    # 이슈 라벨에 따라 적절한 칼럼으로 이동
    if any(label["name"] == "done" for label in issue["labels"]):
        move_to_column(issue, columns["Done"])
    elif any(label["name"] == "in-progress" for label in issue["labels"]):
        move_to_column(issue, columns["In Progress"])
    else:
        move_to_column(issue, columns["To Do"])

def get_issue_from_card(card, repo):
    """카드에서 이슈 정보 추출"""
    if "content_url" in card:
        issue_url = card["content_url"]
        issue_number = int(issue_url.split("/")[-1])
        return repo.get_issue(issue_number)
    return None

def move_to_column(issue, column):
    """이슈를 지정된 칼럼으로 이동"""
    for card in column.get_cards():
        if card.content_url == issue.url:
            return
    column.create_card(content_id=issue.id, content_type="Issue")

def update_issue_status(issue, column_id, columns):
    """이슈 상태 업데이트"""
    status_labels = {
        columns["To Do"].id: "todo",
        columns["In Progress"].id: "in-progress",
        columns["Done"].id: "done"
    }
    
    if column_id in status_labels:
        # 기존 상태 라벨 제거
        for label in issue.labels:
            if label.name in status_labels.values():
                issue.remove_from_labels(label.name)
        
        # 새 상태 라벨 추가
        issue.add_to_labels(status_labels[column_id])

if __name__ == "__main__":
    update_project_board() 
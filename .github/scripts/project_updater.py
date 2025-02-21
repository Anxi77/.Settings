import os
import json
import logging
from github import Github

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def update_project_board():
    logger.info("Starting project board update")
    github_token = os.environ["GITHUB_TOKEN"]
    g = Github(github_token)
    
    logger.debug("Reading GitHub event data")
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    logger.debug(f"Event data: {json.dumps(event, indent=2)}")
    
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
    project_name = repo.name
    logger.info(f"Looking for project: {project_name}")
    project = get_project(repo, project_name)
    
    if not project:
        logger.warning(f"Project '{project_name}' not found")
        return
    
    logger.info("Setting up project columns")
    columns = {
        "To Do": get_or_create_column(project, "To Do"),
        "In Progress": get_or_create_column(project, "In Progress"),
        "Done": get_or_create_column(project, "Done")
    }
    
    event_type = os.environ["GITHUB_EVENT_NAME"]
    logger.info(f"Processing event type: {event_type}")
    
    if event_type == "push":
        if "commits" in event:
            latest_commit = event["commits"][-1]
            logger.info(f"Processing latest commit: {latest_commit['id']}")
            handle_commit_todos(latest_commit, columns, repo)
    elif "project_card" in event:
        logger.info("Processing project card movement")
        handle_card_movement(event["project_card"], columns, repo)
    elif "issue" in event:
        logger.info("Processing issue status change")
        handle_issue_status(event["issue"], columns)
    else:
        logger.warning(f"Unhandled event type: {event_type}")

def handle_commit_todos(commit, columns, repo):
    logger.info(f"Processing TODOs from commit: {commit['id']}")
    message = commit["message"]
    todo_section = ""
    is_todo = False
    
    for line in message.split("\n"):
        if line.strip().lower() == "[todo]":
            is_todo = True
            logger.debug("Found [TODO] marker")
            continue
        if is_todo:
            todo_section += line + "\n"
    
    if not todo_section:
        logger.debug("No TODOs found in commit message")
        return
    
    logger.info("Processing TODO items")
    for line in todo_section.split("\n"):
        line = line.strip()
        if line.startswith("-"):
            todo_text = line[1:].strip()
            logger.debug(f"Processing TODO item: {todo_text}")
            if todo_text.startswith("(issue)"):
                todo_text = todo_text[7:].strip()
                logger.info(f"Creating issue for TODO: {todo_text}")
                issue = repo.create_issue(
                    title=todo_text,
                    body=f"Created from commit {commit['id'][:7]}\n\nOriginal TODO item: {todo_text}",
                    labels=["todo"]
                )
                logger.info(f"Created issue #{issue.number}")
                columns["To Do"].create_card(content_id=issue.id, content_type="Issue")
                logger.info(f"Added card for issue #{issue.number} to To Do column")

def get_project(repo, name):
    """프로젝트 가져오기"""
    logger.info(f"Searching for project: {name}")
    for project in repo.get_projects():
        if project.name == name:
            logger.info(f"Found project: {name}")
            return project
    logger.warning(f"Project not found: {name}")
    return None

def get_or_create_column(project, name):
    """칼럼 가져오기 또는 생성"""
    logger.debug(f"Looking for column: {name}")
    for column in project.get_columns():
        if column.name == name:
            logger.debug(f"Found existing column: {name}")
            return column
    logger.info(f"Creating new column: {name}")
    return project.create_column(name)

def handle_card_movement(card_event, columns, repo):
    """카드 이동 처리"""
    logger.info(f"Processing card movement event: {card_event['id']}")
    if card_event["column_id"]:
        logger.debug(f"Card moved to column ID: {card_event['column_id']}")
        issue = get_issue_from_card(card_event, repo)
        if issue:
            logger.info(f"Updating status for issue #{issue.number}")
            update_issue_status(issue, card_event["column_id"], columns)
        else:
            logger.debug("No associated issue found for card")

def handle_issue_status(issue, columns):
    """이슈 상태 변경 처리"""
    logger.info(f"Processing issue status: #{issue['number']}")
    if any(label["name"] == "done" for label in issue["labels"]):
        logger.info("Moving issue to Done column")
        move_to_column(issue, columns["Done"])
    elif any(label["name"] == "in-progress" for label in issue["labels"]):
        logger.info("Moving issue to In Progress column")
        move_to_column(issue, columns["In Progress"])
    else:
        logger.info("Moving issue to To Do column")
        move_to_column(issue, columns["To Do"])

def get_issue_from_card(card, repo):
    """카드에서 이슈 정보 추출"""
    logger.debug(f"Extracting issue from card: {card['id']}")
    if "content_url" in card:
        issue_url = card["content_url"]
        issue_number = int(issue_url.split("/")[-1])
        logger.debug(f"Found issue #{issue_number}")
        return repo.get_issue(issue_number)
    logger.debug("No content URL found in card")
    return None

def move_to_column(issue, column):
    """이슈를 지정된 칼럼으로 이동"""
    logger.info(f"Moving issue #{issue.number} to column: {column.name}")
    for card in column.get_cards():
        if card.content_url == issue.url:
            logger.debug("Issue already in target column")
            return
    column.create_card(content_id=issue.id, content_type="Issue")
    logger.info(f"Created new card for issue #{issue.number} in column {column.name}")

def update_issue_status(issue, column_id, columns):
    """이슈 상태 업데이트"""
    logger.info(f"Updating status for issue #{issue.number}")
    status_labels = {
        columns["To Do"].id: "todo",
        columns["In Progress"].id: "in-progress",
        columns["Done"].id: "done"
    }
    
    if column_id in status_labels:
        logger.debug(f"Updating labels for column ID: {column_id}")
        for label in issue.labels:
            if label.name in status_labels.values():
                logger.debug(f"Removing label: {label.name}")
                issue.remove_from_labels(label.name)
        
        new_label = status_labels[column_id]
        logger.debug(f"Adding new label: {new_label}")
        issue.add_to_labels(new_label)
    else:
        logger.warning(f"Unknown column ID: {column_id}")

if __name__ == "__main__":
    update_project_board() 
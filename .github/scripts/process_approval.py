import os
from github import Github
from datetime import datetime

# 태스크 카테고리 정의
TASK_CATEGORIES = {
    "🔧 기능 개발": {
        "emoji": "🔧",
        "name": "기능 개발",
        "description": "핵심 기능 구현 및 개발 관련 태스크"
    },
    "🎨 UI/UX": {
        "emoji": "🎨",
        "name": "UI/UX",
        "description": "사용자 인터페이스 및 경험 관련 태스크"
    },
    "🔍 QA/테스트": {
        "emoji": "🔍",
        "name": "QA/테스트",
        "description": "품질 보증 및 테스트 관련 태스크"
    },
    "📚 문서화": {
        "emoji": "📚",
        "name": "문서화",
        "description": "문서 작성 및 관리 관련 태스크"
    },
    "🛠️ 유지보수": {
        "emoji": "🛠️",
        "name": "유지보수",
        "description": "버그 수정 및 성능 개선 관련 태스크"
    }
}

def find_report_issue(repo, project_name):
    """프로젝트의 보고서 이슈를 찾습니다."""
    report_title = f"[{project_name}] 프로젝트 진행보고서"
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if issue.title == report_title:
            return issue
    return None

def get_assignees_string(issue):
    """이슈의 담당자 목록을 문자열로 반환합니다."""
    return ', '.join([assignee.login for assignee in issue.assignees]) if issue.assignees else 'TBD'

def create_task_entry(task_issue):
    """태스크 항목을 생성합니다."""
    assignees = get_assignees_string(task_issue)
    title_parts = task_issue.title.strip('[]').split('] ')
    task_name = title_parts[1]
    return f"| TSK-{task_issue.number} | {task_name} | {assignees} | - | - | 🟡 진행중 | - |"

def get_category_from_labels(issue_labels):
    """이슈의 라벨을 기반으로 카테고리를 결정합니다."""
    for label in issue_labels:
        category_key = label.name
        if category_key in TASK_CATEGORIES:
            return category_key
    return "🔧 기능 개발"  # 기본 카테고리

def create_category_sections():
    """모든 카테고리 섹션을 생성합니다."""
    sections = []
    for category_key, category_info in TASK_CATEGORIES.items():
        section = f"""<details>
<summary><h3>{category_key}</h3></summary>

| 태스크 ID | 태스크명 | 담당자 | 예상 시간 | 실제 시간 | 진행 상태 | 우선순위 |
| --------- | -------- | ------ | --------- | --------- | --------- | -------- |

</details>"""
        sections.append(section)
    return "\n\n".join(sections)

def update_report_content(old_content, new_task_entry, category_key):
    """보고서 내용을 업데이트합니다."""
    # 카테고리 섹션 찾기
    category_start = old_content.find(f"<h3>{category_key}</h3>")
    if category_start == -1:
        return old_content
    
    # 해당 카테고리의 테이블 찾기
    table_header = "| 태스크 ID | 태스크명 | 담당자 | 예상 시간 | 실제 시간 | 진행 상태 | 우선순위 |"
    header_pos = old_content.find(table_header, category_start)
    if header_pos == -1:
        return old_content
    
    # 테이블 끝 찾기
    table_end = old_content.find("</details>", header_pos)
    if table_end == -1:
        return old_content
    
    # 새 태스크 항목 추가
    table_content = old_content[header_pos:table_end].strip()
    if "| TSK-" in table_content:  # 기존 항목이 있는 경우
        new_table = f"{table_content}\\n{new_task_entry}"
    else:  # 첫 항목인 경우
        new_table = f"{table_header}\\n| --------- | -------- | ------ | --------- | --------- | --------- | -------- |\\n{new_task_entry}"
    
    return old_content[:header_pos] + new_table + old_content[table_end:]

def create_report_body(project_name):
    """프로젝트 보고서 템플릿을 생성합니다."""
    return f"""<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=Project%20Report&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=프로젝트%20진행%20보고서&descSize=25&descAlignY=75)

# 📊 프로젝트 진행 보고서

</div>

## 📌 기본 정보

**프로젝트명**: {project_name}  
**보고서 작성일**: {datetime.now().strftime('%Y-%m-%d')}  
**보고 기간**: {datetime.now().strftime('%Y-%m-%d')} ~ 진행중

## 📋 태스크 상세 내역

{create_category_sections()}

## 📊 진행 현황 요약

### 전체 진행률

```mermaid
pie title 태스크 진행 상태
    "진행중" : 100
```

## 📝 특이사항 및 리스크

| 구분 | 내용 | 대응 방안 |
| ---- | ---- | --------- |
| - | - | - |

## 📈 다음 단계 계획

1. 초기 설정 및 환경 구성
2. 세부 작업 항목 정의
3. 진행 상황 정기 업데이트

---
> 이 보고서는 자동으로 생성되었으며, 담당자가 지속적으로 업데이트할 예정입니다.
"""

def process_approval(issue, repo):
    """이슈의 라벨에 따라 승인 처리를 수행합니다."""
    labels = [label.name for label in issue.labels]
    
    # 제목에서 프로젝트명과 태스크명 추출
    title_parts = issue.title.strip('[]').split('] ')
    project_name = repo.name  # 리포지토리명을 프로젝트명으로 사용    project_name = repo.name  # 리포지토리명을 프로젝트명으로 사용
    
    if '✅ 승인완료' in labels:
        # 태스크 카테고리 결정
        category_key = get_category_from_labels(issue.labels)
        
        # 기존 보고서 이슈 찾기
        report_issue = find_report_issue(repo, project_name)
        
        if report_issue:
            # 기존 보고서 업데이트
            task_entry = create_task_entry(issue)
            updated_body = update_report_content(report_issue.body, task_entry, category_key)
            report_issue.edit(body=updated_body)
            report_issue.create_comment(f"✅ 태스크 #{issue.number}이 {category_key} 카테고리에 추가되었습니다.")
        else:
            # 새 보고서 이슈 생성
            report_body = create_report_body(project_name)
            report_issue = repo.create_issue(
                title=f"[{project_name}] 프로젝트 진행보고서",
                body=report_body,
                labels=['📊 진행중']
            )
            # 첫 태스크 추가
            task_entry = create_task_entry(issue)
            updated_body = update_report_content(report_body, task_entry, category_key)
            report_issue.edit(body=updated_body)
        
        # 제안서 이슈 닫기
        issue.create_comment("✅ 태스크가 승인되어 보고서로 전환되었습니다.")
        issue.edit(state='closed')
        
    elif '❌ 반려' in labels:
        issue.create_comment("❌ 태스크가 반려되었습니다. 수정 후 다시 제출해주세요.")
        
    elif '⏸️ 보류' in labels:
        issue.create_comment("⏸️ 태스크가 보류되었습니다. 추가 논의가 필요합니다.")

def main():
    # GitHub 클라이언트 초기화
    github_token = os.getenv('GITHUB_TOKEN')
    github = Github(github_token)
    
    # 저장소 정보 가져오기
    repo_name = os.getenv('GITHUB_REPOSITORY')
    repo = github.get_repo(repo_name)
    
    # 이벤트 정보 가져오기
    event_name = os.getenv('GITHUB_EVENT_NAME')
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if event_name == 'issues':
        # 이슈 번호 가져오기
        with open(event_path, 'r') as f:
            import json
            event_data = json.load(f)
            issue_number = event_data['issue']['number']
        
        # 이슈 처리
        issue = repo.get_issue(issue_number)
        process_approval(issue, repo)

if __name__ == '__main__':
    main() 
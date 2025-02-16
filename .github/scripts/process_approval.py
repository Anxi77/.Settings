import os
from github import Github
from datetime import datetime
import re
import json

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

def get_task_duration(task_issue):
    """태스크의 예상 시간을 계산합니다."""
    body_lines = task_issue.body.split('\n')
    total_days = 0
    
    # Mermaid 간트 차트 파싱
    in_gantt = False
    for line in body_lines:
        line = line.strip()
        if 'gantt' in line:
            in_gantt = True
            continue
        if in_gantt and line and not line.startswith('```') and not line.startswith('title') and not line.startswith('dateFormat') and not line.startswith('section'):
            # 태스크 라인 파싱 (예: "디자인 시안 작성 :2024-02-15, 3d")
            if ':' in line and 'd' in line:
                duration = line.split(',')[-1].strip()
                if duration.endswith('d'):
                    days = int(duration[:-1])
                    total_days += days
    
    return f"{total_days}d"

def parse_time_spent(todo_text):
    """TODO 항목에서 소요 시간을 추출합니다."""
    spent_match = re.search(r'\(spent:\s*(\d+)h\)', todo_text)
    if spent_match:
        return f"{spent_match.group(1)}h"
    return None

def update_task_status(repo, task_number, todo_text):
    """태스크 상태를 업데이트합니다."""
    # 보고서 이슈 찾기
    project_name = repo.name
    report_issue = find_report_issue(repo, project_name)
    if not report_issue:
        return
        
    # 소요 시간 추출
    spent_time = parse_time_spent(todo_text)
    if not spent_time:
        return
        
    # 보고서 내용 업데이트
    body = report_issue.body
    task_pattern = rf"\|\s*\[TSK-{task_number}\].*?\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|\s*-\s*\|\s*🟡\s*진행중\s*\|\s*-\s*\|"
    
    def replace_task(match):
        return match.group(0).replace("| - | 🟡 진행중 |", f"| {spent_time} | ✅ 완료 |")
    
    updated_body = re.sub(task_pattern, replace_task, body)
    if updated_body != body:
        report_issue.edit(body=updated_body)
        report_issue.create_comment(f"✅ TSK-{task_number} 태스크가 완료되었습니다. (소요 시간: {spent_time})")

def process_todo_completion(repo, todo_text):
    """완료된 TODO 항목을 처리합니다."""
    # TSK 번호 추출
    task_match = re.search(r'\[TSK-(\d+)\]', todo_text)
    if not task_match:
        return
        
    task_number = task_match.group(1)
    update_task_status(repo, task_number, todo_text)

def create_task_entry(task_issue):
    """태스크 항목을 생성합니다."""
    assignees = get_assignees_string(task_issue)
    title_parts = task_issue.title.strip('[]').split('] ')
    task_name = title_parts[1]
    issue_url = task_issue.html_url
    expected_time = get_task_duration(task_issue)
    return f"| [TSK-{task_issue.number}]({issue_url}) | {task_name} | {assignees} | {expected_time} | - | 🟡 진행중 | - |"

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
    print(f"\n=== 보고서 내용 업데이트 ===")
    print(f"카테고리: {category_key}")
    
    # 카테고리 섹션 찾기
    category_start = old_content.find(f"<h3>{category_key}</h3>")
    if category_start == -1:
        print("카테고리 섹션을 찾을 수 없습니다.")
        return old_content
    
    # 해당 카테고리의 테이블 찾기
    table_header = "| 태스크 ID | 태스크명 | 담당자 | 예상 시간 | 실제 시간 | 진행 상태 | 우선순위 |"
    header_pos = old_content.find(table_header, category_start)
    if header_pos == -1:
        print("테이블 헤더를 찾을 수 없습니다.")
        return old_content
    
    # 테이블 끝 찾기
    table_end = old_content.find("</details>", header_pos)
    if table_end == -1:
        print("테이블 끝을 찾을 수 없습니다.")
        return old_content
    
    # 현재 테이블 내용 가져오기
    table_content = old_content[header_pos:table_end].strip()
    print("\n현재 테이블 내용:")
    print(table_content)
    
    # 테이블 라인으로 분리
    lines = table_content.split('\n')
    
    # 새 태스크 항목이 이미 있는지 확인
    task_number = re.search(r'TSK-(\d+)', new_task_entry).group(1)
    task_exists = False
    
    print(f"\n태스크 TSK-{task_number} 검사 중...")
    
    for i, line in enumerate(lines):
        if f"TSK-{task_number}" in line:
            print(f"기존 태스크 발견: {line}")
            task_exists = True
            lines[i] = new_task_entry  # 기존 항목 업데이트
            break
    
    if not task_exists:
        print("새로운 태스크 추가")
        if len(lines) > 2:  # 헤더와 구분선이 있는 경우
            lines.append(new_task_entry)
        else:  # 첫 항목인 경우
            lines = [table_header, "| --------- | -------- | ------ | --------- | --------- | --------- | -------- |", new_task_entry]
    
    # 새로운 테이블 생성
    new_table = '\n'.join(lines)
    print("\n업데이트된 테이블:")
    print(new_table)
    
    # 업데이트된 내용 반환
    updated_content = f"{old_content[:header_pos]}{new_table}\n\n{old_content[table_end:]}"
    return updated_content

def calculate_progress_stats(body):
    """보고서 내용에서 태스크 진행 상태를 계산합니다."""
    print("\n=== 진행 상태 계산 ===")
    completed = 0
    in_progress = 0
    total = 0
    
    # 모든 태스크 상태 확인
    for line in body.split('\n'):
        if '| TSK-' in line or '|[TSK-' in line:
            total += 1
            if '✅ 완료' in line:
                completed += 1
            elif '🟡 진행중' in line:
                in_progress += 1
    
    print(f"완료: {completed}, 진행중: {in_progress}, 총: {total}")
    return completed, in_progress, total

def create_progress_section(completed, in_progress, total):
    """진행 현황 섹션을 생성합니다."""
    if total == 0:
        return """### 전체 진행률

```mermaid
pie title 태스크 진행 상태
    "진행중" : 0
    "완료" : 0
```"""
    
    completed_percent = (completed / total) * 100
    in_progress_percent = (in_progress / total) * 100
    
    return f"""### 전체 진행률

진행 상태: {completed}/{total} 완료 ({completed_percent:.1f}%)

```mermaid
pie title 태스크 진행 상태
    "완료" : {completed_percent}
    "진행중" : {in_progress_percent}
```"""

def update_progress_section(body):
    """보고서의 진행 현황 섹션을 업데이트합니다."""
    print("\n=== 진행 현황 섹션 업데이트 ===")
    
    # 진행 상태 계산
    completed, in_progress, total = calculate_progress_stats(body)
    
    # 새로운 진행 현황 섹션 생성
    new_progress_section = create_progress_section(completed, in_progress, total)
    
    # 진행 현황 섹션 업데이트
    progress_start = body.find("### 전체 진행률")
    if progress_start == -1:
        print("진행 현황 섹션을 찾을 수 없습니다.")
        return body
        
    progress_end = body.find("## 📝 특이사항", progress_start)
    if progress_end == -1:
        print("다음 섹션을 찾을 수 없습니다.")
        return body
    
    return f"{body[:progress_start]}{new_progress_section}\n\n{body[progress_end:]}"

def create_report_body(project_name):
    """프로젝트 보고서 템플릿을 생성합니다."""
    # 카테고리 섹션 생성
    category_sections = create_category_sections()
    
    # 초기 진행 현황 섹션 생성
    initial_progress = create_progress_section(0, 0, 0)
    
    return f"""<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=Project%20Report&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=프로젝트%20진행%20보고서&descSize=25&descAlignY=75)

# 📊 프로젝트 진행 보고서

</div>

## 📌 기본 정보

**프로젝트명**: {project_name}  
**보고서 작성일**: {datetime.now().strftime('%Y-%m-%d')}  
**보고 기간**: {datetime.now().strftime('%Y-%m-%d')} ~ 진행중

## 📋 태스크 상세 내역

{category_sections}

## 📊 진행 현황 요약

{initial_progress}

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

def sanitize_project_name(name):
    """프로젝트 이름에서 특수문자를 제거하고 적절한 형식으로 변환합니다."""
    print(f"\n=== 프로젝트 이름 정리 ===")
    print(f"원본 이름: {name}")
    
    # 시작 부분의 . 제거
    while name.startswith('.'):
        name = name[1:]
    
    # 특수문자를 공백으로 변환
    sanitized = re.sub(r'[^\w\s-]', ' ', name)
    
    # 연속된 공백을 하나로 변환하고 앞뒤 공백 제거
    sanitized = ' '.join(sanitized.split())
    
    print(f"변환된 이름: {sanitized}")
    return sanitized

def find_daily_log_issue(repo, project_name):
    """가장 최근의 Daily Log 이슈를 찾습니다."""
    project_name = sanitize_project_name(project_name)  # 프로젝트명 정리
    print(f"\n=== 일일 로그 이슈 검색 ===")
    print(f"프로젝트명: {project_name}")
    
    daily_issues = repo.get_issues(state='open', labels=['daily-log'])
    for issue in daily_issues:
        print(f"검토 중인 이슈: {issue.title}")
        # 이슈 제목에서 프로젝트명 부분만 정리하여 비교
        issue_parts = issue.title.split(' - ')
        if len(issue_parts) == 2:
            issue_project = sanitize_project_name(issue_parts[1])
            if issue_project == project_name:
                print(f"일일 로그 이슈를 찾았습니다: #{issue.number}")
                return issue
            
    print("일일 로그 이슈를 찾지 못했습니다.")
    return None

def create_task_todo(task_issue):
    """태스크 시작을 위한 TODO 항목을 생성합니다."""
    title_parts = task_issue.title.strip('[]').split('] ')
    task_name = title_parts[1]
    category_key = get_category_from_labels(task_issue.labels)
    
    print(f"\n=== TODO 항목 생성 ===")
    print(f"태스크명: {task_name}")
    print(f"카테고리: {category_key}")
    
    # 카테고리 헤더와 태스크 항목 생성
    todo_text = f"""@{TASK_CATEGORIES[category_key]['name']}
- [ ] #{task_issue.number}"""
    print(f"생성된 TODO 텍스트:\n{todo_text}")
    return todo_text

def parse_existing_issue(body):
    """이슈 본문을 파싱하여 기존 TODO 항목들을 추출합니다."""
    print(f"\n=== 이슈 본문 파싱 ===")
    todos = []
    in_todo_section = False
    
    for line in body.split('\n'):
        if '## 📝 Todo' in line:
            print("TODO 섹션 시작")
            in_todo_section = True
            continue
        elif in_todo_section and line.strip() and line.startswith('##'):
            print("TODO 섹션 종료")
            break
        elif in_todo_section and line.strip():
            if line.startswith('- [ ]'):
                todos.append((False, line[6:].strip()))
                print(f"미완료 TODO 추가: {line[6:].strip()}")
            elif line.startswith('- [x]'):
                todos.append((True, line[6:].strip()))
                print(f"완료된 TODO 추가: {line[6:].strip()}")
            elif line.startswith('@'):
                todos.append((None, line.strip()))
                print(f"카테고리 추가: {line.strip()}")
    
    print(f"총 {len(todos)}개의 TODO 항목을 찾았습니다.")
    return {
        'todos': todos
    }

def merge_todos(existing_todos, new_todos):
    """기존 TODO 항목과 새로운 TODO 항목을 병합합니다."""
    print(f"\n=== TODO 항목 병합 ===")
    print(f"기존 TODO 항목 수: {len(existing_todos)}")
    print(f"새로운 TODO 항목 수: {len(new_todos)}")
    
    all_todos = existing_todos.copy()
    
    # 새로운 TODO 항목 추가
    for completed, text in new_todos:
        if text.startswith('@'):
            # 카테고리 헤더는 중복 없이 추가
            if text not in [t[1] for t in all_todos]:
                all_todos.append((None, text))
                print(f"새로운 카테고리 추가: {text}")
        else:
            # 일반 TODO 항목은 중복 체크 후 추가
            if text not in [t[1] for t in all_todos]:
                all_todos.append((completed, text))
                print(f"새로운 TODO 항목 추가: {text}")
            else:
                print(f"중복된 TODO 항목 무시: {text}")
    
    print(f"병합 후 총 TODO 항목 수: {len(all_todos)}")
    return all_todos

def create_todo_section(todos):
    """TODO 섹션을 생성합니다."""
    print(f"\n=== TODO 섹션 생성 ===")
    
    # 카테고리별로 TODO 항목 그룹화
    categories = {}
    current_category = "General"
    uncategorized_todos = []
    
    for completed, text in todos:
        print(f"처리 중인 항목: {text}")
        if completed is None and text.startswith('@'):
            current_category = text[1:]  # @ 제거
            print(f"새 카테고리 시작: {current_category}")
            continue
            
        # 항목이 이미 체크박스 형식인 경우 정리
        if text.startswith('- [ ]') or text.startswith('- [x]'):
            text = text.replace('- [ ]', '').replace('- [x]', '').strip()
            
        if current_category not in categories:
            categories[current_category] = []
            
        categories[current_category].append((completed, text))
        print(f"'{current_category}' 카테고리에 항목 추가: {text}")
    
    # 카테고리별 섹션 생성
    sections = []
    for category, category_todos in categories.items():
        if not category_todos:  # 빈 카테고리는 건너뛰기
            continue
            
        completed_count = sum(1 for completed, _ in category_todos if completed)
        total_count = len(category_todos)
        
        section = f"""<details>
<summary><h3 style="display: inline;">📑 {category} ({completed_count}/{total_count})</h3></summary>

"""
        # TODO 항목 추가
        for completed, text in category_todos:
            checkbox = '[x]' if completed else '[ ]'
            if text.startswith('#'):  # 태스크 참조인 경우
                section += f"- {checkbox} {text}\n"
            else:
                section += f"- {checkbox} {text}\n"
        
        section += "\n⚫\n</details>\n"
        sections.append(section)
    
    result = '\n'.join(sections)
    print(f"\n생성된 TODO 섹션:\n{result}")
    return result

def process_approval(issue, repo):
    """이슈의 라벨에 따라 승인 처리를 수행합니다."""
    print(f"\n=== 승인 처리 시작 ===")
    print(f"이슈 번호: #{issue.number}")
    print(f"이슈 제목: {issue.title}")
    
    labels = [label.name for label in issue.labels]
    print(f"이슈 라벨: {labels}")
    
    # 제목에서 프로젝트명과 태스크명 추출
    title_parts = issue.title.strip('[]').split('] ')
    project_name = repo.name  # 리포지토리명을 프로젝트명으로 사용
    print(f"프로젝트명: {project_name}")
    
    if '✅ 승인완료' in labels:
        print("\n승인완료 처리 시작")
        # 태스크 카테고리 결정
        category_key = get_category_from_labels(issue.labels)
        print(f"태스크 카테고리: {category_key}")
        
        # 기존 보고서 이슈 찾기
        report_issue = find_report_issue(repo, project_name)
        
        if report_issue:
            print(f"\n보고서 이슈 발견: #{report_issue.number}")
            # 기존 보고서 업데이트
            task_entry = create_task_entry(issue)
            print(f"생성된 태스크 항목:\n{task_entry}")
            
            # 태스크 항목 업데이트
            updated_body = update_report_content(report_issue.body, task_entry, category_key)
            
            # 진행 현황 섹션 업데이트
            updated_body = update_progress_section(updated_body)
            
            report_issue.edit(body=updated_body)
            report_issue.create_comment(f"✅ 태스크 #{issue.number}이 {category_key} 카테고리에 추가되었습니다.")
            print("보고서 업데이트 완료")
            
            # Daily Log 이슈 찾기 및 TODO 추가
            print("\n=== Daily Log 처리 시작 ===")
            daily_issue = find_daily_log_issue(repo, project_name)
            if daily_issue:
                print(f"\n일일 로그 이슈 발견: #{daily_issue.number}")
                # TODO 항목 생성
                todo_text = create_task_todo(issue)
                print(f"생성된 TODO 항목:\n{todo_text}")
                
                # 현재 이슈 본문 파싱
                existing_content = parse_existing_issue(daily_issue.body)
                print(f"기존 TODO 항목 수: {len(existing_content['todos'])}")
                
                # 새로운 TODO 항목 추가
                new_todos = [(False, line) for line in todo_text.split('\n')]
                all_todos = merge_todos(existing_content['todos'], new_todos)
                
                # TODO 섹션 업데이트
                todo_section = create_todo_section(all_todos)
                
                # 이슈 본문 업데이트
                print("\n이슈 본문 업데이트 시작")
                if '## 📝 Todo' in daily_issue.body:
                    body_parts = daily_issue.body.split('## 📝 Todo')
                    updated_body = f"{body_parts[0]}## 📝 Todo\n\n{todo_section}"
                    if len(body_parts) > 1 and '##' in body_parts[1]:
                        next_section = body_parts[1].split('##', 1)[1]
                        updated_body += f"\n\n##{next_section}"
                else:
                    # Todo 섹션이 없는 경우 마지막에 추가
                    updated_body = f"{daily_issue.body}\n\n## 📝 Todo\n\n{todo_section}"
                
                daily_issue.edit(body=updated_body)
                daily_issue.create_comment(f"새로운 태스크가 추가되었습니다:\n\n{todo_text}")
                print("일일 로그 업데이트 완료")
            else:
                print(f"오늘자 Daily Log 이슈를 찾을 수 없습니다: {datetime.now().strftime('%Y-%m-%d')}")
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
        
        # 승인 완료 메시지만 추가
        issue.create_comment("✅ 태스크가 승인되어 보고서에 추가되었습니다.")
        
    elif '❌ 반려' in labels:
        issue.create_comment("❌ 태스크가 반려되었습니다. 수정 후 다시 제출해주세요.")
        
    elif '⏸️ 보류' in labels:
        issue.create_comment("⏸️ 태스크가 보류되었습니다. 추가 논의가 필요합니다.")

def main():
    try:
        print("\n=== 스크립트 실행 시작 ===")
        # GitHub 클라이언트 초기화
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GitHub 토큰이 설정되지 않았습니다.")
        github = Github(github_token)
        
        # 저장소 정보 가져오기
        repo_name = os.getenv('GITHUB_REPOSITORY')
        if not repo_name:
            raise ValueError("GitHub 저장소 정보를 찾을 수 없습니다.")
        repo = github.get_repo(repo_name)
        
        # 이벤트 정보 가져오기
        event_name = os.getenv('GITHUB_EVENT_NAME')
        event_path = os.getenv('GITHUB_EVENT_PATH')
        
        print(f"이벤트 타입: {event_name}")
        print(f"이벤트 파일 경로: {event_path}")
        
        if not event_path or not os.path.exists(event_path):
            raise ValueError(f"이벤트 파일을 찾을 수 없습니다: {event_path}")
        
        # 이벤트 데이터 읽기
        with open(event_path, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
            print(f"이벤트 데이터: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
            
            # 이슈 번호 가져오기
            issue_number = event_data['issue']['number']
            print(f"처리할 이슈 번호: #{issue_number}")
            
            # 이슈 정보 가져오기
            issue = repo.get_issue(issue_number)
            labels = [label.name for label in issue.labels]
            print(f"이슈 라벨: {labels}")
            
            # 이벤트 타입에 따른 처리
            if event_name in ['issues', 'issue_comment']:
                # Daily Log의 TODO 완료 처리
                if 'daily-log' in labels and any('[x]' in line and 'TSK-' in line and 'spent:' in line for line in issue.body.split('\n')):
                    print("\n=== Daily Log 완료 처리 시작 ===")
                    for line in issue.body.split('\n'):
                        if '[x]' in line and 'TSK-' in line and 'spent:' in line:
                            process_todo_completion(repo, line)
                
                # 태스크 승인/반려 처리
                if '✅ 승인완료' in labels or '❌ 반려' in labels or '⏸️ 보류' in labels:
                    print("\n=== 태스크 승인/반려 처리 시작 ===")
                    process_approval(issue, repo)
            else:
                print(f"처리할 수 없는 이벤트 타입입니다: {event_name}")
                
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        raise

if __name__ == '__main__':
    main() 
import os
from github import Github
from datetime import datetime

def create_report_body(issue):
    """태스크 보고서 템플릿으로 변환합니다."""
    return f"""<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=Task%20Report&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=프로젝트%20태스크%20관리%20보고서&descSize=25&descAlignY=75)

# 📊 태스크 진행 보고서

</div>

## 📌 기본 정보

**보고서 작성일**: {datetime.now().strftime('%Y-%m-%d')}  
**프로젝트명**: {issue.title.replace('태스크 제안: ', '')}  
**작성자**: {issue.user.login}  
**보고 기간**: {datetime.now().strftime('%Y-%m-%d')} ~ 진행중

## 📋 태스크 상세 내역

<details>
<summary><h3>🔧 기능 개발</h3></summary>

| 태스크 ID | 태스크명 | 담당자 | 예상 시간 | 실제 시간 | 진행 상태 | 우선순위 |
| --------- | -------- | ------ | --------- | --------- | --------- | -------- |
| TSK-{issue.number} | {issue.title.replace('태스크 제안: ', '')} | {issue.assignee.login if issue.assignee else 'TBD'} | - | - | 🟡 진행중 | - |

</details>

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

def process_approval(issue):
    """이슈의 라벨에 따라 승인 처리를 수행합니다."""
    labels = [label.name for label in issue.labels]
    
    if '✅ 승인완료' in labels:
        # 승인된 경우 보고서 형식으로 변환
        new_body = create_report_body(issue)
        issue.edit(body=new_body)
        issue.create_comment("✅ 태스크가 승인되어 보고서 형식으로 변환되었습니다.")
        
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
        process_approval(issue)

if __name__ == '__main__':
    main() 
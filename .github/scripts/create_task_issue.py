import os
import pandas as pd
from github import Github
from pathlib import Path

def read_csv_data(file_path):
    """CSV 파일에서 태스크 데이터를 읽어옵니다."""
    df = pd.read_csv(file_path, encoding='utf-8')
    return df

def create_issue_body(data):
    """태스크 제안서 템플릿 형식으로 이슈 본문을 생성합니다."""
    body = f"""# 프로젝트 태스크 제안서

## 1. 제안 개요

**프로젝트명**: {data['프로젝트명'][0]}  
**제안자**: {data['제안자'][0]}  
**제안일**: {data['제안일'][0]}  
**구현 목표일**: {data['구현목표일'][0]}

## 2. 태스크 요약

### 2.1 목적

{data['[태스크목적]'][0]}

### 2.2 범위

{data['[태스크범위]'][0]}

## 3. 상세 내용

### 메인 요구사항

{data['[필수요구사항]'][0]}

### 선택 요구사항

{data['[선택요구사항]'][0]}

## 4. 승인 절차

이 태스크의 승인을 위해 다음 중 하나의 라벨을 추가해주세요:
- `✅ 승인완료`: 태스크를 승인하고 진행을 시작합니다.
- `❌ 반려`: 태스크를 반려하고 수정을 요청합니다.
- `⏸️ 보류`: 태스크를 보류하고 추가 논의가 필요합니다.

## 5. 일정 계획

```mermaid
gantt
    title 태스크 구현 일정
    dateFormat YYYY-MM-DD
    section 개발
{data['[일정계획]'][0]}
```
"""
    return body

def main():
    # GitHub 클라이언트 초기화
    github_token = os.getenv('GITHUB_TOKEN')
    github = Github(github_token)
    
    # 저장소 정보 가져오기
    repo_name = os.getenv('GITHUB_REPOSITORY')
    repo = github.get_repo(repo_name)
    
    # CSV 파일 찾기
    csv_dir = Path('TaskProposals')
    for csv_file in csv_dir.glob('*.csv'):
        if csv_file.is_file():
            # CSV 데이터 읽기
            data = read_csv_data(csv_file)
            
            # 이슈 생성
            issue_title = f"태스크 제안: {data['프로젝트명'][0]}"
            issue_body = create_issue_body(data)
            
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=['⌛ 검토대기']
            )
            
            # 처리된 CSV 파일 이동 또는 삭제
            os.remove(csv_file)

if __name__ == '__main__':
    main() 
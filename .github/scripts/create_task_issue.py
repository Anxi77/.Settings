import os
from github import Github
from pathlib import Path
import re

def convert_schedule_to_mermaid(schedule_data):
    """CSV 형식의 일정 데이터를 Mermaid 간트 차트 형식으로 변환합니다."""
    tasks = []
    for line in schedule_data.split('\n'):
        if line.strip():
            task, date, duration = [part.strip() for part in line.split(',')]
            tasks.append(f"    {task} :{date}, {duration}")
    return '\n'.join(tasks)

def read_csv_data(file_path):
    """CSV 파일에서 태스크 데이터를 읽어옵니다."""
    data = {}
    current_section = None
    section_content = []
    
    # 다양한 인코딩 시도
    encodings = ['utf-8', 'euc-kr']
    
    for encoding in encodings:
        try:
            print(f"\n=== CSV 파일 읽기 시도 ({encoding}) ===")
            print(f"파일 경로: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                
            print(f"파일 읽기 성공 (인코딩: {encoding})")
            
            for line in lines:
                line = line.strip()
                if not line:  # 빈 줄 건너뛰기
                    continue
                    
                if line.startswith('[') and line.endswith(']'):  # 새로운 섹션 시작
                    if current_section and section_content:
                        data[current_section] = '\n'.join(section_content)
                        section_content = []
                    current_section = line
                    print(f"새로운 섹션 발견: {current_section}")
                    continue
                    
                if current_section:  # 섹션 내용 수집
                    section_content.append(line)
                    print(f"섹션 내용 추가: {line[:50]}...")
                else:  # 헤더 정보 처리
                    if ',' in line:
                        key, value = line.split(',', 1)
                        data[key] = value.strip()
                        print(f"헤더 정보 추가: {key} = {value.strip()}")
                
            # 마지막 섹션 처리
            if current_section and section_content:
                data[current_section] = '\n'.join(section_content)
                
            print(f"\n총 {len(data)}개의 섹션을 읽었습니다.")
            return data
            
        except UnicodeDecodeError:
            print(f"{encoding} 인코딩으로 읽기 실패")
            continue
    
    # 모든 인코딩 시도 실패
    raise UnicodeDecodeError(f"지원하는 인코딩({', '.join(encodings)})으로 파일을 읽을 수 없습니다.")

def create_issue_body(data, project_name):
    """태스크 제안서 템플릿 형식으로 이슈 본문을 생성합니다."""
    # 일정계획 데이터를 Mermaid 형식으로 변환
    schedule_mermaid = convert_schedule_to_mermaid(data['[일정계획]'])
    
    body = f"""# 프로젝트 태스크 제안서

## 1. 제안 개요

**프로젝트명**: {project_name}  
**태스크명**: {data['[태스크명]']}  
**제안자**: {data['제안자']}  
**제안일**: {data['제안일']}  
**구현 목표일**: {data['구현목표일']}

## 2. 태스크 요약

### 2.1 목적

{data['[태스크목적]']}

### 2.2 범위

{data['[태스크범위]']}

## 3. 상세 내용

### 메인 요구사항

{data['[필수요구사항]']}

### 선택 요구사항

{data['[선택요구사항]']}

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
{schedule_mermaid}
```
"""
    return body

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

def main():
    # GitHub 클라이언트 초기화
    github_token = os.getenv('GITHUB_TOKEN')
    github = Github(github_token)
    
    # 저장소 정보 가져오기
    repo_name = os.getenv('GITHUB_REPOSITORY')
    repo = github.get_repo(repo_name)
    project_name = sanitize_project_name(repo.name)  # 리포지토리명 정리
    
    print(f"\n=== 저장소 정보 ===")
    print(f"원본 저장소명: {repo.name}")
    print(f"정리된 프로젝트명: {project_name}")
    
    # CSV 파일 찾기
    csv_dir = Path('TaskProposals')
    print(f"\n=== CSV 파일 검색 ===")
    print(f"검색 디렉토리: {csv_dir.absolute()}")
    
    for csv_file in csv_dir.glob('*.csv'):
        if csv_file.is_file():
            print(f"\n발견된 CSV 파일: {csv_file}")
            # CSV 데이터 읽기
            data = read_csv_data(csv_file)
            
            # 이슈 생성
            issue_title = f"[{project_name}] {data['[태스크명]']}"
            print(f"생성할 이슈 제목: {issue_title}")
            
            issue_body = create_issue_body(data, project_name)
            
            issue = repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=['⌛ 검토대기']
            )
            print(f"이슈 생성 완료: #{issue.number}")
            
            # 처리된 CSV 파일 이동 또는 삭제
            os.remove(csv_file)
            print(f"CSV 파일 삭제 완료: {csv_file}")

if __name__ == '__main__':
    main() 
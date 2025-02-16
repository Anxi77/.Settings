import os
from github import Github
from pathlib import Path
import re
import csv
from io import StringIO

def parse_csv_section(section_content):
    """CSV 섹션 내용을 파싱합니다."""
    if not section_content.strip():
        return []
    
    result = []
    # 개행 문자 정규화
    section_content = section_content.replace('\r\n', '\n')
    
    # 연속된 빈 줄 제거
    lines = [line for line in section_content.split('\n') if line.strip()]
    
    for line in lines:
        # StringIO를 사용하여 CSV 파싱
        f = StringIO(line)
        reader = csv.reader(f, skipinitialspace=True)
        row = next(reader, None)
        
        if row:
            # 빈 필드 제거 및 공백 정리
            cleaned_row = []
            for field in row:
                field = field.strip()
                if field:  # 빈 필드가 아닌 경우만 추가
                    # 따옴표 제거 (시작과 끝에 있는 경우만)
                    if field.startswith('"') and field.endswith('"'):
                        field = field[1:-1]
                    cleaned_row.append(field)
            
            if cleaned_row:  # 비어있지 않은 행만 추가
                result.append(cleaned_row)
    
    return result

def convert_schedule_to_mermaid(schedule_data):
    """일정계획 데이터를 Mermaid 간트 차트 형식으로 변환합니다."""
    tasks = []
    for item in schedule_data:
        task = item['task']
        date = item['date']
        duration = item['duration']
        tasks.append(f"    {task} :{date}, {duration}")
    return '\n'.join(tasks)

def read_csv_data(file_path):
    """CSV 파일에서 태스크 데이터를 읽어옵니다."""
    data = {}
    current_section = None
    section_content = ""
    
    encodings = ['utf-8', 'euc-kr']
    
    for encoding in encodings:
        try:
            print(f"\n=== CSV 파일 읽기 시도 ({encoding}) ===")
            print(f"파일 경로: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            print(f"파일 읽기 성공 (인코딩: {encoding})")
            
            # 기본 정보 처리
            for line in lines:
                line = line.strip()
                if not line:  # 빈 줄 건너뛰기
                    continue
                    
                # 섹션 시작 확인
                if line.startswith('[') and ']' in line:
                    section_name = line.split(',')[0]
                    current_section = section_name
                    section_content = ""
                    continue
                
                # 섹션 내용 수집
                if current_section:
                    section_content += line + "\n"
                    
                    # 기본 정보 (태스크명 섹션의 경우)
                    if current_section == '[태스크명]':
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                        if len(parts) >= 2:
                            key = parts[0]
                            value = parts[1]
                            if key == '태스크명':
                                data[current_section] = value
                            elif not key.startswith('['):  # 기본 정보 필드
                                data[key] = value
                    
                    # 태스크 목적
                    elif current_section == '[태스크목적]':
                        text = line.split(',')[0].strip()
                        if text and not text.startswith('['):
                            data[current_section] = text
                    
                    # 태스크 범위
                    elif current_section == '[태스크범위]':
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                        if parts and not any(p.startswith('[') for p in parts):
                            if current_section not in data:
                                data[current_section] = []
                            data[current_section].extend(parts)
                    
                    # 필수/선택 요구사항
                    elif current_section in ['[필수요구사항]', '[선택요구사항]']:
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                        if parts and not any(p.startswith('[') for p in parts):
                            if current_section not in data:
                                data[current_section] = []
                            data[current_section].extend(parts)
                    
                    # 일정계획
                    elif current_section == '[일정계획]':
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                        if len(parts) >= 3 and not any(p.startswith('[') for p in parts):
                            if current_section not in data:
                                data[current_section] = []
                            data[current_section].append({
                                'task': parts[0],
                                'date': parts[1],
                                'duration': parts[2]
                            })
            
            # 데이터 후처리
            for key in data:
                if isinstance(data[key], list):
                    if key == '[일정계획]':
                        # 일정계획은 그대로 둠
                        pass
                    else:
                        # 리스트 항목들을 문자열로 변환
                        data[key] = '\n'.join(f"- {item}" for item in data[key])
            
            if data:  # 데이터가 성공적으로 파싱된 경우
                print(f"\n총 {len(data)}개의 항목을 읽었습니다.")
                print("\n=== 파싱된 데이터 ===")
                for key, value in data.items():
                    print(f"\n{key}:")
                    print(value)
                    print("-" * 50)
                
                # 태스크명이 없는 경우 기본값 설정
                if '[태스크명]' not in data:
                    data['[태스크명]'] = 'UI/UX 개선 프로젝트'
                
                return data
            
            print("\n데이터가 비어있습니다!")
            print(f"현재 데이터 상태: {data}")
            continue  # 다음 인코딩으로 시도
            
        except UnicodeDecodeError:
            print(f"{encoding} 인코딩으로 읽기 실패")
            continue
        except Exception as e:
            print(f"파일 처리 중 오류 발생: {str(e)}")
            continue
    
    raise ValueError("파일을 읽을 수 없거나 데이터가 없습니다.")

def create_issue_body(data, project_name):
    """태스크 제안서 템플릿 형식으로 이슈 본문을 생성합니다."""
    # 일정계획 데이터를 Mermaid 형식으로 변환
    schedule_mermaid = convert_schedule_to_mermaid(data['[일정계획]'])
    
    body = f"""# 프로젝트 태스크 제안서

## 1. 제안 개요

**프로젝트명**: {project_name}  
**태스크명**: {data['[태스크명]']}  
**제안자**: {data.get('제안자', 'TBD')}  
**제안일**: {data.get('제안일', 'TBD')}  
**구현 목표일**: {data.get('구현목표일', 'TBD')}

## 2. 태스크 요약

### 2.1 목적

{data.get('[태스크목적]', 'TBD')}

### 2.2 범위

{data.get('[태스크범위]', 'TBD')}

## 3. 상세 내용

### 메인 요구사항

{data.get('[필수요구사항]', 'TBD')}

### 선택 요구사항

{data.get('[선택요구사항]', 'TBD')}

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
import csv
import datetime

def read_section(lines, section_name):
    """CSV에서 섹션 데이터를 읽어옵니다."""
    section_data = []
    in_section = False
    
    for line in lines:
        if line.strip() == f'[{section_name}]':
            in_section = True
            continue
        elif line.strip().startswith('[') and in_section:
            break
        elif in_section and line.strip():
            section_data.append(line.strip())
            
    return section_data

def create_gantt_mermaid(schedule_data):
    """일정 데이터로 머메이드 간트 차트를 생성합니다."""
    mermaid = ['```mermaid', 'gantt', '    title 태스크 구현 일정', '    dateFormat YYYY-MM-DD']
    
    current_section = None
    for task in schedule_data[1:]:  # 헤더 제외
        task_name, start_date, duration = task.split(',')
        if current_section != task_name.split()[0]:
            current_section = task_name.split()[0]
            mermaid.append(f'    section {current_section}')
        mermaid.append(f'    {task_name} :{start_date}, {duration}d')
    
    mermaid.append('```')
    return '\n'.join(mermaid)

def convert_to_md():
    """CSV 데이터를 마크다운으로 변환합니다."""
    with open('Documents/task_data.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 기본 정보 읽기
    project_info = {}
    for line in lines[:4]:
        key, value = line.strip().split(',')
        project_info[key] = value
    
    # 각 섹션 데이터 읽기
    purpose = read_section(lines, '태스크목적')[0]
    scope = read_section(lines, '태스크범위')[0]
    required = read_section(lines, '필수요구사항')
    optional = read_section(lines, '선택요구사항')
    implementation = read_section(lines, '구현계획')[1:]  # 헤더 제외
    dev_outputs = read_section(lines, '개발산출물')
    doc_outputs = read_section(lines, '문서산출물')
    schedule = read_section(lines, '일정계획')
    
    # 마크다운 생성
    md_content = f"""# 프로젝트 태스크 제안서

## 1. 제안 개요

**프로젝트명**: {project_info['프로젝트명']}  
**제안자**: {project_info['제안자']}  
**제안일**: {project_info['제안일']}  
**구현 목표일**: {project_info['구현목표일']}

## 2. 태스크 요약

### 2.1 목적

{purpose}

### 2.2 범위

{scope}

## 3. 상세 내용

### 3.1 기술 요구사항

#### 필수 요구사항

{chr(10).join([f'- {req}' for req in required])}

#### 선택 요구사항

{chr(10).join([f'- {opt}' for opt in optional])}

### 3.2 구현 계획

| 단계 | 내용 | 예상 소요 시간 | 담당자 |
|------|------|----------------|---------|
{chr(10).join([f'| {" | ".join(task.split(","))} |' for task in implementation])}

## 4. 산출물

### 4.1 개발 산출물

{chr(10).join([f'- {output}' for output in dev_outputs])}

### 4.2 문서 산출물

{chr(10).join([f'- {output}' for output in doc_outputs])}

## 5. 일정 계획

{create_gantt_mermaid(schedule)}
"""
    
    # 마크다운 파일 저장
    with open('Documents/TaskProposalTemplate.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == '__main__':
    convert_to_md() 
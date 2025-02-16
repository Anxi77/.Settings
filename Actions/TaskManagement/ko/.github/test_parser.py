import csv
from io import StringIO
from pathlib import Path

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

def process_section(section_name, content, data):
    """섹션 내용을 처리하여 데이터 딕셔너리에 저장합니다."""
    if not content:
        print(f"섹션 {section_name}의 내용이 비어있습니다.")
        return
        
    print(f"\n처리 중인 섹션: {section_name}")
    print(f"원본 섹션 내용: {content}")
    
    # 섹션 이름이 포함된 항목 제거
    filtered_content = []
    for parts in content:
        if not any(part.startswith('[') and part.endswith(']') for part in parts):
            filtered_content.append(parts)
    print(f"필터링된 섹션 내용: {filtered_content}")
    
    if not filtered_content:  # 내용이 없으면 처리하지 않음
        print(f"섹션 {section_name}의 필터링된 내용이 비어있습니다.")
        return
    
    try:
        if section_name == '[태스크명]':
            # 기본 정보 처리
            for parts in filtered_content:
                if len(parts) >= 2:
                    key = parts[0]
                    value = parts[1]
                    if key == '태스크명':
                        data[section_name] = value
                        print(f"태스크명 설정: {value}")
                    else:
                        data[f"[{key}]"] = value
                        print(f"기본 정보 추가: {key} = {value}")
        
        elif section_name == '[일정계획]':
            # 일정계획은 원본 형식 유지
            formatted_lines = []
            for parts in filtered_content:
                if len(parts) >= 2:
                    task = parts[0]
                    schedule = ' | '.join(parts[1:])
                    formatted_lines.append(f"{task}: {schedule}")
            if formatted_lines:
                data[section_name] = '\n'.join(formatted_lines)
                print(f"일정계획 저장: {len(formatted_lines)}개 항목")
        
        else:
            # 일반 섹션은 항목별로 정리
            formatted_lines = []
            for parts in filtered_content:
                if parts:
                    formatted_lines.append(f"- {' | '.join(parts)}")
            
            if formatted_lines:
                data[section_name] = '\n'.join(formatted_lines)
                print(f"섹션 내용 저장: {len(formatted_lines)}개 항목")
        
        print(f"섹션 {section_name} 처리 후 데이터 상태: {data}")
        
    except Exception as e:
        print(f"섹션 {section_name} 처리 중 오류 발생: {str(e)}")
        raise

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
                            else:
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

def main():
    # CSV 파일 찾기
    base_dir = Path('D:/ANXI/Dev/Git/.Settings')
    csv_dir = base_dir / 'TaskProposals'
    print(f"\n=== CSV 파일 검색 ===")
    print(f"검색 디렉토리: {csv_dir.absolute()}")
    
    for csv_file in csv_dir.glob('*.csv'):
        if csv_file.is_file():
            print(f"\n발견된 CSV 파일: {csv_file}")
            # CSV 데이터 읽기
            data = read_csv_data(csv_file)
            print("\n=== 파싱 결과 ===")
            for key, value in data.items():
                print(f"{key}:")
                print(value)
                print("-" * 50)

if __name__ == '__main__':
    main() 
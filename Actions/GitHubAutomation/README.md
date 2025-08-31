# GitHub 자동화 시스템

[English](README.en.md) | [한국어](README.md)

---

## 📌 개요

커밋 추적, 태스크 관리, 프로젝트 리포팅을 위한 완전한 GitHub 자동화 시스템입니다. GitHub Issues와 Project 보드와 완전히 통합되어 포괄적인 프로젝트 관리를 제공합니다.

### ✨ 주요 특징
- **완전한 GraphQL API 통합** - 최신 GitHub GraphQL API 기반 구현
- **자동 일일 상태 보고서(DSR) 생성** - 커밋 기반 자동 리포트
- **프로젝트 보드 동기화** - 실시간 이슈 및 태스크 상태 관리
- **스마트 커밋 파싱** - [type] 형식 커밋 메시지 완전 지원
- **라벨 관리 자동화** - 이슈 상태에 따른 자동 라벨 업데이트
- **포괄적인 검증 시스템** - 모든 구성 요소 자동 검증

## 🚀 빠른 설정

### 1. 파일 복사
```bash
# 전체 .github 구조를 저장소에 복사
cp -r Actions/GitHubAutomation/.github/* .github/
```

### 2. 의존성 설치
```bash
# Python 의존성 설치
pip install -r .github/scripts/requirements.txt
```

### 3. GitHub 시크릿 설정
Repository Settings → Secrets and variables → Actions에서 다음을 설정:

| 시크릿 이름 | 설명 | 필수 |
|------------|------|------|
| `GITHUB_TOKEN` | GitHub API 토큰 (repo, project 권한) | ✅ |

### 4. 프로젝트 보드 설정
GitHub Repository → Projects에서 프로젝트 보드를 생성하고 `config.yaml`에서 프로젝트 번호를 설정하세요.

## 🔧 기능 상세

### 📅 자동 DSR (일일 상태 보고서) 생성
- **커밋 기반 자동 생성**: 매일 커밋을 분석하여 자동으로 DSR 이슈 생성
- **TODO 항목 추적**: 커밋 메시지의 Todo 섹션에서 TODO 항목을 자동 추출
- **이전 TODO 이전**: 미완료 TODO를 다음날 DSR로 자동 이전
- **브랜치별 분류**: 브랜치별로 커밋을 분류하여 정리된 리포트 제공
- **스마트 필터링**: 설정된 커밋 타입 제외 및 자동화 봇 필터링

### 📊 프로젝트 보드 동기화
- **실시간 이슈 동기화**: GitHub Issues와 Project V2 보드 완전 동기화
- **자동 필드 업데이트**: 상태, 우선순위, 카테고리 필드 자동 관리
- **라벨 기반 분류**: 이슈 라벨을 기반으로 한 자동 태스크 분류
- **배치 업데이트**: 효율적인 GraphQL 배치 작업으로 성능 최적화
- **통계 생성**: 프로젝트 진행률 및 완료율 자동 계산

### 🏷️ 라벨 관리 자동화
- **상태 라벨 동기화**: 태스크 상태 변경 시 자동 라벨 업데이트
- **우선순위 관리**: priority:high, priority:medium 등 우선순위 라벨 관리
- **카테고리 분류**: category: 접두사를 통한 자동 카테고리 분류
- **스마트 라벨 교체**: 기존 상태 라벨 제거 후 새 라벨 적용

### 📈 프로젝트 리포팅
- **포괄적인 통계**: 태스크 완료율, 상태별 분포, 우선순위별 분포
- **성능 메트릭**: API 사용률, 처리 시간, 성공률 등 운영 메트릭
- **상태 모니터링**: 시스템 상태 체크 및 구성 요소 검증
- **자동 보고서**: 정기적인 프로젝트 진행 보고서 자동 생성

## ⚙️ 설정

### 기본 설정 (`config.yaml`)
```yaml
# 글로벌 설정
global:
  timezone: "Asia/Seoul"          # 타임존 설정
  project_number: 2               # GitHub 프로젝트 번호
  max_retries: 3                  # API 재시도 횟수
  log_level: "INFO"               # 로깅 레벨

# DSR 설정
daily_reporter:
  enabled: true                   # DSR 생성 활성화
  issue_prefix: "📅"             # DSR 이슈 제목 접두사
  dsr_label: "DSR"               # DSR 이슈 라벨
  branch_label_prefix: "branch:" # 브랜치 라벨 접두사
  excluded_commit_types:          # 제외할 커밋 타입
    - "chore"
    - "docs" 
    - "style"
  keep_dsr_days: 7               # DSR 보관 기간

# 프로젝트 동기화 설정
project_sync:
  enabled: true                  # 프로젝트 동기화 활성화
  status_field_name: "Status"   # 상태 필드명
  priority_field_name: "Priority" # 우선순위 필드명
  category_field_name: "Category" # 카테고리 필드명
  
  # 상태 라벨 매핑
  status_labels:
    "todo": "TODO"
    "in-progress": "IN_PROGRESS"
    "in-review": "IN_REVIEW" 
    "done": "DONE"
    "blocked": "BLOCKED"
  
  # 우선순위 라벨 매핑
  priority_labels:
    "priority:low": "LOW"
    "priority:medium": "MEDIUM"
    "priority:high": "HIGH"
    "priority:critical": "CRITICAL"

# GitHub API 설정
github:
  max_retries: 3                 # 최대 재시도 횟수
  base_delay: 1.0               # 기본 지연 시간
  rate_limit_buffer: 100        # 속도 제한 버퍼

# 로깅 설정
logging:
  level: "INFO"                 # 로깅 레벨
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### 환경별 설정
```yaml
environments:
  development:
    log_level: "DEBUG"
    max_retries: 1
    
  production:
    log_level: "WARNING"
    max_retries: 3
    notification_on_critical_error: true
```

## 📝 커밋 컨벤션 가이드

이 시스템은 **[type] format**의 구조화된 커밋 메시지를 사용합니다.

### 기본 구조
```
[type(scope)] 커밋 제목

[Body]
상세 설명 내용
- 변경사항 1
- 변경사항 2

[Todo]
@카테고리
- TODO 항목 1
- TODO 항목 2

[Footer]
이슈 참조 및 메타데이터
- Closes #123
- Related to #124, #125
```

### 지원 커밋 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 추가 | `[feat] 사용자 인증 시스템 추가` |
| `fix` | 버그 수정 | `[fix] 로그인 오류 해결` |
| `docs` | 문서화 변경 | `[docs] README 업데이트` |
| `style` | 코드 포맷팅 (기능 변경 없음) | `[style] 코드 스타일 정리` |
| `refactor` | 코드 리팩토링 | `[refactor] 인증 모듈 구조 개선` |
| `test` | 테스트 코드 추가 | `[test] 유닛 테스트 추가` |
| `chore` | 빌드, 설정 변경 | `[chore] 의존성 업데이트` |
| `design` | UI/UX 디자인 변경 | `[design] 버튼 스타일 개선` |
| `comment` | 주석 추가/변경 | `[comment] API 함수 주석 추가` |
| `rename` | 파일/폴더 이름 변경 | `[rename] 컴포넌트 파일명 변경` |
| `remove` | 파일 삭제 | `[remove] 사용하지 않는 파일 제거` |
| `!BREAKING CHANGE` | 중대한 API 변경 | `[!BREAKING CHANGE] API v2 마이그레이션` |
| `!HOTFIX` | 긴급 버그 수정 | `[!HOTFIX] 보안 취약점 긴급 수정` |

### 섹션별 상세 가이드

#### Body 섹션 (선택사항)
```
[Body]
- 인증 시스템 구현 완료
- JWT 토큰 기반 세션 관리
- 비밀번호 암호화 추가
- 로그인 실패 시 재시도 제한
```

#### Todo 섹션 (선택사항)
```
[Todo]
@authentication
- 소셜 로그인 연동 추가
- 비밀번호 찾기 기능 구현
- 2FA 인증 시스템 도입

@testing
- 인증 플로우 단위 테스트 작성
- 보안 취약점 테스트 추가
```

#### Footer 섹션 (선택사항)
```
[Footer]
Closes #123, #124
Related to #125
Breaking Change: 기존 API v1은 더 이상 지원되지 않습니다
Co-authored-by: 개발자명 <email@example.com>
```

### 커밋 메시지 예시

#### 기본 커밋
```
[feat] 사용자 대시보드 구현
```

#### 스코프 포함 커밋  
```
[fix(auth)] 로그인 세션 만료 버그 수정
```

#### 완전한 구조 커밋
```
[feat] 실시간 알림 시스템 구현

[Body]
- WebSocket 기반 실시간 통신 구현
- 알림 타입별 분류 시스템 추가
- 사용자별 알림 설정 관리 기능
- 알림 히스토리 저장 및 조회

[Todo]
@notification
- 푸시 알림 연동 추가
- 이메일 알림 템플릿 개선
- 알림 통계 대시보드 구현

@performance  
- 알림 큐 최적화
- 대용량 사용자 대응 성능 테스트

[Footer]
Closes #456
Related to #457, #458
```

### 커밋 메시지 검증

시스템은 다음을 자동으로 검증합니다:
- ✅ [type] 형식 준수
- ✅ 지원되는 커밋 타입 사용
- ✅ 섹션 구조 올바름
- ✅ Todo 카테고리 형식 (@카테고리)
- ✅ Footer 이슈 참조 형식

## 🎯 워크플로우

### 자동 트리거
- **Push to main/master/develop**: DSR 생성 및 프로젝트 동기화
- **Issues 변경**: 프로젝트 보드 자동 업데이트
- **Project 보드 변경**: 이슈 라벨 자동 동기화
- **수동 실행**: GitHub Actions에서 수동 트리거 가능

### 실행 모드
```bash
# 워크플로우 추적 (DSR 생성)
python main.py --mode workflow

# 태스크 관리 (프로젝트 동기화) 
python main.py --mode task-management

# 프로젝트 리포트 생성
python main.py --mode report

# 시스템 상태 체크
python main.py --health-check

# 드라이 런 (변경사항 없이 테스트)
python main.py --dry-run --verbose
```

## 🔍 모니터링 및 검증

### 시스템 상태 체크
```bash
# 전체 시스템 검증
python validate_implementation.py

# 개별 구성 요소 체크
python main.py --health-check
```

### 로그 확인
시스템 로그는 다음 레벨로 출력됩니다:
- `DEBUG`: 상세한 실행 정보
- `INFO`: 일반적인 실행 상태  
- `WARNING`: 주의가 필요한 상황
- `ERROR`: 오류 발생 상황

## 🛠 고급 설정

### 사용자 정의 필드 매핑
```yaml
project_sync:
  custom_fields:
    "Estimate": "estimate_field_id"
    "Sprint": "sprint_field_id"
```

### 알림 설정 (선택사항)
```yaml
notifications:
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
  
  email:
    enabled: false
    recipients: ["team@example.com"]
```

### 성능 최적화
```yaml
performance:
  batch_size: 50              # 배치 처리 크기
  concurrent_requests: 5      # 동시 요청 수
  cache_duration: 300         # 캐시 지속 시간 (초)
```

## 📊 메트릭 및 분석

시스템은 다음 메트릭을 자동으로 수집합니다:
- API 호출 성공/실패율
- 처리 시간 통계  
- 프로젝트 완료율
- DSR 생성 통계
- 에러 발생 빈도

## 🤝 기여하기

시스템 개선에 기여하고 싶으시면:
1. Issues 탭에서 버그 리포트나 기능 제안
2. Pull Request를 통한 코드 기여
3. 문서화 개선 제안

## 📄 라이선스

이 프로젝트는 개인/팀 사용을 위한 설정 템플릿입니다. 자유롭게 사용하고 수정하세요.

---

<div align="center">

### 🔗 관련 링크

[메인 Settings 저장소](../../) • 
[TaskManagement](../TaskManagement/) •
[BaekjoonLogging](../BaekjoonLogging/)

**🚀 GitHub 자동화로 더 효율적인 개발 워크플로우를 경험하세요!**

</div>
# Daily Development Log 액션 사용 설명서

## 📌 개요

이 GitHub 액션은 커밋 메시지를 기반으로 일일 개발 로그를 자동으로 생성하고 관리합니다. 브랜치별 작업 내역과 TODO 항목을 체계적으로 관리할 수 있습니다.

## 🔧 주요 기능

1. **일일 개발 로그 자동 생성**

   - 당일 날짜의 개발 로그 이슈 자동 생성
   - 브랜치별 커밋 내역 정리
   - TODO 항목 관리

2. **브랜치 관리**

   - 브랜치별 커밋 히스토리 누적
   - 커밋 상세 정보 (시간, 작성자, 타입) 표시
   - 관련 이슈 연결

3. **TODO 관리**
   - 체크박스 형식의 TODO 항목 관리
   - 이전 날짜의 미완료 TODO 자동 이전
   - TODO 상태 (완료/미완료) 보존
   - 중복 TODO 처리

## 💫 커밋 메시지 작성 방법

커밋 메시지는 다음 형식을 따라야 합니다:

```
[type] 제목

[Body]
상세 내용을 작성합니다.
여러 줄로 작성 가능합니다.

[Todo]
- 새로운 TODO 항목 1
- 새로운 TODO 항목 2

[Footer]
#관련-이슈 #태그
```

### 커밋 타입 종류

- `feat`: ✨ 새로운 기능
- `fix`: 🐛 버그 수정
- `refactor`: ♻️ 코드 리팩토링
- `docs`: 📝 문서 수정
- `test`: ✅ 테스트 코드
- `chore`: 🔧 빌드/설정 변경
- `style`: 💄 코드 스타일 변경
- `perf`: ⚡️ 성능 개선

## ⚙️ 환경 설정

`.github/workflows/create-issue-from-commit.yml` 파일에서 다음 설정을 변경할 수 있습니다:

```yaml
env:
  TIMEZONE: "Asia/Seoul" # 타임존 설정
  ISSUE_PREFIX: "📅" # 이슈 제목 접두사
  ISSUE_LABEL: "daily-log" # 기본 라벨
  EXCLUDED_COMMITS: "^(chore|docs|style):" # 제외할 커밋 타입
```

## 📋 자동 생성되는 이슈 형식

```markdown
# 📅 Daily Development Log (YYYY-MM-DD) - Repository Name

<div align="center">

## 📊 Branch Summary

</div>

<details>
<summary><h3>✨ Branch Name</h3></summary>
커밋 상세 내용
</details>

<div align="center">

## 📝 Todo

</div>

- [ ] TODO 항목 1
- [x] TODO 항목 2 (완료됨)
```

## 🔍 디버그 출력

액션 실행 시 다음과 같은 정보가 출력됩니다:

1. 현재 이슈의 TODO 목록
2. TODO 항목 통계
3. 새로 추가되는 TODO 목록
4. 이전 날짜에서 이전된 TODO 목록
5. 최종 결과

## ⚠️ 주의사항

1. 커밋 메시지 형식을 정확히 지켜주세요.
2. TODO 항목은 `-` 또는 `*`로 시작해야 합니다.
3. 이전 날짜의 이슈는 자동으로 닫힙니다.
4. `chore`, `docs`, `style` 타입의 커밋은 기본적으로 제외됩니다.

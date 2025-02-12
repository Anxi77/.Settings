<div align="center">

![header](https://capsule-render.vercel.app/api?type=waving&height=300&color=gradient&text=One%20Of%20Neglected)

<h1>One Of Neglected Develop Repository</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Unity-000000?style=for-the-badge&logo=unity&logoColor=white"/>
  <img src="https://img.shields.io/badge/Team_Project-FF4154?style=for-the-badge&logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/Game_Development-4B32C3?style=for-the-badge&logo=gamemaker&logoColor=white"/>
</p>

# [Anxi - Quetions(One Of Neglected Original Sound Track)](https://soundcloud.com/musicbyanxi/anxi-questions/s-bjkkxGDTL1S?si=8ab28d0af9f74fae8e85c0e5828ef7f3&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing)

<details>
<summary><h1>📁 프로젝트 리소스 안내</h1></summary>
<div align="center">

### 🎮 게임 기획서

&nbsp;&nbsp;&nbsp;• \_Game_Designer_Info 폴더에서 기획서 관련 자료를 확인할 수 있습니다.<br>

### 🗂️ 에셋 관리

&nbsp;&nbsp;&nbsp;• 모든 에셋은 Import 후 Resources 폴더로 경로를 이동해주세요.<br>
&nbsp;&nbsp;&nbsp;• 에셋 이동 시 참조 경로가 깨지지 않도록 주의해주세요.<br>

</div>
</details>

<details>
<summary><h1>💬 커밋 컨벤션</h1></summary>
<div align="center">

#### 📝 커밋 메시지 구조

━━━━━━━━━━━━━━━━━━━━━━

#### • 기본 구조

[Type] 커밋 제목
<br></br>
[Body]

커밋 내용 상세 설명

&nbsp;- 첫 번째 변경 사항

&nbsp;- 두 번째 변경 사항
<br></br>
[Todo]

할일 목록 상세 설명

&nbsp; @todo 카테고리

&nbsp;- 실제 태스크

<br></br>
[Footer]

이슈 번호 참조

&nbsp;- Closes/Fixes #123 (해당 이슈가 자동으로 종료됨)

&nbsp;- Related to #124, #125 (관련 이슈 링크만 걸림, 종료되지 않음)
<br></br>
━━━━━━━━━━━━━━━━━━━━━━

#### • 커밋 타입 종류

| 타입             | 설명                                              |
| ---------------- | ------------------------------------------------- |
| feat             | 새로운 기능 추가                                  |
| fix              | 버그 수정                                         |
| docs             | 문서 수정                                         |
| style            | 코드 포맷팅, 세미콜론 누락, 코드 변경이 없는 경우 |
| refactor         | 코드 리팩토링                                     |
| test             | 테스트 코드 추가                                  |
| chore            | 빌드 업무 수정, 패키지 매니저 수정 (잡일)         |
| design           | UI/UX 디자인 변경                                 |
| comment          | 필요한 주석 추가 및 변경                          |
| rename           | 파일 혹은 폴더명을 수정하거나 옮기는 작업         |
| remove           | 파일을 삭제하는 작업                              |
| !BREAKING CHANGE | 커다란 API 변경                                   |
| !HOTFIX          | 급하게 치명적인 버그를 고치는 경우                |

━━━━━━━━━━━━━━━━━━━━━━

<div align="center">

### • 커밋 메시지 예시

[feat]
실시간 채팅 시스템 구현
<br></br>
[Body]

&nbsp;- 1:1 채팅방 생성 및 관리 기능

&nbsp;- 이모티콘 시스템 통합

&nbsp;- 채팅 히스토리 저장 구현

&nbsp;- 실시간 메시지 알림 기능
<br></br>
[Todo]

&nbsp;- (issue) 채팅 메시지 암호화 기능 추가

&nbsp;- (issue) 이모티콘 크기 최적화 작업

&nbsp;- 채팅 히스토리 백업 시스템 구현

&nbsp;- 오프라인 메시지 처리 로직 개선

&nbsp;- 채팅방 최대 인원 제한 기능 추가
<br></br>
[Footer]

Closes #128

&nbsp;Related to #125, #126

</div>

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

<details>
<summary><h1>📋 Daily Development Log 액션 사용 설명서</h1></summary>
<div align="center">

## 📌 개요

이 GitHub 액션은 커밋 메시지를 기반으로 일일 개발 로그를 자동으로 생성하고 관리합니다. 브랜치별 작업 내역과 TODO 항목을 체계적으로 관리할 수 있습니다.

## 🔧 주요 기능

### ✨ 일일 개발 로그 자동 생성

&nbsp;&nbsp;&nbsp;• 당일 날짜의 개발 로그 이슈 자동 생성<br>
&nbsp;&nbsp;&nbsp;• 브랜치별 커밋 내역 정리<br>
&nbsp;&nbsp;&nbsp;• TODO 항목 관리<br>

### 🌿 브랜치 관리

&nbsp;&nbsp;&nbsp;• 브랜치별 커밋 히스토리 누적<br>
&nbsp;&nbsp;&nbsp;• 커밋 상세 정보 (시간, 작성자, 타입) 표시<br>
&nbsp;&nbsp;&nbsp;• 관련 이슈 연결<br>

### 📝 TODO 관리

&nbsp;&nbsp;&nbsp;• 체크박스 형식의 TODO 항목 관리<br>
&nbsp;&nbsp;&nbsp;• 이전 날짜의 미완료 TODO 자동 이전<br>
&nbsp;&nbsp;&nbsp;• TODO 상태 (완료/미완료) 보존<br>
&nbsp;&nbsp;&nbsp;• 중복 TODO 처리<br>
&nbsp;&nbsp;&nbsp;• @카테고리 문법으로 TODO 항목 분류<br>
&nbsp;&nbsp;&nbsp;• 대소문자 구분 없는 카테고리 처리<br>
&nbsp;&nbsp;&nbsp;• 미분류 항목을 위한 General 카테고리 자동 생성<br>
&nbsp;&nbsp;&nbsp;• 카테고리별 완료/전체 통계 자동 생성 (예: Combat (2/5))<br>
&nbsp;&nbsp;&nbsp;• (issue) 접두사로 할일 항목 자동 이슈화<br>

### 💫 카테고리 기능 사용법

```markdown
[Todo]
@Combat

- 몬스터 전투 시스템 구현
- 플레이어 공격 패턴 추가
- (issue) 보스 AI 패턴 최적화 필요

@UI

- 전투 UI 레이아웃 디자인
- 데미지 표시 효과 구현

@Sound

- 전투 효과음 추가
- BGM 전환 시스템 구현

- 버그 수정 및 테스트 (자동으로 General 카테고리로 분류)
```

### 📑 카테고리 표시 형식

```markdown
<details>
<summary>📑 General (0/1)</summary>
- [ ] 버그 수정 및 테스트
</details>

<details>
<summary>📑 Combat (1/3)</summary>
- [ ] 몬스터 전투 시스템 구현
- [x] 플레이어 공격 패턴 추가
- [ ] #123 (자동 생성된 보스 AI 이슈)
</details>

<details>
<summary>📑 UI (0/2)</summary>
- [ ] 전투 UI 레이아웃 디자인
- [ ] 데미지 표시 효과 구현
</details>
```

### ✨ 카테고리 기능 특징

&nbsp;&nbsp;&nbsp;• `@카테고리명`으로 새 카테고리 생성 또는 전환<br>
&nbsp;&nbsp;&nbsp;• 대소문자 구분 없이 동일 카테고리로 처리 (@COMBAT = @Combat)<br>
&nbsp;&nbsp;&nbsp;• 원본 카테고리의 대소문자는 표시에서 유지<br>
&nbsp;&nbsp;&nbsp;• 카테고리 없는 항목은 자동으로 General에 포함<br>
&nbsp;&nbsp;&nbsp;• 카테고리별로 접었다 펼 수 있는 details 태그로 정리<br>
&nbsp;&nbsp;&nbsp;• 각 카테고리의 진행 상황이 (완료/전체) 형식으로 표시<br>
&nbsp;&nbsp;&nbsp;• `(issue)` 접두사가 붙은 항목은 자동으로 이슈로 생성되고 번호로 대체<br>

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

## ⚠️ 주의사항

&nbsp;&nbsp;&nbsp;1. 커밋 메시지 형식을 정확히 지켜주세요.<br>
&nbsp;&nbsp;&nbsp;2. TODO 항목은 `-`로 시작해야 합니다.<br>
&nbsp;&nbsp;&nbsp;3. 이전 날짜의 이슈는 자동으로 닫힙니다.<br>

</div>
</details>

# 알고리즘 문제 풀이 세팅

[English](README.en.md) | [한국어](README.md)

## 📋 개요

알고리즘 문제 풀이를 위한 CMAKE 및 vscode 세팅입니다.

## 🔧 주요 기능

### 테스트 케이스 관리

- 테스트 케이스 디렉토리 자동 생성
- 입출력 파일 리다이렉션 처리
- 문제당 다중 테스트 케이스 지원

### 빌드 시스템

- CMake 기반 빌드 구성
- 실행 파일 자동 생성
- Debug/Release 모드 지원

### VS Code 통합

- 사전 구성된 C++ IntelliSense
- 통합 디버깅 설정
- 커스텀 빌드 작업
- 미리 구성된 bits/stdc++.h 헤더

## 📦 디렉토리 구조

```
AlgorithmSolving/
├── .vscode/                  # VS Code 설정
│   ├── bits/                 # 미리 컴파일된 헤더
│   ├── c_cpp_properties.json # C++ 설정
│   ├── launch.json          # 디버그 설정
│   ├── settings.json        # 에디터 설정
│   └── tasks.json           # 빌드 작업
├── CMakeLists.txt           # CMake 설정
└── .gitignore               # Git 제외 규칙
```

## 🚀 시작하기

1. 필수 프로그램 설치:

   - MinGW G++ 컴파일러
   - CMake
   - VS Code (C/C++ 확장 포함)

2. 프로젝트 설정:

   - 이 디렉토리를 작업 공간에 복사
   - VS Code에서 열기
   - CMake가 자동으로 구성됨

3. 새 솔루션 만들기:
   - Solutions 디렉토리에 새 .cpp 파일 생성
   - Ctrl+Shift+B로 빌드
   - F5로 디버그

## ⚙️ 설정

### 컴파일러 설정

- C++17 표준 활성화
- UTF-8 인코딩
- 빌드 타입별 최적화 플래그

### VS Code 설정

- 저장 시 포맷팅 활성화
- 커스텀 스니펫 지원
- 통합 터미널 구성

## 🔍 사용 팁

1. 테스트 케이스 관리:

   ```cpp
   // 파일에서 입력
   freopen("input.txt", "r", stdin);
   // 파일로 출력
   freopen("output.txt", "w", stdout);
   ```

2. 디버그 설정:
   - 중단점 지원
   - 변수 검사
   - 콘솔 입출력 리다이렉션

## 🤝 기여하기

개선사항 제안이나 문제 보고를 환영합니다.

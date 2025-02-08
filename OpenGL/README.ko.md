# OpenGL 개발 환경

## 📋 개요

이 세팅은 GLFW와 CMake를 사용하는 OpenGL 개발 환경입니다.

## 🔧 주요 기능

### OpenGL 설정

- OpenGL (4.5+) 지원
- GLFW 윈도우 관리
- 셰이더 컴파일 유틸리티
- 크로스 플랫폼 호환성

### 빌드 시스템

- CMake 기반 구성
- 자동 의존성 관리
- Debug/Release 구성
- 플랫폼별 최적화

### 개발 도구

- VS Code 통합
- 디버깅 지원
- 성능 프로파일링
- 메모리 추적

## 📦 디렉토리 구조

```
OpenGL/
├── .vscode/                  # VS Code 설정
│   ├── c_cpp_properties.json # C++ 설정
│   ├── launch.json          # 디버그 설정
│   ├── settings.json        # 에디터 설정
│   └── tasks.json           # 빌드 작업
├── CMakeLists.txt           # CMake 설정
├── include/                 # 외부 의존성
│   └── GLFW/               # GLFW 헤더
└── .gitignore              # Git 제외 규칙
```

## 🚀 시작하기

1. 필수 요구사항:

   - MinGW G++ 컴파일러
   - CMake 3.10 이상
   - GLFW 라이브러리
   - OpenGL 드라이버

2. 환경 설정:

   - 이 디렉토리를 프로젝트에 복사
   - GLFW 의존성 설치
   - VS Code에서 열기
   - CMake가 자동으로 구성됨

3. 새 프로젝트 생성:
   - CMakeLists.txt를 프로젝트에 맞게 수정
   - 소스 파일 추가
   - 셰이더 파일 생성
   - Ctrl+Shift+B로 빌드

## ⚙️ 설정

### OpenGL 설정

- 코어 프로파일 컨텍스트
- 디버그 컨텍스트 지원
- 확장 기능 로딩
- 뷰포트 구성

### 빌드 옵션

- 플랫폼별 설정
- 최적화 레벨
- 디버그 심볼
- 경고 레벨

## 🔍 사용 팁

1. 컨텍스트 생성:

   ```cpp
   // GLFW 초기화
   glfwInit();
   glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
   glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
   glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
   ```

2. 디버그 기능:
   - OpenGL 디버그 출력
   - GPU 메모리 추적
   - 성능 카운터
   - 프레임 분석

## 🤝 기여하기

개선사항 제안이나 버그 리포트를 환영합니다.

# DirectX 개발 환경

[English](README.en.md) | [한국어](README.md)

## 📋 개요

이 세팅은 DirectX 11과 HLSL 셰이더를 사용하는 개발 환경입니다.

## 🔧 주요 기능

### HLSL 셰이더 개발

- 통합 셰이더 컴파일
- 디버그 셰이더 지원
- 셰이더 리플렉션 도구
- 핫 리로드 기능

### 빌드 시스템

- CMake 기반 구성
- 자동 셰이더 컴파일
- Debug/Release 구성
- UTF-8 인코딩 지원

### Visual Studio 통합

- IntelliSense 구성
- 디버깅 도구 설정
- 성능 프로파일링
- 그래픽스 디버깅

## 📦 디렉토리 구조

```
DirectX/
├── .vscode/                  # VS Code 설정
│   ├── c_cpp_properties.json # C++ 설정
│   ├── launch.json          # 디버그 설정
│   ├── settings.json        # 에디터 설정
│   └── tasks.json           # 빌드 작업
├── CMakeLists.txt           # CMake 설정
├── shaders/                 # HLSL 셰이더 파일
│   ├── *.hlsl              # 셰이더 소스 파일
│   └── compiled/           # 컴파일된 셰이더 객체
└── .gitignore              # Git 제외 규칙
```

## 🚀 시작하기

1. 필수 요구사항:

   - Visual Studio 2022
   - Windows SDK 10.0.19041.0 이상
   - DirectX 11 SDK
   - CMake 3.20 이상

2. 환경 설정:

   - 이 디렉토리를 프로젝트에 복사
   - VS Code에서 열기
   - CMake가 자동으로 구성됨
   - c_cpp_properties.json에서 SDK 경로 확인

3. 새 프로젝트 생성:
   - CMakeLists.txt를 프로젝트에 맞게 수정
   - 소스 파일 추가
   - shaders/ 폴더에 HLSL 셰이더 추가
   - Ctrl+Shift+B로 빌드

## ⚙️ 설정

### 셰이더 컴파일

- 런타임 컴파일 지원
- 디버그 정보 생성
- 최적화 레벨
- 다중 셰이더 모델 대상

### 디버그 기능

- 그래픽스 디버깅
- 셰이더 디버깅
- 성능 분석
- 메모리 누수 감지

## 🔍 사용 팁

1. 셰이더 개발:

   ```hlsl
   // 버텍스 셰이더 예제
   cbuffer Constants : register(b0)
   {
       matrix WorldViewProj;
   };

   struct VSInput
   {
       float3 Position : POSITION;
       float2 TexCoord : TEXCOORD;
   };
   ```

2. 디버그 구성:
   - PIX 통합
   - Visual Studio 그래픽스 디버거
   - 성능 프로파일링 도구

## 🤝 기여하기

개선사항 제안이나 버그 리포트를 환영합니다.

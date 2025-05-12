# NAVER 스마트 스토어 FAQ 챗봇 API

## Initialize
1. '_.env_' 파일 설정: '.env.example'에서 OPENAI_API_KEY를 채우고, 파일 이름을 '.env'로 변경합니다.
2. 의존성 패키지 설치
    ```
    poetry install
    ```

## Run
1. fastapi cli를 이용한 API server 구동
    ```
    fastapi dev main.py
    ```

## Test
1. pytest cli를 이용한 test 시작
    ```
    pytest
    ```
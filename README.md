# AI Assistant Project

[English](#english) | [한국어](#한국어)

## English

An AI question-and-answer web application built with Next.js and FastAPI.
The project aims to become a research assistant for exploring AI infrastructure companies and related documents.
The current implementation sends user questions to the OpenAI API through the backend and displays the answers in the browser.

### Current Features

- Question input and AI answer display
- Loading indicators and request error messages
- Backend health check API (`GET /health`)

Each question is currently processed independently. Conversation context, chat history storage, document uploads, and document search are not yet implemented.

### Tech Stack

- **Frontend:** Next.js App Router, React, TypeScript, Tailwind CSS, TanStack Query
- **Backend:** Python, FastAPI, Uvicorn
- **AI integration:** OpenAI Python SDK, Responses API

### Project Structure

```text
ai-assistant-project/
├── backend/
│   ├── main.py             # API endpoints and AI integration
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── app/                # Pages and global configuration
│   ├── components/         # Question form and backend status component
│   ├── lib/api.ts          # Backend request helpers
│   └── package.json        # Frontend dependencies and scripts
├── docs/                   # Learning notes
└── README.md
```

### Local Setup

You will need Python 3, Node.js with npm, and an OpenAI API key.
The commands below are for macOS/Linux. Run the backend and frontend in separate terminals.

#### 1. Set Up the Backend

From the project root, run:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `backend/.env` with the following values.
Replace the placeholders with your API key and a model ID you have access to.

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_id_here
```

Start the development server from the `backend` directory:

```bash
python -m uvicorn main:app --reload
```

- Backend: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

#### 2. Set Up the Frontend

Open a new terminal and run the following from the project root:

```bash
cd frontend
npm install
```

Create `frontend/.env.local` with the following value:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server from the `frontend` directory:

```bash
npm run dev
```

Open http://localhost:3000 in your browser and enter a question.
The backend's current CORS configuration allows this frontend address.

### API Reference

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Returns the server status: `{"status":"ok"}` |
| POST | `/ask` | Accepts a question and returns an AI answer |

Example `POST /ask` request:

```json
{
  "question": "What is AI infrastructure?"
}
```

Response format:

```json
{
  "answer": "The AI-generated answer to your question"
}
```

### Development Commands

Run these commands from the `frontend` directory:

```bash
npm run lint   # Check code with ESLint
npm run build  # Create a production build
npm run start  # Serve the built frontend
```

### Configuration and Troubleshooting

- If the backend fails to start, check your virtual environment, installed dependencies, and `OPENAI_API_KEY` setting.
- If a question request fails, check the backend terminal for errors and verify `OPENAI_MODEL`.
- If the frontend cannot reach the API, confirm that the backend is running and `NEXT_PUBLIC_API_URL` is correct. Restart the frontend development server after changing environment variables.
- Store your API key only in `backend/.env`. The current `.gitignore` excludes the backend `.env` and frontend `.env*` files.

---

## 한국어

Next.js와 FastAPI로 만드는 AI 질문·답변 웹 애플리케이션입니다.
AI 인프라 기업과 관련 문서를 조사하는 리서치 도우미를 목표로 개발하고 있습니다.
현재는 사용자가 입력한 질문을 백엔드에서 OpenAI API로 전달하고, 반환된 답변을 화면에 표시하는 기본 기능을 구현했습니다.

### 현재 기능

- 질문 입력 및 AI 답변 표시
- 답변 요청 중 로딩 상태와 요청 실패 메시지 표시
- 백엔드 상태 확인 API (`GET /health`)

현재 각 질문은 독립적으로 처리됩니다. 이전 대화를 이어가는 기능, 대화 저장, 문서 업로드 및 검색은 아직 구현하지 않았습니다.

### 기술 스택

- **프론트엔드:** Next.js App Router, React, TypeScript, Tailwind CSS, TanStack Query
- **백엔드:** Python, FastAPI, Uvicorn
- **AI 연동:** OpenAI Python SDK, Responses API

### 프로젝트 구조

```text
ai-assistant-project/
├── backend/
│   ├── main.py             # API 엔드포인트 및 AI 연동
│   └── requirements.txt    # Python 의존성
├── frontend/
│   ├── app/                # 페이지 및 전역 설정
│   ├── components/         # 질문 폼, 백엔드 상태 컴포넌트
│   ├── lib/api.ts          # 백엔드 요청 함수
│   └── package.json        # 프론트엔드 의존성 및 실행 명령
├── docs/                   # 학습 기록
└── README.md
```

### 로컬 실행 방법

Python 3, Node.js와 npm, OpenAI API 키가 필요합니다.
아래 명령은 macOS/Linux 터미널 기준이며, 프론트엔드와 백엔드를 각각 별도 터미널에서 실행합니다.

#### 1. 백엔드 설정

프로젝트 루트에서 실행합니다.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`backend/.env` 파일을 만들고 다음 두 값을 입력합니다.
예시의 값을 실제 API 키와 사용할 수 있는 모델 ID로 바꾸세요.

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_id_here
```

`backend` 폴더에서 개발 서버를 실행합니다.

```bash
python -m uvicorn main:app --reload
```

- 백엔드: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 상태 확인: http://localhost:8000/health

#### 2. 프론트엔드 설정

새 터미널을 열고 프로젝트 루트에서 실행합니다.

```bash
cd frontend
npm install
```

`frontend/.env.local` 파일을 만들고 다음 값을 입력합니다.

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`frontend` 폴더에서 개발 서버를 실행합니다.

```bash
npm run dev
```

브라우저에서 http://localhost:3000 을 열고 질문을 입력하세요.
현재 백엔드의 CORS 설정은 이 프론트엔드 주소를 허용합니다.

### API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/health` | 서버 상태 반환: `{"status":"ok"}` |
| POST | `/ask` | 질문을 전달하고 AI 답변 반환 |

`POST /ask` 요청 예시:

```json
{
  "question": "AI 인프라란 무엇인가요?"
}
```

응답 형식:

```json
{
  "answer": "질문에 대한 AI 답변"
}
```

### 개발 명령어

`frontend` 폴더에서 실행합니다.

```bash
npm run lint   # 코드 규칙 검사
npm run build  # 프로덕션 빌드
npm run start  # 빌드한 프론트엔드 실행
```

### 설정 확인

- 백엔드가 시작되지 않으면 가상환경, 의존성 설치, `OPENAI_API_KEY` 설정을 확인하세요.
- 질문 요청이 실패하면 백엔드 터미널의 오류와 `OPENAI_MODEL` 값을 확인하세요.
- 프론트엔드에서 API에 연결되지 않으면 백엔드 실행 여부와 `NEXT_PUBLIC_API_URL`을 확인하세요. 환경변수를 변경했다면 프론트엔드 개발 서버를 재시작하세요.
- API 키는 `backend/.env`에만 저장하세요. 현재 `.gitignore`는 백엔드 `.env`와 프론트엔드 `.env*` 파일을 제외하도록 설정되어 있습니다.

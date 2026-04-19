# ⚡ TaskFlow – FastAPI Task Manager

A full-stack Task Manager web application built with FastAPI, SQLite, JWT authentication, and a clean responsive frontend.

## 🌐 Live Demo
> **https://your-app.onrender.com** ← Replace after deploying

## 📌 Project Overview

TaskFlow lets users register, log in, and manage personal tasks. Each user only sees their own tasks. The REST API is fully documented via Swagger at `/docs`.

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite |
| Authentication | JWT (python-jose), bcrypt (passlib) |
| Frontend | HTML, CSS, JavaScript (single page) |
| Testing | pytest, httpx |
| Container | Docker, docker-compose |

---

## 📁 Folder Structure

```
taskmanager/
├── backend/
│   ├── main.py              # App entry, CORS, static file serving
│   ├── requirements.txt
│   ├── .env.example
│   ├── pytest.ini
│   ├── core/
│   │   ├── config.py        # Pydantic settings
│   │   └── security.py      # JWT creation, password hashing, auth dependency
│   ├── db/
│   │   └── database.py      # SQLAlchemy engine + session factory
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── task.py          # Task ORM model
│   ├── schemas/
│   │   ├── user.py          # Pydantic request/response schemas
│   │   └── task.py          # Task schemas with pagination
│   ├── routers/
│   │   ├── auth.py          # POST /register, POST /login
│   │   └── tasks.py         # Full CRUD + pagination + filtering
│   └── tests/
│       └── test_api.py      # 12 pytest test cases
├── frontend/
│   └── index.html           # Single-page app (no framework)
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Local Setup

### Requirements
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/taskmanager.git
cd taskmanager

# 2. Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env — set a strong SECRET_KEY

# 5. Start the server
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — the frontend loads automatically.
API docs: **http://localhost:8000/docs**

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret **(required, keep secret)** | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `30` |
| `DATABASE_URL` | SQLAlchemy DB connection string | `sqlite:///./taskmanager.db` |

> ⚠️ Never commit `.env`. It is in `.gitignore`.

---

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | ✗ | Register a new user |
| POST | `/login` | ✗ | Login and receive JWT token |

### Tasks (all require `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | List all tasks (paginated, filterable) |
| GET | `/tasks/{id}` | Get a specific task |
| PUT | `/tasks/{id}` | Update a task (title, description, completed) |
| DELETE | `/tasks/{id}` | Delete a task |

### Query Parameters for `GET /tasks`
| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 10, max: 100) |
| `completed` | bool | Filter: `true` = completed, `false` = pending |

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

**12 test cases covering:**
- User registration (success + duplicate)
- Login (success + wrong password)
- Task CRUD (create, read, update, delete)
- Task filtering by completion status
- Pagination
- User task isolation (User A cannot see User B's tasks)

---

## 🐳 Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t taskmanager .
docker run -p 8000:8000 -e SECRET_KEY=your-secret taskmanager
```

---

## 🚀 Deploying to Render

1. Push this repo to a **public GitHub repository**
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables in Render dashboard:
   - `SECRET_KEY` → a long random string
   - `DATABASE_URL` → `sqlite:///./taskmanager.db`
6. Click **Deploy**

---

## ✅ Feature Checklist

- [x] User registration & login
- [x] JWT authentication with bcrypt password hashing
- [x] Create, view, update, delete tasks
- [x] Users can only access their own tasks
- [x] Pagination (`?page=1&page_size=10`)
- [x] Filter by status (`?completed=true`)
- [x] Proper HTTP status codes (200, 201, 204, 400, 401, 404)
- [x] Error handling with clear messages
- [x] Clean folder structure (no logic mixed in one file)
- [x] Pydantic models for all request/response schemas
- [x] SQLAlchemy ORM with SQLite
- [x] Responsive single-page frontend
- [x] Register, login, create, view, complete, delete from UI
- [x] 12 pytest test cases
- [x] Dockerfile + docker-compose
- [x] `.env.example` included, `.env` in `.gitignore`
- [x] README with full setup instructions

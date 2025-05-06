# 📚 BookTrack Frontend

![CI](https://github.com/sedoxxx/booktrack-frontend/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/sedoxxx/booktrack-frontend)
![Docker](https://img.shields.io/docker/image-size/sedoxxx/booktrack-frontend/latest)

A **Streamlit** single-page UI for BookTrack — your personal reading tracker.

---

## 🚀 Table of Contents

1. [Overview](#overview)  
2. [Tech Stack & Architecture](#tech-stack--architecture)  
3. [Prerequisites](#prerequisites)  
4. [Setup & Run Locally](#setup--run-locally)  
5. [Environment Variables](#environment-variables)  
6. [Docker Usage](#docker-usage)  
7. [Testing](#testing)  
8. [CI/CD Pipeline](#cicd-pipeline)  
9. [Folder Structure](#folder-structure)  
10. [Coding Standards](#coding-standards)  
11. [Contributing](#contributing)  
12. [License](#license)

---

## 📖 Overview

BookTrack Frontend is a thin** client that consumes a FastAPI backend to let users:
- Search & discover public-domain books
- View detailed metadata & descriptions
- Mark books as favourites
- Track reading status (“Want”, “Reading”, “Read”)
- See simple dashboard metrics

---

## 🧩 Tech Stack & Architecture

- **Python 3.11**  
- **Streamlit** ≥1.30  
- **Requests** for HTTP  
- **CI**: GitHub Actions  
- **Container**: Docker (image ≤ 500 MB)  
- **Tests**: Pytest + Selenium  

```text
┌───────────────┐      ┌────────────────┐      ┌───────────────┐
│  Streamlit    │ <--> │  FastAPI API   │ <--> │   SQLite DB   │
│  Frontend     │      │  (auth, books) │      │               │
└───────────────┘      └────────────────┘      └───────────────┘
      │
      │ HTTP
      ▼
  User Browser
```

## 🔧 Prerequisites

* Python 3.11 installed
* [ChromeDriver](https://chromedriver.chromium.org/) for integration tests
* Docker & Docker Compose (optional)
* Git

---

## ⚙️ Setup & Run Locally

1. **Clone repo**

   ```bash
   git clone https://github.com/your-org/booktrack-frontend.git
   cd booktrack-frontend
   ```
2. **Virtual env & deps**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run**

   ```bash
   ./run.sh
   # visit http://localhost:8501
   ```
4. **Alternative: Run with Fake Data**
   ```
   USE_FAKE_DATA=true 
   BYPASS_AUTH=true
   streamlit run app/main.py
   ```

---

## 🛠️ Environment Variables

Create a `.env` in project root:

```ini
API_BASE_URL=http://localhost:8000/api/v1
BYPASS_AUTH=false
USE_FAKE_DATA=false
PER_PAGE=20
```

* **API\_BASE\_URL**: Base URL of the FastAPI backend
* **BYPASS\_AUTH**: Skip auth headers for demo
* **USE\_FAKE\_DATA**: Serve built-in dummy data
* **PER\_PAGE**: Number of results per page

---

## 🐳 Docker Usage

```bash
docker build -t booktrack-frontend .
docker run -d -p 8501:8501 \
  -e API_BASE_URL=http://backend:8000/api/v1 \
  -e USE_FAKE_DATA=true \
  booktrack-frontend
```

---

## 🧪 Testing

* **Unit**

  ```bash
  pytest tests/unit
  ```
* **Integration**

  1. Start server locally (`./run.sh`)
  2. In a second terminal:

     ```bash
     pytest tests/integration
     ```
* **Lint & Coverage**

  ```bash
  ruff check .
  flake8 .
  pytest --cov=app
  ```

---

## 🤖 CI/CD Pipeline

*On every PR/push to `main`*:

1. Checkout & setup Python 3.11
2. Install dev deps (`ruff`, `flake8`, `pytest`)
3. **Lint**: ruff & flake8
4. **Test**: unit + integration
5. **Coverage**: fail if < 65 %
6. On `main` only: build Docker image

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for details.

---

## 📂 Folder Structure

```
booktrack-frontend/
├── .github/             # CI configuration
├── app/                 # source code
│   ├── components/      # reusable widgets
│   ├── pages/           # page modules
│   ├── api_client.py    # HTTP wrappers
│   ├── config.py        # settings
│   ├── state.py         # st.session_state helpers
│   └── main.py          # app entrypoint
├── tests/               # unit & integration tests
├── Dockerfile
├── run.sh
├── requirements.txt
└── README.md
```

---



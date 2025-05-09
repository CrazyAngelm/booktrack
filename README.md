# BookTrack

**BookTrack** is a personal reading tracker: a single-page web app built with FastAPI (backend), Streamlit (frontend), and SQLite for persistence. It integrates the Gutendex public-domain book API to help you discover and track your reading.

---

## 🛠️ Prerequisites

- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Quick Start

All services (backend, frontend, proxy) can be brought up with a single command:

```bash
docker-compose up --build
````

This will:

1. Build your backend and frontend images
2. Start the FastAPI backend on port **8000**
3. Start the Streamlit frontend on port **8501**
4. (Optional) Start Nginx as an HTTPS-only proxy

Once started:

* **Frontend** → [http://localhost:8501](http://localhost:8501)
* **API docs** → [http://localhost:8000/docs](http://localhost:8000/docs)

Use Ctrl+C to shut everything down, or:

```bash
docker-compose down
```

---

## ⚙️ Environment Variables

Create a `.env` file next to your `docker-compose.yml`, or set these in your environment:

| Variable                   | Description                                        | Example                     |
| -------------------------- | -------------------------------------------------- | --------------------------- |
| `DATABASE_URL`             | SQLAlchemy database URL                            | `sqlite:///./dev.db`        |
| `JWT_SECRET`               | Secret key for signing JWTs                        | `a1b2c3d4e5f6...`           |
| `JWT_ALGORITHM`            | Algorithm for JWTs                                 | `HS256`                     |
| `ACCESS_TOKEN_EXPIRATION`  | Access token lifetime (seconds)                    | `3600`                      |
| `REFRESH_TOKEN_EXPIRATION` | Refresh token lifetime (seconds)                   | `7200`                      |
| `GUTINDEX_BASE_URL`        | Base URL for Gutendex API                          | `https://gutendex.com`      |
| `USE_FAKE_DATA`            | Toggle fake data mode in frontend (`true`/`false`) | `false`                     |
| `API_BASE_URL`             | Base URL the frontend uses to talk to the backend  | `http://localhost:8000/api` |

> **Tip:** You can copy a `.env.example` (if provided) and fill in your secrets.

---

## 📦 Project Structure

```
.
├── .github/             # Github workflows
├── backend/           # FastAPI app, database models, routers
├── frontend/          # Streamlit app  
├── nginx/             # Nginx proxy configuration  
├── docs/              # Quality reports
├── docker-compose.yml  
├── run_quality_checks.sh
├── poetry.lock
├── pyproject.toml  
└── README.md
```

---

## 📊 Quality Metrics Analysis

We continuously validate these key quality attributes:

* **Maintainability:**

  * Code coverage ≥ 65 % (pytest + coverage)
  * Mutation score ≥ 70 % (mutmut)
  * Maintainability Index ≥ 70/100 (radon)
  * Zero lint warnings (ruff, flake8)

* **Performance:**

  * Lighthouse desktop score ≥ 90 (lhci)
  * API average response time ≤ 5000 ms at 50 Mb/s for heavy requests (locust)

* **Security:**

  * HTTPS-only transport (Nginx proxy)
  * BCrypt ≥ 12 rounds for password storage
  * Zero critical issues in static analysis (bandit)
  * SonarCloud Security Rating **A**

* **Reliability:**

  * Uptime ≥ 99 % over 1 week (UptimeRobot)
  * SonarCloud Reliability Rating **A**
  * Audit log rotation ≥ 24 h retention (end-to-end test)

Many of these checks are automated in our CI pipeline via `run_quality_checks.sh`.

---

## 📞 Contact

If you have any questions, feature requests, or run into issues, feel free to reach out:

* **Telegram:** [@LouayFarah](https://t.me/LouayFarah)
* **Email:** [louayfarah5@gmail.com](mailto:louayfarah5@gmail.com)

Happy reading! 📚



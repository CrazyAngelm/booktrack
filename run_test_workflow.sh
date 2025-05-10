#!/usr/bin/env bash
set -e

echo "Initializing directories…"
mkdir -p docs
mkdir -p docs/quality
mkdir -p docs/quality/maintainability
mkdir -p docs/quality/performance/locust
mkdir -p docs/quality/performance/lighthouse
mkdir -p docs/quality/security
mkdir -p backend/logs


echo
echo "======================================"
echo "1) Backend tests + coverage (≥ 65 %)"
echo "======================================"
cd backend
echo "> Running pytest with coverage on core/"
poetry run pytest tests/ \
  --cov=core \
  --cov-branch \
  --cov-report=term \
  --cov-report=html \
  --cov-fail-under=65 2>&1 \
  | tee ../docs/quality/maintainability/coverage_backend.txt

echo
echo "======================================"
echo "Fuzz Tests (Hypothesis)"
echo "======================================"
poetry run pytest tests/fuzz --maxfail=1 --disable-warnings -q \
  | tee ../docs/quality/maintainability/fuzz_tests.txt
cd ..

echo
echo "======================================"
echo "2) Frontend tests + coverage (≥ 60 %)"
echo "======================================"
cd frontend
echo "> Running pytest with coverage on app/"
poetry run pytest tests/ \
--cov=. \
  --cov-branch \
  --cov-report=term \
  --cov-report=html \
  --cov-fail-under=60 2>&1 \
  | tee ../docs/quality/maintainability/coverage_frontend.txt
cd ..

echo
echo "======================================"
echo "3) Mutation testing (mutmut)"
echo "======================================"
cd backend
echo "> Generating & running mutants"
poetry run mutmut run
echo "> Writing mutation report"
poetry run mutmut results > ../docs/quality/maintainability/mutation.txt
echo "> Cleaning up mutant files"
rm -rf mutants/
cd ..

echo
echo "======================================================="
echo "4) Maintainability Index (radon) for backend & frontend"
echo "======================================================="
echo "> Calculating MI on backend/core, routers, services, util, config, main.py and frontend/app.py"
poetry run radon mi \
  backend/core \
  backend/routers \
  backend/services \
  backend/util \
  backend/config \
  backend/main.py \
  frontend/app.py \
  -s --sort > docs/quality/maintainability/maintainability_index.txt

echo
echo "======================================"
echo "5) Linting with Ruff (no F401, F403)"
echo "======================================"
echo "> Running ruff check on the same files"
poetry run ruff check \
  backend/core \
  backend/routers \
  backend/services \
  backend/util \
  backend/config \
  backend/main.py \
  frontend/app.py \
  --ignore F401,F403

echo
echo "======================================"
echo "6) Linting with Flake8 (max 100 cols)"
echo "======================================"
echo "> Running flake8 with ignores and max-line-length=100"
poetry run flake8 \
  backend/core \
  backend/routers \
  backend/services \
  backend/util \
  backend/config \
  backend/main.py \
  --ignore F401,F403,W293,W291 \
  --max-line-length 100

echo
echo "======================================"
echo "7) Performance testing (Locust)"
echo "======================================"
cd backend
echo "> Running locust headlessly against http://localhost:8000"
poetry run locust -f locustfile.py --headless \
  --host http://localhost:8000 \
  -u 50 -r 10 \
  --run-time=60s \
  --csv=../docs/quality/performance/locust/report \
  --csv-full-history
cd ..

echo
echo "======================================"
echo "8) Performance testing (Lighthouse)"
echo "======================================"
echo "> Installing Lighthouse"
npm install --save-dev @lhci/cli@0.7
echo "> Running LHCI against http://localhost:8501"
npx lhci autorun --config=lighthouserc.json


echo
echo "======================================"
echo "9) Static security scan (Bandit)"
echo "======================================"
echo "> Running bandit and saving output to docs/quality/security/bandit.txt"
mkdir -p docs/quality/security
poetry run bandit -r backend/core backend/routers backend/services backend/util frontend/app.py \
  --exit-zero -lll 2>&1 | tee docs/quality/security/bandit.txt

if poetry run bandit -r backend/core backend/routers backend/services backend/util frontend/app.py --quiet --severity-level high | grep -q '>> Issue:'; then
  echo "::error ::Bandit found CRITICAL issues"
  exit 1
fi

echo
echo "All quality checks completed successfully!"

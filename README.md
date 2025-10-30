🧮 FastAPI Calculator — Module 8 (IS601)

A simple yet production-ready FastAPI calculator application demonstrating containerized REST API development, complete test coverage, structured logging, and CI/CD automation via GitHub Actions.

🚀 Run Locally

1️⃣ Clone the repository
git clone git@github.com
:jasonj2010/module8_is601.git
cd module8_is601

2️⃣ Create and activate a virtual environment
python -m venv venv
source venv/Scripts/activate # Windows (Git Bash)

or

source venv/bin/activate # Mac/Linux

3️⃣ Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

4️⃣ Run the FastAPI app
uvicorn main:app --reload

Then open your browser to:
👉 http://127.0.0.1:8000

👉 Interactive API docs: http://127.0.0.1:8000/docs

🧪 Running Tests

Run all tests (unit + integration + E2E):
pytest -q --cov=app --cov-report=term-missing

If E2E tests fail initially, install the Playwright browser engine:
python -m playwright install chromium
pytest -q

✅ Expect 29 tests passing.

🧾 Logging

Application logs are written to logs/app.log.
Each request, response, and exception is logged, for example:
2025-10-29 21:10:22 | INFO | fastapi-calculator | REQ POST /add
2025-10-29 21:10:22 | INFO | fastapi-calculator | ADD: 5 + 2 = 7
2025-10-29 21:10:22 | INFO | fastapi-calculator | RESP POST /add -> 200
Logging uses a RotatingFileHandler to keep log size manageable.

🔄 Continuous Integration (CI)

A GitHub Actions workflow at .github/workflows/ci.yml automatically runs on every push or pull request.
It performs environment setup (Python 3.12), dependency installation, Playwright browser install, and full testing with coverage.
View results under the Actions tab in GitHub.

🐳 Docker Support (Optional)

Build the Docker image:
docker build -t fastapi-calculator .

Run the container:
docker run -p 8000:8000 fastapi-calculator

Then open http://localhost:8000
 in your browser.

🧠 Key Features
Feature	Description
FastAPI App	Lightweight REST API with Pydantic validation
Structured Logging	Rotating file + console logging
Testing	Unit, integration, and end-to-end tests
CI Pipeline	Automated testing via GitHub Actions
100% Coverage	app/operations fully tested
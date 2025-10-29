import subprocess
import time
import requests
import sys
import os
import signal
import pytest
from playwright.sync_api import sync_playwright  # ✅ Added import

@pytest.fixture(scope='session')
def fastapi_server():
    """
    Start the FastAPI server with the SAME Python interpreter running pytest.
    Ensures imports (fastapi, uvicorn, etc.) resolve in your venv.
    """
    env = os.environ.copy()
    fastapi_process = subprocess.Popen([sys.executable, 'main.py'], env=env)

    server_url = 'http://127.0.0.1:8000/'
    timeout = 45  # generous for Windows
    start_time = time.time()
    server_up = False

    print("Starting FastAPI server...")

    while time.time() - start_time < timeout:
        try:
            response = requests.get(server_url)
            if response.status_code == 200:
                server_up = True
                print("FastAPI server is up and running.")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    if not server_up:
        fastapi_process.terminate()
        fastapi_process.wait(timeout=10)
        raise RuntimeError("FastAPI server failed to start within timeout period.")

    yield

    # Teardown
    if os.name == "nt":
        fastapi_process.terminate()
    else:
        fastapi_process.send_signal(signal.SIGINT)
    try:
        fastapi_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        fastapi_process.kill()


@pytest.fixture(scope="session")
def playwright_instance_fixture():
    """
    Fixture to manage Playwright's lifecycle.
    """
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance_fixture):
    """
    Fixture to launch a browser instance.
    """
    browser = playwright_instance_fixture.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """
    Fixture to create a new page for each test.
    """
    page = browser.new_page()
    yield page
    page.close()

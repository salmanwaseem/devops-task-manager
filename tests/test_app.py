"""Browser tests; run after Docker Compose is serving the app."""
import os
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


def test_homepage_title(driver):
    driver.get(BASE_URL)
    assert "DevOps Task Manager" in driver.title


def test_add_task_form_visible(driver):
    driver.get(BASE_URL)
    assert WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "task-input"))
    ).is_displayed()
    assert driver.find_element(By.ID, "add-task-btn").is_enabled()


def test_create_task(driver):
    driver.get(BASE_URL)
    unique_title = f"Selenium exam task {uuid.uuid4().hex[:8]}"
    driver.find_element(By.ID, "task-input").send_keys(unique_title)
    driver.find_element(By.ID, "add-task-btn").click()
    WebDriverWait(driver, 10).until(
        lambda d: any(
            el.text == unique_title
            for el in d.find_elements(By.CSS_SELECTOR, "#task-list .task-title")
        )
    )
    assert "added" in driver.find_element(By.ID, "success-message").text.lower()


def test_health_endpoint(driver):
    driver.get(BASE_URL + "/health")
    assert '"status": "ok"' in driver.page_source.lower() or '"status":"ok"' in driver.page_source.lower()

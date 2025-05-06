import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost:8501")
    yield driver
    driver.quit()


def test_open_search_tab(driver):
    tab = driver.find_element(
        By.XPATH,
        "//div[@role='tab' and text()='Search']"
    )
    tab.click()
    assert "Discover Books" in driver.page_source


def test_open_favourites_tab(driver):
    fav_tab = driver.find_element(
        By.XPATH, "//div[@role='tab' and text()='Favourites']"
    )
    fav_tab.click()
    assert "My Favourites" in driver.page_source


def test_open_reading_list_tab(driver):
    rl_tab = driver.find_element(
        By.XPATH,
        "//div[@role='tab' and text()='Reading List']"
    )
    rl_tab.click()
    assert "My Reading List" in driver.page_source


def test_open_dashboard_tab(driver):
    dash_tab = driver.find_element(
        By.XPATH,
        "//div[@role='tab' and text()='Dashboard']"
    )
    dash_tab.click()
    assert "Dashboard" in driver.page_source
    assert "Currently Reading" in driver.page_source
    assert "Completed" in driver.page_source

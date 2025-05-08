import pytest
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:8501"


# ---------- driver ----------
@pytest.fixture(scope="module")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")          # drop “new” for Chrome<115 or remove for headed mode
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def reset_session(driver):
    driver.get(BASE_URL)


# ============ 1. AUTH ============

@pytest.mark.parametrize(
    "email,pwd,expect_ok",
    [
        ("a@a.a", "aaaaaa", True),
        ("bademail", "short", False),
        ("", "", False),
    ],
)
def test_login(driver, email, pwd, expect_ok):
    driver.get(BASE_URL)
    WebDriverWait(driver, 15)
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//button[.='Logout']"))
        ).click()
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass
    email_in = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".st-key-login_email input"))
    )
    pwd_in = driver.find_element(By.CSS_SELECTOR, ".st-key-login_pwd input")

    email_in.clear(); email_in.send_keys(email)
    pwd_in.clear();   pwd_in.send_keys(pwd)

    login = driver.find_element(By.XPATH, "//button[.='Login']")
    login.click()
    time.sleep(1)
    login.click()
    print(email)
    if expect_ok:
        WebDriverWait(driver,15).until(
            EC.visibility_of_element_located((By.XPATH,".//h3[.//text()[contains(., 'Welcome')]]"))
        )
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//button[.='Logout']"))
        ).click()
    else:
        if login.get_attribute("disabled"):
            assert True
        else:
            WebDriverWait(driver,15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,".stAlert"))
            )


@pytest.mark.parametrize(
    "fn,ln,email,pwd1,pwd2,ok",
    [
        ("John","Doe","john@example.com","hunter2","hunter2",True),
        ("","Doe","john@example.com","hunter2","hunter2",False),
        ("John","","john@example.com","hunter2","hunter2",False),
        ("John","Doe","bademail","hunter2","hunter2",False),
        ("John","Doe","john@example.com","123","123",False),
        ("John","Doe","john@example.com","foo1","foo2",False),
    ],
)
def test_register(driver, fn, ln, email, pwd1, pwd2, ok):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//button[.='Logout']"))
        ).click()
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass
    WebDriverWait(driver,15).until(
        EC.visibility_of_element_located((By.XPATH, "//button[.='📝 Register']"))
    ).click()

    WebDriverWait(driver,15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".st-key-reg_name input"))
    ).send_keys(fn)
    driver.find_element(By.CSS_SELECTOR, ".st-key-reg_surname input").send_keys(ln)
    driver.find_element(By.CSS_SELECTOR, ".st-key-reg_email input").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, ".st-key-reg_pwd1 input").send_keys(pwd1)
    driver.find_element(By.CSS_SELECTOR, ".st-key-reg_pwd2 input").send_keys(pwd2)

    reg = driver.find_element(By.XPATH, "//button[.='Register']")
    reg.click()
    time.sleep(1)
    reg.click()

    if ok:
        WebDriverWait(driver,5).until(
            EC.visibility_of_element_located((By.XPATH,".//h3[.//text()[contains(., 'Welcome')]]"))
        )
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//button[.='Logout']"))
        ).click()
    else:
        if reg.get_attribute("disabled"):
            assert True
        else:
            WebDriverWait(driver,5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,".stError"))
            )


# helper to ensure we’re logged in for later tests
def _quick_login(driver):
    test_login(driver,"valid@example.com","correcthorsebatterystaple",True)


# ============ 2. SEARCH / PAGINATION / SORT ============

@pytest.mark.parametrize(
    "query,sort_order,trigger,expect_rows",
    [
        ("",      "Most downloaded","Next →", True),
        ("",      "Least downloaded","Next →", True),
        ("Alice", "Most downloaded","Search", True),
        ("NoSuchBookWillExist","Least downloaded","Search", False),
    ],
)
def test_search(driver, query, sort_order, trigger, expect_rows):
    _quick_login(driver)

    qbox = WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,".st-key-search_query input"))
    )
    qbox.clear(); qbox.send_keys(query)

    Select(driver.find_element(By.CSS_SELECTOR,".st-key-sort_order select"))\
        .select_by_visible_text(sort_order)
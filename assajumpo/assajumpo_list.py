import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--start-maximized")

# 크롬 드라이버 및 웹페이지 실행
driver = webdriver.Chrome(options=options)
driver.get('https://xn--v69ap5so3hsnb81e1wfh6z.com/grid')

# 업종 선택
driver.find_element(By.XPATH, '//*[@id="form_search"]/div[2]/div/div[3]/div[2]').click()
driver.find_element(By.XPATH, '//*[@id="tab_40"]/div[10]').click()
driver.find_element(By.XPATH, '//*[@id="form_search"]/div[2]/div/div[3]/div[2]').click()

# 스크롤할 div 선택자
scroll_container_selector = "#grid_list"

# 내부 스크롤 내리기 루프
last_height = driver.execute_script(f"return document.querySelector('{scroll_container_selector}').scrollHeight")

while True:
    driver.execute_script(f"""
        const container = document.querySelector('{scroll_container_selector}');
        container.scrollTop = container.scrollHeight;
    """)
    time.sleep(2)  # 콘텐츠 로딩 대기
    new_height = driver.execute_script(f"return document.querySelector('{scroll_container_selector}').scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 스크롤 후 항목 수집
items = driver.find_elements(By.CSS_SELECTOR, 'a.pointer.item')
print(f"총 {len(items)}개의 항목을 찾았습니다.")

for item in items:
    print(item.get_attribute('href'))

driver.quit()

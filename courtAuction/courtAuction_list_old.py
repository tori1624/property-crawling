import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')

# 크롬 드라이버 및 웹페이지 실행
driver = webdriver.Chrome(options=options)
driver.get('https://www.courtauction.go.kr/pgj/index.on')
time.sleep(3)

# 물건 상세 검색 이동
driver.find_element(By.XPATH, '//*[@id="mf_wq_uuid_260"]').click()

# 법원 목록 가져오기
court_list = driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_sbx_rletCortOfc"]/option')
courts = list(map(lambda x: x.text, court_list))[1:]

# 법원 지정
setCourt = Select(driver.find_element(By.ID, 'mf_wfm_mainFrame_sbx_rletCortOfc'))
setCourt.select_by_visible_text(courts[0])
driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_gdsDtlSrch"]').click()

# 법원별 물건 및 정보 가져오기
element_xpath = '//*[@id="mf_wfm_mainFrame_grd_gdsDtlSrchResult_cell_0_'

tmp_case = driver.find_elements(By.XPATH, f'{element_xpath}1"]/nobr')[0].text
court = tmp_case.split('\n')[0] # 법원
case_no = tmp_case # 사건번호

item_no = driver.find_elements(By.XPATH, f'{element_xpath}2"]/nobr')[0].text # 물건 번호
usage = driver.find_elements(By.XPATH, f'{element_xpath}8"]/nobr')[0].text # 용도
address = driver.find_elements(By.XPATH, f'{element_xpath}3"]/nobr/div/a')[0].text # 소재지

tmp_info = driver.find_elements(By.XPATH, f'{element_xpath}3"]/nobr/div/text')[0].text
info_strt = tmp_info[1:-1].split('\n')[0] # 내역_구조
info_area = tmp_info[1:-1].split('\n')[1] # 내역_면적

remarks = driver.find_elements(By.XPATH, f'{element_xpath}5"]/nobr')[0].text # 비고
appraisal_price = driver.find_elements(By.XPATH, f'{element_xpath}6"]/nobr')[0].text # 감정평가액
min_bid_price = driver.find_elements(By.XPATH, f'{element_xpath}9"]/nobr')[0].text # 최저매각가격

tmp_final = driver.find_elements(By.XPATH, f'{element_xpath}7"]/nobr')[0].text
court_div = tmp_final.split('\n')[0] # 담당계
sale_date = tmp_final.split('\n')[1] # 매각기일

status = driver.find_elements(By.XPATH, f'{element_xpath}10"]/nobr')[0].text # 진행상태

driver.quit()

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')

# 크롬 드라이버 및 웹페이지 실행
driver = webdriver.Chrome(options=options)
driver.get('https://www.jumpoline.com/')

# 웹페이지에서 element 가져오기
base_xpath = '//*[@id="content"]/div/div[1]/div[12]/div[3]/div/ul/'  # [Home] 스페셜 AD
jumpo_len = len(driver.find_elements(By.XPATH, f'{base_xpath}li'))

columns = ['ad_type', 'nocode', 't_mcate', 'region', 'floor', 'area', 'date', 'title', 'map_link', 'frc_name', 'premium',
           'frc_cost', 'mth_profit', 'mth_rate', 'premium_term', 'deposit', 'mth_fee', 'total_fee']
jumpo_df = pd.DataFrame(columns=columns)  # 빈 데이터 프레임

for i in range(jumpo_len):

    # element 경로
    element_xpath = os.path.join(base_xpath, f'li[{i+1}]/div/div/div[3]/')

    # 기본 정보
    nocode = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[1]/strong').text  # 매물번호
    t_mcate = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[2]/strong').text  # 업종
    region = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[2]').text[:-len(t_mcate)]  # 지역
    floor = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[3]/strong').text  # 층
    area = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[4]/strong').text  # 면적
    date = driver.find_element(By.XPATH, f'{element_xpath}div[1]/div/span[1]').text[11:]  # 실매물 주인확인 날짜
    hits = driver.find_element(By.XPATH, f'{element_xpath}div[1]/div/span[2]').text[6:]  # 조회수
    title = driver.find_element(By.XPATH, f'{element_xpath}h4').text  # 가게 이름

    # 지도 링크
    try:
        map_link = driver.find_element(By.XPATH, f'{element_xpath}a').get_attribute('href')
    except:
        map_link = ''

    # 가맹점 이름
    try:
        frc_name = driver.find_element(By.XPATH, f'{element_xpath}div[1]/a/span').text
    except:
        frc_name = ''

    # 가격 정보
    premium = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[1]/strong').text  # 권리금
    frc_cost = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[2]').text[5:]  # 가맹비용
    mth_profit = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[3]').text[4:]  # 월수익
    mth_rate = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[4]').text[5:]  # 월수익률

    standard = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[5]').text
    if '권리금 회수기간' in standard:
        premium_term = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[5]/strong').text  # 권리금 회수기간
        deposit = ''  # 보증금
        mth_fee = ''  # 월세
        total_fee = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[6]/span/strong').text  # 총투자액
    elif '보증금' in standard:
        premium_term = ''  # 권리금 회수기간
        deposit = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[5]/span[1]/strong').text  # 보증금
        mth_fee = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[5]/span[2]/strong').text  # 월세
        total_fee = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[5]/span[3]/strong').text  # 총투자액

    ad_type = '홈화면 스페셜 광고'

    # 데이터 프레임 병합
    tmp_list = [ad_type, nocode, t_mcate, region, floor, area, date, title, map_link, frc_name, premium, frc_cost,
                mth_profit, mth_rate, premium_term, deposit, mth_fee, total_fee]
    tmp_df = pd.DataFrame(data=[tmp_list], columns=columns)
    jumpo_df = pd.concat([jumpo_df, tmp_df])

# index 리셋
jumpo_df.reset_index(drop=True, inplace=True)

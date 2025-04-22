import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 업종 정보 불러오기
type_df = pd.read_csv('./type.csv', encoding='utf-8')  # 작업 경로 설정
type_df['scode'] = type_df['scode'].map(str)
type_df['scode'] = type_df['scode'].map(lambda x: '0'+x if (len(x) == 1) else x)

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')

# 업종별 크롤링
columns = ['ad_type', 'nocode', 't_mcate', 'region', 'floor', 'area', 'date', 'title', 'map_link', 'frc_name', 'premium',
           'frc_cost', 'mth_profit', 'mth_rate', 'premium_term', 'deposit', 'mth_fee', 'total_fee', 'contents_link']
jumpo_df = pd.DataFrame(columns=columns)  # 빈 데이터 프레임

for i in range(len(type_df)):

    # 업종 코드 할당
    mcode = type_df['mcode'][i]
    scode = type_df['scode'][i]

    # 크롬 드라이버 및 웹페이지 실행
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.jumpoline.com/_jumpo/jumpoListMaster.asp?mcode={mcode}&scode={scode}')
    time.sleep(5)

    # 프리미엄, 일반 광고 크롤링 경로 설정
    assum_len1 = len(driver.find_elements(By.XPATH, f'//*[@id="marketChargeListTable"]/div/ul/li'))
    assum_len2 = len(driver.find_elements(By.XPATH, f'//*[@id="marketChargeListTable"]/div[2]/ul/li'))

    if assum_len1 > 0 and assum_len2 > 0:
        base_xpath1 = '//*[@id="marketChargeListTable"]/div[2]/ul/'
    elif assum_len2 == 0:
        base_xpath1 = '//*[@id="marketChargeListTable"]/div/ul/'

    base_xpath = [base_xpath1,  # [업종] 프리미엄 매물광고
                  '//*[@id="marketListTable"]/ul/']  # [업종] 일반 매물광고
    jumpo_len = [len(driver.find_elements(By.XPATH, f'{base_xpath[0]}li')),
                 len(driver.find_elements(By.XPATH, f'{base_xpath[1]}li'))]

    # 웹페이지에서 element 가져오기
    for j in range(len(base_xpath)):

        page = 1

        while True: # 페이지를 끝까지 반복
            print(f"현재 페이지: {page}")

            k = 0

            while True: #for k in range(jumpo_len[j]):

                # element 경로
                element_xpath = os.path.join(base_xpath[j], f'li[{k+1}]/div/div/div[2]/')

                # 기본 정보
                try:
                    nocode = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[1]/strong').text  # 매물번호
                    k += 1
                except:
                    break
                t_mcate = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[2]/strong').text  # 업종
                region = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[2]').text[:-len(t_mcate)]  # 지역
                floor = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[3]/strong').text  # 층
                area = driver.find_element(By.XPATH, f'{element_xpath}div[1]/span[4]').text  # 면적
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
                try:
                    test = driver.find_element(By.XPATH, f'{element_xpath}p[3]/span[1]/strong').text
                    p = 3
                except:
                    p = 2

                premium = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[1]/strong').text  # 권리금
                frc_cost = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[2]').text[5:]  # 가맹비용
                mth_profit = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[3]').text[4:]  # 월수익
                mth_rate = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[4]').text[5:]  # 월수익률

                standard = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[5]').text
                if '권리금 회수기간' in standard:
                    premium_term = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[5]/strong').text  # 권리금 회수기간
                    deposit = ''  # 보증금
                    mth_fee = ''  # 월세
                    total_fee = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[6]/span/strong').text  # 총투자액
                elif '보증금' in standard:
                    premium_term = ''  # 권리금 회수기간
                    deposit = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[5]/span[1]/strong').text  # 보증금
                    mth_fee = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[5]/span[2]/strong').text  # 월세
                    total_fee = driver.find_element(By.XPATH, f'{element_xpath}p[{p}]/span[5]/span[3]/strong').text  # 총투자액

                # 크롤링 source
                ad_type = ['업종별 프리미엄 광고', '업종별 일반 광고'][j]

                # 매물 link
                jumpo_id = driver.find_element(By.XPATH, f'{element_xpath}h4').get_attribute('onclick').split(',')[1].strip("'\"")
                contents_link = f'https://www.jumpoline.com/_jumpo/jumpo_view.asp?webjofrsid={jumpo_id}'

                # 데이터 프레임 병합
                tmp_list = [ad_type, nocode, t_mcate, region, floor, area, date, title, map_link, frc_name, premium, frc_cost,
                            mth_profit, mth_rate, premium_term, deposit, mth_fee, total_fee, contents_link]
                tmp_df = pd.DataFrame(data=[tmp_list], columns=columns)

                jumpo_df = pd.concat([jumpo_df, tmp_df])

            # 페이지 반복
            if j == 0:
                break
            else:
                try:
                    idx = page

                    if 1 < page < 11: # 페이지 꼬임 방지 (2페이지로 넘어갈수록 a[{page}]가 변함)
                        driver.find_element(By.XPATH, f'//*[@id="dvPaging"]/div/div/a[2]/span').click()
                        time.sleep(3)  # 페이지 로딩 대기
                        idx = page
                    elif page >= 11:
                        idx = '12' if str(page)[-1] == '0' else str(int(str(page)[-1])+2)

                    next_page = driver.find_element(By.XPATH, f'//*[@id="dvPaging"]/div/div/a[{idx}]')
                    if '끝' in next_page.text:
                        print(f"{type_df['type1'][i]}-{type_df['type2'][i]} - 총 {page} 페이지 완료")
                        break
                    next_page.click()
                    page += 1
                    time.sleep(3)  # 페이지 로딩 대기
                except:
                    print(f"{type_df['type1'][i]}-{type_df['type2'][i]} - 총 {page} 페이지 완료")
                    break  # 다음 버튼이 없으면 종료

    print(f"{type_df['type1'][i]}-{type_df['type2'][i]} 크롤링 완료")
    driver.quit()

# index 리셋
jumpo_df.reset_index(drop=True, inplace=True)

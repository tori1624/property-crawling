import time
import random
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


def auction_list():

    # 빈 데이터 프레임 생성
    columns = [
        'main_category', 'court', 'case_no(line)', 'item_no', 'usage', 'address', 'info', 'remarks', 'appraisal_price',
        'min_bid_price', 'court_div', 'sale_date', 'status', 'case_no', 'search_year', 'search_no'
    ]

    auction_df = pd.DataFrame(columns=columns)  # 빈 데이터 프레임

    # 크롬 드라이버 옵션
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--start-maximized")

    # 크롬 드라이버 및 웹페이지 실행
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.courtauction.go.kr/pgj/index.on')

    # 물건 상세 검색 이동
    driver.find_element(By.XPATH, '//*[@id="mf_wq_uuid_260"]').click()
    time.sleep(random.uniform(1, 1.5))

    # 용도 목록 가져오기
    use_elements = driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_sbx_rletLclLst"]/option')
    use_list = list(map(lambda x: x.text, use_elements))[1:]

    # 경매 정보 크롤링
    for use in use_list:

        # 법원 전체 지정
        setCourt = Select(driver.find_element(By.ID, 'mf_wfm_mainFrame_sbx_rletCortOfc'))
        setCourt.select_by_visible_text('전체')

        # 용도 지정
        setUse = Select(driver.find_element(By.ID, 'mf_wfm_mainFrame_sbx_rletLclLst'))
        setUse.select_by_visible_text(use)
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_gdsDtlSrch"]').click()
        time.sleep(random.uniform(1, 1.5))

        # 용도별 마지막 페이지 추출
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_pgl_gdsDtlSrchPage_nextPage_btn"]/button').click()
        time.sleep(random.uniform(1, 1.5))
        last_page = int(driver.find_elements(By.XPATH, '//ul[@class="w2pageList_ul"]/li')[-3].text)
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_pgl_gdsDtlSrchPage_prevPage_btn"]/button').click()
        time.sleep(random.uniform(1, 1.5))

        # 용도별 물건 및 정보 가져오기
        page = 1

        while True:
            try:
                print(f'{use} - 현재 페이지: {page}')

                rows = driver.find_elements(By.XPATH, '//table[@id="mf_wfm_mainFrame_grd_gdsDtlSrchResult_body_table"]/tbody/tr')

                merged_data = []

                for i in range(0, len(rows), 2):
                    upper_cells = rows[i].find_elements(By.TAG_NAME, "td")
                    upper_data = [cell.text.strip() for cell in upper_cells]

                    if i + 1 < len(rows):
                        lower_cells = rows[i + 1].find_elements(By.TAG_NAME, "td")
                        lower_data = [cell.text.strip() for cell in lower_cells]
                    else:
                        lower_data = []

                    merged_row = upper_data + lower_data
                    merged_data.append(merged_row)

                tmp_columns = [
                    'case_no(total)', 'case_no(line)', 'item_no', 'address/info', 'map', 'remarks', 'appraisal_price',
                    'court_div/sale_date', 'usage', 'min_bid_price', 'status'
                ]

                df = pd.DataFrame(merged_data, columns=tmp_columns)
                df = df[df['map'] != '']

                # 추가 전처리
                df['main_category'] = use
                df['court'] = df['case_no(line)'].str.split('\n').str[0]  # 법원
                df['address'] = df['address/info'].str.split('\n').str[0]  # 소재지
                df['info'] = df['address/info'].str.split('[').str[1].str[:-1]  # 내역
                df['court_div'] = df['court_div/sale_date'].str.split('\n').str[0]  # 담당계
                df['sale_date'] = df['court_div/sale_date'].str.split('\n').str[1]  # 매각기일

                # 상세 링크 접속 정보를 위한 전처리
                df['case_no'] = df['case_no(line)'].str.split('\n').str[1]
                df['search_year'] = df['case_no'].str.split('타경').str[0]
                df['search_no'] = df['case_no'].str.split('타경').str[1]

                sorted_df = df[columns]

                # 결측치 대체
                cols_to_fill = sorted_df.columns.difference(['remarks', 'search_year', 'search_no'])

                for col in cols_to_fill:
                    sorted_df[col] = sorted_df[col].replace('', np.nan)  # 빈 문자열을 NaN으로
                    sorted_df[col] = sorted_df[col][::-1].bfill()[::-1]  # 아래쪽 값으로 채움

                # 데이터 병합
                auction_df = pd.concat([auction_df, sorted_df])

                # 페이지 이동
                if page == last_page:  # 마지막 페이지일 경우 종료
                    print(f'{use} - 총 {page} 완료')
                    break
                elif page % 500 == 0:  # 500 단위 페이지일 경우, 3분 쉬고 다음 페이지 목록으로 이동
                    time.sleep(180)
                    driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_pgl_gdsDtlSrchPage_next_btn"]/button').click()
                    page += 1
                elif page % 10 == 0:  # 10 단위 페이지일 경우, 다음 페이지 목록으로 이동
                    driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_pgl_gdsDtlSrchPage_next_btn"]/button').click()
                    page += 1
                    time.sleep(random.uniform(0.5, 1))
                else:  # 그 외에는 다음 페이지로 이동
                    page += 1
                    driver.find_elements(By.XPATH, f'//*[@id="mf_wfm_mainFrame_pgl_gdsDtlSrchPage_page_{page}"]')[0].click()
                    time.sleep(random.uniform(0.5, 1))

            except Exception as e:
                print("Error:", e)
                continue

        # 물건 상세 검색으로 돌아가기
        driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
        time.sleep(10)

    driver.quit()

    # index 리셋
    auction_df.reset_index(drop=True, inplace=True)

    # 데이터 저장 (DB 저장으로 변경 필요)
    auction_df.to_csv('auction_df.csv', index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    auction_list()

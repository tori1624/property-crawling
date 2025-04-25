import os
import time
import random
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 사건 번호 가져오기 (추후에는 DB 활용 방법으로 코드 수정 필요)
wd = {working directory}
auction_list = pd.read_csv(os.path.join(wd, 'auction_df.csv'), encoding='utf-8-sig')
search_info = auction_list[['court', 'case_no', 'search_year', 'search_no']].dropna(axis=0, ignore_index=True)
search_info = search_info.drop_duplicates(['case_no'], keep='first', ignore_index=True)
search_info.update({col: search_info[col].astype(int).astype(str) for col in ['search_year', 'search_no']})

test_search = search_info.iloc[:100, :]

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')

# 크롬 드라이버 및 웹페이지 실행
driver = webdriver.Chrome(options=options)
driver.get('https://www.courtauction.go.kr/pgj/index.on')

# 물건 상세 검색 이동
driver.find_element(By.XPATH, '//*[@id="mf_wq_uuid_260"]').click()
time.sleep(random.uniform(0.5, 1))

data_list = []

for i in range(len(test_search)):
    # 법원 지정
    setCourt = Select(driver.find_element(By.ID, 'mf_wfm_mainFrame_sbx_rletCortOfc'))
    setCourt.select_by_visible_text(test_search['court'][i])

    # 사건 번호 지정
    setYear = Select(driver.find_element(By.ID, 'mf_wfm_mainFrame_sbx_rletCsYear'))
    setYear.select_by_visible_text(test_search['search_year'][i])

    setNo = driver.find_element(By.ID, 'mf_wfm_mainFrame_ibx_rletCsNo')
    setNo.clear()
    setNo.send_keys(test_search['search_no'][i])

    # 물건 검색
    driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_gdsDtlSrch"]').click()
    time.sleep(random.uniform(0.5, 1))

    try:
        # 상세페이지 이동
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_grd_gdsDtlSrchResult_cell_0_3"]/nobr/div/a').click()
        time.sleep(random.uniform(2, 2.5))
    except:
        # 물건 상세 검색으로 돌아가기
        try:
            driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
            time.sleep(random.uniform(1, 1.5))
            continue
        except:
            time.sleep(random.uniform(1, 1.5))
            driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
            time.sleep(random.uniform(1, 1.5))
            continue

    # 물건 정보 크롤링
    data = {
        'case_no': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchUserCsNo').text,
        'item_no': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchGdsSeq').text,
        'usage': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchGdsKnd').text,
        'appraisal_price': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchAeeEvlAmt').text,
        'min_bid_price': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchlwsDspsl').text,
        'bid_method': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchBidDvs').text,
        'sale_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchDspslDxdy').text,
        'item_remarks': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchRmk').text,
        'address': driver.find_element('id', 'mf_wfm_mainFrame_gen_lstSt_0_spn_gdsDtlSrchStCtt').text,
        'court_department': (
            driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchCortNm').text + ' ' +
            driver.find_element('id', 'mf_wfm_mainFrame_spn_cortAuctnJdbnNm').text.replace('|', '').strip()
        ),
        'case_filed_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchCsRcptYmd').text,
        'auction_start_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchAuctnStrtDay').text,
        'claim_deadline': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchDstrtDemnLstprd').text,
        'claim_amount': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchClmAmt').text
    }

    data_list.append(data)

    print(f"{test_search['court'][i]} {test_search['case_no'][i]} 완료")

    # 물건 상세 검색으로 돌아가기
    driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_trigger1"]')[0].click()
    time.sleep(random.uniform(1.5, 2))
    driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
    time.sleep(random.uniform(1, 1.5))

df = pd.DataFrame(data_list)

driver.quit()

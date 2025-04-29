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
wd = 'C:/Users/YU.LEE/PycharmProjects/PythonProject/skykey/'
auction_list = pd.read_csv(os.path.join(wd, 'auction_df.csv'), encoding='utf-8-sig')
search_info = auction_list[['court', 'case_no', 'search_year', 'search_no', 'sale_date']].dropna(axis=0, ignore_index=True)
search_info = search_info.drop_duplicates(['case_no'], keep='first', ignore_index=True)
search_info.update({col: search_info[col].astype(int).astype(str) for col in ['search_year', 'search_no']})

test_search = search_info.loc[search_info['sale_date'] == '2025.05.02', :].reset_index(drop=True)

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless')

# 크롬 드라이버 및 웹페이지 실행
driver = webdriver.Chrome(options=options)
driver.get('https://www.courtauction.go.kr/pgj/index.on')

# 물건 상세 검색 이동
driver.find_element(By.XPATH, '//*[@id="mf_wq_uuid_260"]').click()
time.sleep(random.uniform(0.5, 1))

# 빈 데이터 생성
# 1) 기본 물건 정보
basicData_list = []

# 2) 기일 내역
dateData_columns = ['case_no', 'date', 'date_type', 'place', 'min_bid_price', 'result']
date_df = pd.DataFrame(columns=dateData_columns)

# 3) 목록 내역
listData_columns = ['case_no', 'list_no', 'list_type', 'details']
list_df = pd.DataFrame(columns=listData_columns)

# 4) 인근매각통계
saleStat_columns = ['case_no', 'period', 'sale_count', 'avg_appraisal', 'avg_sale_price', 'sale_price_rate', 'avg_unsuccessful']
saleStat_df = pd.DataFrame(columns=saleStat_columns)

# 5) 배당요구종기내역
claimDead_columns = ['case_no', 'list_no', 'address', 'claim_deadline']
claimDead_df = pd.DataFrame(columns=claimDead_columns)

# 6) 당사자내역
party_columns = ['case_no', 'party_type1', 'party_name1', 'party_type2', 'party_name2']
party_df = pd.DataFrame(columns=party_columns)

# 7) 문건처리내역
docs_columns = ['case_no', 'received_date', 'receipt_detail', 'receipt_result']
docs_df = pd.DataFrame(columns=docs_columns)

# 8) 송달내역
service_columns = ['case_no', 'service_date', 'service_detail', 'service_result']
service_df = pd.DataFrame(columns=service_columns)


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

    # 기본 물건 정보 크롤링
    basicData = {
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

    basicData_list.append(basicData)

    # 기일 내역 크롤링
    dateTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_grd_dxdyDtsLst_body_table')
    dateRows = dateTable.find_elements(By.TAG_NAME, 'tr')

    tmp_dateData = []
    for row in dateRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:  # 셀이 있는 경우에만
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_dateData.append(row_data)

    tmp_date_df = pd.DataFrame(tmp_dateData, columns=dateData_columns)
    date_df = pd.concat([date_df, tmp_date_df])

    # 목록 내역 크롤링
    listTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_wq_uuid_987_body_table')
    listRows = listTable.find_elements(By.TAG_NAME, 'tr')

    tmp_listData = []
    for row in listRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_listData.append(row_data)

    tmp_list_df = pd.DataFrame(tmp_listData, columns=listData_columns)
    list_df = pd.concat([list_df, tmp_list_df])

    # 인근매각통계 크롤링
    saleStatTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_wq_uuid_1000_body_table')
    saleStatRows = saleStatTable.find_elements(By.TAG_NAME, 'tr')

    tmp_saleStat = []
    for row in saleStatRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_saleStat.append(row_data)

    tmp_saleStat_df = pd.DataFrame(tmp_saleStat, columns=saleStat_columns)
    saleStat_df = pd.concat([saleStat_df, tmp_saleStat_df])

    # 사건상세조회 클릭
    driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_moveCsDtl"]').click()
    time.sleep(random.uniform(0.5, 1))

    # 배당요구종기내역 크롤링
    claimDeadTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_grd_dstrtDemnDts_body_table')
    claimDeadRows = claimDeadTable.find_elements(By.TAG_NAME, 'tr')

    tmp_claimDead = []
    for row in claimDeadRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_claimDead.append(row_data)

    tmp_claimDead_df = pd.DataFrame(tmp_claimDead, columns=claimDead_columns)
    claimDead_df = pd.concat([claimDead_df, tmp_claimDead_df])

    # 당사자내역 크롤링
    partyTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_grd_ttt_body_tbody')
    partyRows = partyTable.find_elements(By.TAG_NAME, 'tr')

    tmp_party = []
    for row in partyRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_party.append(row_data)

    tmp_party_df = pd.DataFrame(tmp_party, columns=party_columns)
    party_df = pd.concat([party_df, tmp_party_df])

    # 문건/송달내역 클릭
    driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_tac_srchRsltDvs_tab_tabs3_tabHTML"]').click()
    time.sleep(random.uniform(0.5, 1))

    # 문건처리내역 크롤링
    docsTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_wfm_ofdocDlvrDts_wq_uuid_1514_body_table')
    docsRows = docsTable.find_elements(By.TAG_NAME, 'tr')

    tmp_docs = []
    for row in docsRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_docs.append(row_data)

    tmp_docs_df = pd.DataFrame(tmp_docs, columns=docs_columns)
    docs_df = pd.concat([docs_df, tmp_docs_df])

    # 송달내역 크롤링
    serviceTable = driver.find_element(By.ID, 'mf_wfm_mainFrame_wfm_ofdocDlvrDts_wq_uuid_1517_body_table')
    serviceRows = serviceTable.find_elements(By.TAG_NAME, 'tr')

    tmp_service = []
    for row in serviceRows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            row_data = [test_search['case_no'][i]] + [cell.text.strip() for cell in cells]
            tmp_service.append(row_data)

    tmp_service_df = pd.DataFrame(tmp_service, columns=service_columns)
    service_df = pd.concat([service_df, tmp_service_df])

    print(f"{test_search['court'][i]} {test_search['case_no'][i]} 완료")

    # 물건 상세 검색으로 돌아가기
    driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_trigger1"]')[0].click()
    time.sleep(random.uniform(1.5, 2))
    driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
    time.sleep(random.uniform(1, 1.5))

basic_df = pd.DataFrame(basicData_list)

driver.quit()

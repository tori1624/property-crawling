import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from auction.crawling_utils import crawling_table, crawling_car_detail

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def auction_info():
    # 사건 번호 가져오기 (추후에는 DB 활용 방법으로 코드 수정 필요)
    wd = 'C:/Users/YU.LEE/PycharmProjects/PythonProject/skykey/data'
    auction_list = pd.read_csv(os.path.join(wd, 'auction_df.csv'), encoding='utf-8-sig')
    search_info = auction_list[['court', 'case_no', 'search_year', 'search_no', 'sale_date']].dropna(axis=0, ignore_index=True)
    search_info = search_info.drop_duplicates(['case_no'], keep='first', ignore_index=True)
    search_info.update({col: search_info[col].astype(int).astype(str) for col in ['search_year', 'search_no']})
    test_search = search_info

    # 크롬 드라이버 옵션
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--start-maximized")

    # 크롬 드라이버 및 웹페이지 실행
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.courtauction.go.kr/pgj/index.on')

    # 물건 상세 검색 이동
    driver.find_element(By.XPATH, '//*[@id="mf_wq_uuid_260"]').click()
    time.sleep(random.uniform(0.5, 1))

    # 빈 데이터 생성
    basicData_list = [] # 기본 물건 정보

    crawling_infos = {
        'date': { # 기일내역
            'columns': ['case_no', 'date', 'date_type', 'place', 'min_bid_price', 'result'],
            'table_summary': "//table[@summary='기일내역']",
            'df': pd.DataFrame()
        },
        'list': { # 목록내역
            'columns': ['case_no', 'list_no', 'list_type', 'details'],
            'table_summary': "//table[@summary='목록내역']",
            'df': pd.DataFrame()
        },
        'car': { # 물건내역
            'columns': ['case_no', 'list_no', 'appraisal_price', 'car_name', 'car_type', 'registration_no', 'year',
                        'manufacturer', 'fuel_type', 'transmission', 'engine_type', 'approval_no', 'vin', 'displacement',
                        'mileage', 'storage_place'],
            'table_summary': "//table[@summary='물건내역']",
            'df': pd.DataFrame()
        },
        'saleStat': { # 인근매각통계
            'columns': ['case_no', 'period', 'sale_count', 'avg_appraisal', 'avg_sale_price', 'sale_price_rate', 'avg_unsuccessful'],
            'table_summary': "//table[@summary='인근매각통계']",
            'df': pd.DataFrame()
        },
        'saleItem': { # 인근매각물건
            'columns': ['case_no', 'near_case_no', 'usage', 'address/info', 'appraisal_price', 'sale_month', 'sale_price'],
            'table_summary': "//table[@summary='인근매각물건']",
            'df': pd.DataFrame()
        },
        'claimDead': { # 배당요구종기내역
            'columns': ['case_no', 'list_no', 'address', 'claim_deadline'],
            'table_summary': "//table[@summary='배당요구 종기내역']",
            'df': pd.DataFrame()
        },
        'party': { # 당사자 내역
            'columns': ['case_no', 'party_type1', 'party_name1', 'party_type2', 'party_name2'],
            'table_summary': "//table[@summary='당사자 내역']",
            'df': pd.DataFrame()
        },
        'docs': { # 문건처리내역
            'columns': ['case_no', 'received_date', 'receipt_detail', 'receipt_result'],
            'table_summary': "//table[@summary='문건처리 내역']",
            'df': pd.DataFrame()
        },
        'service': { # 송달내역
            'columns': ['case_no', 'service_date', 'service_detail', 'service_result'],
            'table_summary': "//table[@summary='송달 내역']",
            'df': pd.DataFrame()
        }
    }


    # 크롤링 진행
    for i in range(len(test_search)):

        case_no = test_search['court'][i] + ' ' + test_search['case_no'][i]

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
        time.sleep(random.uniform(1, 1.5))

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
            'case_no': case_no,
            'item_no': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchGdsSeq').text,
            'usage': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchGdsKnd').text,
            'appraisal_price': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchAeeEvlAmt').text,
            'min_bid_price': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchlwsDspsl').text,
            'bid_method': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchBidDvs').text,
            'sale_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchDspslDxdy').text,
            'item_remarks': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchRmk').text,
            'court_department': (
                driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchCortNm').text + ' ' +
                driver.find_element('id', 'mf_wfm_mainFrame_spn_cortAuctnJdbnNm').text.replace('|', '').strip()
            ),
            'case_filed_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchCsRcptYmd').text,
            'auction_start_date': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchAuctnStrtDay').text,
            'claim_deadline': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchDstrtDemnLstprd').text,
            'claim_price': driver.find_element('id', 'mf_wfm_mainFrame_spn_gdsDtlSrchClmAmt').text
        }

        # 감정평가서 링크 크롤링
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_aeeWevl1"]').click()

        iframe = driver.find_element(By.ID, 'sbx_iframeTest')
        driver.switch_to.frame(iframe)
        time.sleep(random.uniform(0.5, 1))
        basicData['appraisal_pdf'] = driver.find_element(By.TAG_NAME, 'iframe').get_attribute('src')
        driver.switch_to.default_content()
        time.sleep(random.uniform(0.2, 0.3))
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        # 매각물건명세서 링크 크롤링
        try:
            driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_dspslGdsSpcfc1"]').click()
            time.sleep(random.uniform(0.2, 0.3))
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(random.uniform(0.2, 0.3))
            basicData['saleItem_url'] = driver.current_url
            driver.switch_to.window(driver.window_handles[0])
        except:
            basicData['saleItem_url'] = ''
            print(f'{case_no} 매각물건명세서 없음')

        basicData_list.append(basicData)

        # 기일내역 크롤링
        crawling_table(driver, case_no, crawling_infos['date'])

        # 목록내역 크롤링
        try:
            crawling_table(driver, case_no, crawling_infos['list'])
        except:
            crawling_car_detail(driver, case_no, crawling_infos['car'])

        # 인근매각통계 크롤링
        crawling_table(driver, case_no, crawling_infos['saleStat'])

        # 인근매각물건 크롤링
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_tac_aroundGdsExm_tab_tabs2_tabHTML"]').click()
        time.sleep(random.uniform(0.2, 0.5))
        crawling_table(driver, case_no, crawling_infos['saleItem'])

        # 사건상세조회 클릭
        driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_moveCsDtl"]').click()
        time.sleep(random.uniform(0.5, 1))

        # 배당요구종기내역 크롤링
        crawling_table(driver, case_no, crawling_infos['claimDead'])

        # 당사자내역 크롤링
        crawling_table(driver, case_no, crawling_infos['party'])

        # 문건/송달내역 클릭
        try:
            driver.find_element(By.XPATH, '//*[@id="mf_wfm_mainFrame_tac_srchRsltDvs_tab_tabs3_tabHTML"]').click()
            time.sleep(random.uniform(0.5, 1))

        except:
            print(f"{test_search['court'][i]} {test_search['case_no'][i]} 문건/송달내역 크롤링 실패")
            # 물건 상세 검색으로 돌아가기
            driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevBtn"]')[0].click()
            time.sleep(random.uniform(1, 1.5))
            driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_btn_prevPage"]')[0].click()
            time.sleep(random.uniform(0.5, 1))
            continue

        # 문건처리내역 크롤링
        crawling_table(driver, case_no, crawling_infos['docs'])

        # 송달내역 크롤링
        crawling_table(driver, case_no, crawling_infos['service'])

        print(f"{test_search['court'][i]} {test_search['case_no'][i]} 완료")

        # 물건 상세 검색으로 돌아가기
        driver.find_elements(By.XPATH, '//*[@id="mf_wfm_mainFrame_wfm_sideMenu_spn_gdsDtlSrch"]')[0].click()
        time.sleep(random.uniform(1, 1.5))

    basic_df = pd.DataFrame(basicData_list)

    driver.quit()

    # 데이터 저장 (DB 저장으로 변경 필요)
    basic_df.to_csv('detailInfo_basic.csv', index=False, encoding='utf-8-sig')
    crawling_infos['date']['df'].to_csv('detailInfo_date.csv', index=False, encoding='utf-8-sig')
    crawling_infos['list']['df'].to_csv('detailInfo_list.csv', index=False, encoding='utf-8-sig')
    crawling_infos['saleStat']['df'].to_csv('detailInfo_saleStat.csv', index=False, encoding='utf-8-sig')
    crawling_infos['saleItem']['df'].to_csv('detailInfo_saleItem.csv', index=False, encoding='utf-8-sig')
    crawling_infos['claimDead']['df'].to_csv('detailInfo_claim.csv', index=False, encoding='utf-8-sig')
    crawling_infos['party']['df'].to_csv('detailInfo_party.csv', index=False, encoding='utf-8-sig')
    crawling_infos['docs']['df'].to_csv('detailInfo_docs.csv', index=False, encoding='utf-8-sig')
    crawling_infos['service']['df'].to_csv('detailInfo_service.csv', index=False, encoding='utf-8-sig')
    crawling_infos['car']['df'].to_csv('detailInfo_car.csv', index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    auction_info()

import pandas as pd
from selenium.webdriver.common.by import By


def crawling_table(driver, case_no, table_info):
    table = driver.find_element(By.XPATH, table_info['table_summary'])
    rows = table.find_elements(By.TAG_NAME, 'tr')

    tmp_data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:  # 셀이 있는 경우에만
            row_data = [case_no] + [cell.text.strip() for cell in cells]
            tmp_data.append(row_data)

    tmp_df = pd.DataFrame(tmp_data, columns=table_info['columns'])
    table_info['df'] = pd.concat([table_info['df'], tmp_df], ignore_index=True)

def crawling_car_detail(driver, case_no, table_info):
    table = driver.find_element(By.XPATH, table_info['table_summary'])
    rows = table.find_elements(By.TAG_NAME, 'tr')

    data_dict = {'case_no': case_no}
    for row in rows:
        ths = row.find_elements(By.TAG_NAME, 'th')
        tds = row.find_elements(By.TAG_NAME, 'td')
        for th, td in zip(ths, tds):
            key = th.text.strip()
            val = td.text.strip()
            if key:  # 빈 key 무시
                data_dict[key] = val

    tmp_df = pd.DataFrame([data_dict])
    tmp_df.columns = table_info['columns']
    table_info['df'] = pd.concat([table_info['df'], tmp_df], ignore_index=True)

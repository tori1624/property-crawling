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

# 업종 정보
main_base = '//*[@id="form_search"]/div[2]/div/div[3]/div[3]/div/ul/'

upjong_infos = {
    'food': { # 외식업
        'main': os.path.join(main_base, 'li[1]'),
        'sub': "//*[@id='tab_40']/div[1]"
    },
    'service': { # 서비스업
        'main': os.path.join(main_base, 'li[2]'),
        'sub': "//*[@id='tab_25']/div[1]"
    },
    'retail': { # 도/소매업
        'main': os.path.join(main_base, 'li[3]'),
        'sub': "//*[@id='tab_29']/div[1]"
    },
    'art_sport': { # 예술/스포츠/시설업
        'main': os.path.join(main_base, 'li[4]'),
        'sub': "//*[@id='tab_32']/div[1]"
    },
    'education': { # 교육/학원업
        'main': os.path.join(main_base, 'li[5]'),
        'sub': "//*[@id='tab_80']/div[1]"
    },
    'lodging': { # 숙박업
        'main': os.path.join(main_base, 'li[6]'),
        'sub': "//*[@id='tab_86']/div[1]"
    }
}


# 업종별 크롤링
assajumpo_df = pd.DataFrame()

for i in range(len(upjong_infos)):

    # 업종 선택
    driver.find_element(By.XPATH, '//*[@id="form_search"]/div[2]/div/div[3]/div[2]').click()

    if i > 0:
        driver.find_element(By.XPATH, upjong_infos[list(upjong_infos.keys())[i-1]]['main']).click()
        driver.find_element(By.XPATH, upjong_infos[list(upjong_infos.keys())[i-1]]['sub']).click()

    driver.find_element(By.XPATH, upjong_infos[list(upjong_infos.keys())[i]]['main']).click()
    driver.find_element(By.XPATH, upjong_infos[list(upjong_infos.keys())[i]]['sub']).click()
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
        time.sleep(1)  # 콘텐츠 로딩 대기
        new_height = driver.execute_script(f"return document.querySelector('{scroll_container_selector}').scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 스크롤 후 항목 수집
    items = driver.find_elements(By.CSS_SELECTOR, 'a.pointer.item')
    print(f'{list(upjong_infos.keys())[i]} 총 {len(items)}개의 항목 존재')

    data = []

    for item in items:
        try:
            category = item.find_element(By.CSS_SELECTOR, '.data-category').text.strip()
            top_etcs = item.find_elements(By.CSS_SELECTOR, '.top_etcs')
            floor = top_etcs[0].text.strip()
            area = top_etcs[2].text.strip()

            # 가격 정보
            price_spans = item.find_elements(By.CSS_SELECTOR, '.data-price .price_span')
            try:
                price_index = price_spans.index(
                    item.find_element(By.XPATH, ".//span[contains(text(),'월세')]/following-sibling::span")
                )
                if price_index == 3:
                    deposit = price_spans[0].text.strip() + price_spans[1].text.strip() + price_spans[2].text.strip()
                    rent = price_spans[3].text.strip() + price_spans[4].text.strip()
                else:
                    deposit = price_spans[0].text.strip() + price_spans[1].text.strip()
                    rent = price_spans[2].text.strip() + price_spans[3].text.strip()
            except:
                deposit = price_spans[0].text.strip() + price_spans[1].text.strip()
                rent = ''

            # 권리금은 무권리금일 경우 처리 필요
            try:
                premium_tag = item.find_element(By.CSS_SELECTOR, '.price_block.detail_0.price_premium')
                premium_index = price_spans.index(
                    item.find_element(By.XPATH, ".//span[contains(text(),'권리금')]/following-sibling::span")
                )
                try:
                    premium = price_spans[premium_index].text.strip() + price_spans[premium_index + 1].text.strip() + price_spans[premium_index + 2].text.strip()
                except:
                    premium = price_spans[premium_index].text.strip() + price_spans[premium_index + 1].text.strip()
            except:
                premium = item.find_element(By.CSS_SELECTOR, '.price_span.price_premium_no.m-r-xs').text.strip()

            # 매출과 수익
            try:
                sales_info = item.find_element(By.CSS_SELECTOR, '.data-sales').text.strip()
                sales, profit = sales_info.replace('월매출', '').replace('월수익', '').replace(' ', '').split('/')
            except:
                sales = ''
                profit = ''

            # 링크
            href = item.get_attribute('href')

            data.append({
                'category': category,
                'floor': floor,
                'area': area,
                'deposit': deposit,
                'rent': rent,
                'premium': premium,
                'sales': sales,
                'profit': profit,
                'url': href
            })

        except Exception as e:
            print("Error parsing item:", e)
            continue

    print(f'{list(upjong_infos.keys())[i]} 크롤링 완료')

    # 데이터 병합
    tmp_df = pd.DataFrame(data)
    dup_df = tmp_df.drop_duplicates(['url'], keep='first', ignore_index=True)

    assajumpo_df = pd.concat([assajumpo_df, dup_df])

driver.quit()

# index 리셋
assajumpo_df.reset_index(drop=True, inplace=True)

# main/sub category 분리
assajumpo_df[['main_category', 'sub_category']] = assajumpo_df['category'].apply(
    lambda x: pd.Series(x.split('|')) if '|' in x else pd.Series([x, ''])
)

assajumpo_df['main_category'] = assajumpo_df['main_category'].str.strip()
assajumpo_df['sub_category'] = assajumpo_df['sub_category'].str.strip()

assajumpo_df.loc[assajumpo_df['main_category'].str.contains('도'), 'main_category'] = '도/소매업'
assajumpo_df.loc[assajumpo_df['main_category'].str.contains('예'), 'main_category'] = '예술/스포츠/시설업'
assajumpo_df.loc[assajumpo_df['main_category'].str.contains('교'), 'main_category'] = '교육/학원업'

# 데이터 저장
assajumpo_df.to_csv('assajumpo_df.csv', index=False, encoding='utf-8-sig')

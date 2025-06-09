import re
import time
import requests
import pandas as pd

# url 및 header 설정
url = "https://xn--v69ap5so3hsnb81e1wfh6z.com/item/get_item_json/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://xn--v69ap5so3hsnb81e1wfh6z.com",
    "Referer": "https://xn--v69ap5so3hsnb81e1wfh6z.com/map",
    "X-Requested-With": "XMLHttpRequest"
}

# 크롤링 진행
results = []
jumpo_df = pd.DataFrame()

for dong_id in range(1, 5500):

    payload = {"dong_id": str(dong_id)}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=5)
        status = response.status_code
        response_df = pd.DataFrame(response.json())
        data = response_df.empty
        tmp_df = pd.json_normalize(response_df['item'])

    except Exception as e:
        status = f"error: {str(e)}"

    results.append({
        "dong_id": dong_id,
        "status_code": status,
        "data_empty": data
    })

    jumpo_df = pd.concat([jumpo_df, tmp_df], ignore_index=True)

    print(f'{dong_id}: {status}, {data}')

    # 서버에 과부하 주지 않도록 약간 대기
    time.sleep(0.5)

# status 결과를 Data Frame으로 변환 (크롤링 확인용)
df_status = pd.DataFrame(results)

# 변수 정리
assajumpo_df = jumpo_df.drop(columns=[
    col for col in jumpo_df.columns
    if jumpo_df[col].replace('', pd.NA).isna().all()
])

# 월수익 변수 생성
def extract_monthly_profit(html):
    match = re.search(r'월수익\s*(-?[\d,]+)만', html)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

assajumpo_df['p_monthly_profit'] = assajumpo_df['html_data'].apply(extract_monthly_profit)

# 데이터 저장
assajumpo_df.to_csv('assajumpo_df.csv', index=False, encoding='utf-8-sig')

import time
import requests
import pandas as pd

url = "https://xn--v69ap5so3hsnb81e1wfh6z.com/item/get_item_json/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://xn--v69ap5so3hsnb81e1wfh6z.com",
    "Referer": "https://xn--v69ap5so3hsnb81e1wfh6z.com/map",
    "X-Requested-With": "XMLHttpRequest"
}

payload = {
    "dong_id": "1956"
}

response = requests.post(url, headers=headers, data=payload)

# 응답 확인 및 JSON -> DataFrame
if response.status_code == 200:
    try:
        df = pd.DataFrame(response.json())
        items_df = pd.json_normalize(df['item'])

    except ValueError:
        print("JSON 디코딩 실패 - 실제 응답 내용:", response.text[:500])
else:
    print("요청 실패:", response.status_code)

results = []

for dong_id in range(1, 5000):
    payload = {"dong_id": str(dong_id)}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=5)
        status = response.status_code
    except Exception as e:
        status = f"error: {str(e)}"

    results.append({
        "dong_id": dong_id,
        "status_code": status
    })

    # 서버에 과부하 주지 않도록 약간 대기
    time.sleep(0.1)

# 결과를 DataFrame으로 변환
df_status = pd.DataFrame(results)

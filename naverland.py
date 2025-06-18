# 코드 출처 : https://cocoabba.tistory.com/63

import requests
import json
import pandas as pd


# HTTP 요청 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": "https://new.land.naver.com/complexes",
    "X-Requested-With": "XMLHttpRequest"
}

# 시/도 코드 및 이름 추출
def get_sidolist():
    # 시/도 결정을 위한 URL 설정
    url = 'https://new.land.naver.com/api/regions/list?cortarNo=0000000000'

    # HTTP GET 요청 보내기
    # data={"sameAddressGroup":"false"}: GET 요청의 쿼리 : “동일매물 묶기”:체크해제 옵션
    r = requests.get(url, data={"sameAddressGroup": "false"}, headers=headers)

    # HTTP 응답 데이터의 인코딩 설정
    r.encoding = "utf-8-sig"

    # HTTP 응답 데이터를 JSON 형태로 파싱
    temp = json.loads(r.text)

    # 'regionList' 키를 가진 리스트에서 'cortarNo' 및 'cortarName' 추출
    cities = list(pd.DataFrame(temp["regionList"])["cortarName"])  # 도시명 추출
    code = list(pd.DataFrame(temp["regionList"])["cortarNo"])  # 도시 코드 추출

    # 도시 코드와 도시명을 dictionary 타입으로 묶기
    sido_dicts = dict(zip(cities, code))

    return sido_dicts


# 시/군/구 및 읍/면/동 목록 추출 함수
def get_sigungulist(param):
    url = f'https://new.land.naver.com/api/regions/list?cortarNo={param}'

    # GET 요청 전송 (data 파라미터는 일반적으로 필요 없음)
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8-sig"

    # JSON 응답 파싱
    data = json.loads(response.text)

    # 지역 코드 및 이름 추출
    cities = list(pd.DataFrame(data["regionList"])["cortarName"])  # 지역 이름
    code = list(pd.DataFrame(data["regionList"])["cortarNo"])  # 지역 코드

    sigungu_dicts = dict(zip(cities, code))

    return sigungu_dicts


# 단지 목록 추출 함수 정의
def get_danjilist(dong_code):
    # 단지 조회 URL 구성
    url = f'https://new.land.naver.com/api/regions/complexes?cortarNo={dong_code}&realEstateType=APT&order='

    # HTTP GET 요청 (GET이므로 data 대신 params가 일반적으로 권장됨)
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8-sig"

    # JSON 응답 파싱
    data = json.loads(response.text)

    # 단지 목록이 없는 경우 처리
    if len(pd.DataFrame(data["complexList"])) < 1:
        print("목록 없음")
        return 0
    else:
        # 단지 번호 및 이름 추출
        complex_code = list(pd.DataFrame(data["complexList"])["complexNo"])  # 단지 코드
        complex_names = list(pd.DataFrame(data["complexList"])["complexName"])  # 단지 이름
        complex_dicts = dict(zip(complex_code, complex_names))

        return complex_dicts

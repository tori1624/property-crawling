# 부동산 관련 데이터 크롤링 프로젝트

## 📌 프로젝트 개요
> 개인적으로 부동산 시장 동향을 데이터 기반으로 파악하고, 투자 판단의 근거를 만들기 위해 여러 부동산 관련 사이트의 데이터를 크롤링하여 정제·구조화하는 프로젝트입니다. 크롤링된 데이터는 추후 시각화, 통계 분석, 머신러닝 기반 예측 모델 개발 등에 활용할 수 있도록 데이터 구조를 설계하고 있습니다.
<br/>

## 🔍 크롤링 대상 사이트 및 주요 수집 정보

<br/>

| 사이트 | 수집 정보 | 링크 |
|------|---------|-------------|
| 대법원 경매정보 | 부동산 경매 관련 정보 - 경매 일정, 감정가, 입찰 결과 등 | [Link](https://www.courtauction.go.kr/pgj/index.on) |
| Jumpoline | 점포 매매 관련 정보 - 지역, 면적, 권리금, 월수익 등 | [Link](https://www.jumpoline.com/) |
| 아싸점포거래소 | 점포 매매 관련 정보 - 보증금, 월세, 권리금, 월매출, 월수익 등 | [Link](https://xn--v69ap5so3hsnb81e1wfh6z.com/) |

<br/>

(※ 수집 대상은 계속해서 추가 예정)

<br/>

## 🛠️ 기술 스택
- Python
- Selenium
- Pandas
<br/>

## 📁 폴더 구조
```
property-crawling/
├── assajumpo/
│ └── assajumpo_list.py
├── courtAuction/
│ └── courtAuction_info.py
│ └── courtAuction_list.py
│ └── courtAuction_list_old.py
├── jumpoline/
│ └── jumpoline_home.py
│ └── jumpoline_type.py
└── README.md
```

<br/>

## ⚙️ 실행 방법
```bash
git clone https://github.com/tori1624/property-crawling.git
cd property-crawling

# 예: 대법원 경매 리스트 크롤링 실행
python courtAuction/courtAuction_list.py
```

<br/>

## ⚠️ 주의사항
- 일부 사이트는 동적 페이지로 구성되어 있어 Selenium 사용이 필요합니다.
- 사이트 구조 변경 시 크롤링 코드 수정이 필요할 수 있습니다.

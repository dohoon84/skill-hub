---
name: global_economy_briefing
type: app
description: 매일 아침 글로벌 주요 지수, 환율, 암호화폐, 거시경제 지표를 한 번에 정리해 브리핑
skills:
  - finance
  - exchange_rate
  - crypto_price
  - world_bank
  - news_rss
  - quickchart
schedule: "0 7 * * 1-5"
trigger_keywords: 경제 브리핑,아침 브리핑,글로벌 경제,시장 현황,오늘 시장
output_channel: telegram
enabled: true
version: 1.0.0
author: openchiken
tags: finance, economy, briefing, daily
---

## 글로벌 경제 브리핑

매일 평일 오전 7시에 자동 실행되어 주요 금융 시장 현황을 한눈에 정리합니다.
텔레그램에서 `/run global_economy_briefing` 또는 "경제 브리핑"이라고 입력해도 즉시 실행됩니다.

### 실행 단계

1. finance 도구로 다음 주요 지수의 현재가와 전일 대비 등락률을 조회하라: 나스닥(^IXIC), S&P500(^GSPC), 다우존스(^DJI), KOSPI(^KS11), 니케이225(^N225). 각 지수를 한 줄로 요약하라.
2. exchange_rate 도구로 USD/KRW, EUR/KRW, JPY/KRW, CNY/KRW 환율을 조회하라. 전일 대비 원화 강세/약세 방향도 표시하라.
3. crypto_price 도구로 BTC, ETH, SOL의 현재 USD 가격과 24시간 변동률을 조회하라.
4. world_bank 도구로 한국·미국·중국의 최근 GDP 성장률 및 인플레이션 데이터를 조회하라. 해당 데이터가 시장에 미치는 의미를 1~2줄로 해석하라.
5. news_rss 도구로 글로벌 금융·경제 관련 RSS 피드에서 오늘 오전 기준 주요 뉴스 5건을 수집하고 각각 한 줄 요약하라.
6. quickchart 도구로 1단계에서 수집한 5개 지수의 등락률을 막대 차트로 시각화하라. 차트 제목은 "오늘의 글로벌 지수 등락률(%)"으로 설정하라.
7. 수집한 모든 데이터를 종합하여 다음 형식으로 브리핑 리포트를 작성하라:
   📊 [글로벌 경제 브리핑 — {날짜}]

   🏦 주요 지수
   • 나스닥 {가격} ({등락률}%) | S&P500 {가격} ({등락률}%)
   • KOSPI {가격} ({등락률}%) | 니케이 {가격} ({등락률}%)

   💱 주요 환율 (원화 기준)
   • USD {환율}원 | EUR {환율}원 | JPY {환율}원

   🪙 암호화폐
   • BTC ${가격} ({변동률}%) | ETH ${가격} ({변동률}%)

   🌐 거시경제 시그널
   • {world_bank 해석 1~2줄}

   📰 오늘의 주요 뉴스
   1. {뉴스 요약}
   ...

   📈 차트: {quickchart 이미지 URL}

### 분석 기준

- 지수 등락률 ±2% 이상: 주요 변동으로 강조 표시
- 환율 전일 대비 ±1% 이상: 큰 변동으로 강조 표시
- BTC 24H 변동 ±5% 이상: 변동성 경보 표시

---
name: wallstreetbets
description: Reddit WallStreetBets 및 투자 관련 서브레딧 감성 분석 (API 키 불필요)
enabled: true
version: 1.0.0
tags: finance, sentiment
---

## Reddit 투자 커뮤니티 감성 분석 도구

Reddit의 r/wallstreetbets, r/investing, r/stocks, r/CryptoCurrency 등 투자 관련 커뮤니티의 게시물 및 댓글을 분석하여 특정 종목 또는 자산에 대한 커뮤니티 심리를 파악합니다. API 키 없이 사용할 수 있습니다.

### 사용 가능한 도구

- **get_wsb_sentiment**: 특정 종목/자산에 대한 Reddit 감성 분석

### 파라미터

- `ticker`: 분석할 주식 티커 또는 암호화폐 심볼 (예: AAPL, GME, BTC, ETH)
- `subreddit`: 분석할 서브레딧 (기본값: wallstreetbets, 선택: investing, stocks, CryptoCurrency)
- `limit`: 분석할 게시물 수 (기본값: 50)

### 반환 데이터

- **감성 비율**: 긍정/부정/중립 게시물 비율 (%)
- **언급 빈도**: 최근 24시간 내 언급 횟수
- **상위 게시물**: 업보트 수 상위 관련 게시물 요약
- **주요 키워드**: 자주 등장하는 연관 키워드

### 감성 해석 기준

| 긍정 비율 | 해석 |
|-----------|------|
| 80% 이상 | 강한 강세 신호 |
| 60~79% | 완만한 강세 |
| 40~59% | 혼조세 |
| 40% 미만 | 약세 심리 우세 |

### 사용법

- 기술적 분석 보조 지표로 활용
- 단기 모멘텀 파악 (개인투자자 심리 반영)
- 특정 종목의 밈 주식 가능성 탐지
- 암호화폐 커뮤니티 온도 측정

### 주의사항

Reddit 감성은 개인투자자 의견을 반영하며 전문 투자 조언이 아닙니다. 다른 지표와 함께 보조 참고용으로만 활용하세요.

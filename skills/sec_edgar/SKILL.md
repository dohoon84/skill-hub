---
name: sec_edgar
description: SEC EDGAR 미국 공개기업 연간/분기 보고서 조회 (API 키 불필요)
enabled: true
version: 1.0.0
tags: finance, sec
---

## SEC EDGAR 재무보고서 조회 도구

미국 증권거래위원회(SEC)의 EDGAR 시스템 공개 API를 사용하여 미국 상장기업의 공식 재무보고서를 조회합니다. API 키 없이 사용할 수 있습니다.

### 사용 가능한 도구

- **get_sec_filings**: 기업의 SEC 제출 문서 조회

### 파라미터

- `ticker`: 주식 티커 심볼 (예: AAPL, TSLA, NVDA, MSFT)
- `form_type`: 보고서 유형 (10-K: 연간보고서, 10-Q: 분기보고서, 8-K: 수시공시)

### 반환 데이터 (10-K 기준)

- **매출액(Revenue)**: 연간 총 매출
- **순이익(Net Income)**: 당기순이익
- **영업이익(Operating Income)**: 영업이익 및 영업이익률
- **총자산/총부채**: 자산 건전성 지표
- **EPS(주당순이익)**: 기본 및 희석 EPS
- **현금흐름**: 영업/투자/재무 활동별 현금흐름

### 사용법

- 투자 전 기업 재무 건전성 분석
- PER·PBR 계산을 위한 기초 데이터 수집
- 경쟁사 재무 비교 분석
- 분기 실적 추이 파악

### 참고

- 미국 증권거래소(NYSE, NASDAQ) 상장 기업만 지원
- 데이터는 SEC에 제출된 공식 문서 기반으로 신뢰성 높음

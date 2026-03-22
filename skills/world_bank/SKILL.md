---
name: world_bank
description: World Bank 공개 API 기반 글로벌 거시경제 데이터 조회 (API 키 불필요)
enabled: true
version: 1.0.0
tags: finance, economics
---

## World Bank 거시경제 데이터 도구

세계은행(World Bank)의 공개 데이터 API를 사용하여 전 세계 국가별 경제 지표를 조회합니다. API 키 없이 사용할 수 있습니다.

### 사용 가능한 도구

- **get_world_bank_data**: 국가별 경제 지표 조회

### 파라미터

- `country_code`: ISO 3166-1 alpha-2 국가코드 (예: KR, US, CN, JP, DE)
- `indicator`: 조회할 지표 코드 (기본값: 주요 거시경제 지표 세트)
- `year_range`: 조회 연도 범위 (예: 2020~2024)

### 주요 지표 목록

| 지표 코드 | 설명 |
|-----------|------|
| NY.GDP.MKTP.KD.ZG | GDP 성장률 (%) |
| FP.CPI.TOTL.ZG | 소비자물가 상승률 (%) |
| SL.UEM.TOTL.ZS | 실업률 (%) |
| NE.EXP.GNFS.ZS | 수출 (GDP 대비 %) |
| GC.DOD.TOTL.GD.ZS | 정부 부채 (GDP 대비 %) |
| NY.GNP.PCAP.CD | 1인당 GNI (USD) |

### 반환 데이터

- 지표명 및 연도별 수치
- 전년 대비 변화율
- 국가 간 비교 시 상대적 위치

### 사용법

- 국가 경제 건전성 비교 분석
- 투자 대상국 거시경제 리스크 평가
- 아침 경제 브리핑의 배경 맥락 제공
- 도시 이민·이주 의사결정 시 경제 환경 파악

---
name: arxiv
description: arXiv 학술 논문 검색 및 요약 (API 키 불필요)
enabled: true
version: 1.0.0
tags: research, science
---

## arXiv 논문 검색 도구

arXiv.org의 공개 API를 사용하여 AI, 물리학, 수학, 컴퓨터과학 등 다양한 분야의 최신 학술 논문을 검색합니다. API 키 없이 사용할 수 있습니다.

### 사용 가능한 도구

- **search_arxiv**: 키워드 기반 논문 검색

### 파라미터

- `query`: 검색 키워드 (예: "large language model", "transformer", "diffusion model")
- `max_results`: 최대 반환 건수 (기본값: 5)
- `category`: arXiv 카테고리 필터 (선택, 예: cs.AI, cs.LG, quant-ph)

### 반환 데이터

- **제목(Title)**: 논문 제목
- **저자(Authors)**: 저자 목록
- **초록(Abstract)**: 논문 요약
- **발표일(Published)**: arXiv 등록 날짜
- **arXiv ID 및 URL**: 직접 링크

### 주요 카테고리

| 카테고리 | 분야 |
|----------|------|
| cs.AI | 인공지능 |
| cs.LG | 머신러닝 |
| cs.CL | 자연어처리 |
| cs.CV | 컴퓨터 비전 |
| cs.RO | 로보틱스 |
| quant-ph | 양자물리학 |
| math.ST | 통계학 |

### 사용법

- 특정 연구 분야 최신 동향 파악
- AI/ML 논문 트렌드 분석
- 주간 기술 브리핑에서 주목할 논문 선별

---
name: tech_trend_weekly
type: app
description: 매주 월요일 Hacker News·arXiv·YouTube·웹 검색을 통해 지난주 기술 트렌드를 요약 브리핑
skills:
  - hacker_news
  - arxiv
  - youtube
  - web_search
  - quickchart
schedule: "0 9 * * 1"
trigger_keywords: 기술 트렌드,테크 뉴스,tech trend,주간 기술,AI 트렌드,개발 트렌드
output_channel: telegram
enabled: true
version: 1.0.0
author: openchiken
tags: tech, ai, news, weekly, research
---

## 주간 기술 트렌드 브리핑

매주 월요일 오전 9시에 자동 실행되어 지난 한 주간의 기술 트렌드를 한눈에 정리합니다.
텔레그램에서 `/run tech_trend_weekly` 또는 "기술 트렌드 알려줘"로 즉시 실행할 수 있습니다.

### 실행 단계

1. hacker_news 도구로 지난 7일 이내 업로드된 상위 포인트 기사 10건을 조회하라. 각 기사의 제목, 포인트, 댓글 수를 포함하여 한 줄씩 요약하라. 카테고리(AI/보안/웹/시스템 등)를 함께 표시하라.
2. arxiv 도구로 "artificial intelligence", "large language model", "machine learning" 키워드로 최근 7일 이내 발표된 논문 5편을 검색하라. 각 논문의 제목, 저자, 핵심 기여(기존 방법 대비 개선점)를 2~3줄로 요약하라.
3. youtube 도구로 "tech news this week", "AI news" 키워드로 조회수 상위 트렌딩 영상 5개를 검색하라. 제목, 채널명, 조회수를 포함하여 어떤 주제인지 한 줄씩 설명하라.
4. web_search 도구로 "technology news this week {현재 날짜 기준 주}" 쿼리로 이번 주 주요 기술 이슈(신제품 출시, 대규모 업데이트, 주요 인수합병 등) 5건을 검색하고 요약하라.
5. 1~4단계에서 수집한 데이터를 분석하여 이번 주 기술 트렌드 키워드 상위 5개를 추출하라. 각 키워드가 왜 주목받는지 1~2줄로 설명하라.
6. quickchart 도구로 5단계에서 추출한 키워드별 언급 빈도(Hacker News 포인트 기준)를 가로 막대 차트로 시각화하라. 차트 제목은 "이번 주 Tech 키워드 트렌드"로 설정하라.
7. 모든 데이터를 종합하여 다음 형식으로 주간 브리핑 리포트를 작성하라:
   🚀 [주간 기술 트렌드 브리핑 — {날짜 범위}]

   🔥 이번 주 핵심 키워드
   1. {키워드} — {설명}
   2. {키워드} — {설명}
   ...

   📰 HackerNews TOP 3
   1. [{제목}] — {요약} (👍{포인트})
   ...

   🔬 주목할 AI 논문
   1. [{논문 제목}] — {핵심 기여}
   ...

   🎥 YouTube 화제의 영상
   1. [{제목}] ({채널}, {조회수}회) — {주제}
   ...

   🌐 이번 주 Big Tech 뉴스
   1. {뉴스 요약}
   ...

   📊 트렌드 차트: {quickchart URL}

### 분석 기준

- HackerNews 500포인트 이상: 업계 주요 관심사
- arXiv 논문: 기존 SOTA 대비 명확한 개선이 있는 논문 우선 선정
- YouTube 조회수 100만 이상: 대중 관심도 높은 트렌드 반영

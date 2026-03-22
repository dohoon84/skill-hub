---
name: youtube
description: YouTube Data API v3 기반 동영상 검색, 채널/동영상 상세 정보, 트렌딩, 댓글, 재생목록 조회
enabled: true
version: 1.1.0
author: dohoon84
tags: video, youtube, media, search
requires_google_auth: true
---

## YouTube 도구

YouTube Data API v3를 사용하여 동영상 검색, 채널 정보, 트렌딩, 댓글, 재생목록을 조회합니다.

Gmail/Calendar와 동일한 Google OAuth2 인증을 사용합니다. 별도 API 키가 필요 없으며,
[Google Cloud Console](https://console.cloud.google.com/)에서 **YouTube Data API v3** 를 활성화하기만 하면 됩니다.

### 사용 가능한 도구

- **youtube_search**: 키워드로 YouTube 동영상 검색
  - `query`: 검색어 (한국어/영어 모두 지원)
  - `max_results`: 결과 수 (최대 50, 기본 10)
  - `order`: 정렬 기준 — `relevance`(관련도순), `date`(최신순), `viewCount`(조회수순), `rating`(평점순)
  - `published_after`: 특정 날짜 이후 영상만 (예: `2024-01-01T00:00:00Z`)
  - `region_code`: 지역 코드 (기본 `KR`)
  - `video_duration`: 길이 필터 — `short`(4분 미만), `medium`(4~20분), `long`(20분 초과)

- **youtube_video_info**: 동영상 ID 또는 URL로 상세 정보 조회
  - 제목, 채널, 업로드 날짜, 길이, 조회수, 좋아요, 댓글 수, 태그, 설명 포함
  - URL 형식 자동 파싱 (youtu.be, youtube.com/watch, /shorts 모두 지원)

- **youtube_channel_info**: 채널 ID, @핸들, 또는 채널 이름으로 채널 정보 조회
  - 구독자 수, 총 동영상 수, 총 조회수, 채널 소개, 키워드 포함

- **youtube_trending**: 지역별 YouTube 트렌딩(인기) 동영상 조회
  - `region_code`: `KR`(한국), `US`(미국), `JP`(일본) 등
  - `category_id`: 0=전체, 10=음악, 15=동물, 17=스포츠, 20=게임, 22=Vlog, 24=엔터테인먼트, 25=뉴스, 28=과학기술

- **youtube_comments**: 동영상 댓글 조회 (인기순 또는 최신순)
  - 댓글 작성자, 내용, 좋아요 수, 작성일, 답글 수 포함

- **youtube_playlist_items**: 재생목록 ID 또는 URL로 재생목록 내 동영상 목록 조회

- **youtube_channel_videos**: 특정 채널의 최근 업로드 동영상 목록 조회
  - 채널 ID 또는 @핸들로 검색 가능

### 사전 준비

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Gmail/Calendar에서 사용 중인 프로젝트 선택
3. **API 및 서비스 → 라이브러리** 에서 `YouTube Data API v3` 검색 후 **사용 설정** 클릭
4. 기존 credentials.json/token.json 그대로 사용 (별도 API 키 불필요)

### 사용 규칙

- youtube_video_info, youtube_comments 사용 시 반드시 youtube_search로 먼저 실제 ID를 확보하세요.
- youtube_search 결과에서 반환된 `ID: xxxxxxxx` 값을 그대로 다음 도구에 전달하세요. 임의로 ID를 생성하지 마세요.

### 사용 예시

| 요청 | 사용 도구 |
|------|-----------|
| "파이썬 강의 영상 찾아줘" | `youtube_search(query="파이썬 강의")` |
| "오늘 한국 유튜브 트렌딩 알려줘" | `youtube_trending(region_code="KR")` |
| "이 영상 상세 정보 알려줘 [URL]" | `youtube_video_info(video_id="[URL]")` |
| "MrBeast 채널 정보 알려줘" | `youtube_channel_info(channel_query="@MrBeast")` |
| "이 영상 댓글 보여줘" | `youtube_comments(video_id="...")` |
| "이 재생목록 뭐가 있어?" | `youtube_playlist_items(playlist_id="...")` |
| "채널 최신 영상 목록" | `youtube_channel_videos(channel_id="@...")` |

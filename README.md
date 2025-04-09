# jq-sitemap-for-tistory 🛰️

**티스토리 블로그**를 위한 자동 사이트맵 생성기입니다.  
블로그 글 목록을 크롤링하여 `sitemap.xml` 파일을 자동으로 만들어줍니다.
검색엔진 색인 최적화를 위해 sitemap.xml을 직접 생성해 업로드할 수 있습니다.

## 🔥 주요 기능

- 티스토리 글 목록을 크롤링하여 `sitemap.xml` 자동 생성
- 작성한 포스트의 URL을 자동 수집
- 날짜 기반 정렬 및 중복 제거
- Bing, 구글 서치콘솔 제출 가능
- ❌ 네이버는 도메인 다를경우 제출 불가능

---

## 설정

### 📦 사용 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 작성
cp config.sample.json config.json
# config.json 내부에 자신의 블로그 주소 입력
```

### 실행

```
python sitemap_generator.py
```

### ⚙️ config.json 예시

```
{   "blog_url": "https://jeeqong.tistory.com",   "max_pages": 50 }
```

### 📁 결과물 예시

- sitemap.xml 이 프로젝트 루트에 생성됩니다.
- 생성된 sitemap을 구글/네이버 서치콘솔에 제출하면 색인됩니다.
- 티스토리 관리 → 플러그인 → robots.txt 설정 또는 직접 업로드 가능.

### ✅ 적용 가능한 Tistory 스킨 목록 (2025.04 기준)

| **스킨 이름** | **지원 여부** | **비고**                       |
| ------------- | ------------- | ------------------------------ |
| BookClub      | ✅ 사용 가능  | 안정적 구조                    |
| Ray           | ✅ 사용 가능  |                                |
| Ray2          | ✅ 사용 가능  |                                |
| xf_Letter     | ✅ 사용 가능  |                                |
| xf_Magazine   | ✅ 사용 가능  |                                |
| xf_Odyssey    | ✅ 사용 가능  |                                |
| xf_Portfolio  | ✅ 사용 가능  |                                |
| xf_Poster     | 🔺 부분 가능  | **날짜 데이터 없음**           |
| Square        | ❌ 사용 불가  | **모든 요소가 구분 불가 구조** |

#### 🛠️ 참고사항

- ❌ 제외된 스킨은 sitemap.xml 생성 시 게시글 날짜 추출이 불가능하거나, <a> 태그가 인기글/연관글과 구분되지 않아 자동화 불가한 구조입니다.
- ✅ 스킨들은 정규 표현식 기반으로 날짜와 링크 추출이 검증되었습니다.
- 스킨에 따라 class명 없이 구조만으로 분석하는 경우가 많아 스킨 구조 변경 시 다시 확인이 필요합니다.
- `🔺 xf_Poster` 스킨은 해당스킨에 날짜가 지원되지 않아 url 만 생성합니다.

### 🛠 향후 개선 예정

- 자동 GitHub Pages 배포
- 커맨드라인 UI
- 자동 커밋 및 push 기능
- 블로그 플랫폼 확장 (velog, brunch 등)

### 🪪 라이선스

MIT

---

> Created with ❤️ by [jeeqong](https://jeeqong.tistory.com)

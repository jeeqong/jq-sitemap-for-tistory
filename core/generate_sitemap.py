import logging

from bs4 import BeautifulSoup

from core.utils import find_nearby_date, is_valid_post_link, parse_date_string

logger = logging.getLogger(__name__)

def generate_sitemap_from_soup(blog_url: str, soup: BeautifulSoup, selector_config: dict) -> list:
    post_info_dict = {}  # ✅ 중복 URL은 첫번째 항목만 저장

    link_selector = selector_config.get("link_selector", "")
    date_selector = selector_config.get("date_selector", "")

    # 1. 제목/썸네일 기반 링크 요소 먼저 찾기
    link_candidates = soup.select(link_selector)
    logger.debug(f"[디버깅] 링크 후보 수: {len(link_candidates)}")

    for link_tag in link_candidates:
        href = link_tag.get("href")
        if not is_valid_post_link(href):
            continue

        # 절대 경로 만들기
        full_url = href if href.startswith("http") else blog_url + href

        # ✅ 중복 검사 (가장 먼저 나온 항목만 저장)
        if full_url in post_info_dict:
            logger.warning(f"⚠️ 중복 URL 스킵 (이미 저장됨): {full_url}")
            continue

        # 날짜 추출
        date_tag = find_nearby_date(link_tag, date_selector)
        date_str = date_tag.text if date_tag else None
        if date_str is None:
            logger.debug(f"[디버깅] ❌ date not found: date_str = {date_str}")
            lastmod = None
        else:
            lastmod = parse_date_string(date_str)

        
        # 날짜 있을 때만 포함
        post_info = {"url": full_url}
        if lastmod:
            post_info["lastmod"] = lastmod

        post_info_dict[full_url] = post_info

    return list(post_info_dict.values())
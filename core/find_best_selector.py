import logging

from bs4 import BeautifulSoup

from core.utils import is_valid_post_link

logger = logging.getLogger(__name__)

CANDIDATE_LINK_SELECTORS = [
    ".thumbnail",
    ".link-article",
    ".index-item-link",
    ".title",
    ".post-item > a",
    ".post-item .title",
    ".thumbnail_post",
    ".link_post",
    ".link_title",  
    ".link_thumb",  
    ".link_category",  
]

CANDIDATE_DATE_SELECTORS = [
    ".date",
    ".digit",
    ".post-item .date",
    ".detail_info",
]

def merge_selectors(config_value: str, built_in_candidates: list[str]) -> list[str]:
    """config 값 + 내부 후보 셀렉터를 합치되 중복 제거"""
    config_list = [s.strip() for s in config_value.split(",") if s.strip()]
    combined = list(dict.fromkeys(config_list + built_in_candidates))  # 순서 유지 + 중복 제거
    return combined

def find_best_selector(soup: BeautifulSoup, selector_config: dict) -> dict:
    """
    셀렉터 후보군 중 가장 잘 매칭되는 link/date 셀렉터를 찾아주는 함수
    - soup: HTML 파싱된 BeautifulSoup 객체
    - selector_config: config.json 내 selector 딕셔너리
    """
    best_link = None
    best_date = None

    # 1️⃣ 링크 셀렉터 후보군 합치기
    all_link_candidates = merge_selectors(selector_config.get("link_selector", ""), CANDIDATE_LINK_SELECTORS)
    for selector in all_link_candidates:
        candidates = soup.select(selector)
        for tag in candidates:
            href = tag.get("href")
            if is_valid_post_link(href):
                best_link = selector
                break
        if best_link:
            break

    # 2️⃣ 날짜 셀렉터 후보군 합치기
    all_date_candidates = merge_selectors(selector_config.get("date_selector", ""), CANDIDATE_DATE_SELECTORS)
    for selector in all_date_candidates:
        candidates = soup.select(selector)
        for tag in candidates:
            if tag.text and len(tag.text.strip()) >= 10:
                best_date = selector
                break
        if best_date:
            break

    logger.debug(f"🔍 best_link: {best_link}")
    logger.debug(f"🔍 best_date: {best_date}")

    return {
        "link_selector": best_link or selector_config.get("link_selector", ""),
        "date_selector": best_date or selector_config.get("date_selector", "")
    }
import json
import logging
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from bs4 import Tag

logger = logging.getLogger(__name__)


def load_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config, config_path: str):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)  # noqa: F821

def clean_date_string(date_str: str) -> str:
    """날짜 문자열에서 특수 문자, 공백 등을 정리"""
    # 유니코드 특수문자 제거
    date_str = re.sub(r"[^\w\s.:]", "", date_str)  # ← 특수 이모지 등 제거
    # 연속된 공백을 하나로
    date_str = re.sub(r"\s+", " ", date_str)
    return date_str.strip()

def parse_date_string(date_str: str) -> str:
    """
    다양한 형태의 날짜 문자열을 ISO 8601 형식으로 변환 (예: 2025-04-08T06:29:57Z)
    문자열 안에 날짜 + 다른 텍스트가 섞여 있어도 날짜만 추출해서 처리
    """

    original = date_str
    date_str = clean_date_string(date_str)  # ← 중요!!

    # logger.debug(f"original: {original[:100]}")
    # logger.debug(f"cleaned: {date_str[:100]}")
    # ✅ 날짜 패턴이 텍스트에 섞여 있을 경우 → 날짜만 추출
    regex_patterns = [
        r"\d{4}\. ?\d{1,2}\. ?\d{1,2}\. ?\d{1,2}:\d{2}",  # 2025. 4. 16. 15:32
        r"\d{4}\. ?\d{1,2}\. ?\d{1,2}",                  # 2025.04.07
        r"\d{2}:\d{2}:\d{2}",                            # 00:00:35
    ]

    for pattern in regex_patterns:
        match = re.search(pattern, date_str)
        if match:
            date_str = match.group()
            break  # 첫 번째 매칭된 날짜만 사용

    # ✅ 시도할 포맷들
    candidates = [
        "%Y. %m. %d.",
        "%Y. %m. %d",          # ← 끝에 마침표 없는 케이스!
        "%Y.%m.%d",
        "%Y.%m.%d.",
        "%Y. %m. %d. %H:%M",
        "%Y. %m. %d. %H:%M:%S",
        "%Y-%m-%d",
        "%H:%M:%S",
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(date_str, fmt)
            if fmt == "%H:%M:%S":
                today = datetime.utcnow().date()
                dt = datetime.combine(today, dt.time())
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue

    logger.warning(f"⚠️ 날짜 파싱 실패: {original}")
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def is_valid_post_link(href: str) -> bool:
    """href 유효성 필터링"""
    if not href:
        return False
    if href.startswith("#"):
        return False
    if "/category" in href or "/tag" in href:
        return False
    if "tistory.com" not in href and not href.startswith("/"):
        return False
    return True


def write_sitemap(post_infos: list, output_file: str):
    """sitemap.xml 파일로 저장"""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for info in post_infos:
        url_element = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_element, "loc")
        loc.text = info["url"]
        if "lastmod" in info and info["lastmod"]:
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = info["lastmod"]


    tree = ET.ElementTree(urlset)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    logger.info(f"✅ sitemap.xml 생성 완료 → {output_file}")

DATE_PATTERN = re.compile(r"\d{4}\.\s*\d{1,2}\.\s*\d{1,2}(\.\s*\d{1,2}:\d{2}(:\d{2})?)?")

def find_nearby_date(tag: Tag, date_selectors: str):
    """
    태그 근처에서 날짜 문자열이 포함된 span 등을 찾아 반환
    """
    selectors = [s.strip() for s in date_selectors.split(",")]

    # 1. tag 내부에서 직접 탐색
    for sel in selectors:
        found = tag.select_one(sel)
        if found and DATE_PATTERN.search(found.text):
            return found

    # 2. 부모, 조부모 안에서 탐색
    for ancestor in [tag.parent, tag.find_parent()]:
        if ancestor:
            for sel in selectors:
                found = ancestor.select_one(sel)
                if found and DATE_PATTERN.search(found.text):
                    return found

    # 3. 주변 모든 span/date-like 텍스트 탐색 (태그 상관없이)
    for candidate in tag.find_all_next():
        if candidate.name in ["span", "div"] and DATE_PATTERN.search(candidate.get_text()):
            return candidate

    return None

def get_blog_url_from_path(file_path: str) -> str:
    """
    예: "_temp/jeeqong.html" → "https://jeeqong.tistory.com"
    """
    filename = os.path.basename(file_path)
    blog_id = os.path.splitext(filename)[0]
    return f"https://{blog_id}.tistory.com"

def html_path_to_id(file_path: str) -> str:
    """
    예: "_temp/jeeqong.html" → "jeeqong"
    """
    filename = os.path.basename(file_path)
    blog_id = os.path.splitext(filename)[0]
    return f"{blog_id}"
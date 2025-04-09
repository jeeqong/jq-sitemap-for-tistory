# url_crawler_runner.py
# [운영용] 실제 블로그 페이지에서 실시간으로 sitemap 생성

import logging

import requests
from bs4 import BeautifulSoup

from core.find_best_selector import find_best_selector
from core.generate_sitemap import generate_sitemap_from_soup
from core.utils import load_config, save_config, write_sitemap

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

CONFIG_PATH = "config.json"

def main():
    config = load_config(CONFIG_PATH)
    blog_url = config["blog_url"].rstrip("/")
    max_pages = config.get("max_pages", 5)
    selector_config = config["selector"]
    output_file = config.get("output_file", "sitemap.xml")

    all_post_infos = []
    seen_urls = set()

    for page in range(1, max_pages + 1):
        url = f"{blog_url}/category?page={page}"
        logger.info(f"🌐 크롤링: {url}")
        res = requests.get(url)
        if res.status_code != 200:
            logger.error(f"❌ 페이지 실패: {url}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")    
        main = soup.find("main") or soup

        # is_initialized: 자동 셀렉터 탐지 실행
        if not config.get("is_initialized", False):
            logger.info("🔍 is_initialized: False → 셀렉터 탐지 감지 중...")
            detected = find_best_selector(main, selector_config)
            config["selector"].update(detected)
            config["is_initialized"] = True
            save_config(config, CONFIG_PATH)
            logger.info("✅ 셀렉터 저장 완료!")

        # sitemap 정보 수집
        post_infos = generate_sitemap_from_soup(blog_url, soup, selector_config)
        # all_post_infos.extend(post_infos)
        
        for info in post_infos:
            url = info["url"]
            if url in seen_urls:
                logger.warning(f"⚠️ 전체 중복 URL 스킵: {url}")
                continue
            seen_urls.add(url)
            all_post_infos.append(info)

    # sitemap 생성
    write_sitemap(all_post_infos, output_file)
    logger.info(f"✅ sitemap.xml 저장 완료 → {output_file}")

if __name__ == "__main__":
    logger.info("✅ 운영 모드 실행중")
    main()
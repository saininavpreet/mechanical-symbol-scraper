import os
import time
import requests
import argparse
from playwright.sync_api import sync_playwright

def create_folder(keyword: str):
    folder = f"data/{keyword.replace(' ', '_')}/"
    os.makedirs(folder, exist_ok=True)
    return folder

def download_image(url: str, path: str):
    try:
        img_data = requests.get(url, timeout=10).content
        with open(path, "wb") as f:
            f.write(img_data)
        return True
    except Exception:
        return False

def scrape_images(keyword: str, limit: int = 20):
    folder = create_folder(keyword)
    print(f"📂 Saving images to: {folder}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        query = keyword.replace(" ", "+")
        url = f"https://www.bing.com/images/search?q={query}"
        page.goto(url)
        page.wait_for_timeout(3000)

        for _ in range(15):
            page.mouse.wheel(0, 6000)
            page.wait_for_timeout(800)

        imgs = page.locator("img.mimg, img.dg_u")  # bing selectors
        count = imgs.count()
        print("🔍 Found images:", count)

        downloaded = 0

        for i in range(count):
            if downloaded >= limit:
                break
            try:
                src = imgs.nth(i).get_attribute("src")
                if src and src.startswith("http"):
                    existing = len(os.listdir(folder))
                    file_path = os.path.join(folder, f"{keyword}_{existing + 1}.jpg")

                    if download_image(src, file_path):
                        print(f"✔ Downloaded: {file_path}")
                        downloaded += 1
            except Exception:
                continue

        browser.close()

    print(f"🎯 Completed — Downloaded {downloaded} images!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword", help="Search keyword e.g. 'mechanical symbols'")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    scrape_images(args.keyword, args.limit)



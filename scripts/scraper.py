"""
Automated Scraper for Kamal Saad Store Catalog
Runs in GitHub Actions / Local to update products.json and products.js
"""

import sys
import os
import json
import re
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

BASE_URL = "https://www.kamalsaad.com"

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,en;q=0.9",
}

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ar,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.kamalsaad.com/"
}


def get_all_category_slugs():
    print("[*] Fetching categories from store...")
    cats = {}
    target_urls = [f"{BASE_URL}/all-categories", BASE_URL]
    
    for url in target_urls:
        try:
            req = urllib.request.Request(url, headers=HTML_HEADERS)
            with urllib.request.urlopen(req, timeout=20) as res:
                soup = BeautifulSoup(res.read().decode("utf-8"), "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/category/" in href:
                        slug = href.split("/category/")[-1].strip("/").split("?")[0]
                        clean_name = urllib.parse.unquote(slug).replace("-", " ").strip()
                        clean_name = re.sub(r'(SALE|NEW|\d+)$', '', clean_name).strip()
                        if slug and slug not in cats:
                            cats[slug] = clean_name or slug
        except Exception as e:
            print(f"[-] Warning while fetching {url}: {e}")

    print(f"[+] Found {len(cats)} categories.")
    return cats


def scrape_category(slug, cat_name):
    encoded_slug = urllib.parse.quote(slug) if not slug.startswith("%") else slug
    url = f"{BASE_URL}/category-products/{encoded_slug}/ar"
    
    req = urllib.request.Request(url, headers=API_HEADERS)
    products = []
    
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode("utf-8"))
            html = data.get("productsPartial", "")
            if not html:
                return []
            
            soup = BeautifulSoup(html, "html.parser")
            items = soup.find_all("div", class_=re.compile(r"grid-view-item"))
            
            seen_urls = set()
            for it in items:
                a_link = it.find("a", href=lambda h: h and "/product-details/" in h)
                if not a_link:
                    continue
                
                prod_url = a_link["href"]
                if not prod_url.startswith("http"):
                    prod_url = urllib.parse.urljoin(BASE_URL, prod_url)
                
                if prod_url in seen_urls:
                    continue
                seen_urls.add(prod_url)
                
                img = it.find("img")
                img_url = ""
                title_from_img = ""
                if img:
                    img_url = img.get("data-src") or img.get("src") or ""
                    title_from_img = img.get("title") or img.get("alt") or ""
                
                if img_url and not img_url.startswith("http"):
                    img_url = urllib.parse.urljoin(BASE_URL, img_url)

                title = ""
                if title_from_img and title_from_img != "product image":
                    title = title_from_img.strip()
                
                if not title:
                    title_elem = it.find("div", class_=re.compile(r"product-name", re.I))
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                if not title:
                    title_slug = prod_url.split("/product-details/")[-1].split("?")[0]
                    title = urllib.parse.unquote(title_slug).replace("-", " ").strip()

                brand_elem = it.find("div", class_=re.compile(r"brand-name", re.I))
                sub_cat = brand_elem.get_text(strip=True) if brand_elem else cat_name
                final_category = sub_cat if sub_cat else cat_name

                price_str = ""
                numeric_price = 0.0
                price_elem = it.find("span", class_=re.compile(r"price", re.I)) or it.find(class_=re.compile(r"price", re.I))
                if price_elem:
                    price_str = price_elem.get_text(strip=True)
                else:
                    price_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:جنيه|EGP|LE)?", it.get_text())
                    if price_match:
                        price_str = price_match.group(0).strip()
                
                num_match = re.search(r"\d+(?:\.\d+)?", price_str)
                if num_match:
                    try:
                        numeric_price = float(num_match.group(0))
                    except ValueError:
                        numeric_price = 0.0

                if title:
                    products.append({
                        "id": len(products) + 1,
                        "title": title,
                        "category": final_category,
                        "price": numeric_price,
                        "price_formatted": f"{numeric_price:,.2f} ج.م" if numeric_price > 0 else (price_str or "غير محدد"),
                        "image": img_url,
                        "url": prod_url
                    })
    except Exception as e:
        print(f"[-] Error scraping category {cat_name}: {e}")

    return products


def main():
    start_time = time.time()
    categories = get_all_category_slugs()
    all_products = []
    seen_prods = set()
    
    for idx, (slug, cat_name) in enumerate(categories.items(), 1):
        print(f"[{idx}/{len(categories)}] Scraping: {cat_name}...", end=" ", flush=True)
        prods = scrape_category(slug, cat_name)
        new_count = 0
        for p in prods:
            if p["url"] not in seen_prods:
                seen_prods.add(p["url"])
                p["id"] = len(all_products) + 1
                all_products.append(p)
                new_count += 1
        print(f"-> +{new_count} items (total: {len(all_products)})")
        time.sleep(0.2)

    if not all_products:
        print("[-] No products extracted.")
        return

    # Root directory (one level up from scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == "scripts" else script_dir
    json_path = os.path.join(root_dir, "products.json")
    js_path = os.path.join(root_dir, "products.js")

    # Save products.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    # Save products.js
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.PRODUCTS_DATA = " + json.dumps(all_products, ensure_ascii=False) + ";")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[SUCCESS] Extracted {len(all_products)} unique products in {elapsed}s.")
    print(f"Saved: {json_path} and {js_path}")


if __name__ == "__main__":
    main()

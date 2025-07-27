from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re

# ---------- CONFIG ---------- #
KEYWORDS = ["วิศวกรรมคอมพิวเตอร์", "วิศวกรรมปัญญาประดิษฐ์"]
BASE_URL = "https://course.mytcas.com"
OUTPUT_FILE = "tuition_fees.xlsx"

# ---------- FUNCTION DEFINITIONS ---------- #
def load_existing_links(output_file):
    try:
        existing_df = pd.read_excel(output_file)
        return existing_df, set(existing_df["ลิงค์"].tolist())
    except FileNotFoundError:
        return pd.DataFrame(), set()

def detect_program_language(title: str) -> str:
    title_lower = title.lower()
    international_keywords = ["นานาชาติ", "อินเตอร์", "inter", "international", "english", "ภาษาอังกฤษ"]
    return "นานาชาติ" if any(kw in title_lower for kw in international_keywords) else "ภาษาไทยปกติ"

def extract_fee_text(detail_soup, html) -> str:
    try:
        dt_tags = detail_soup.find_all("dt")
        for dt in dt_tags:
            if "ค่าใช้จ่าย" in dt.get_text():
                dd = dt.find_next_sibling("dd")
                return dd.get_text(strip=True) if dd else "ไม่พบ"

        # fallback: ใช้ regex หาใน raw HTML
        match = re.search(r"(?:ค่าใช้จ่าย|ค่าเทอม)[^:\n]*[:\s]*([\d,]+)\s*บาท", html)
        return match.group(1) + " บาท" if match else "ไม่พบ"
    except:
        return "ไม่พบ"

def extract_programs_from_keyword(page, keyword, existing_links):
    results = []
    print(f"\n🔍 ค้นหา: {keyword}")

    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_selector("input#search")

    search_input = page.locator("input#search")
    search_input.click()
    search_input.type(keyword, delay=100)
    time.sleep(1.5)
    search_input.press("ArrowDown")
    search_input.press("Enter")
    time.sleep(2)

    content = page.inner_html("ul.t-programs")
    soup = BeautifulSoup(content, "html.parser")

    for li in soup.find_all("li"):
        try:
            a_tag = li.find("a")
            href = a_tag["href"]
            full_url = BASE_URL + href
            if full_url in existing_links:
                continue

            title = li.find("h3").get_text(strip=True)
            faculty = li.find("b").get_text(" ", strip=True)
            university = li.find_all("span")[-1].get_text(strip=True)
            program_type = detect_program_language(title)

            # เข้าไปดึงข้อมูลรายละเอียดค่าใช้จ่าย
            page.goto(full_url, wait_until="networkidle")
            time.sleep(1)
            html = page.content()
            detail_soup = BeautifulSoup(html, "html.parser")
            fee_text = extract_fee_text(detail_soup, html)

            results.append({
                "หลักสูตร": title,
                "คณะ": faculty,
                "มหาวิทยาลัย": university,
                "ประเภทหลักสูตร": program_type,
                "ลิงค์": full_url,
                "ค่าใช้จ่าย": fee_text
            })
            print(f"✅ {title} | {program_type} | {university}")

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            continue

    return results

# ---------- MAIN PROCESS ---------- #
def main():
    existing_df, existing_links = load_existing_links(OUTPUT_FILE)
    all_programs = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for keyword in KEYWORDS:
            programs = extract_programs_from_keyword(page, keyword, existing_links)
            all_programs.extend(programs)

        browser.close()

    new_df = pd.DataFrame(all_programs)
    final_df = pd.concat([existing_df, new_df], ignore_index=True) if not existing_df.empty else new_df
    final_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n📄 บันทึกข้อมูลทั้งหมดแล้วที่: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
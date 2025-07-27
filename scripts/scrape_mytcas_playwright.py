from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time

keywords = ["วิศวกรรมคอมพิวเตอร์", "วิศวกรรมปัญญาประดิษฐ์"]
base_url = "https://course.mytcas.com"
output_file = "tuition_fees.xlsx"
all_programs = []

# ดึงข้อมูลเดิมจาก Excel (ถ้ามี)
try:
    existing_df = pd.read_excel(output_file)
    existing_links = set(existing_df["ลิงค์"].tolist())
except FileNotFoundError:
    existing_df = pd.DataFrame()
    existing_links = set()

# ฟังก์ชันหาค่าใช้จ่ายจาก <dt> + <dd>
def extract_fee_from_dt_dd(soup):
    dt_tags = soup.find_all("dt")
    for dt in dt_tags:
        if "ค่าใช้จ่าย" in dt.get_text(strip=True):
            dd = dt.find_next_sibling("dd")
            if dd:
                fee_line = dd.get_text(strip=True)
                return fee_line
    return None

# ฟังก์ชัน fallback หากไม่มี <dt> + <dd>
def extract_fee_text(tag):
    if not tag:
        return "ไม่พบ"
    full_text = tag.get_text(separator="\n", strip=True)
    lines = full_text.splitlines()
    matched_lines = [line for line in lines if ("ค่าใช้จ่าย" in line or "ค่าเทอม" in line) and re.search(r"\d[\d,\.]*\s*บาท", line)]
    if matched_lines:
        return " / ".join(matched_lines)
    fallback_lines = [line for line in lines if re.search(r"\d[\d,\.]*\s*บาท", line)]
    return " / ".join(fallback_lines) if fallback_lines else "ไม่พบ"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    for keyword in keywords:
        print(f"🔍 ค้นหา: {keyword}")
        page.goto(base_url, wait_until="networkidle")
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
                full_url = base_url + href

                if full_url in existing_links:
                    continue  # ข้ามถ้าเคยดึงมาแล้ว

                title = li.find("h3").get_text(strip=True)
                faculty = li.find("b").get_text(" ", strip=True)
                university = li.find_all("span")[-1].get_text(strip=True)

                # เข้าไปยังหน้าหลักสูตร
                page.goto(full_url, wait_until="networkidle")
                time.sleep(1)

                html = page.content()
                soup_detail = BeautifulSoup(html, "html.parser")

                # หาค่าเทอม
                fee_text = extract_fee_from_dt_dd(soup_detail)
                if not fee_text:
                    fee_tag = soup_detail.find(lambda tag: tag.name in ["div", "section", "td", "p"]
                                               and any(kw in tag.get_text() for kw in ["ค่าใช้จ่าย", "ค่าเทอม"]))
                    fee_text = extract_fee_text(fee_tag)

                all_programs.append({
                    "หลักสูตร": title,
                    "มหาวิทยาลัย": university,
                    "คณะ": faculty,
                    "ลิงค์": full_url,
                    "ค่าใช้จ่าย": fee_text.strip() if fee_text else "ไม่พบ"
                })
                print(f"✅ ดึงข้อมูล: {title} - {university}")

            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
                continue

    browser.close()

# รวมกับข้อมูลเก่า
new_df = pd.DataFrame(all_programs)
if not existing_df.empty:
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    final_df = new_df

# บันทึกลง Excel
final_df.to_excel(output_file, index=False)
print(f"\n📄 บันทึกข้อมูลทั้งหมดแล้วที่: {output_file}")

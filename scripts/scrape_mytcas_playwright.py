from playwright.sync_api import sync_playwright
import time
import re
import openpyxl

def extract_program_info(text):
    # แยกชื่อสาขา คณะ และมหาวิทยาลัยออกจากข้อความที่รวมกัน
    parts = text.replace('\n', ' ').split('›')
    try:
        title_part = parts[0].strip()
        faculty_and_university = parts[1].strip().split()

        faculty = faculty_and_university[0] if len(faculty_and_university) > 0 else "ไม่พบคณะ"
        university = faculty_and_university[-1] if len(faculty_and_university) > 0 else "ไม่พบมหาวิทยาลัย"
        return title_part, faculty, university
    except:
        return text.strip(), "ไม่พบคณะ", "ไม่พบมหาวิทยาลัย"

def extract_tuition_from_program(page, url):
    full_url = f"https://course.mytcas.com{url}"
    page.goto(full_url)
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    try:
        body_text = page.inner_text("body")
        match = re.search(r"(?:ค่าใช้จ่าย|ค่าเทอม)[^:\n]*[:\s]*([\d,]+)\s*บาท", body_text)
        if match:
            return match.group(1) + " บาท"
        else:
            fallback = re.search(r"([\d,]+)\s*บาท", body_text)
            return fallback.group(1) + " บาท" if fallback else "ไม่พบ"
    except:
        return "ดึงข้อมูลล้มเหลว"

def search_and_extract_all():
    results_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://course.mytcas.com/")
        page.wait_for_selector("input#search")

        search_input = page.locator("input#search")
        search_input.click()
        search_input.type("วิศวกรรมคอมพิวเตอร์", delay=100)
        time.sleep(1.5)
        search_input.press("ArrowDown")
        search_input.press("Enter")

        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # ✅ เก็บข้อมูลทั้งหมดล่วงหน้า (ก่อน navigate)
        links = page.locator("li > a[href^='/programs/']")
        count = links.count()
        print(f"พบหลักสูตรทั้งหมด: {count}")

        entries = []
        for i in range(count):
            link = links.nth(i)
            href = link.get_attribute("href")
            text = link.inner_text().strip().replace('\n', ' ')
            entries.append((text, href))

        # ✅ ดึงค่าเทอมจากแต่ละหน้าหลักสูตร
        for text, href in entries:
            title, faculty, university = extract_program_info(text)
            tuition = extract_tuition_from_program(page, href)

            print(f"\n📘 {title}")
            print(f"🏫 {faculty} - {university}")
            print(f"🔗 https://course.mytcas.com{href}")
            print(f"💰 ค่าเทอม: {tuition}")

            results_data.append({
                "ชื่อหลักสูตร": title,
                "คณะ": faculty,
                "มหาวิทยาลัย": university,
                "ลิงก์": f"https://course.mytcas.com{href}",
                "ค่าเทอม": tuition
            })

        browser.close()

    return results_data

def save_to_excel(data, filename="tuition_fees.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tuition Data"

    # เขียนหัวตาราง
    ws.append(["ชื่อหลักสูตร", "คณะ", "มหาวิทยาลัย", "ลิงก์", "ค่าเทอม"])

    for row in data:
        ws.append([row["ชื่อหลักสูตร"], row["คณะ"], row["มหาวิทยาลัย"], row["ลิงก์"], row["ค่าเทอม"]])

    wb.save(filename)
    print(f"\n📄 บันทึกข้อมูลแล้วที่: {filename}")

if __name__ == "__main__":
    results = search_and_extract_all()
    save_to_excel(results)

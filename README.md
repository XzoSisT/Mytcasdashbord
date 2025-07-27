# 🎓 Thai University Tuition Dashboard

แดชบอร์ดนี้เป็นเครื่องมือสำหรับดูข้อมูลค่าใช้จ่ายของหลักสูตรในระบบ [MyTCAS](https://course.mytcas.com/) โดยเฉพาะหลักสูตรด้าน **วิศวกรรมคอมพิวเตอร์**, **วิศวกรรมปัญญาประดิษฐ์** และสาขาที่เกี่ยวข้อง สร้างด้วย [Dash by Plotly](https://dash.plotly.com/) เพื่อให้นักเรียนที่กำลังจะเข้ามหาวิทยาลัยในปีถัดไป สามารถดูข้อมูลและตัดสินใจเลือกหลักสูตรได้ง่ายขึ้น

---

## 📚 คุณสมบัติ (Features)

- ดึงข้อมูลหลักสูตรและค่าใช้จ่ายจากเว็บไซต์ MyTCAS ผ่าน web scraping
- ทำความสะอาดและประมวลผลข้อมูลค่าใช้จ่ายให้อยู่ในรูปแบบที่เข้าใจง่าย
- แสดงข้อมูลผ่านแดชบอร์ดที่สามารถโต้ตอบได้ (Interactive Dashboard)
- กรองข้อมูลหลักสูตรตามประเภทและช่วงราคาที่สนใจ
- แสดงกราฟแท่ง (Bar Chart) และกราฟวงกลม (Pie Chart) แบบ interactive
- ตารางข้อมูลที่สามารถค้นหาและกรองได้สะดวก

---

## ⚙️ วิธีใช้งาน

### 1. เตรียม environment และติดตั้ง dependencies

```bash
git clone https://github.com/your-username/tuition-dashboard.git
cd tuition-dashboard

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install

python scrape_tuition.py

python clean_data.py

python app.py

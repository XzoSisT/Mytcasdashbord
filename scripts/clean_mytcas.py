import pandas as pd
import re

def detect_program_type(name):
    """ระบุประเภทหลักสูตร: นานาชาติ / ภาษาอังกฤษ หรือ ปกติ"""
    if any(word in name.lower() for word in ["inter", "international", "ภาษาอังกฤษ", "นานาชาติ", "english"]):
        return "นานาชาติ"
    return "ปกติ"

def clean_fee_column(df, fee_column="ค่าใช้จ่าย", program_column="หลักสูตร"):
    cleaned_amounts = []
    cleaned_units = []
    program_types = []
    fee_per_term = []
    fee_total = []

    for i, row in df.iterrows():
        raw_text = str(row[fee_column]).strip()
        program_name = str(row[program_column])
        program_type = detect_program_type(program_name)
        program_types.append(program_type)

        if "ไม่พบ" in raw_text or not raw_text:
            cleaned_amounts.append(None)
            cleaned_units.append("ไม่พบ")
            fee_per_term.append(None)
            fee_total.append(None)
            continue

        # ดึงจำนวนเงิน
        amount_match = re.search(r"(\d[\d,]*)", raw_text)
        amount = int(amount_match.group(1).replace(",", "")) if amount_match else None

        # ดึงหน่วย
        unit_match = re.search(r"(ภาคการศึกษา|ปี|เทอม|หน่วยกิต|หลักสูตร)", raw_text)
        unit = unit_match.group(1) if unit_match else "ไม่ระบุ"

        cleaned_amounts.append(amount)
        cleaned_units.append(unit)

        # แปลงเป็นค่าใช้จ่ายต่อภาคการศึกษา
        if unit == "ภาคการศึกษา":
            fee_term = amount
        elif unit == "ปี":
            fee_term = amount / 2  # สมมุติ 1 ปีมี 2 ภาค
        elif unit == "หลักสูตร":
            fee_term = amount / 8  # สมมุติหลักสูตรมี 8 ภาค
        elif unit == "เทอม":
            fee_term = amount
        else:
            fee_term = None

        fee_per_term.append(int(fee_term) if fee_term is not None else None)

        # คำนวณค่าตลอดหลักสูตร
        total_fee = fee_term * 8 if fee_term else None
        fee_total.append(int(total_fee) if total_fee is not None else None)

    # เพิ่มคอลัมน์ใหม่
    df["ประเภทหลักสูตร"] = program_types
    df["จำนวนเงิน (บาท)"] = cleaned_amounts
    df["หน่วย"] = cleaned_units
    df["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"] = fee_per_term
    df["ค่าใช้จ่ายตลอดหลักสูตร (ประมาณ)"] = fee_total

    return df

# โหลดข้อมูล
df = pd.read_excel("tuition_fees.xlsx")

# Clean & enrich
df_clean = clean_fee_column(df)

# บันทึก
df_clean.to_excel("tuition_cleaned.xlsx", index=False)
print("✅ บันทึกไฟล์แล้วที่: tuition_cleaned.xlsx")

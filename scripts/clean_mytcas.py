import pandas as pd
import re

def clean_fee_column(df, fee_column="ค่าใช้จ่าย"):
    cleaned_amounts = []
    cleaned_units = []

    for raw_text in df[fee_column]:
        text = str(raw_text).strip()

        # กรณีไม่มีข้อมูลหรือเป็น "ไม่พบ"
        if "ไม่พบ" in text or not text:
            cleaned_amounts.append(None)
            cleaned_units.append("ไม่พบ")
            continue

        # ดึงจำนวนเงิน เช่น 20,000
        amount_match = re.search(r"(\d[\d,]*)", text)
        amount = int(amount_match.group(1).replace(",", "")) if amount_match else None

        # ดึงหน่วย เช่น ภาคการศึกษา, ปี, หลักสูตร ฯลฯ
        unit_match = re.search(r"(ภาคการศึกษา|ปี|เทอม|หน่วยกิต|หลักสูตร)", text)
        unit = unit_match.group(1) if unit_match else "ไม่ระบุ"

        cleaned_amounts.append(amount)
        cleaned_units.append(unit)

    df["จำนวนเงิน (บาท)"] = cleaned_amounts
    df["หน่วย"] = cleaned_units
    return df

# โหลดและ clean
df = pd.read_excel("tuition_fees.xlsx")
df_clean = clean_fee_column(df)
df_clean.to_excel("tuition_cleaned.xlsx", index=False)
print("✅ บันทึกไฟล์ที่: tuition_cleaned.xlsx")

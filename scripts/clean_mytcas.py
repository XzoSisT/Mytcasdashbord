import pandas as pd
import re

def clean_fee_column(df, fee_column="ค่าใช้จ่าย"):
    cleaned_amounts = []
    cleaned_units = []

    for text in df[fee_column]:
        # ดึงเฉพาะตัวเลข
        match = re.search(r"(\d[\d,]*)", str(text))
        if match:
            amount = int(match.group(1).replace(",", ""))
        else:
            amount = None

        # หาหน่วย เช่น /ปี /ภาค
        unit_match = re.search(r"(?:/)?(ภาคการศึกษา|ปี|เทอม|หน่วยกิต|หลักสูตร)", str(text))
        unit = unit_match.group(1) if unit_match else "ไม่ระบุ"

        cleaned_amounts.append(amount)
        cleaned_units.append(unit)

    df["จำนวนเงิน (บาท)"] = cleaned_amounts
    df["หน่วย"] = cleaned_units
    return df

df = pd.read_excel("tuition_fees.xlsx")
df_clean = clean_fee_column(df)
df_clean.to_excel("tuition_cleaned.xlsx", index=False)
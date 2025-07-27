import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# โหลดข้อมูล
df = pd.read_excel("data/tuition_cleaned.xlsx")

# เริ่มต้น Dash app
app = dash.Dash(__name__)
app.title = "Tuition Fee Dashboard"

# สร้างกราฟตัวอย่าง
fig_fee_distribution = px.box(
    df,
    x="ประเภทหลักสูตร",
    y="ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)",
    points="all",
    title="การกระจายของค่าใช้จ่ายต่อภาคการศึกษา"
)

fig_total_fee = px.histogram(
    df,
    x="ค่าใช้จ่ายตลอดหลักสูตร (ประมาณ)",
    color="ประเภทหลักสูตร",
    nbins=20,
    title="ค่าศึกษาตลอดหลักสูตรตามประเภทหลักสูตร"
)

# Layout ของแอป
app.layout = html.Div([
    html.H1("📊 Dash Dashboard: ค่าใช้จ่ายการศึกษา", style={"textAlign": "center"}),

    dcc.Markdown("### การเปรียบเทียบค่าใช้จ่ายในหลักสูตรที่ค้นหา"),

    dcc.Graph(figure=fig_fee_distribution),
    dcc.Graph(figure=fig_total_fee),

    html.Div("ข้อมูลจาก: https://course.mytcas.com/", style={"textAlign": "right", "marginTop": "30px"})
])

# Run server
if __name__ == "__main__":
    app.run(debug=True)


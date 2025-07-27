import pandas as pd
import dash
from dash import html, dcc, dash_table, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data
df = pd.read_excel("data/tuition_cleaned.xlsx")

# Filter only rows with tuition data
df = df[df["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"].notnull()]

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/style.css"])
app.title = "Tuition Dashboard - MyTCAS"

# Layout
app.layout = dbc.Container([
    html.H1("🎓 MyTCAS Tuition Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("ประเภทหลักสูตร"),
            dcc.Dropdown(
                options=[{"label": pt, "value": pt} for pt in sorted(df["ประเภทหลักสูตร"].unique())],
                multi=True,
                id="type-filter",
                placeholder="เลือกประเภทหลักสูตร..."
            ),
        ], md=4),

        dbc.Col([
            html.Label("ช่วงค่าใช้จ่ายต่อภาคการศึกษา (บาท)"),
            dcc.RangeSlider(
                id="fee-range",
                min=0, max=int(df["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"].max()),
                step=5000,
                marks={0: "0", 100000: "100k", 200000: "200k", 300000: "300k"},
                value=[0, int(df["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"].max())],
            )
        ], md=8),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id="tuition-table",
                columns=[{"name": col, "id": col} for col in ["หลักสูตร", "ประเภทหลักสูตร", "ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)", "ค่าใช้จ่ายตลอดหลักสูตร (ประมาณ)"]],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "fontFamily": "Arial"},
                page_size=10,
            )
        ])
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="bar-chart")
        ], md=6),

        dbc.Col([
            dcc.Graph(id="pie-chart")
        ], md=6)
    ])

], fluid=True)

# Callback
@app.callback(
    [Output("tuition-table", "data"),
     Output("bar-chart", "figure"),
     Output("pie-chart", "figure")],
    [Input("type-filter", "value"),
     Input("fee-range", "value")]
)
def update_dashboard(type_selected, fee_range):
    filtered = df.copy()

    # Filter
    if type_selected:
        filtered = filtered[filtered["ประเภทหลักสูตร"].isin(type_selected)]
    filtered = filtered[
        (filtered["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"] >= fee_range[0]) &
        (filtered["ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)"] <= fee_range[1])
    ]

    # Bar chart
    bar_fig = px.bar(
        filtered.sort_values("ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)", ascending=False).head(10),
        x="ค่าใช้จ่ายต่อภาคการศึกษา (ประมาณ)",
        y="หลักสูตร",
        orientation="h",
        title="Top 10 หลักสูตรที่มีค่าใช้จ่ายต่อภาคการศึกษาสูงสุด",
        color="ประเภทหลักสูตร",
        template="plotly_white"
    )

    # Pie chart
    pie_fig = px.pie(
        filtered,
        names="ประเภทหลักสูตร",
        values="ค่าใช้จ่ายตลอดหลักสูตร (ประมาณ)",
        title="สัดส่วนค่าใช้จ่ายตลอดหลักสูตรตามประเภทหลักสูตร",
        hole=0.4
    )

    return filtered.to_dict("records"), bar_fig, pie_fig

if __name__ == '__main__':
    app.run(debug=True)
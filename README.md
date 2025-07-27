# 🎓 Thai University Tuition Dashboard

This dashboard provides an interactive tool to explore tuition fee information of academic programs listed on the [MyTCAS](https://course.mytcas.com/) platform — with a focus on **Computer Engineering**, **Artificial Intelligence Engineering**, and related programs. Built with [Dash by Plotly](https://dash.plotly.com/), this tool is especially useful for high school students who plan to apply to universities in Thailand.

---

## 📚 Features

- Scrape academic program and tuition fee data directly from the MyTCAS website
- Clean and process tuition data into a user-friendly format
- Interactive dashboard with real-time filtering and visualization
- Filter programs by type, language, and tuition cost range
- Visualizations include interactive bar charts and pie charts
- Searchable and filterable data table for detailed inspection

---

## ⚙️ How to Use

### 1. Set up the environment and install dependencies

```bash
git clone https://github.com/your-username/tuition-dashboard.git
cd tuition-dashboard

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install

python scrape_tuition.py

python clean_data.py

python app.py

Open your browser at http://127.0.0.1:8050
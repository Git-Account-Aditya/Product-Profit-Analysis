# Product Profit Analysis

This project digs into product-level profitability for the **Nassau Candy Distributor** dataset. It pairs hands-on Jupyter notebook analysis with an interactive Streamlit dashboard so you can explore margins, costs, and trends visually.

---

## Project Structure

```
Product-Profit-Analysis/
│
├── datasets/
│   ├── Nassau Candy Distributor.csv   # Original raw dataset
│   └── cleaned_dataset.csv            # Cleaned and validated version
│
├── notebooks/
│   ├── data_cleaning.ipynb            # Data cleaning and validation
│   ├── profit_metrics.ipynb           # Core profit KPI calculations
│   ├── division_metrics.ipynb         # Division-level breakdowns
│   ├── pareto_analysis.ipynb          # Pareto (80/20) analysis
│   └── cost_structure_diagnostics.ipynb  # Cost structure deep-dive
│
├── frontend/
│   ├── app.py                         # Main Streamlit app (entry point)
│   ├── config.py                      # Colors, chart defaults, layout helpers
│   ├── styles.py                      # Custom CSS (glassmorphism dark theme)
│   ├── data_loader.py                 # Data loading and caching
│   ├── metrics.py                     # KPI and metrics computation
│   ├── analysis_helpers.py            # Pareto, cost diagnostics, congestion
│   ├── components.py                  # Reusable UI components (KPI cards, headers)
│   └── modules/
│       ├── product_profitability.py   # Product margin leaderboard and contributions
│       ├── division_performance.py    # Division-level comparisons and heatmaps
│       ├── cost_diagnostics.py        # Cost vs margin scatter and quadrant analysis
│       ├── profit_concentration.py    # Pareto charts and dependency risk
│       └── raw_data.py               # Filterable data table with CSV download
│
├── requirements.txt
└── README.md
```

---

## Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/Git-Account-Aditya/Product-Profit-Analysis.git
   cd Product-Profit-Analysis
   ```

2. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the dashboard**

   ```bash
   cd frontend
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

---

## Notebooks Overview

Each notebook tackles a specific angle of the analysis. You can run them independently in any order (after data cleaning).

| Notebook | What it does |
|---|---|
| `data_cleaning.ipynb` | Cleans the raw dataset — handles missing values, fixes types, and exports the cleaned CSV |
| `profit_metrics.ipynb` | Calculates key profitability KPIs like gross margin, profit per unit, and contribution percentages |
| `division_metrics.ipynb` | Breaks down revenue, cost, and margin by business division |
| `pareto_analysis.ipynb` | Runs 80/20 analysis to find which products drive most of the revenue and profit |
| `cost_structure_diagnostics.ipynb` | Examines cost ratios, markup distribution, and flags products needing attention |

---

## Dashboard Tabs

The Streamlit dashboard has five tabs, each focusing on a different aspect:

- **Product Profitability** — Margin leaderboard, tier classification, contribution donut/treemap, and volatility charts
- **Division Performance** — Revenue vs profit comparison, health classification, margin distribution, and heatmaps
- **Cost vs Margin Diagnostics** — Cost-sales scatter plot, quadrant analysis, risk flags, and action recommendations
- **Profit Concentration** — Pareto curves, HHI-based dependency indicators, and state-level congestion detection
- **Raw Data** — Browse and filter the complete dataset, with CSV download

---

## Tech Stack

- **Python 3.10+**
- **Pandas / NumPy** — Data wrangling and computation
- **Plotly** — Interactive charts and visualizations
- **Streamlit** — Web-based dashboard framework

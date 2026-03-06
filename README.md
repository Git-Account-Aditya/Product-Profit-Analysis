# Product Profit Analysis

A data analysis project that explores product-level profitability for the Nassau Candy distributor dataset. It includes Jupyter notebooks for in-depth analysis and a Streamlit dashboard for interactive visualization.

## Project Structure

```
├── datasets/               # Raw and cleaned CSV data
├── notebooks/              # Jupyter analysis notebooks
│   ├── data_cleaning.ipynb
│   ├── profit_metrics.ipynb
│   ├── division_metrics.ipynb
│   ├── pareto_analysis.ipynb
│   └── cost_structure_diagnostics.ipynb
├── frontend/               # Streamlit dashboard
│   ├── app.py
│   └── analysis_helpers.py
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Git-Account-Aditya/Product-Profit-Analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   cd frontend
   streamlit run app.py
   ```

## Notebooks

| Notebook | Description |
|---|---|
| `data_cleaning.ipynb` | Cleans and validates the raw dataset |
| `profit_metrics.ipynb` | Computes key profit KPIs |
| `division_metrics.ipynb` | Breaks down metrics by division |
| `pareto_analysis.ipynb` | Identifies top products driving profit |
| `cost_structure_diagnostics.ipynb` | Analyzes cost components and margins |

## Tech Stack

- **Python 3.10+**
- **Pandas / NumPy** – data manipulation
- **Plotly** – interactive charts
- **Streamlit** – web dashboard

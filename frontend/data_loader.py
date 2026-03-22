import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and parse the cleaned dataset with proper date types."""
    data_path = Path(__file__).resolve().parent.parent / "datasets" / "cleaned_dataset.csv"
    df = pd.read_csv(data_path)
    
    # ── Standardize product and division labels ──
    df["Product Name"] = df["Product Name"].str.strip()
    df["Division"] = df["Division"].str.strip()
    
    # ── Remove zero-sales records ──
    df = df[df["Sales"] > 0]
    
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", dayfirst=True)
    return df

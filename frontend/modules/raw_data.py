import streamlit as st
from components import module_header


def render(filtered_df, full_df, start_date, end_date, selected_divisions):
    """Render the Raw Data Explorer tab."""

    module_header("", "cyan", "Raw Data Explorer",
                  "Browse, search, and download filtered dataset")

    st.markdown(
        f"<div class='insight-callout'>"
        f"Showing <strong>{len(filtered_df):,}</strong> of <strong>{len(full_df):,}</strong> records • "
        f"Date range: <strong>{start_date}</strong> to <strong>{end_date}</strong> • "
        f"Divisions: <strong>{', '.join(selected_divisions)}</strong>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.dataframe(filtered_df, use_container_width=True, height=520)

    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="filtered_profit_data.csv",
            mime="text/csv",
        )

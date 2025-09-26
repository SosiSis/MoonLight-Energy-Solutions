# app/main.py - Enhanced Streamlit Dashboard for Solar Radiation Analysis
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Handle imports for both local development and Streamlit Cloud deployment
import sys
import os

# Add the project root to Python path for imports
if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'app')):
    # Running from project root
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from app.utils import (
        load_all_countries, daily_agg_for_country, plot_timeseries_streamlit,
        cleaning_impact_report, compute_correlations, create_wind_analysis,
        generate_summary_stats, create_zscore_analysis, create_bubble_charts
    )
else:
    # Running from app directory or Streamlit Cloud
    try:
        from utils import (
            load_all_countries, daily_agg_for_country, plot_timeseries_streamlit,
            cleaning_impact_report, compute_correlations, create_wind_analysis,
            generate_summary_stats, create_zscore_analysis, create_bubble_charts
        )
    except ImportError:
        # Fallback: add current directory to path
        sys.path.append(os.path.dirname(__file__))
        from utils import (
            load_all_countries, daily_agg_for_country, plot_timeseries_streamlit,
            cleaning_impact_report, compute_correlations, create_wind_analysis,
            generate_summary_stats, create_zscore_analysis, create_bubble_charts
        )

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="MoonLight Energy Solutions - Solar Radiation Analysis",
    page_icon="☀️"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">☀️ MoonLight Energy Solutions</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header" style="font-size: 1.5rem;">Solar Radiation Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
**Strategic Investment Analysis for Solar Farm Development**  
*Analyzing solar radiation data from Benin, Sierra Leone, and Togo to identify high-potential regions for sustainable energy investments.*
""")

# Sidebar controls
st.sidebar.header("🎛️ Dashboard Controls")

# Country selection
countries = ["Benin", "Sierra Leone", "Togo"]
country = st.sidebar.selectbox("Select Country", options=countries)

# Analysis type selection
analysis_options = [
    "Overview & Summary",
    "Time Series Analysis",
    "Data Quality Assessment",
    "Correlation Analysis",
    "Wind Analysis",
    "Temperature Analysis",
    "Distribution Analysis",
    "Outlier Analysis",
    "Bubble Charts",
    "Country Comparison",
    "Strategic Recommendations"
]
analysis_type = st.sidebar.selectbox("Analysis Type", options=analysis_options)

# Load data
@st.cache_data
def load_data():
    return load_all_countries()

try:
    data = load_data()
    df = data.get(country)

    if df is None:
        st.error(f"❌ Data not found for {country}. Please ensure CSV files are in data/raw/ directory.")
        st.stop()

    # Main content based on analysis type
    if analysis_type == "Overview & Summary":
        st.markdown('<div class="section-header">📊 Data Overview & Summary Statistics</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Date Range", f"{df['Timestamp'].min().date()} to {df['Timestamp'].max().date()}")
        with col3:
            ghi_mean = df['GHI'].mean() if 'GHI' in df.columns else 0
            st.metric("Avg GHI", f"{ghi_mean:.1f} W/m²")

        # Summary statistics
        st.subheader("📈 Summary Statistics")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary_stats = generate_summary_stats(df, numeric_cols[:10])  # Limit columns for display
        st.dataframe(summary_stats.round(2))

        # Data preview
        st.subheader("🔍 Data Preview")
        st.dataframe(df.head(10))

    elif analysis_type == "Time Series Analysis":
        st.markdown('<div class="section-header">📈 Time Series Analysis</div>', unsafe_allow_html=True)

        # Daily aggregates
        daily = daily_agg_for_country(df)

        # Time series plots
        st.subheader("Solar Radiation Time Series")
        plot_timeseries_streamlit(daily, ['GHI', 'DNI', 'DHI'])

        # Temperature time series
        if 'Tamb' in daily.columns:
            st.subheader("Temperature Time Series")
            plot_timeseries_streamlit(daily, ['Tamb'])

        # Cleaning impact analysis
        st.subheader("🧹 Cleaning Impact Analysis")
        if 'Cleaning' in df.columns:
            impact = cleaning_impact_report(df, metric='ModA')
            if impact:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Events Analyzed", impact.get('n_events', 0))
                with col2:
                    st.metric("Pre-Cleaning Mean", f"{impact.get('mean_pre', 0):.2f}")
                with col3:
                    st.metric("Post-Cleaning Mean", f"{impact.get('mean_post', 0):.2f}")

                st.info(f"Cleaning improves sensor readings by {impact.get('mean_diff', 0):.2f} W/m² on average")

    elif analysis_type == "Data Quality Assessment":
        st.markdown('<div class="section-header">🔍 Data Quality Assessment</div>', unsafe_allow_html=True)

        # Missing values analysis
        st.subheader("Missing Values Analysis")
        missing_data = df.isnull().sum().reset_index()
        missing_data.columns = ['Column', 'Missing Count']
        missing_data['Missing %'] = (missing_data['Missing Count'] / len(df) * 100).round(2)
        st.dataframe(missing_data[missing_data['Missing Count'] > 0])

        # Data types
        st.subheader("Data Types")
        dtypes_df = pd.DataFrame({'Column': df.columns, 'Data Type': df.dtypes.astype(str)})
        st.dataframe(dtypes_df)

        # Negative values check
        st.subheader("Negative Values Check")
        non_negative_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Precipitation', 'WS', 'WSgust']
        neg_check = {}
        for col in non_negative_cols:
            if col in df.columns:
                neg_count = (df[col] < 0).sum()
                neg_check[col] = neg_count
        neg_df = pd.DataFrame(list(neg_check.items()), columns=['Column', 'Negative Count'])
        st.dataframe(neg_df[neg_df['Negative Count'] > 0])

    elif analysis_type == "Correlation Analysis":
        st.markdown('<div class="section-header">🔗 Correlation Analysis</div>', unsafe_allow_html=True)

        correlations = compute_correlations(df)

        # Correlation heatmap
        st.subheader("Correlation Matrix")
        if correlations is not None and not correlations.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlations, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
            st.pyplot(fig)

        # Key correlations display
        st.subheader("Key Correlation Insights")
        key_correlations = []
        if 'GHI' in correlations.index and 'DNI' in correlations.columns:
            key_correlations.append(("GHI-DNI", correlations.loc['GHI', 'DNI']))
        if 'GHI' in correlations.index and 'Tamb' in correlations.columns:
            key_correlations.append(("GHI-Temperature", correlations.loc['GHI', 'Tamb']))
        if 'WS' in correlations.index and 'GHI' in correlations.columns:
            key_correlations.append(("Wind Speed-GHI", correlations.loc['WS', 'GHI']))

        for corr_name, corr_value in key_correlations:
            st.metric(corr_name, f"{corr_value:.3f}")

    elif analysis_type == "Wind Analysis":
        st.markdown('<div class="section-header">💨 Wind Analysis</div>', unsafe_allow_html=True)

        wind_stats = create_wind_analysis(df)

        if wind_stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Wind Speed", f"{wind_stats.get('mean_ws', 0):.2f} m/s")
            with col2:
                st.metric("Max Wind Speed", f"{wind_stats.get('max_ws', 0):.2f} m/s")
            with col3:
                st.metric("Wind Speed Std", f"{wind_stats.get('std_ws', 0):.2f} m/s")
            with col4:
                st.metric("Direction Std", f"{wind_stats.get('std_wd', 0):.2f}°")

            # Wind rose plot would go here if implemented
            st.info("Wind rose visualization available in notebook analysis")

    elif analysis_type == "Temperature Analysis":
        st.markdown('<div class="section-header">🌡️ Temperature Analysis</div>', unsafe_allow_html=True)

        if 'Tamb' in df.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Temperature", f"{df['Tamb'].mean():.2f}°C")
            with col2:
                st.metric("Max Temperature", f"{df['Tamb'].max():.2f}°C")
            with col3:
                st.metric("Min Temperature", f"{df['Tamb'].min():.2f}°C")

            # Temperature distribution
            st.subheader("Temperature Distribution")
            fig, ax = plt.subplots()
            df['Tamb'].hist(bins=50, ax=ax)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

            # Hourly temperature patterns
            if 'Timestamp' in df.columns:
                st.subheader("Daily Temperature Patterns")
                df_temp = df.copy()
                df_temp['hour'] = df_temp['Timestamp'].dt.hour
                hourly_temp = df_temp.groupby('hour')['Tamb'].mean()

                fig, ax = plt.subplots()
                hourly_temp.plot(kind='bar', ax=ax)
                ax.set_xlabel("Hour of Day")
                ax.set_ylabel("Average Temperature (°C)")
                ax.set_title("Temperature by Hour")
                plt.xticks(rotation=0)
                st.pyplot(fig)

    elif analysis_type == "Distribution Analysis":
        st.markdown('<div class="section-header">📊 Distribution Analysis</div>', unsafe_allow_html=True)

        # Select variable to analyze
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        selected_var = st.selectbox("Select Variable", numeric_cols)

        if selected_var:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Histogram
            df[selected_var].hist(bins=50, ax=ax1, alpha=0.7)
            ax1.set_title(f"{selected_var} Distribution")
            ax1.set_xlabel(selected_var)
            ax1.set_ylabel("Frequency")
            ax1.axvline(df[selected_var].mean(), color='red', linestyle='--', label='Mean')
            ax1.axvline(df[selected_var].median(), color='green', linestyle='--', label='Median')
            ax1.legend()

            # Box plot
            df[selected_var].plot(kind='box', ax=ax2)
            ax2.set_title(f"{selected_var} Box Plot")

            st.pyplot(fig)

            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{df[selected_var].mean():.2f}")
            with col2:
                st.metric("Median", f"{df[selected_var].median():.2f}")
            with col3:
                st.metric("Std Dev", f"{df[selected_var].std():.2f}")
            with col4:
                st.metric("Skewness", f"{df[selected_var].skew():.2f}")

    elif analysis_type == "Outlier Analysis":
        st.markdown('<div class="section-header">🔍 Outlier Analysis (Z-Score Method)</div>', unsafe_allow_html=True)

        outlier_data = create_zscore_analysis(df)

        if outlier_data:
            st.subheader("Outlier Summary")
            outlier_df = pd.DataFrame(outlier_data).T
            st.dataframe(outlier_df.round(2))

            # Z-score distribution for selected variable
            zscore_vars = [col for col in df.columns if col.replace('_z', '') != col and '_z' in col]
            if zscore_vars:
                selected_zvar = st.selectbox("Select variable for Z-score plot", [v.replace('_z', '') for v in zscore_vars])

                if selected_zvar and f"{selected_zvar}_z" in df.columns:
                    fig, ax = plt.subplots()
                    df[f"{selected_zvar}_z"].hist(bins=50, ax=ax)
                    ax.axvline(3, color='red', linestyle='--', label='Z = ±3')
                    ax.axvline(-3, color='red', linestyle='--')
                    ax.set_xlabel("Z-Score")
                    ax.set_ylabel("Frequency")
                    ax.set_title(f"{selected_zvar} Z-Score Distribution")
                    ax.legend()
                    st.pyplot(fig)

    elif analysis_type == "Bubble Charts":
        st.markdown('<div class="section-header">🫧 Bubble Charts - Complex Relationships</div>', unsafe_allow_html=True)

        bubble_data = create_bubble_charts(df)

        if bubble_data:
            # Interactive bubble chart
            sample = df.sample(min(1000, len(df)))

            if all(col in sample.columns for col in ['GHI', 'Tamb', 'WS', 'RH']):
                fig = px.scatter(sample, x='Tamb', y='GHI', size='RH', color='WS',
                               title='GHI vs Temperature (Bubble: RH, Color: WS)',
                               labels={'Tamb': 'Temperature (°C)', 'GHI': 'GHI (W/m²)',
                                      'RH': 'Relative Humidity (%)', 'WS': 'Wind Speed (m/s)'})
                st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Country Comparison":
        st.markdown('<div class="section-header">🌍 Country Comparison</div>', unsafe_allow_html=True)

        # Compare key metrics across countries
        comparison_data = {}
        for c, c_df in data.items():
            if 'GHI' in c_df.columns:
                comparison_data[c] = {
                    'Mean GHI': c_df['GHI'].mean(),
                    'Mean Temperature': c_df['Tamb'].mean() if 'Tamb' in c_df.columns else None,
                    'Mean Wind Speed': c_df['WS'].mean() if 'WS' in c_df.columns else None,
                    'Data Points': len(c_df)
                }

        comp_df = pd.DataFrame(comparison_data).T
        st.dataframe(comp_df.round(2))

        # Bar chart comparison
        st.subheader("GHI Comparison")
        if 'Mean GHI' in comp_df.columns:
            fig, ax = plt.subplots()
            comp_df['Mean GHI'].plot(kind='bar', ax=ax)
            ax.set_ylabel("Mean GHI (W/m²)")
            ax.set_title("Average Global Horizontal Irradiance by Country")
            plt.xticks(rotation=45)
            st.pyplot(fig)

    elif analysis_type == "Strategic Recommendations":
        st.markdown('<div class="section-header">🎯 Strategic Recommendations</div>', unsafe_allow_html=True)

        # Calculate scores for all countries
        country_scores = {}
        for c, c_df in data.items():
            daily_agg = daily_agg_for_country(c_df)
            # Simple scoring based on GHI and temperature
            ghi_score = daily_agg['GHI'].mean() / 100  # Normalize
            temp_penalty = max(0, (daily_agg['Tamb'].mean() - 25) / 10) if 'Tamb' in daily_agg.columns else 0
            score = ghi_score - temp_penalty
            country_scores[c] = score

        # Rank countries
        ranked = sorted(country_scores.items(), key=lambda x: x[1], reverse=True)

        st.subheader("🏆 Investment Priority Ranking")
        for i, (country_name, score) in enumerate(ranked, 1):
            priority = "🔴 HIGH" if i == 1 else "🟡 MEDIUM" if i == 2 else "🟢 LOW"
            st.markdown(f"**{i}. {country_name}** - Score: {score:.2f} - {priority}")

        # Recommendations
        st.subheader("💡 Key Insights & Recommendations")

        top_country = ranked[0][0]
        st.success(f"**Primary Recommendation:** Focus initial investments in {top_country} due to superior solar irradiance potential.")

        st.info("""
        **Key Strategic Insights:**
        - Prioritize locations with high GHI and moderate temperatures
        - Consider hybrid solar-wind installations where wind resources are strong
        - Implement regular sensor cleaning schedules to maintain efficiency
        - Monitor seasonal variations for optimal project planning
        - Account for temperature correlations in panel placement and cooling systems
        """)

        st.subheader("📋 Next Steps")
        st.markdown("""
        1. **Site Visits:** Conduct detailed site assessments in top-ranked locations
        2. **Feasibility Studies:** Perform comprehensive technical and financial analysis
        3. **Pilot Projects:** Launch small-scale installations for testing and validation
        4. **Technology Selection:** Choose appropriate solar technologies based on local conditions
        5. **Partnership Development:** Engage with local stakeholders and governments
        """)

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure CSV files are placed in the `data/raw/` directory with proper column names.")

# Footer
st.markdown("---")
st.markdown("*Dashboard created for MoonLight Energy Solutions - Week 0 Challenge*")
st.markdown("*Built with Streamlit, Pandas, and Plotly*")

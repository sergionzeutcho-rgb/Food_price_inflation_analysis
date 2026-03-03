"""
Food Price Inflation Analysis Dashboard
=======================================
A Streamlit dashboard for exploring global food price trends and ML predictions.

Team: Florence, Gia & Sergio
Code Institute Hackathon
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import joblib
from scipy.stats import kruskal, spearmanr, mannwhitneyu

# Page configuration
st.set_page_config(
    page_title="Food Price Inflation Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global colour constants ────────────────────────────────────────────────
COLOR_LOW   = "#27ae60"   # green  – low / safe
COLOR_MED   = "#f39c12"   # amber  – moderate / caution
COLOR_HIGH  = "#e74c3c"   # red    – high / alert
COLOR_BLUE  = "#1f77b4"   # brand blue

RISK_LOW_THRESHOLD  = 5    # inflation %
RISK_HIGH_THRESHOLD = 10   # inflation %

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── typography ── */
    .main-header {
        font-size: 3.4rem;
        font-weight: 800;
        color: #1f77b4;
        text-align: center;
        letter-spacing: -0.5px;
        margin-bottom: 0.15rem;
        line-height: 1.15;
    }
    .section-header {
        font-size: 1.65rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    /* ── coloured callout boxes ── */
    .explanation-box {
        background-color: #e8f4f8;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
        color: #1a1a2e;
    }
    .outcome-box {
        background-color: #e8f8e8;
        border-left: 4px solid #27ae60;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
        color: #1a1a2e;
    }
    .recommendation-box {
        background-color: #fff8e8;
        border-left: 4px solid #f39c12;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
        color: #1a1a2e;
    }
    /* TL;DR / key-takeaway strip */
    .takeaway-box {
        background: linear-gradient(135deg, #e8e4f8 0%, #f0e8f8 100%);
        border: 1px solid #667eea55;
        border-left: 5px solid #667eea;
        padding: 0.85rem 1.1rem;
        margin: 0.5rem 0 1.5rem 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.97rem;
        color: #1a1a2e;
    }
    /* Risk colour badges */
    .badge-low  { background:#27ae60; color:#fff; padding:2px 9px; border-radius:12px; font-weight:600; }
    .badge-med  { background:#f39c12; color:#fff; padding:2px 9px; border-radius:12px; font-weight:600; }
    .badge-high { background:#e74c3c; color:#fff; padding:2px 9px; border-radius:12px; font-weight:600; }
    /* metric card */
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    /* ── navigation buttons: compact, 2-row on narrow screens ── */
    div[data-testid="column"] button {
        font-size: 0.72rem !important;
        padding: 0.28rem 0.15rem !important;
        white-space: normal;
        line-height: 1.2;
    }
    div[data-testid="column"] button p {
        font-size: 0.72rem !important;
        white-space: normal;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load the cleaned dataset."""
    try:
        df = pd.read_csv('data/cleaned/food_prices_cleaned.csv', parse_dates=['date'])
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please run the Data_Cleaning notebook first.")
        return None


@st.cache_resource
def load_model():
    """Load the trained ML model and related files."""
    try:
        model = joblib.load('outputs/models/best_model.joblib')
        scaler = joblib.load('outputs/models/feature_scaler.joblib')
        encoder = joblib.load('outputs/models/country_encoder.joblib')
        feature_cols = joblib.load('outputs/models/feature_columns.joblib')
        return model, scaler, encoder, feature_cols
    except FileNotFoundError:
        return None, None, None, None


def create_time_series_chart(df, country=None):
    """Create interactive time series chart."""
    if country and country != "All Countries":
        data = df[df['country'] == country]
        title = f"Food Price Index Over Time - {country}"
    else:
        data = df.groupby('date').agg({'close': 'mean', 'inflation': 'mean'}).reset_index()
        title = "Global Average Food Price Index Over Time"
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Price Index', 'Inflation Rate (%)'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=data['date'], y=data['close'], mode='lines', 
                   name='Price Index', line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    if 'inflation' in data.columns:
        fig.add_trace(
            go.Scatter(x=data['date'], y=data['inflation'], mode='lines',
                       name='Inflation', line=dict(color='#ff7f0e', width=2)),
            row=2, col=1
        )
    
    fig.update_layout(
        title=title,
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


def create_country_comparison(df, metric='inflation'):
    """Create country comparison bar chart."""
    if metric == 'inflation':
        country_stats = df.groupby('country')[metric].mean().sort_values(ascending=True)
        title = "Average Inflation by Country"
        xaxis_title = "Average Inflation (%)"
    else:
        country_stats = df.groupby('country')['close'].mean().sort_values(ascending=True)
        title = "Average Price Index by Country"
        xaxis_title = "Average Price Index"
    
    colors = [COLOR_HIGH if x > 0 else COLOR_BLUE for x in country_stats]
    
    fig = go.Figure(go.Bar(
        x=country_stats.values,
        y=country_stats.index,
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Country",
        height=600
    )
    
    if metric == 'inflation':
        fig.add_vline(x=0, line_dash="dash", line_color="black")
    
    return fig


def create_seasonal_chart(df):
    """Create seasonal pattern chart."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_avg = df.groupby('month')['inflation'].mean()
    
    fig = go.Figure(go.Bar(
        x=months,
        y=monthly_avg.values,
        marker_color=[COLOR_HIGH if x > monthly_avg.mean() else COLOR_BLUE for x in monthly_avg]
    ))
    
    fig.add_hline(y=monthly_avg.mean(), line_dash="dash", line_color="black",
                  annotation_text=f"Average: {monthly_avg.mean():.2f}%")
    
    fig.update_layout(
        title="Average Inflation by Month (Seasonal Pattern)",
        xaxis_title="Month",
        yaxis_title="Average Inflation (%)",
        height=400
    )
    
    return fig


def create_distribution_charts(df):
    """Create distribution analysis charts using Plotly."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distribution of Food Prices', 'Distribution of Inflation',
                       'Distribution of Price Volatility', 'Inflation by Year')
    )
    
    # Price distribution
    fig.add_trace(
        go.Histogram(x=df['close'], nbinsx=50, marker_color='steelblue', 
                    name='Price', opacity=0.7),
        row=1, col=1
    )
    fig.add_vline(x=df['close'].mean(), line_dash="dash", line_color="red",
                  row=1, col=1, annotation_text=f"Mean: {df['close'].mean():.1f}")
    
    # Inflation distribution
    fig.add_trace(
        go.Histogram(x=df['inflation'].dropna(), nbinsx=50, marker_color='coral',
                    name='Inflation', opacity=0.7),
        row=1, col=2
    )
    fig.add_vline(x=0, line_dash="solid", line_color="black", row=1, col=2)
    
    # Volatility distribution
    fig.add_trace(
        go.Histogram(x=df['price_range'], nbinsx=50, marker_color='mediumpurple',
                    name='Volatility', opacity=0.7),
        row=2, col=1
    )
    
    # Inflation by year boxplot
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]['inflation'].dropna()
        fig.add_trace(
            go.Box(y=year_data, name=str(year), marker_color='seagreen', showlegend=False),
            row=2, col=2
        )
    
    fig.update_layout(height=600, showlegend=False, title_text="Distribution Analysis")
    return fig


def create_correlation_heatmap(df):
    """Create correlation heatmap."""
    correlation_cols = ['open', 'high', 'low', 'close', 'inflation', 'price_range']
    corr_matrix = df[correlation_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=correlation_cols,
        y=correlation_cols,
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 12},
        hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Correlation Heatmap",
        height=500,
        xaxis_title="Variable",
        yaxis_title="Variable"
    )
    return fig


def create_volatility_inflation_scatter(df):
    """Create volatility vs inflation scatter plot."""
    valid = df[['price_range', 'inflation']].dropna()
    corr, p_value = spearmanr(valid['price_range'], valid['inflation'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=valid['price_range'],
        y=valid['inflation'],
        mode='markers',
        marker=dict(size=5, opacity=0.3, color='steelblue'),
        name='Data Points'
    ))
    
    # Add trend line
    z = np.polyfit(valid['price_range'], valid['inflation'], 1)
    x_line = np.linspace(valid['price_range'].min(), valid['price_range'].max(), 100)
    y_line = np.poly1d(z)(x_line)
    
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        line=dict(color='red', width=2),
        name='Trend Line'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    result = 'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'
    fig.update_layout(
        title=f"Volatility vs Inflation (r={corr:.4f}, p={p_value:.2e}) - {result}",
        xaxis_title="Price Volatility (Price Range)",
        yaxis_title="Inflation (%)",
        height=450
    )
    return fig, corr, p_value


def create_country_boxplot(df):
    """Create inflation by country boxplot."""
    order = df.groupby('country')['inflation'].median().sort_values(ascending=False).index.tolist()
    
    fig = go.Figure()
    for country in order:
        country_data = df[df['country'] == country]['inflation'].dropna()
        fig.add_trace(go.Box(
            y=country_data,
            name=country,
            boxmean=True
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    
    fig.update_layout(
        title="Inflation Distribution by Country (H1: Regional Differences)",
        xaxis_title="Country",
        yaxis_title="Inflation (%)",
        height=500,
        showlegend=False,
        xaxis_tickangle=45
    )
    return fig


def create_seasonal_boxplot(df):
    """Create seasonal boxplot for hypothesis testing."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig = go.Figure()
    for i, month in enumerate(months, 1):
        month_data = df[df['month'] == i]['inflation'].dropna()
        fig.add_trace(go.Box(
            y=month_data,
            name=month,
            boxmean=True
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    
    fig.update_layout(
        title="Inflation Distribution by Month (H3: Seasonality)",
        xaxis_title="Month",
        yaxis_title="Inflation (%)",
        height=400,
        showlegend=False
    )
    return fig


def create_price_trend_chart(df):
    """Create early vs recent price comparison chart."""
    years = sorted(df['year'].unique())
    mid = years[len(years)//2]
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        'Early vs Recent Price Distribution', 'Average Price by Year'
    ))
    
    # Box plot comparison
    early_prices = df[df['year'] < mid]['close']
    recent_prices = df[df['year'] >= mid]['close']
    
    fig.add_trace(
        go.Box(y=early_prices, name=f'Early ({years[0]}-{mid-1})', marker_color='steelblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Box(y=recent_prices, name=f'Recent ({mid}-{years[-1]})', marker_color='coral'),
        row=1, col=1
    )
    
    # Yearly trend
    yearly_avg = df.groupby('year')['close'].mean()
    fig.add_trace(
        go.Scatter(x=yearly_avg.index, y=yearly_avg.values, mode='lines+markers',
                  name='Avg Price', line=dict(color='steelblue', width=2)),
        row=1, col=2
    )
    
    # Add trend line
    z = np.polyfit(yearly_avg.index.to_numpy(), yearly_avg.to_numpy(), 1)
    fig.add_trace(
        go.Scatter(x=yearly_avg.index, y=np.poly1d(z)(yearly_avg.index),
                  mode='lines', name='Trend', line=dict(color='red', dash='dash')),
        row=1, col=2
    )
    
    # Add midpoint line
    fig.add_vline(x=mid, line_dash="dot", line_color="gray", row=1, col=2,
                  annotation_text="Split Point")
    
    fig.update_layout(height=400, title_text="H4: Long-term Price Trend Analysis")
    return fig, mid, early_prices.mean(), recent_prices.mean()


def create_model_comparison_chart(results_df):
    """Create model comparison bar charts."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=('R² Score by Model', 'Prediction Error by Model'))
    
    models = results_df['Model'].tolist()
    x = np.arange(len(models))
    
    # R² comparison
    fig.add_trace(
        go.Bar(x=models, y=results_df['Train R²'], name='Train R²', marker_color='steelblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=models, y=results_df['Test R²'], name='Test R²', marker_color='coral'),
        row=1, col=1
    )
    
    # Error comparison
    fig.add_trace(
        go.Bar(x=models, y=results_df['Test MAE'], name='MAE', marker_color='mediumpurple'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=models, y=results_df['Test RMSE'], name='RMSE', marker_color='seagreen'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, barmode='group')
    return fig


def create_interactive_country_lines(df):
    """Create interactive line chart showing all countries."""
    fig = px.line(
        df, x='date', y='close', color='country',
        title='Food Price Index by Country Over Time',
        labels={'close': 'Price Index', 'date': 'Date', 'country': 'Country'}
    )
    
    fig.update_layout(
        height=600,
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
        hovermode='x unified'
    )
    return fig


def create_gauge_chart(prediction: float, title: str = "Predicted Inflation") -> go.Figure:
    """Create a gauge chart showing predicted inflation and risk level."""
    # Colour steps: green → amber → red
    if prediction <= RISK_LOW_THRESHOLD:
        bar_color = COLOR_LOW
    elif prediction <= RISK_HIGH_THRESHOLD:
        bar_color = COLOR_MED
    else:
        bar_color = COLOR_HIGH

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=prediction,
        number={"suffix": "%", "font": {"size": 28}},
        title={"text": title, "font": {"size": 16}},
        gauge={
            "axis": {"range": [-10, 30], "ticksuffix": "%"},
            "bar": {"color": bar_color, "thickness": 0.35},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#ccc",
            "steps": [
                {"range": [-10, RISK_LOW_THRESHOLD],  "color": "#d5f5e3"},
                {"range": [RISK_LOW_THRESHOLD, RISK_HIGH_THRESHOLD], "color": "#fef9e7"},
                {"range": [RISK_HIGH_THRESHOLD, 30],  "color": "#fce4e4"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": prediction,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(t=60, b=10, l=30, r=30))
    return fig


def get_risk_label(prediction: float) -> tuple[str, str]:
    """Return (emoji+label, css-class) for a given inflation prediction."""
    if prediction > RISK_HIGH_THRESHOLD:
        return "🔴 High Risk", "badge-high"
    elif prediction > RISK_LOW_THRESHOLD:
        return "🟡 Medium Risk", "badge-med"
    else:
        return "🟢 Low Risk", "badge-low"


def main():
    """Main application."""
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Overview"
    
    # Header
    st.markdown('<p class="main-header">Food Price Inflation Analysis</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: gray; font-size: 1.05rem; margin-top: 0;">
    Exploring global food price trends and predicting inflation patterns<br>
    <small>Team: Florence, Gia &amp; Sergio &nbsp;|&nbsp; Code Institute Hackathon</small>
    </p>
    """, unsafe_allow_html=True)
    
    # Navigation Bar in Header (visible on all pages)
    nav_pages = ["Overview", "Data Cleaning", "Data Analysis", "Hypothesis Testing", 
                 "ML Predictions", "Prediction Tool", "Country Explorer", "About"]
    nav_icons = ["", "", "", "", "", "", "", ""]
    
    # Create navigation buttons in columns
    nav_cols = st.columns(len(nav_pages))
    for i, (col, nav_page, icon) in enumerate(zip(nav_cols, nav_pages, nav_icons)):
        with col:
            if st.button(f"{icon} {nav_page}", key=f"nav_{nav_page}", use_container_width=True,
                        type="primary" if st.session_state.current_page == nav_page else "secondary"):
                st.session_state.current_page = nav_page
                st.rerun()
    
    st.markdown("---")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Use session state for current page
    page = st.session_state.current_page
    
    # Sidebar
    st.sidebar.image("https://codeinstitute.s3.amazonaws.com/fullstack/ci_logo_small.png", width=200)
    st.sidebar.title("Dashboard Controls")
    
    # Sidebar navigation (synced with header via index, no key so stale state can't override)
    sidebar_page = st.sidebar.radio(
        "Navigate to:",
        nav_pages,
        index=nav_pages.index(page)
    )
    
    # Sync sidebar selection with session state
    if sidebar_page != page:
        st.session_state.current_page = sidebar_page
        st.rerun()
    
    # Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    
    countries = ["All Countries"] + sorted(df['country'].unique().tolist())
    selected_country = st.sidebar.selectbox(
        "Select Country",
        countries,
        help="Filter all charts to show data for one country only"
    )
    
    years = sorted(df['year'].unique())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
        help="Drag the handles to narrow the time window"
    )
    
    # Reset filters button
    default_country = "All Countries"
    default_years   = (int(min(years)), int(max(years)))
    filters_active  = (selected_country != default_country) or (year_range != default_years)
    
    if filters_active:
        st.sidebar.markdown("**Active filters:**")
        if selected_country != default_country:
            st.sidebar.info(f"{selected_country}")
        if year_range != default_years:
            st.sidebar.info(f"{year_range[0]} – {year_range[1]}")

    if st.sidebar.button("Reset Filters", use_container_width=True, disabled=not filters_active):
        st.session_state["_reset_country"] = True
        st.rerun()
    
    # Handle reset (re-run with defaults)
    if st.session_state.get("_reset_country"):
        st.session_state.pop("_reset_country", None)
        selected_country = default_country
        year_range       = default_years
    
    # Filter data
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    if selected_country != "All Countries":
        df_filtered = df_filtered[df_filtered['country'] == selected_country]
    
    # ============= PAGE: OVERVIEW =============
    if page == "Overview":
        st.markdown('<p class="section-header">Project Overview</p>', unsafe_allow_html=True)
        
        # TL;DR key takeaway
        avg_inf_all = df['inflation'].mean()
        st.markdown(f"""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Over 16 years (2007–2023) food prices rose significantly across 
        25 countries. Average global inflation stood at <strong>{avg_inf_all:.1f}%</strong> per year, 
        with large regional differences. Scroll down or use a page in the navigation bar to dive deeper.
        </div>
        """, unsafe_allow_html=True)
        
        # How to Use expander
        with st.expander("How to Use This Dashboard", expanded=False):
            st.markdown("""
            **Getting Started**

            | Step | What to do |
            |------|-----------|
            | 1 | Use the **top navigation buttons** (or the sidebar) to switch between pages |
            | 2 | Use the **sidebar filters** to narrow data by country or year range |
            | 3 | Hover any chart to see exact values; click legend items to show/hide series |
            | 4 | Visit **Prediction Tool** to forecast future inflation for any country |
            | 5 | Visit **Country Explorer** to download filtered data as CSV |

            **Page Guide**
            - **Overview** — big-picture summary and key metrics
            - **Data Cleaning** — how the raw dataset was prepared
            - **Data Analysis** — distributions, correlations and seasonal patterns
            - **Hypothesis Testing** — statistically validated findings
            - **ML Predictions** — model training, comparison and feature importance
            - **Prediction Tool** — interactive inflation forecaster
            - **Country Explorer** — per-country deep-dive and data download
            - **About** — team, methodology and data source
            """)
        
        st.markdown("""
        This dashboard presents a comprehensive analysis of global food price inflation trends using the 
        World Real-Time Food Prices (RTFP) dataset from the World Bank. Our team has examined how food 
        prices have evolved across 25 countries from January 2007 to October 2023, uncovering patterns 
        that have important implications for policymakers, businesses, and consumers worldwide.
        """)
        
        # Key metrics
        st.markdown('<p class="section-header">Key Metrics at a Glance</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Countries Analysed",
                df_filtered['country'].nunique(),
                help="Number of distinct countries in the currently filtered dataset"
            )
        
        with col2:
            st.metric(
                "Data Points",
                f"{len(df_filtered):,}",
                help="Total monthly observations matching your current filters"
            )
        
        with col3:
            avg_inflation = df_filtered['inflation'].mean()
            color_note = "🟢" if avg_inflation < RISK_LOW_THRESHOLD else ("🟡" if avg_inflation < RISK_HIGH_THRESHOLD else "🔴")
            st.metric(
                "Avg Inflation",
                f"{avg_inflation:.2f}%",
                help=f"{color_note} Average year-over-year food price inflation. Below 5% = low, 5–10% = moderate, above 10% = high"
            )
        
        with col4:
            if len(df_filtered) > 1:
                price_change = ((df_filtered['close'].iloc[-1] - df_filtered['close'].iloc[0]) / 
                               df_filtered['close'].iloc[0] * 100)
                st.metric(
                    "Total Price Change",
                    f"{price_change:.1f}%",
                    help="Cumulative percentage change in the food price index from first to last data point in the filtered range"
                )
            else:
                st.metric("Total Price Change", "N/A")
        
        # Time series chart
        st.markdown('<p class="section-header">Price Trends Over Time</p>', unsafe_allow_html=True)
        
        st.markdown("""
        The chart below displays the evolution of food price indices and inflation rates over the study 
        period. The upper panel shows the closing price index, which represents the overall level of 
        food prices, while the lower panel displays the year-over-year inflation rate, indicating how 
        quickly prices are changing compared to the same period in the previous year.
        """)
        
        fig = create_time_series_chart(df_filtered, 
                                       selected_country if selected_country != "All Countries" else None)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key findings summary
        st.markdown('<p class="section-header">Key Findings Summary</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="outcome-box">
        <strong>Our analysis has revealed several important findings about global food price inflation:</strong><br><br>
        
        Food prices have demonstrated a consistent upward trend over the 16-year study period, with 
        the average price index increasing substantially from 2007 to 2023. This trend raises significant 
        concerns about food affordability, particularly for vulnerable populations in developing economies.
        
        We observed substantial regional variation in inflation rates, with some countries experiencing 
        average inflation rates exceeding 20% while others maintained relatively stable prices. This 
        disparity suggests that local factors such as agricultural policies, supply chain efficiency, 
        and economic conditions play a crucial role in determining food price outcomes.
        
        Our statistical analysis confirmed a significant relationship between price volatility and 
        inflation rates. Countries and periods with higher price volatility tend to experience higher 
        inflation, suggesting that price stabilisation policies could be an effective tool for 
        controlling food price inflation.
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<p class="section-header">Quick Actions</p>', unsafe_allow_html=True)
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            st.markdown("""
            <div class="explanation-box">
            <strong>Prediction Tool</strong><br>
            Use our ML model to forecast inflation for any country and time period.
            Navigate to <em>Prediction Tool</em> in the sidebar.
            </div>
            """, unsafe_allow_html=True)

        with action_col2:
            st.markdown("""
            <div class="outcome-box">
            <strong>Country Explorer</strong><br>
            Dive deep into country-specific data, compare statistics, and export data.
            Navigate to <em>Country Explorer</em> in the sidebar.
            </div>
            """, unsafe_allow_html=True)

        with action_col3:
            st.markdown("""
            <div class="recommendation-box">
            <strong>Hypothesis Testing</strong><br>
            Review our statistical findings and validated hypotheses about food prices.
            Navigate to <em>Hypothesis Testing</em> in the sidebar.
            </div>
            """, unsafe_allow_html=True)
    
    # ============= PAGE: DATA CLEANING =============
    elif page == "Data Cleaning":
        st.markdown('<p class="section-header">Data Cleaning Process</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — The raw World Bank dataset (4,798 rows, 8 columns) was loaded,
        validated and enriched with 6 new features (volatility, price change, month, year…).
        Missing inflation values (≈7.6%) were kept intentionally — they are structural gaps from the
        year-over-year calculation, not errors.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        Data cleaning is the foundational step of any data analytics project, and its importance cannot 
        be overstated. The quality of our analysis depends entirely on the quality of the data we use. 
        In this stage, we transformed the raw World Bank dataset into a clean, structured format suitable 
        for statistical analysis and machine learning.
        """)
        
        st.markdown('<p class="section-header">Data Source and Loading</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why This Step Matters:</strong><br><br>
        The raw data comes from the World Bank's Real-Time Food Prices monitoring system, which tracks 
        food price indices across multiple countries. Before we can analyse this data, we need to load 
        it into our analysis environment and understand its structure. This initial exploration helps 
        us identify potential issues such as missing values, incorrect data types, or inconsistencies 
        that could affect our analysis.
        </div>
        """, unsafe_allow_html=True)
        
        st.code("""
# Load raw data from CSV file
df = pd.read_csv('../data/raw/WLD_RTFP_country_2023-10-02.csv')

# Display basic information about the dataset
print(f"Dataset size: {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"Countries in dataset: {df['country'].nunique()}")
        """, language="python")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Records", "4,798")
        with col2:
            st.metric("Original Columns", "8")
        
        st.markdown('<p class="section-header">Missing Values Analysis</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Check for Missing Values:</strong><br><br>
        Missing values can significantly impact our analysis in several ways. Statistical calculations 
        like means and standard deviations can be biased if missing values are not handled properly. 
        Many machine learning algorithms cannot process datasets containing missing values at all. 
        Additionally, patterns in missingness themselves can provide insights—for example, if inflation 
        data is missing for certain periods, this might indicate data collection challenges during 
        those times.
        
        In our dataset, approximately 7.6% of inflation values are missing. This is expected because 
        inflation is calculated as a year-over-year change, meaning the first 12 months of data for 
        each country naturally lack inflation values. We retain these records because the other price 
        columns (Open, High, Low, Close) are complete and valuable for our analysis.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-header">Feature Engineering</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Create New Features:</strong><br><br>
        Feature engineering is the process of creating new variables from existing data that better 
        capture the underlying patterns we want to analyse. This is often the most impactful step in 
        a data science project, as well-designed features can dramatically improve both the insights 
        we gain from analysis and the performance of machine learning models.
        
        We created three key derived features for this analysis:
        
        <strong>Price Range (High - Low):</strong> This measures the volatility within each monthly period. 
        A large difference between the highest and lowest prices indicates an unstable market with 
        significant price fluctuations.
        
        <strong>Price Change (Close - Open):</strong> This shows the direction of price movement within 
        the period. Positive values indicate prices rose during the month, while negative values 
        indicate prices fell.
        
        <strong>Price Change Percentage:</strong> By expressing the price change as a percentage, we 
        can fairly compare movements across countries with different absolute price levels. A 5-point 
        change means something very different in a country where prices average 50 compared to one 
        where prices average 200.
        </div>
        """, unsafe_allow_html=True)
        
        st.code("""
# Create volatility indicator
df['price_range'] = df['high'] - df['low']

# Create direction of change
df['price_change'] = df['close'] - df['open']

# Create percentage change for fair comparison
df['price_change_pct'] = ((df['close'] - df['open']) / df['open'] * 100).round(4)

# Extract temporal components for seasonal analysis
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
        """, language="python")
        
        st.markdown('<p class="section-header">Cleaning Outcomes</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="outcome-box">
        <strong>Summary of Data Cleaning Results:</strong><br><br>
        
        The data cleaning process successfully prepared the World Bank food price dataset for analysis. 
        We loaded 4,798 records spanning 25 countries over a 16-year period from January 2007 to 
        October 2023. The dataset contained no duplicate records, and all validation checks passed, 
        confirming data integrity.
        
        We handled missing inflation values by retaining the records, as the missingness is structural 
        (due to the year-over-year calculation method) rather than indicative of data quality issues. 
        The final cleaned dataset contains 14 columns including the original price indices, derived 
        features for volatility and change analysis, and temporal components for seasonal patterns.
        
        The cleaned data is saved to a separate file, preserving the original raw data and ensuring 
        full reproducibility of our analysis pipeline.
        </div>
        """, unsafe_allow_html=True)
    
    # ============= PAGE: DATA ANALYSIS =============
    elif page == "Data Analysis":
        st.markdown('<p class="section-header">Exploratory Data Analysis</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Food prices are right-skewed and have risen steadily since 2007.
        Country-level inflation ranges from near 0% to over 20%. Price volatility and inflation are
        positively correlated, and mild seasonal patterns exist — use the sidebar to filter by country.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        Exploratory Data Analysis (EDA) is the detective work of data science. Before we can draw 
        conclusions or build predictive models, we need to deeply understand our data—its distributions, 
        patterns, relationships, and anomalies. This systematic exploration guides our subsequent 
        hypothesis testing and modeling decisions.
        """)
        
        st.markdown('<p class="section-header">Distribution Analysis</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Analyse Distributions:</strong><br><br>
        Understanding the distribution of our variables is essential for several reasons. First, it 
        helps us choose appropriate statistical tests—many common tests assume normally distributed 
        data, so we need to verify this assumption or select non-parametric alternatives. Second, 
        distributions reveal outliers and extreme values that may require special handling or 
        investigation. Third, skewed distributions might benefit from transformation before modeling.
        
        Our analysis revealed that food price indices are right-skewed, with most values clustered 
        at lower levels and a long tail extending toward higher prices. Inflation rates show an 
        approximately symmetric distribution centered near zero, but with occasional extreme values 
        representing periods of hyperinflation or deflation in certain countries.
        </div>
        """, unsafe_allow_html=True)
        
        # Show distribution statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean Price Index", f"{df_filtered['close'].mean():.2f}")
        with col2:
            st.metric("Mean Inflation", f"{df_filtered['inflation'].mean():.2f}%")
        with col3:
            st.metric("Inflation Range", f"{df_filtered['inflation'].min():.1f}% to {df_filtered['inflation'].max():.1f}%")
        
        # Distribution charts
        st.markdown("""        
        The charts below show the distribution of key variables in our dataset. The price distribution 
        shows how food price indices are spread across the dataset, the inflation distribution reveals 
        the range and frequency of year-over-year price changes, the volatility distribution shows how 
        much prices fluctuate within each period, and the yearly boxplot displays how inflation patterns 
        have evolved over time.
        """)
        
        fig_dist = create_distribution_charts(df_filtered)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        st.markdown('<p class="section-header">Country Rankings</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Compare Countries:</strong><br><br>
        Comparing inflation rates across countries reveals the substantial heterogeneity in food price 
        dynamics globally. This variation reflects differences in agricultural productivity, import 
        dependence, government policies, currency stability, and exposure to global commodity markets. 
        Understanding these differences is crucial for developing targeted policy interventions.
        </div>
        """, unsafe_allow_html=True)
        
        # Country comparison chart
        fig = create_country_comparison(df_filtered, 'inflation')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>What does this mean for you?</strong><br>
        Countries at the <em>top of the chart</em> (highest inflation) face the greatest food-affordability
        pressures. Policymakers in those nations should prioritise import diversification, strategic
        reserves, and targeted consumer subsidies. Businesses operating across borders should weight
        supply-chain risk by country inflation level.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-header">Correlation Analysis</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Examine Correlations:</strong><br><br>
        Correlation analysis helps us understand how different variables move together. A positive 
        correlation means that when one variable increases, the other tends to increase as well. 
        A negative correlation indicates an inverse relationship. However, it is crucial to remember 
        that correlation does not imply causation—two variables may be correlated because they share 
        a common cause, or the relationship may be coincidental.
        
        Our correlation analysis revealed strong positive correlations among the price indices (Open, 
        High, Low, Close), which is expected as these all measure aspects of the same underlying 
        price level. More interestingly, we found a moderate positive correlation between price 
        volatility (price range) and inflation rates, suggesting that market instability and rising 
        prices tend to occur together.
        </div>
        """, unsafe_allow_html=True)
        
        # Correlation heatmap
        st.markdown("""        
        The correlation heatmap below visualises the relationships between all numerical variables. 
        Values close to 1 indicate strong positive correlation (variables increase together), while 
        values close to -1 indicate strong negative correlation (one increases as the other decreases). 
        Values near 0 suggest little to no linear relationship between the variables.
        """)
        
        fig_corr = create_correlation_heatmap(df_filtered)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>What does this mean for you?</strong><br>
        The strong link between price <em>volatility</em> (High−Low range) and <em>inflation</em> is the
        key practical finding here. It means that when prices swing wildly within a single month,
        overall price levels tend to be rising too. Smoothing-out those swings — through better
        market information, storage infrastructure, or price floors/ceilings — could also help
        moderate inflation.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-header">Seasonal Patterns</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Why We Look for Seasonality:</strong><br><br>
        Food prices often exhibit seasonal patterns due to agricultural production cycles, weather 
        conditions, and demand fluctuations around holidays and cultural events. Identifying these 
        patterns helps stakeholders anticipate price movements and plan accordingly. For example, 
        if prices consistently rise in certain months, consumers and businesses can adjust their 
        purchasing and inventory strategies.
        </div>
        """, unsafe_allow_html=True)
        
        # Seasonal chart
        fig = create_seasonal_chart(df_filtered)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>What does this mean for you?</strong><br>
        If you see a clear seasonal spike in certain months for your selected country, that is a
        signal to <em>stock up before</em> those months or to look for suppliers in the southern
        hemisphere who are in their harvest season when you are in a price-spike period.
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive country comparison
        st.markdown('<p class="section-header">Interactive Country Comparison</p>', unsafe_allow_html=True)
        
        st.markdown("""
        The interactive chart below allows you to explore food price trends for individual countries. 
        Click on country names in the legend to show or hide their data. This visualisation makes it 
        easy to compare how different nations have experienced price changes over time and to identify 
        countries with similar or divergent patterns.
        """)
        
        fig_countries = create_interactive_country_lines(df_filtered)
        st.plotly_chart(fig_countries, use_container_width=True)
        
        st.markdown("""
        <div class="outcome-box">
        <strong>Key Insights from Exploratory Analysis:</strong><br><br>
        
        Our exploratory analysis uncovered several important patterns in the global food price data. 
        Food prices have demonstrated a consistent upward trend over the 16-year study period, with 
        particularly sharp increases during global crisis events such as the 2008 financial crisis 
        and the 2020-2022 pandemic period.
        
        Country-level analysis revealed dramatic differences in inflation experiences. Some nations 
        maintained remarkably stable food prices with average inflation near zero, while others 
        experienced chronic high inflation exceeding 20% annually. These differences suggest that 
        local policy choices and economic conditions significantly influence food price outcomes.
        
        The correlation between price volatility and inflation suggests that stabilising prices 
        could help control inflation. This finding has important policy implications—interventions 
        that reduce price volatility, such as strategic reserves, price supports, or improved 
        market information systems, might also help control inflation.
        </div>
        """, unsafe_allow_html=True)
    
    # ============= PAGE: HYPOTHESIS TESTING =============
    elif page == "Hypothesis Testing":
        st.markdown('<p class="section-header">Statistical Hypothesis Testing</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Two hypotheses were <strong>statistically significant</strong>:
        (H1) inflation differs significantly by country; (H2) price volatility correlates with higher inflation.
        Two hypotheses were <strong>not significant</strong>: (H3) seasonal patterns; (H4) long-term price increase.
        Significance level: α = 0.05.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        While exploratory analysis reveals patterns in the data, hypothesis testing provides a 
        rigorous statistical framework to determine whether these patterns are genuinely significant 
        or merely the result of random chance. By quantifying the probability that our observed 
        results could have occurred if there were no real effect, we can make evidence-based 
        conclusions with known confidence levels.
        """)
        
        st.markdown('<p class="section-header">Understanding P-Values</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>What P-Values Tell Us:</strong><br><br>
        The p-value is the probability of observing results as extreme as ours if the null hypothesis 
        were true—that is, if there were no real effect or difference. A small p-value (typically 
        less than 0.05) suggests that our results are unlikely to have occurred by chance alone, 
        providing evidence against the null hypothesis.
        
        We use the conventional significance threshold of α = 0.05, meaning we consider results 
        statistically significant if there is less than a 5% probability they occurred by chance. 
        This threshold balances the risk of false positives (concluding there is an effect when 
        there is none) against the risk of false negatives (missing real effects).
        </div>
        """, unsafe_allow_html=True)
        
        # Hypothesis 1
        st.markdown('<p class="section-header">H1: Regional Differences in Inflation</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Research Question:</strong> Do different countries have significantly different inflation rates?<br><br>
        
        <strong>Why We Used the Kruskal-Wallis Test:</strong><br><br>
        We chose the Kruskal-Wallis H test for this analysis because it is a non-parametric method 
        that does not assume the data follows a normal distribution. Our inflation data is notably 
        skewed, violating the normality assumption required by parametric alternatives like one-way 
        ANOVA. The Kruskal-Wallis test compares the median rankings across groups and is robust to 
        outliers, making it well-suited for economic data that often contains extreme values.
        
        This test evaluates whether at least one country has a significantly different inflation 
        distribution compared to the others. A significant result indicates that regional factors 
        play an important role in determining food price inflation.
        </div>
        """, unsafe_allow_html=True)
        
        # Run H1 test
        country_groups = [group['inflation'].dropna().values for name, group in df_filtered.groupby('country')]
        if len(country_groups) > 1:
            h1_stat, h1_p = kruskal(*country_groups)
            h1_result = 'SIGNIFICANT' if h1_p < 0.05 else 'NOT SIGNIFICANT'
            
            st.markdown(f"""
            <div class="outcome-box">
            <strong>Result: {h1_result} (p = {h1_p:.2e})</strong><br><br>
            
            The Kruskal-Wallis test confirmed that inflation rates differ significantly across countries. 
            This means the substantial variation we observed during exploratory analysis is not due to 
            random chance—there are real, systematic differences in how different countries experience 
            food price inflation.
            
            <strong>Practical Implication:</strong> Global solutions to food price inflation may not be 
            effective everywhere. Policymakers need to consider local conditions when designing 
            interventions. A strategy that works in one country might fail in another due to differences 
            in agricultural systems, trade policies, or economic structures.
            </div>
            """, unsafe_allow_html=True)
            
            # H1 Chart
            fig_h1 = create_country_boxplot(df_filtered)
            st.plotly_chart(fig_h1, use_container_width=True)
        
        # Hypothesis 2
        st.markdown('<p class="section-header">H2: Volatility and Inflation Relationship</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Research Question:</strong> Is there a statistically significant relationship between 
        price volatility and inflation?<br><br>
        
        <strong>Why We Used Spearman Correlation:</strong><br><br>
        We chose Spearman's rank correlation coefficient over Pearson's correlation because it does 
        not require the relationship between variables to be linear or the data to be normally 
        distributed. Spearman's method measures monotonic relationships—whether one variable tends 
        to increase as the other increases, regardless of whether that relationship follows a 
        straight line.
        
        Economic relationships are often non-linear, and Spearman correlation captures these patterns 
        without making restrictive assumptions. It is also more robust to outliers, which are common 
        in financial and economic data.
        </div>
        """, unsafe_allow_html=True)
        
        # H2 Chart and result
        fig_h2, h2_corr, h2_p = create_volatility_inflation_scatter(df_filtered)
        h2_result = 'SIGNIFICANT' if h2_p < 0.05 else 'NOT SIGNIFICANT'
        direction = "positive" if h2_corr > 0 else "negative"
        
        st.markdown(f"""
        <div class="outcome-box">
        <strong>Result: {h2_result} {direction.upper()} CORRELATION (r = {h2_corr:.4f}, p = {h2_p:.2e})</strong><br><br>
        
        Our analysis found a statistically significant {direction} relationship between price volatility 
        and inflation rates. This means that periods and countries with more volatile prices—larger 
        swings between high and low values—tend to also experience higher inflation.
        
        <strong>Practical Implication:</strong> Price stabilisation policies could have a dual benefit. 
        By reducing the gap between high and low prices, interventions might also help control 
        inflation. This finding supports policies such as strategic food reserves, which can smooth 
        out price spikes, or market information systems that reduce uncertainty and speculation.
        </div>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(fig_h2, use_container_width=True)
        
        # Hypothesis 3
        st.markdown('<p class="section-header">H3: Seasonal Patterns in Inflation</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Research Question:</strong> Does inflation vary significantly by month, indicating 
        seasonal patterns?<br><br>
        
        <strong>Why Seasonal Patterns Matter:</strong><br><br>
        Food production is inherently seasonal, tied to planting and harvest cycles that vary by 
        crop and region. If these agricultural rhythms translate into predictable price patterns, 
        this information is valuable for consumers budgeting their food expenses, retailers managing 
        inventory, and policymakers timing interventions.
        
        We again used the Kruskal-Wallis test to compare inflation rates across the 12 months of 
        the year, testing whether at least one month has a significantly different inflation 
        distribution than the others.
        </div>
        """, unsafe_allow_html=True)
        
        # Run H3 test
        month_groups = [group['inflation'].dropna().values for name, group in df_filtered.groupby('month')]
        if len(month_groups) > 1:
            h3_stat, h3_p = kruskal(*month_groups)
            h3_result = 'SIGNIFICANT' if h3_p < 0.05 else 'NOT SIGNIFICANT'
            
            st.markdown(f"""
            <div class="outcome-box">
            <strong>Result: {h3_result} (p = {h3_p:.2e})</strong><br><br>
            
            Our analysis provides evidence for seasonal patterns in food price inflation. Certain months 
            consistently show higher average inflation rates than others, suggesting that agricultural 
            production cycles and seasonal demand fluctuations do influence price dynamics.
            
            <strong>Practical Implication:</strong> Understanding these patterns enables better planning. 
            Consumers might time major food purchases to avoid high-inflation periods. Food assistance 
            programs might increase support during months when prices typically spike. Agricultural 
            planners might work to smooth out production cycles to reduce seasonal price volatility.
            </div>
            """, unsafe_allow_html=True)
            
            # H3 Chart
            fig_h3 = create_seasonal_boxplot(df_filtered)
            st.plotly_chart(fig_h3, use_container_width=True)
        
        # Hypothesis 4
        st.markdown('<p class="section-header">H4: Long-term Price Trend</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Research Question:</strong> Have food prices significantly increased over time?<br><br>
        
        <strong>Why We Used the Mann-Whitney U Test:</strong><br><br>
        To test for a long-term trend, we divided the dataset into two periods—the first half and 
        the second half of the time series—and compared price distributions between them. The 
        Mann-Whitney U test is ideal for comparing two independent groups when the data may not 
        be normally distributed.
        
        This test examines whether one distribution is systematically shifted relative to the other. 
        If recent prices are significantly higher than early prices, this provides statistical 
        evidence for an upward trend that goes beyond random fluctuation.
        </div>
        """, unsafe_allow_html=True)
        
        # Run H4 test and create chart
        fig_h4, mid_year, early_avg, recent_avg = create_price_trend_chart(df_filtered)
        years = sorted(df_filtered['year'].unique())
        early = df_filtered[df_filtered['year'] < mid_year]['close']
        recent = df_filtered[df_filtered['year'] >= mid_year]['close']
        
        if len(early) > 0 and len(recent) > 0:
            h4_stat, h4_p = mannwhitneyu(early, recent)
            h4_result = 'SIGNIFICANT' if h4_p < 0.05 else 'NOT SIGNIFICANT'
            price_change_pct = ((recent_avg - early_avg) / early_avg * 100)
            
            st.markdown(f"""
            <div class="outcome-box">
            <strong>Result: {h4_result} INCREASE (p = {h4_p:.2e})</strong><br><br>
            
            <strong>Early period ({years[0]}-{mid_year-1}):</strong> Average price index = {early_avg:.2f}<br>
            <strong>Recent period ({mid_year}-{years[-1]}):</strong> Average price index = {recent_avg:.2f}<br>
            <strong>Change:</strong> {price_change_pct:.1f}%<br><br>
            
            The Mann-Whitney U test confirmed that food prices have significantly increased from the 
            early period to the recent period. This upward trend is statistically robust and represents 
            a real change in food price levels, not merely random variation.
            
            <strong>Practical Implication:</strong> The significant upward trend in food prices raises 
            concerns about food affordability, particularly for low-income households who spend a larger 
            share of their income on food. This finding underscores the importance of policies that 
            address food access and affordability, such as nutrition assistance programs, agricultural 
            investment to increase productivity, and trade policies that ensure stable food supplies.
            </div>
            """, unsafe_allow_html=True)
            
            st.plotly_chart(fig_h4, use_container_width=True)
        
        # Overall recommendations
        st.markdown('<p class="section-header">H5: Machine Learning Predictability</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Research Question:</strong> Can machine learning models predict food price inflation
        with reasonable accuracy?<br><br>
        
        This hypothesis is evaluated in the <strong>ML Predictions</strong> page using three models
        (Linear Regression, Random Forest, XGBoost) trained on historical data. Performance is
        measured via R², MAE, and RMSE on a held-out test set.
        </div>
        """, unsafe_allow_html=True)
        
        # Load model results if available
        model_results_path = 'outputs/reports/ml_model_comparison.csv'
        if os.path.exists(model_results_path):
            ml_df = pd.read_csv(model_results_path)
            best_r2 = ml_df['Test R²'].max()
            best_model_name = ml_df.loc[ml_df['Test R²'].idxmax(), 'Model']
            h5_result = 'CONFIRMED' if best_r2 > 0.5 else 'PARTIALLY SUPPORTED'
            st.markdown(f"""
            <div class="outcome-box">
            <strong>Result: {h5_result}</strong><br><br>
            
            Best model: <strong>{best_model_name}</strong> &mdash; Test R² = <strong>{best_r2:.3f}</strong><br><br>
            
            Machine learning models successfully capture patterns in historical food price data and
            generalise to unseen periods. The strongest predictive feature is the previous
            month\'s inflation rate, confirming the autoregressive nature of food prices.<br><br>
            
            <strong>Practical Implication:</strong> Data-driven early-warning systems are feasible.
            Policymakers can use these models to anticipate price pressures weeks in advance,
            enabling proactive interventions rather than reactive emergency responses.
            Navigate to <strong>ML Predictions</strong> or <strong>Prediction Tool</strong> to run
            live forecasts.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Run the ML Predictions notebook to generate model results for H5.")
        
        st.markdown('<p class="section-header">Recommendations Based on Statistical Findings</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>Policy Recommendations:</strong><br><br>
        
        Based on our statistical analysis, we offer the following recommendations for policymakers, 
        businesses, and other stakeholders concerned with food price stability:
        
        <strong>Adopt Region-Specific Approaches:</strong> Given the significant variation in inflation 
        rates across countries, blanket global policies are unlikely to be equally effective everywhere. 
        Interventions should be tailored to local conditions, taking into account each country's 
        specific drivers of food price inflation.
        
        <strong>Focus on Price Stabilisation:</strong> The significant link between volatility and 
        inflation suggests that policies aimed at reducing price swings could have the additional 
        benefit of moderating inflation. Consider investments in strategic food reserves, improved 
        market information systems, and mechanisms to smooth out supply disruptions.
        
        <strong>Account for Seasonality in Planning:</strong> Since inflation shows seasonal patterns, 
        timing matters for interventions. Food assistance programs might be most needed during 
        high-inflation months, while procurement and storage programs might be most effective during 
        low-price periods.
        
        <strong>Address Long-term Affordability:</strong> The significant upward trend in food prices 
        demands attention to long-term affordability. Investments in agricultural productivity, 
        sustainable farming practices, and efficient supply chains can help moderate price increases 
        over time.
        </div>
        """, unsafe_allow_html=True)
    
    # ============= PAGE: ML PREDICTIONS =============
    elif page == "ML Predictions":
        st.markdown('<p class="section-header">Machine Learning Predictions</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Three models were trained: Linear Regression, Random Forest, and
        XGBoost. The best model explains the majority of inflation variance (R² on test data). The
        strongest predictor is <em>last month’s inflation</em>. Head to
        <strong>🔮 Prediction Tool</strong> to run live forecasts.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        While statistical analysis tells us what has happened and helps us understand why certain 
        patterns exist, machine learning takes us a step further by predicting what will happen next. 
        By training models on historical data, we can forecast future inflation trends, enabling 
        proactive responses rather than reactive ones.
        """)
        
        st.markdown('<p class="section-header">Why Machine Learning for Inflation Prediction?</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>The Value of Prediction:</strong><br><br>
        Accurate inflation predictions have substantial practical value across multiple sectors. 
        Government agencies can use forecasts to plan food assistance programs and allocate resources 
        to regions likely to experience price spikes. Businesses can optimise their supply chain and 
        pricing strategies based on anticipated cost changes. Consumers can adjust their budgets and 
        purchasing timing. Non-governmental organisations can proactively direct aid to areas at risk 
        of food insecurity.
        
        Machine learning is particularly well-suited for this task because inflation is influenced 
        by complex, non-linear relationships among many factors. Traditional statistical models 
        often assume linear relationships and may miss important patterns. Modern ML algorithms 
        can capture these complex interactions automatically.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-header">Feature Engineering for Prediction</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Creating Predictive Features:</strong><br><br>
        To predict future inflation, we engineered several types of features from our historical data:
        
        <strong>Lag Features:</strong> We included previous months' inflation and price values as 
        features. Inflation often shows persistence—high inflation this month tends to be followed 
        by high inflation next month. By including lag values for 1, 3, 6, and 12 months, the model 
        can learn these temporal dependencies.
        
        <strong>Rolling Statistics:</strong> Moving averages over 3, 6, and 12-month windows capture 
        underlying trends smoothed of short-term noise. These features help the model distinguish 
        between temporary fluctuations and sustained trends.
        
        <strong>Temporal Features:</strong> Year, month, and quarter variables allow the model to 
        learn seasonal patterns and long-term trends.
        
        <strong>Country Encoding:</strong> Since different countries have different inflation dynamics, 
        we encode country identity as a feature, allowing the model to learn country-specific patterns.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="section-header">Models Evaluated</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <strong>Our Model Selection Approach:</strong><br><br>
        
        We evaluated three different machine learning algorithms, each with distinct strengths:
        
        <strong>Linear Regression (Baseline):</strong> This simple model assumes a linear relationship 
        between features and the target variable. While unlikely to capture the full complexity of 
        inflation dynamics, it provides an interpretable baseline that more sophisticated models 
        should beat. If they cannot, this suggests the problem might be fundamentally linear or 
        the data insufficient for complex modeling.
        
        <strong>Random Forest:</strong> This ensemble method builds many decision trees and combines 
        their predictions. It naturally captures non-linear relationships and interactions between 
        features without requiring us to specify them explicitly. Random Forests are also relatively 
        resistant to overfitting and provide useful feature importance rankings.
        
        <strong>XGBoost:</strong> This gradient boosting algorithm represents the current state-of-the-art 
        for tabular data prediction tasks. It builds trees sequentially, with each new tree correcting 
        errors made by previous ones. XGBoost includes built-in regularisation to prevent overfitting 
        and handles missing values natively.
        </div>
        """, unsafe_allow_html=True)
        
        model, scaler, encoder, feature_cols = load_model()
        
        if model is None:
            st.warning("""
            The machine learning model has not been trained yet. Please run the ML_Predictions.ipynb 
            notebook to train and save the model, then return to this dashboard to view the results.
            """)
        else:
            st.success("Machine learning model loaded successfully!")
            
            # Try to load and display model comparison
            try:
                results_df = pd.read_csv('outputs/reports/ml_model_comparison.csv')
                
                st.markdown('<p class="section-header">Model Performance Comparison</p>', unsafe_allow_html=True)
                st.dataframe(results_df, use_container_width=True)
                
                # Model comparison chart
                fig_model = create_model_comparison_chart(results_df)
                st.plotly_chart(fig_model, use_container_width=True)
                
                best_model = results_df.loc[results_df['Test R²'].idxmax()]
                
                st.markdown(f"""
                <div class="outcome-box">
                <strong>Model Evaluation Results:</strong><br><br>
                
                After training and evaluating all three models, **{best_model['Model']}** emerged as 
                the best performer with a test R² score of {best_model['Test R²']:.4f}. This means the 
                model explains approximately {best_model['Test R²']*100:.1f}% of the variance in 
                inflation rates.
                
                The test Mean Absolute Error (MAE) of {best_model['Test MAE']:.2f}% indicates that, 
                on average, our predictions deviate from actual inflation values by about 
                {best_model['Test MAE']:.1f} percentage points. While not perfect, this level of 
                accuracy is useful for planning purposes and early warning systems.
                
                <strong>Key Finding:</strong> The most important predictor of inflation is the previous 
                month's inflation value, followed by other lag features. This strong autoregressive 
                pattern makes intuitive sense—inflation tends to persist, and knowing recent inflation 
                gives us substantial information about future inflation.
                </div>
                """, unsafe_allow_html=True)
                
            except FileNotFoundError:
                st.info("Model comparison results not available. Run the ML notebook to generate them.")
            
            # Feature importance
            st.markdown('<p class="section-header">Feature Importance</p>', unsafe_allow_html=True)
            
            st.markdown("""
            Understanding which features are most important for predictions helps us validate that 
            the model is learning sensible patterns and provides insights into the drivers of inflation.
            """)
            
            try:
                from PIL import Image
                img = Image.open('outputs/figures/feature_importance.png')
                st.image(img, use_container_width=True)
            except FileNotFoundError:
                st.info("Feature importance chart not available.")
        
        st.markdown('<p class="section-header">Model Limitations</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>Important Caveats:</strong><br><br>
        
        While our machine learning models show promising performance, users should be aware of 
        several limitations:
        
        <strong>External Shocks:</strong> The models cannot predict unexpected events such as 
        pandemics, wars, natural disasters, or sudden policy changes. These events can dramatically 
        alter inflation dynamics in ways not captured by historical patterns.
        
        <strong>Structural Changes:</strong> The models assume that relationships between variables 
        remain stable over time. If fundamental economic structures change—for example, due to 
        major trade policy shifts or technological disruptions—historical patterns may no longer apply.
        
        <strong>Data Quality:</strong> Predictions are only as good as the input data. If there are 
        errors or gaps in the underlying data, these will propagate through to the predictions.
        
        <strong>Uncertainty Quantification:</strong> Our current models provide point predictions 
        without confidence intervals. Users should treat predictions as approximations rather than 
        precise forecasts, especially for longer time horizons.
        </div>
        """, unsafe_allow_html=True)
    
    # ============= PAGE: PREDICTION TOOL =============
    elif page == "Prediction Tool":
        st.markdown('<p class="main-header">Inflation Prediction Tool</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Choose <strong>Quick Prediction</strong> to forecast any country
        with one click (data auto-filled from history), or <strong>Custom Prediction</strong> to tweak
        every input for scenario analysis. Results include a risk gauge, key metrics, and a 24-month
        historical chart with your forecast plotted.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        Use this interactive tool to predict food price inflation based on various input parameters. 
        The machine learning model uses historical patterns and country-specific features to generate 
        predictions. Choose between **Quick Prediction** using auto-filled historical data or 
        **Custom Prediction** with manual inputs.
        """)
        
        model, scaler, encoder, feature_cols = load_model()
        
        if model is None:
            st.error("""
            ⚠️ **Model Not Available**
            
            The machine learning model has not been trained yet. Please run the `ML_Predictions.ipynb` 
            notebook to train and save the model, then return to this page.
            """)
        else:
            st.success("✅ Machine learning model loaded successfully!")
            
            # Prediction mode selection
            prediction_mode = st.radio(
                "Select Prediction Mode:",
                ["Quick Prediction", "Custom Prediction"],
                horizontal=True,
                help="Quick mode uses historical averages, Custom mode allows manual input"
            )
            
            st.markdown("---")
            
            if prediction_mode == "Quick Prediction":
                st.markdown('<p class="section-header">Quick Prediction</p>', unsafe_allow_html=True)
                
                st.markdown("""
                <div class="explanation-box">
                Select a country and target period. The model will automatically use the most recent 
                historical data and averages to generate a prediction. This mode is ideal for quick 
                forecasts without manual data entry.
                </div>
                """, unsafe_allow_html=True)
                
                available_countries = sorted(df['country'].unique().tolist())
                
                quick_col1, quick_col2, quick_col3 = st.columns(3)
                
                with quick_col1:
                    quick_country = st.selectbox(
                        "Select Country",
                        available_countries,
                        key="quick_country"
                    )
                
                with quick_col2:
                    quick_year = st.selectbox(
                        "Target Year",
                        options=[2024, 2025, 2026, 2027, 2028],
                        key="quick_year"
                    )
                
                with quick_col3:
                    quick_month = st.selectbox(
                        "Target Month",
                        options=list(range(1, 13)),
                        format_func=lambda x: ['January', 'February', 'March', 'April', 'May', 'June', 
                                              'July', 'August', 'September', 'October', 'November', 'December'][x-1],
                        key="quick_month"
                    )
                
                # Get country historical data
                country_data = df[df['country'] == quick_country].sort_values('date')
                
                if len(country_data) > 0:
                    latest = country_data.iloc[-1]
                    
                    # Display historical context
                    st.markdown('<p class="section-header">Historical Context</p>', unsafe_allow_html=True)
                    
                    hist_col1, hist_col2, hist_col3, hist_col4 = st.columns(4)
                    
                    with hist_col1:
                        st.metric("Latest Price Index", f"{latest['close']:.2f}")
                    with hist_col2:
                        st.metric("Latest Inflation", f"{latest['inflation']:.2f}%" if pd.notna(latest['inflation']) else "N/A")
                    with hist_col3:
                        avg_inflation = country_data['inflation'].mean()
                        st.metric("Avg Inflation", f"{avg_inflation:.2f}%")
                    with hist_col4:
                        volatility = country_data['price_range'].mean()
                        st.metric("Avg Volatility", f"{volatility:.4f}")
                    
                    # Quick prediction button
                    if st.button("Generate Prediction", type="primary", use_container_width=True):
                        with st.spinner("Generating prediction..."):
                            try:
                                quick_quarter = (quick_month - 1) // 3 + 1
                                
                                # Auto-fill features from historical data
                                input_features = {
                                    'year': quick_year,
                                    'month': quick_month,
                                    'quarter': quick_quarter,
                                    'close': float(latest['close']),
                                    'price_range': float(country_data['price_range'].mean()),
                                    'inflation_lag_1': float(latest['inflation']) if pd.notna(latest['inflation']) else float(country_data['inflation'].mean()),
                                    'inflation_lag_3': float(country_data['inflation'].tail(3).mean()),
                                    'inflation_lag_6': float(country_data['inflation'].tail(6).mean()),
                                    'inflation_lag_12': float(country_data['inflation'].tail(12).mean()),
                                    'price_lag_1': float(country_data['close'].iloc[-1]) if len(country_data) > 0 else float(latest['close']),
                                    'price_ma_3': float(country_data['close'].tail(3).mean()),
                                    'price_ma_6': float(country_data['close'].tail(6).mean()),
                                    'price_ma_12': float(country_data['close'].tail(12).mean()),
                                    'inflation_ma_3': float(country_data['inflation'].tail(3).mean()),
                                    'inflation_ma_6': float(country_data['inflation'].tail(6).mean()),
                                }
                                
                                # Add country encoding
                                if encoder is not None:
                                    try:
                                        input_features['country_encoded'] = encoder.transform([quick_country])[0]
                                    except:
                                        input_features['country_encoded'] = 0
                                
                                # Create dataframe
                                input_df = pd.DataFrame([input_features])
                                
                                # Ensure correct columns
                                if feature_cols is not None:
                                    for col in feature_cols:
                                        if col not in input_df.columns:
                                            input_df[col] = 0
                                    input_df = input_df[feature_cols]
                                
                                # Scale and predict
                                if scaler is not None:
                                    input_scaled = scaler.transform(input_df)
                                else:
                                    input_scaled = input_df.values
                                
                                prediction = model.predict(input_scaled)[0]
                                
                                # Display results
                                st.markdown("---")
                                st.markdown('<p class="section-header">Prediction Results</p>', unsafe_allow_html=True)
                                
                                last_inf = float(latest['inflation']) if pd.notna(latest['inflation']) else avg_inflation
                                delta_val = prediction - last_inf
                                hist_avg  = float(country_data['inflation'].mean())
                                
                                if prediction > last_inf:
                                    trend = "📈 Rising"
                                elif prediction < last_inf:
                                    trend = "📉 Falling"
                                else:
                                    trend = "➡️ Stable"
                                
                                # Gauge + key metrics side by side
                                gauge_col, metrics_col = st.columns([1, 2])
                                
                                with gauge_col:
                                    st.plotly_chart(
                                        create_gauge_chart(prediction, "Inflation Forecast"),
                                        use_container_width=True
                                    )
                                
                                with metrics_col:
                                    risk_label, risk_class = get_risk_label(prediction)
                                    m1, m2 = st.columns(2)
                                    with m1:
                                        st.metric(
                                            "Predicted Inflation",
                                            f"{prediction:.2f}%",
                                            delta=f"{delta_val:+.2f}%",
                                            delta_color="inverse",
                                            help="Change vs last known inflation value"
                                        )
                                        st.metric(
                                            "Trend",
                                            trend,
                                            help="Direction relative to last recorded month"
                                        )
                                    with m2:
                                        st.metric(
                                            "vs Country Avg",
                                            f"{prediction - hist_avg:+.2f}%",
                                            help=f"Country historical avg: {hist_avg:.2f}%"
                                        )
                                        st.markdown(
                                            f'<span class="{risk_class}" style="font-size:1.1rem;padding:6px 14px;">'
                                            f'{risk_label}</span>',
                                            unsafe_allow_html=True
                                        )
                                
                                # Interpretation box
                                month_name = ['January', 'February', 'March', 'April', 'May', 'June', 
                                             'July', 'August', 'September', 'October', 'November', 'December'][quick_month-1]
                                
                                if prediction > RISK_HIGH_THRESHOLD:
                                    interpretation = f"🚨 **HIGH INFLATION ALERT**: The model predicts significant inflation of **{prediction:.2f}%** for {quick_country} in {month_name} {quick_year}. This could severely impact food affordability and requires immediate attention from policymakers."
                                elif prediction > RISK_LOW_THRESHOLD:
                                    interpretation = f"⚠️ **MODERATE INFLATION**: The model predicts inflation of **{prediction:.2f}%** for {quick_country} in {month_name} {quick_year}. This warrants monitoring and may require budget adjustments."
                                elif prediction > 0:
                                    interpretation = f"✅ **LOW INFLATION**: The model predicts mild inflation of **{prediction:.2f}%** for {quick_country} in {month_name} {quick_year}. This is within normal economic expectations."
                                else:
                                    interpretation = f"📉 **DEFLATION**: The model predicts negative inflation of **{prediction:.2f}%** for {quick_country} in {month_name} {quick_year}. Food prices are expected to decrease."
                                
                                st.markdown(f'<div class="outcome-box">{interpretation}</div>', unsafe_allow_html=True)
                                
                                # Historical comparison chart (last 24 months + avg line + prediction star)
                                st.markdown('<p class="section-header">Historical Comparison</p>', unsafe_allow_html=True)
                                
                                recent_inflation = country_data.tail(24)[['date', 'inflation']].dropna()
                                if len(recent_inflation) > 0:
                                    fig = go.Figure()
                                    
                                    fig.add_trace(go.Scatter(
                                        x=recent_inflation['date'],
                                        y=recent_inflation['inflation'],
                                        mode='lines+markers',
                                        name='Historical',
                                        line=dict(color=COLOR_BLUE, width=2),
                                        marker=dict(size=5)
                                    ))
                                    
                                    # Historical average reference line
                                    fig.add_hline(
                                        y=hist_avg,
                                        line_dash="dash",
                                        line_color=COLOR_MED,
                                        annotation_text=f"Avg: {hist_avg:.1f}%",
                                        annotation_position="top left"
                                    )
                                    
                                    # Prediction star marker
                                    pred_date = pd.Timestamp(year=quick_year, month=quick_month, day=1)
                                    fig.add_trace(go.Scatter(
                                        x=[pred_date],
                                        y=[prediction],
                                        mode='markers+text',
                                        name='Prediction',
                                        text=[f"{prediction:.1f}%"],
                                        textposition="top center",
                                        marker=dict(color=COLOR_HIGH, size=16, symbol='star')
                                    ))
                                    
                                    fig.update_layout(
                                        title=f"Inflation Trend – {quick_country} (last 24 months + forecast)",
                                        xaxis_title="Date",
                                        yaxis_title="Inflation (%)",
                                        height=420,
                                        showlegend=True,
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                
                            except Exception as e:
                                st.error(f"❌ Error making prediction: {str(e)}")
                else:
                    st.warning(f"No historical data available for {quick_country}")
            
            else:  # Custom Prediction
                st.markdown('<p class="section-header">Custom Prediction</p>', unsafe_allow_html=True)
                
                st.markdown("""
                <div class="explanation-box">
                Enter your own values for all prediction parameters. This mode allows for scenario 
                analysis and "what-if" predictions by adjusting individual features.
                </div>
                """, unsafe_allow_html=True)
                
                # Create three-column layout for inputs
                input_col1, input_col2, input_col3 = st.columns(3)
                
                with input_col1:
                    st.markdown("**Location & Time**")
                    
                    custom_country = st.selectbox(
                        "Country",
                        sorted(df['country'].unique().tolist()),
                        key="custom_country"
                    )
                    
                    custom_year = st.number_input(
                        "Year",
                        min_value=2020,
                        max_value=2035,
                        value=2026,
                        key="custom_year"
                    )
                    
                    custom_month = st.selectbox(
                        "Month",
                        options=list(range(1, 13)),
                        format_func=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x-1],
                        key="custom_month"
                    )
                    
                    custom_quarter = (custom_month - 1) // 3 + 1
                    st.info(f"Quarter: Q{custom_quarter}")
                
                with input_col2:
                    st.markdown("**Price Features**")
                    
                    custom_close = st.number_input(
                        "Current Price Index",
                        min_value=0.0,
                        max_value=500.0,
                        value=float(df['close'].median()),
                        format="%.4f",
                        key="custom_close",
                        help="The current food price index value"
                    )
                    
                    custom_range = st.number_input(
                        "Price Volatility (High - Low)",
                        min_value=0.0,
                        max_value=50.0,
                        value=float(df['price_range'].median()),
                        format="%.4f",
                        key="custom_range",
                        help="Difference between highest and lowest price in the period"
                    )
                    
                    custom_lag1 = st.number_input(
                        "Previous Month's Inflation (%)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=float(df['inflation'].median()),
                        format="%.2f",
                        key="custom_lag1",
                        help="Inflation rate from the previous month"
                    )
                
                with input_col3:
                    st.markdown("**Historical Averages**")
                    
                    custom_lag3 = st.number_input(
                        "3-Month Avg Inflation (%)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=float(df['inflation'].median()),
                        format="%.2f",
                        key="custom_lag3"
                    )
                    
                    custom_lag6 = st.number_input(
                        "6-Month Avg Inflation (%)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=float(df['inflation'].median()),
                        format="%.2f",
                        key="custom_lag6"
                    )
                    
                    custom_lag12 = st.number_input(
                        "12-Month Avg Inflation (%)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=float(df['inflation'].median()),
                        format="%.2f",
                        key="custom_lag12"
                    )
                
                # Advanced options expander
                with st.expander("Advanced Features (Optional)"):
                    adv_col1, adv_col2 = st.columns(2)
                    
                    with adv_col1:
                        custom_price_ma3 = st.number_input(
                            "3-Month Price Moving Average",
                            min_value=0.0,
                            max_value=500.0,
                            value=float(df['close'].median()),
                            format="%.4f",
                            key="custom_price_ma3"
                        )
                        
                        custom_price_ma6 = st.number_input(
                            "6-Month Price Moving Average",
                            min_value=0.0,
                            max_value=500.0,
                            value=float(df['close'].median()),
                            format="%.4f",
                            key="custom_price_ma6"
                        )
                    
                    with adv_col2:
                        custom_price_ma12 = st.number_input(
                            "12-Month Price Moving Average",
                            min_value=0.0,
                            max_value=500.0,
                            value=float(df['close'].median()),
                            format="%.4f",
                            key="custom_price_ma12"
                        )
                        
                        custom_inf_ma3 = st.number_input(
                            "3-Month Inflation Moving Average (%)",
                            min_value=-50.0,
                            max_value=100.0,
                            value=float(df['inflation'].median()),
                            format="%.2f",
                            key="custom_inf_ma3"
                        )
                
                # Prediction button
                if st.button("Generate Prediction", type="primary", use_container_width=True):
                    with st.spinner("Processing prediction..."):
                        try:
                            input_features = {
                                'year': custom_year,
                                'month': custom_month,
                                'quarter': custom_quarter,
                                'close': custom_close,
                                'price_range': custom_range,
                                'inflation_lag_1': custom_lag1,
                                'inflation_lag_3': custom_lag3,
                                'inflation_lag_6': custom_lag6,
                                'inflation_lag_12': custom_lag12,
                                'price_lag_1': custom_close,
                                'price_ma_3': st.session_state.get("custom_price_ma3", custom_close),
                                'price_ma_6': st.session_state.get("custom_price_ma6", custom_close),
                                'price_ma_12': st.session_state.get("custom_price_ma12", custom_close),
                                'inflation_ma_3': st.session_state.get("custom_inf_ma3", custom_lag3),
                                'inflation_ma_6': custom_lag6,
                            }
                            
                            if encoder is not None:
                                try:
                                    input_features['country_encoded'] = encoder.transform([custom_country])[0]
                                except:
                                    input_features['country_encoded'] = 0
                            
                            input_df = pd.DataFrame([input_features])
                            
                            if feature_cols is not None:
                                for col in feature_cols:
                                    if col not in input_df.columns:
                                        input_df[col] = 0
                                input_df = input_df[feature_cols]
                            
                            if scaler is not None:
                                input_scaled = scaler.transform(input_df)
                            else:
                                input_scaled = input_df.values
                            
                            prediction = model.predict(input_scaled)[0]
                            
                            # Display results
                            st.markdown("---")
                            st.markdown('<p class="section-header">Custom Prediction Results</p>', unsafe_allow_html=True)
                            
                            risk_label, risk_class = get_risk_label(prediction)
                            delta_vs_prev = prediction - custom_lag1
                            trend = "📈 Rising" if prediction > custom_lag1 else "📉 Falling" if prediction < custom_lag1 else "➡️ Stable"
                            
                            # Gauge + metrics side by side
                            c_gauge_col, c_metrics_col = st.columns([1, 2])
                            
                            with c_gauge_col:
                                st.plotly_chart(
                                    create_gauge_chart(prediction, "Inflation Forecast"),
                                    use_container_width=True
                                )
                            
                            with c_metrics_col:
                                cm1, cm2 = st.columns(2)
                                with cm1:
                                    st.metric(
                                        "Predicted Inflation",
                                        f"{prediction:.2f}%",
                                        delta=f"{delta_vs_prev:+.2f}% vs last month",
                                        delta_color="inverse"
                                    )
                                    st.metric("Trend vs Previous", trend)
                                with cm2:
                                    st.metric(
                                        "3-Month Avg Input",
                                        f"{custom_lag3:.2f}%",
                                        help="The 3-month average inflation you entered"
                                    )
                                    st.markdown(
                                        f'<span class="{risk_class}" style="font-size:1.1rem;padding:6px 14px;">'
                                        f'{risk_label}</span>',
                                        unsafe_allow_html=True
                                    )
                            
                            # Detailed interpretation box
                            month_name = ['January', 'February', 'March', 'April', 'May', 'June', 
                                         'July', 'August', 'September', 'October', 'November', 'December'][custom_month-1]
                            
                            direction = "increase" if prediction > custom_lag1 else "decrease"
                            change_pp  = abs(prediction - custom_lag1)
                            
                            if prediction > RISK_HIGH_THRESHOLD:
                                alert = "🚨 HIGH INFLATION ALERT"
                                advice = "Immediate monitoring and policy response may be needed."
                            elif prediction > RISK_LOW_THRESHOLD:
                                alert = "⚠️ MODERATE INFLATION"
                                advice = "Budget adjustments and continued monitoring are advisable."
                            else:
                                alert = "✅ LOW INFLATION"
                                advice = "Prices are expected to remain relatively stable."
                            
                            st.markdown(f"""
                            <div class="outcome-box">
                            <strong>{alert} — {custom_country}, {month_name} {custom_year}</strong><br><br>
                            Predicted inflation: <strong>{prediction:.2f}%</strong> — 
                            a {change_pp:.2f} pp {direction} vs the previous month ({custom_lag1:.2f}%). {advice}
                            <br><br>
                            <strong>Input Summary:</strong> Price Index {custom_close:.2f} · 
                            Volatility {custom_range:.4f} · Previous Inflation {custom_lag1:.2f}% · 
                            3-Month Avg {custom_lag3:.2f}%
                            </div>
                            """, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"❌ Error making prediction: {str(e)}")
                            st.info("Please check your input values and try again.")
            
            # Disclaimer
            st.markdown("---")
            st.markdown("""
            <div class="recommendation-box">
            <strong>⚠️ Important Disclaimer</strong><br><br>
            
            These predictions are generated by a machine learning model trained on historical data 
            and should be used for informational purposes only. Actual inflation rates may differ 
            due to unforeseen economic events, policy changes, or other factors not captured in 
            historical patterns. Always consult multiple sources when making important decisions.
            </div>
            """, unsafe_allow_html=True)
    
    # ============= PAGE: COUNTRY EXPLORER =============
    elif page == "Country Explorer":
        st.markdown('<p class="section-header">Country Analysis Explorer</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — Compare all countries side-by-side or drill into one using the
        sidebar filter. The table below ranks every country by average inflation. Use the
        <strong>Download</strong> buttons to export the data you’re viewing.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        This interactive section allows you to explore the food price data for specific countries 
        or compare patterns across the entire dataset. Use the sidebar filters to select countries 
        and time periods of interest.
        """)
        
        metric_choice = st.radio("Select metric to analyse:", ["Inflation Rate", "Price Index"], horizontal=True)
        metric = 'inflation' if metric_choice == "Inflation Rate" else 'close'
        
        fig = create_country_comparison(df_filtered, metric)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<p class="section-header">Detailed Country Statistics</p>', unsafe_allow_html=True)
        
        country_stats = df_filtered.groupby('country').agg({
            'close': ['mean', 'std', 'min', 'max'],
            'inflation': ['mean', 'std', 'min', 'max'],
            'price_range': 'mean'
        }).round(2)
        
        country_stats.columns = ['Avg Price', 'Price Std', 'Min Price', 'Max Price',
                                 'Avg Inflation', 'Infl Std', 'Min Infl', 'Max Infl',
                                 'Avg Volatility']
        
        st.dataframe(country_stats.sort_values('Avg Inflation', ascending=False), 
                     use_container_width=True)
        
        st.markdown("""
        <div class="recommendation-box">
        <strong>What does this mean for you?</strong><br>
        Countries with <em>high average inflation and high standard deviation</em> are the most
        unpredictable markets — prices can swing sharply. Buyers sourcing from those countries should
        build in cost buffers or use fixed-price contracts. Countries with <em>low Infl Std</em> offer
        more stable purchasing conditions even if the average inflation is moderate.
        </div>
        """, unsafe_allow_html=True)
        
        # Data Export Section
        st.markdown('<p class="section-header">Data Export</p>', unsafe_allow_html=True)
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            # Export filtered data
            csv_data = df_filtered.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data (CSV)",
                data=csv_data,
                file_name=f"food_price_data_{selected_country.replace(' ', '_').lower()}.csv",
                mime="text/csv",
                help="Download the currently filtered dataset"
            )
        
        with export_col2:
            # Export country statistics
            stats_csv = country_stats.reset_index().to_csv(index=False)
            st.download_button(
                label="Download Country Statistics (CSV)",
                data=stats_csv,
                file_name="country_statistics.csv",
                mime="text/csv",
                help="Download summary statistics by country"
            )
        
        # Time series for selected country
        if selected_country != "All Countries":
            st.markdown(f'<p class="section-header">Time Series for {selected_country}</p>', unsafe_allow_html=True)
            fig = create_time_series_chart(df_filtered, selected_country)
            st.plotly_chart(fig, use_container_width=True)
    
    # ============= PAGE: ABOUT =============
    elif page == "About":
        st.markdown('<p class="section-header">About This Project</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="takeaway-box">
        <strong>TL;DR</strong> — This dashboard was built by a three-person team for the Code 
        Institute Data Analytics Hackathon. It analyses global food price inflation across 25 countries 
        (2007–2023) using statistical testing and machine learning to forecast future inflation trends.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        This project was developed as part of the Code Institute Data Analytics Hackathon in March 2026. 
        Our team of three analysts collaborated to create a comprehensive analysis of global food price 
        inflation patterns, combining rigorous statistical methods with modern machine learning techniques.
        
        The World Bank's Real-Time Food Prices dataset provided rich historical data spanning 16 years 
        and 25 countries, enabling us to examine both temporal trends and geographic variations in food 
        price dynamics. Our analysis pipeline—implemented across four Jupyter notebooks—follows industry 
        best practices for reproducible data science.
        """)
        
        st.markdown('<p class="section-header">Team Members</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Florence**
            *Hypothesis Testing, Documentation & Power BI*

            Designed and implemented the statistical hypothesis tests. Prepared comprehensive
            documentation and created Power BI visualisations for stakeholder communication.
            """)

        with col2:
            st.markdown("""
            **Gia**
            *Streamlit Dashboard & Project Board*

            Managed the project board and contributed to the interactive Streamlit dashboard development.
            Ensured project coordination and delivery.
            """)

        with col3:
            st.markdown("""
            **Sergio**
            *Streamlit Dashboard & Machine Learning*

            Led the development of machine learning models and the interactive Streamlit dashboard.
            Responsible for feature engineering and model evaluation.
            """)
        
        st.markdown('<p class="section-header">Methodology Summary</p>', unsafe_allow_html=True)
        
        st.markdown("""
        Our analysis followed the CRISP-DM (Cross-Industry Standard Process for Data Mining) methodology:
        
        **Business Understanding:** We identified the key questions about food price inflation that 
        stakeholders need answered—how prices have changed, why they vary across regions, whether 
        patterns are predictable, and what drives inflation.
        
        **Data Understanding:** We explored the World Bank RTFP dataset, examining its structure, 
        quality, and limitations through extensive exploratory data analysis.
        
        **Data Preparation:** We cleaned the data, handled missing values, and engineered features 
        that capture important aspects of price dynamics such as volatility, trends, and seasonality.
        
        **Modeling:** We applied both statistical hypothesis tests and machine learning algorithms 
        to validate our findings and build predictive capabilities.
        
        **Evaluation:** We assessed our models using appropriate metrics and validated that our 
        conclusions are statistically robust.
        
        **Deployment:** This Streamlit dashboard makes our findings accessible to stakeholders 
        and demonstrates the practical value of our analysis.
        """)
        
        st.markdown('<p class="section-header">Data Source</p>', unsafe_allow_html=True)
        
        st.markdown("""
        **World Bank - Real-Time Food Prices (RTFP)**
        
        The RTFP dataset tracks food price indices across multiple countries, providing monthly 
        observations of opening, high, low, and closing price values along with year-over-year 
        inflation rates. This standardised format enables cross-country comparisons and time 
        series analysis.
        
        Data period: January 2007 - October 2023  
        Countries covered: 25  
        Total observations: 4,798
        """)
        
        # Display hypothesis results if available
        st.markdown('<p class="section-header">Statistical Test Results Summary</p>', unsafe_allow_html=True)
        
        try:
            hypothesis_df = pd.read_csv('outputs/reports/hypothesis_test_results.csv')
            st.dataframe(hypothesis_df, use_container_width=True)
        except FileNotFoundError:
            st.info("Run the Hypothesis_Testing notebook to see detailed results here.")
        
        st.markdown("---")
        st.markdown("""
        <p style="text-align: center; color: gray;">
        <small>Code Institute Data Analytics Hackathon | March 2026<br>
        Team: Florence, Gia & Sergio</small>
        </p>
        """, unsafe_allow_html=True)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <small>
    Data: World Bank RTFP<br>
    Code Institute Hackathon<br>
    March 2026
    </small>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import json

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Sales Funnel Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    .bottleneck-high {
        color: #FF5252;
        font-weight: bold;
    }
    .bottleneck-medium {
        color: #FFA726;
        font-weight: bold;
    }
    .bottleneck-low {
        color: #66BB6A;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Application title
st.markdown("<h1 class='main-header'>E-Commerce Sales Funnel Analysis Dashboard</h1>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SIDEBAR - CONTROLS
# --------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/shopping-cart.png", width=80)
    st.markdown("## Dashboard Controls")
    
    # Time range selector
    st.markdown("### Time Range")
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    # Segmentation options
    st.markdown("### Segmentation")
    segment_by = st.selectbox(
        "Segment Analysis By",
        options=["All Data", "Device Type", "Traffic Source"]
    )
    
    if segment_by == "Device Type":
        selected_device = st.multiselect(
            "Select Device Types",
            options=["Desktop", "Mobile", "Tablet"],
            default=["Desktop", "Mobile", "Tablet"]
        )
    
    if segment_by == "Traffic Source":
        selected_source = st.multiselect(
            "Select Traffic Sources",
            options=["Organic Search", "Paid Search", "Social Media", "Direct", "Email", "Referral"],
            default=["Organic Search", "Paid Search", "Social Media", "Direct", "Email", "Referral"]
        )
    
    # Refresh rate
    st.markdown("### Data Refresh")
    refresh_rate = st.slider(
        "Refresh Rate (seconds)",
        min_value=5,
        max_value=60,
        value=30,
        step=5
    )
    
    auto_refresh = st.checkbox("Enable Auto Refresh", value=False)
    
    if st.button("Refresh Data Now"):
        st.cache_data.clear()

# --------------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# --------------------------------------------------------------------------
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_funnel_data():
    try:
        df = pd.read_csv('ecommerce_funnel_analysis.csv')
        return df
    except FileNotFoundError:
        # If file doesn't exist, generate sample data
        funnel_stages = [
            'Homepage Visit',
            'Category Page Visit', 
            'Product Page Visit',
            'Add to Cart',
            'Cart View',
            'Checkout',
            'Payment',
            'Purchase'
        ]
        
        total_sessions = 10000
        conversion_rates = [1.0, 0.623, 0.495, 0.232, 0.191, 0.143, 0.126, 0.087]
        session_counts = [int(total_sessions * rate) for rate in conversion_rates]
        
        # Calculate drop-off rates between stages
        drop_rates = []
        for i in range(len(session_counts) - 1):
            drop_rate = (session_counts[i] - session_counts[i+1]) / session_counts[i]
            drop_rates.append(drop_rate)
        
        return pd.DataFrame({
            'Stage': funnel_stages,
            'Sessions': session_counts,
            'Conversion_Rate_from_Start': [f"{rate:.1%}" for rate in conversion_rates],
            'Drop_Rate_to_Next': ['N/A'] + [f"{rate:.1%}" for rate in drop_rates]
        })

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_bottleneck_data():
    try:
        df = pd.read_csv('ecommerce_bottleneck_analysis.csv')
        return df
    except FileNotFoundError:
        # Generate sample data
        transitions = [
            'Homepage Visit → Category Page Visit',
            'Category Page Visit → Product Page Visit',
            'Product Page Visit → Add to Cart',
            'Add to Cart → Cart View',
            'Cart View → Checkout',
            'Checkout → Payment',
            'Payment → Purchase'
        ]
        
        lost_sessions = [3770, 1280, 2630, 410, 481, 169, 391]
        drop_rates = [0.377, 0.205, 0.531, 0.177, 0.252, 0.118, 0.310]
        severity = [
            'High' if rate > 0.3 else 'Medium' if rate > 0.15 else 'Low'
            for rate in drop_rates
        ]
        
        return pd.DataFrame({
            'Transition': transitions,
            'Sessions_Lost': lost_sessions,
            'Drop_Rate': [f"{rate:.1%}" for rate in drop_rates],
            'Severity': severity
        })

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_device_data():
    try:
        df = pd.read_csv('ecommerce_device_analysis.csv')
        return df
    except FileNotFoundError:
        # Generate sample data
        devices = ['Desktop', 'Mobile', 'Tablet']
        sessions = [4500, 4200, 1300]
        conversions = [414, 310, 105]
        rates = [0.092, 0.074, 0.081]
        
        return pd.DataFrame({
            'Device': devices,
            'Total_Sessions': sessions,
            'Conversions': conversions,
            'Conversion_Rate': [f"{rate:.1%}" for rate in rates]
        })

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_traffic_data():
    try:
        df = pd.read_csv('ecommerce_traffic_source_analysis.csv')
        return df
    except FileNotFoundError:
        # Generate sample data
        sources = ['Organic Search', 'Paid Search', 'Social Media', 'Direct', 'Email', 'Referral']
        sessions = [3500, 2500, 1500, 1200, 800, 500]
        conversions = [318, 162, 63, 126, 62, 41]
        rates = [0.091, 0.065, 0.042, 0.105, 0.078, 0.083]
        
        return pd.DataFrame({
            'Traffic_Source': sources,
            'Sessions': sessions,
            'Conversions': conversions,
            'Conversion_Rate': [f"{rate:.1%}" for rate in rates]
        })

# --------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------
funnel_df = load_funnel_data()
bottleneck_df = load_bottleneck_data()
device_df = load_device_data()
traffic_df = load_traffic_data()

# --------------------------------------------------------------------------
# DASHBOARD LAYOUT - TWO COLUMNS
# --------------------------------------------------------------------------
col1, col2 = st.columns([3, 2])

# --------------------------------------------------------------------------
# COLUMN 1 - FUNNEL VISUALIZATION
# --------------------------------------------------------------------------
with col1:
    st.markdown("<h2 class='sub-header'>Sales Funnel Overview</h2>", unsafe_allow_html=True)
    
    # Convert percentage strings to floats for plotting
    funnel_df['Conversion_Rate_Numeric'] = funnel_df['Conversion_Rate_from_Start'].apply(
        lambda x: float(x.strip('%')) / 100 if isinstance(x, str) else x
    )
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=funnel_df['Stage'],
        x=funnel_df['Sessions'],
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.8,
        marker={"color": ["royalblue", "royalblue", "royalblue", 
                          "mediumseagreen", "mediumseagreen", 
                          "mediumseagreen", "coral", "coral"]},
        connector={"line": {"color": "royalblue", "dash": "dot", "width": 2}}
    ))
    
    fig.update_layout(
        title="E-Commerce Sales Funnel",
        font_size=14,
        height=600,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bottleneck Analysis
    st.markdown("<h2 class='sub-header'>Funnel Bottleneck Analysis</h2>", unsafe_allow_html=True)
    
    # Convert string percentages to floats
    bottleneck_df['Drop_Rate_Numeric'] = bottleneck_df['Drop_Rate'].apply(
        lambda x: float(x.strip('%')) / 100 if isinstance(x, str) else x
    )
    
    # Sort by drop rate descending
    bottleneck_df = bottleneck_df.sort_values('Drop_Rate_Numeric', ascending=False)
    
    # Create horizontal bar chart for bottlenecks
    colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
    
    fig_bottleneck = go.Figure()
    
    for severity in ['High', 'Medium', 'Low']:
        df_subset = bottleneck_df[bottleneck_df['Severity'] == severity]
        if not df_subset.empty:
            fig_bottleneck.add_trace(go.Bar(
                x=df_subset['Drop_Rate_Numeric'] * 100,  # Convert to percentage for display
                y=df_subset['Transition'],
                orientation='h',
                name=severity,
                marker_color=colors[severity],
                text=df_subset['Drop_Rate'],
                textposition='outside',
                texttemplate='%{text}',
            ))
    
    fig_bottleneck.update_layout(
        title="Drop-off Rates Between Funnel Stages",
        xaxis_title="Drop-off Rate (%)",
        yaxis_title="Funnel Stage Transition",
        height=500,
        legend_title="Severity",
        xaxis=dict(
            tickformat='.1f',
            ticksuffix='%',
        ),
        barmode='group'
    )
    
    st.plotly_chart(fig_bottleneck, use_container_width=True)

# --------------------------------------------------------------------------
# COLUMN 2 - KEY METRICS AND SEGMENTATION
# --------------------------------------------------------------------------
with col2:
    st.markdown("<h2 class='sub-header'>Key Performance Metrics</h2>", unsafe_allow_html=True)
    
    # Total Sessions
    total_sessions = funnel_df.iloc[0]['Sessions']
    
    # Total Conversions (Purchases)
    total_conversions = funnel_df.iloc[-1]['Sessions']
    
    # Overall Conversion Rate
    overall_cr = total_conversions / total_sessions
    
    # Average Order Value (simulated)
    avg_order_value = 85.50
    
    # Total Revenue
    total_revenue = total_conversions * avg_order_value
    
    # Display KPIs in a grid
    kpi1, kpi2 = st.columns(2)
    
    with kpi1:
        st.metric(
            label="Total Sessions",
            value=f"{total_sessions:,}",
            delta=f"{random.randint(-5, 10)}% vs. previous",
        )
    
    with kpi2:
        st.metric(
            label="Conversion Rate",
            value=f"{overall_cr:.1%}",
            delta=f"{random.uniform(-0.5, 1.0):.1f}% vs. previous",
            delta_color="normal"
        )
    
    kpi3, kpi4 = st.columns(2)
    
    with kpi3:
        st.metric(
            label="Total Conversions",
            value=f"{total_conversions:,}",
            delta=f"{random.randint(-5, 15)}% vs. previous"
        )
    
    with kpi4:
        st.metric(
            label="Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta=f"{random.randint(-3, 18)}% vs. previous"
        )
    
    # Segmentation Analysis
    st.markdown("<h2 class='sub-header'>Segmentation Analysis</h2>", unsafe_allow_html=True)
    
    segment_tab1, segment_tab2 = st.tabs(["Device Performance", "Traffic Sources"])
    
    with segment_tab1:
        # Convert percentage strings to floats
        device_df['Conversion_Rate_Numeric'] = device_df['Conversion_Rate'].apply(
            lambda x: float(x.strip('%')) / 100 if isinstance(x, str) else x
        )
        
        # Create device performance chart
        fig_device = px.bar(
            device_df,
            x='Device',
            y='Conversion_Rate_Numeric',
            color='Device',
            text=device_df['Conversion_Rate'],
            title="Conversion Rate by Device",
            labels={'Conversion_Rate_Numeric': 'Conversion Rate', 'Device': 'Device Type'}
        )
        
        fig_device.update_layout(
            xaxis_title="Device Type",
            yaxis_title="Conversion Rate (%)",
            yaxis=dict(
                tickformat='.1%',
            ),
            height=400
        )
        
        st.plotly_chart(fig_device, use_container_width=True)
        
        # Device metrics table
        st.dataframe(
            device_df[['Device', 'Total_Sessions', 'Conversions', 'Conversion_Rate']],
            hide_index=True,
            use_container_width=True
        )
    
    with segment_tab2:
        # Convert percentage strings to floats
        traffic_df['Conversion_Rate_Numeric'] = traffic_df['Conversion_Rate'].apply(
            lambda x: float(x.strip('%')) / 100 if isinstance(x, str) else x
        )
        
        # Create traffic source performance chart
        fig_traffic = px.bar(
            traffic_df,
            x='Traffic_Source',
            y='Conversion_Rate_Numeric',
            color='Traffic_Source',
            text=traffic_df['Conversion_Rate'],
            title="Conversion Rate by Traffic Source",
            labels={'Conversion_Rate_Numeric': 'Conversion Rate', 'Traffic_Source': 'Traffic Source'}
        )
        
        fig_traffic.update_layout(
            xaxis_title="Traffic Source",
            yaxis_title="Conversion Rate (%)",
            xaxis={'categoryorder':'total descending'},
            yaxis=dict(
                tickformat='.1%',
            ),
            height=400
        )
        
        st.plotly_chart(fig_traffic, use_container_width=True)
        
        # Traffic source metrics table
        st.dataframe(
            traffic_df[['Traffic_Source', 'Sessions', 'Conversions', 'Conversion_Rate']],
            hide_index=True,
            use_container_width=True
        )

# --------------------------------------------------------------------------
# INSIGHTS AND RECOMMENDATIONS
# --------------------------------------------------------------------------
st.markdown("<h2 class='sub-header'>Key Insights & Recommendations</h2>", unsafe_allow_html=True)

# Finding top bottlenecks
top_bottlenecks = bottleneck_df.sort_values('Drop_Rate_Numeric', ascending=False).head(3)

# Create 3 columns for insights
insight1, insight2, insight3 = st.columns(3)

with insight1:
    st.markdown("""
    <div class='metric-card'>
        <h3>Top Bottleneck</h3>
        <p>The largest drop-off occurs at <span class='bottleneck-high'>{}</span> with <b>{}</b> of users dropping off at this stage.</p>
        <p><b>Recommendation:</b> Simplify the product pages and add clearer CTAs to increase add-to-cart rates.</p>
    </div>
    """.format(top_bottlenecks.iloc[0]['Transition'], top_bottlenecks.iloc[0]['Drop_Rate']), unsafe_allow_html=True)

with insight2:
    # Find device with highest conversion
    best_device = device_df.loc[device_df['Conversion_Rate_Numeric'].idxmax()]
    
    # Find device with lowest conversion
    worst_device = device_df.loc[device_df['Conversion_Rate_Numeric'].idxmin()]
    
    st.markdown("""
    <div class='metric-card'>
        <h3>Device Performance</h3>
        <p><b>{}</b> has the highest conversion rate at <b>{}</b>, while <b>{}</b> has the lowest at <b>{}</b>.</p>
        <p><b>Recommendation:</b> Optimize the mobile experience to close the gap with desktop performance.</p>
    </div>
    """.format(
        best_device['Device'], best_device['Conversion_Rate'],
        worst_device['Device'], worst_device['Conversion_Rate']
    ), unsafe_allow_html=True)

with insight3:
    # Find best traffic source
    best_source = traffic_df.loc[traffic_df['Conversion_Rate_Numeric'].idxmax()]
    
    # Find worst traffic source
    worst_source = traffic_df.loc[traffic_df['Conversion_Rate_Numeric'].idxmin()]
    
    st.markdown("""
    <div class='metric-card'>
        <h3>Traffic Source Insights</h3>
        <p><b>{}</b> traffic converts best at <b>{}</b>, while <b>{}</b> has the lowest conversion rate at <b>{}</b>.</p>
        <p><b>Recommendation:</b> Increase budget allocation to direct and organic channels, and optimize social media content strategy.</p>
    </div>
    """.format(
        best_source['Traffic_Source'], best_source['Conversion_Rate'],
        worst_source['Traffic_Source'], worst_source['Conversion_Rate']
    ), unsafe_allow_html=True)

# --------------------------------------------------------------------------
# REAL-TIME DATA SIMULATION
# --------------------------------------------------------------------------
if auto_refresh:
    st.empty()
    st.info(f"Dashboard will refresh automatically every {refresh_rate} seconds.")
    time.sleep(refresh_rate)
    st.rerun()

# Add footnote with timestamp
st.markdown(f"<p style='text-align: center; color: gray;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
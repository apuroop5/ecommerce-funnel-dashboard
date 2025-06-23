import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
import time

# Define the key funnel stages for analysis
FUNNEL_STAGES = [
    ('homepage', 'page_view'),       # Homepage Visit
    ('category_page', 'page_view'),  # Category Page Visit
    ('product_page', 'page_view'),   # Product Page Visit
    ('product_page', 'add_to_cart'), # Add to Cart
    ('cart_page', 'page_view'),      # Cart View
    ('checkout_page', 'page_view'),  # Checkout
    ('payment_page', 'page_view'),   # Payment
    ('payment_page', 'purchase')     # Purchase
]

FUNNEL_LABELS = [
    'Homepage Visit', 
    'Category Page Visit', 
    'Product Page Visit', 
    'Add to Cart', 
    'Cart View', 
    'Checkout', 
    'Payment', 
    'Purchase'
]

def load_clickstream_data(filename='clickstream_data.csv'):
    """Load clickstream data from CSV file"""
    try:
        df = pd.read_csv(filename)
        
        # Parse timestamp column to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Parse JSON metadata
        df['metadata'] = df['metadata'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        
        return df
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Run data_generator.py first.")
        return pd.DataFrame()

def generate_funnel_analysis(df, time_filter=None):
    """
    Generate funnel analysis from clickstream data
    
    Parameters:
    df (DataFrame): Clickstream data
    time_filter (tuple): Optional (start_date, end_date) for filtering data
    
    Returns:
    DataFrame: Funnel analysis data
    """
    if df.empty:
        print("No data available for analysis.")
        return pd.DataFrame()
    
    # Apply time filter if provided
    if time_filter:
        start_date, end_date = time_filter
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Get unique sessions
    unique_sessions = df['session_id'].nunique()
    
    # Count sessions for each funnel stage
    funnel_counts = []
    
    for (page, action) in FUNNEL_STAGES:
        stage_sessions = df[(df['page'] == page) & (df['action'] == action)]['session_id'].nunique()
        funnel_counts.append(stage_sessions)
    
    # Calculate conversion rates from start
    conversion_rates = [count / unique_sessions if unique_sessions > 0 else 0 for count in funnel_counts]
    
    # Calculate drop-off rates between stages
    drop_rates = []
    drop_rates.append('N/A')  # No drop-off for first stage
    
    for i in range(len(funnel_counts) - 1):
        if funnel_counts[i] > 0:
            drop_rate = (funnel_counts[i] - funnel_counts[i+1]) / funnel_counts[i]
        else:
            drop_rate = 0
        drop_rates.append(f"{drop_rate:.1%}")
    
    # Create funnel analysis DataFrame
    funnel_df = pd.DataFrame({
        'Stage': FUNNEL_LABELS,
        'Sessions': funnel_counts,
        'Conversion_Rate_from_Start': [f"{rate:.1%}" for rate in conversion_rates],
        'Drop_Rate_to_Next': drop_rates
    })
    
    return funnel_df

def generate_bottleneck_analysis(funnel_df):
    """
    Generate bottleneck analysis from funnel data
    
    Parameters:
    funnel_df (DataFrame): Funnel analysis data
    
    Returns:
    DataFrame: Bottleneck analysis data
    """
    if funnel_df.empty:
        return pd.DataFrame()
    
    bottleneck_data = []
    
    for i in range(len(FUNNEL_LABELS) - 1):
        # Get sessions at current and next stage
        current_sessions = funnel_df.iloc[i]['Sessions']
        next_sessions = funnel_df.iloc[i+1]['Sessions']
        
        # Calculate drop-off
        sessions_lost = current_sessions - next_sessions
        
        # Calculate drop rate
        if current_sessions > 0:
            drop_rate = sessions_lost / current_sessions
        else:
            drop_rate = 0
        
        # Assign severity
        if drop_rate > 0.3:
            severity = 'High'
        elif drop_rate > 0.15:
            severity = 'Medium'
        else:
            severity = 'Low'
        
        bottleneck_data.append({
            'Transition': f"{FUNNEL_LABELS[i]} → {FUNNEL_LABELS[i+1]}",
            'Sessions_Lost': sessions_lost,
            'Drop_Rate': f"{drop_rate:.1%}",
            'Drop_Rate_Numeric': drop_rate,
            'Severity': severity
        })
    
    # Convert to DataFrame and sort by drop rate
    bottleneck_df = pd.DataFrame(bottleneck_data)
    bottleneck_df = bottleneck_df.sort_values('Drop_Rate_Numeric', ascending=False)
    
    return bottleneck_df

def generate_device_analysis(df):
    """
    Generate device performance analysis
    
    Parameters:
    df (DataFrame): Clickstream data
    
    Returns:
    DataFrame: Device analysis data
    """
    if df.empty:
        return pd.DataFrame()
    
    # Get unique devices
    devices = df['device'].unique()
    
    device_data = []
    
    for device in devices:
        # Filter events by device
        device_df = df[df['device'] == device]
        
        # Total sessions for this device
        total_sessions = device_df['session_id'].nunique()
        
        # Sessions that completed a purchase
        purchase_sessions = device_df[
            (device_df['page'] == 'payment_page') & 
            (device_df['action'] == 'purchase')
        ]['session_id'].nunique()
        
        # Calculate conversion rate
        if total_sessions > 0:
            conversion_rate = purchase_sessions / total_sessions
        else:
            conversion_rate = 0
        
        device_data.append({
            'Device': device.capitalize(),
            'Total_Sessions': total_sessions,
            'Conversions': purchase_sessions,
            'Conversion_Rate': f"{conversion_rate:.1%}",
            'Conversion_Rate_Numeric': conversion_rate
        })
    
    return pd.DataFrame(device_data)

def generate_traffic_analysis(df):
    """
    Generate traffic source performance analysis
    
    Parameters:
    df (DataFrame): Clickstream data
    
    Returns:
    DataFrame: Traffic source analysis data
    """
    if df.empty:
        return pd.DataFrame()
    
    # Get unique traffic sources
    sources = df['traffic_source'].unique()
    
    traffic_data = []
    
    for source in sources:
        # Filter events by traffic source
        source_df = df[df['traffic_source'] == source]
        
        # Total sessions for this source
        total_sessions = source_df['session_id'].nunique()
        
        # Sessions that completed a purchase
        purchase_sessions = source_df[
            (source_df['page'] == 'payment_page') & 
            (source_df['action'] == 'purchase')
        ]['session_id'].nunique()
        
        # Calculate conversion rate
        if total_sessions > 0:
            conversion_rate = purchase_sessions / total_sessions
        else:
            conversion_rate = 0
        
        traffic_data.append({
            'Traffic_Source': source.replace('_', ' ').title(),
            'Sessions': total_sessions,
            'Conversions': purchase_sessions,
            'Conversion_Rate': f"{conversion_rate:.1%}",
            'Conversion_Rate_Numeric': conversion_rate
        })
    
    return pd.DataFrame(traffic_data)

def process_and_save_all_data():
    """Process clickstream data and save analysis files"""
    # Load clickstream data
    df = load_clickstream_data()
    
    if df.empty:
        print("No data available for processing.")
        return
    
    # Generate funnel analysis
    funnel_df = generate_funnel_analysis(df)
    funnel_df.to_csv('ecommerce_funnel_analysis.csv', index=False)
    
    # Generate bottleneck analysis
    bottleneck_df = generate_bottleneck_analysis(funnel_df)
    bottleneck_df.to_csv('ecommerce_bottleneck_analysis.csv', index=False)
    
    # Generate device analysis
    device_df = generate_device_analysis(df)
    device_df.to_csv('ecommerce_device_analysis.csv', index=False)
    
    # Generate traffic source analysis
    traffic_df = generate_traffic_analysis(df)
    traffic_df.to_csv('ecommerce_traffic_source_analysis.csv', index=False)
    
    print("Data processing complete. Analysis files have been saved.")
    
    # Print summary
    print("\nSummary:")
    print(f"Total Events: {len(df)}")
    print(f"Unique Sessions: {df['session_id'].nunique()}")
    print(f"Conversion Rate: {funnel_df.iloc[-1]['Conversion_Rate_from_Start']}")
    
    # Print top bottlenecks
    print("\nTop Bottlenecks:")
    for i, row in bottleneck_df.head(3).iterrows():
        print(f"{row['Transition']}: {row['Drop_Rate']} drop-off ({row['Severity']} severity)")

def run_continuous_processing(interval_seconds=60):
    """Run continuous data processing to keep analysis files updated"""
    print(f"Starting continuous data processing every {interval_seconds} seconds...")
    
    try:
        while True:
            # Process and save data
            process_and_save_all_data()
            
            # Sleep for interval seconds
            print(f"Next update in {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Data processing stopped by user.")

if __name__ == "__main__":
    # Run once or continuously
    import argparse
    parser = argparse.ArgumentParser(description='Process e-commerce clickstream data for funnel analysis')
    parser.add_argument('--continuous', action='store_true', help='Run continuous processing')
    parser.add_argument('--interval', type=int, default=60, help='Interval in seconds between processing updates')
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_processing(interval_seconds=args.interval)
    else:
        process_and_save_all_data()
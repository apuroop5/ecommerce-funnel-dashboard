import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json
import time
import os

# Initialize faker generator
fake = Faker()

# Define the possible steps in the e-commerce customer journey
PAGES = ['homepage', 'category_page', 'product_page', 'cart_page', 'checkout_page', 'payment_page', 'order_confirmation']
TRAFFIC_SOURCES = ['organic_search', 'paid_search', 'social_media', 'direct', 'email', 'referral']
DEVICES = ['desktop', 'mobile', 'tablet']
USER_ACTIONS = ['page_view', 'click', 'add_to_cart', 'remove_from_cart', 'begin_checkout', 'purchase']
PRODUCT_CATEGORIES = ['electronics', 'clothing', 'books', 'home_decor', 'toys', 'beauty']

def generate_event(session_id, user_id, timestamp):
    """Generate a single clickstream event with realistic constraints"""
    page = np.random.choice(PAGES, p=[0.3, 0.25, 0.2, 0.1, 0.08, 0.05, 0.02])  # Probability distribution
    action = np.random.choice(USER_ACTIONS, p=[0.7, 0.15, 0.08, 0.03, 0.03, 0.01])  # Probability distribution
    
    # Different pages have different possible actions
    if page in ['homepage', 'category_page'] and action in ['add_to_cart', 'remove_from_cart', 'begin_checkout', 'purchase']:
        action = 'click'  # Can only click on homepage/category
    
    if page == 'product_page' and action in ['begin_checkout', 'purchase']:
        action = 'add_to_cart'  # Can't purchase directly from product page
    
    if page in ['checkout_page', 'payment_page'] and action in ['add_to_cart']:
        action = 'click'  # Can't add to cart from checkout/payment
    
    if page == 'order_confirmation' and action not in ['page_view']:
        action = 'page_view'  # Can only view the order confirmation page
    
    # Create metadata based on page and action
    metadata = {}
    
    if action == 'add_to_cart' or action == 'remove_from_cart':
        product_id = random.randint(1000, 9999)
        product_name = fake.word() + " " + random.choice(['Pro', 'Max', 'Ultra', 'Basic', 'Premium', 'Lite'])
        product_category = random.choice(PRODUCT_CATEGORIES)
        product_price = round(random.uniform(10, 500), 2)
        metadata = {
            'product_id': product_id,
            'product_name': product_name,
            'product_category': product_category,
            'product_price': product_price
        }
    
    if action == 'purchase':
        order_id = random.randint(100000, 999999)
        products = []
        num_products = random.randint(1, 4)
        order_total = 0
        for _ in range(num_products):
            product_price = round(random.uniform(10, 500), 2)
            product = {
                'product_id': random.randint(1000, 9999),
                'product_name': fake.word() + " " + random.choice(['Pro', 'Max', 'Ultra', 'Basic', 'Premium', 'Lite']),
                'product_category': random.choice(PRODUCT_CATEGORIES),
                'product_price': product_price,
                'quantity': random.randint(1, 3)
            }
            order_total += product['product_price'] * product['quantity']
            products.append(product)
        
        metadata = {
            'order_id': order_id,
            'order_total': round(order_total, 2),
            'products': products
        }
    
    event = {
        'event_id': fake.uuid4(),
        'session_id': session_id,
        'user_id': user_id,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'page': page,
        'action': action,
        'device': random.choice(DEVICES),
        'traffic_source': random.choice(TRAFFIC_SOURCES),
        'metadata': metadata
    }
    
    return event

def generate_session():
    """Generate a sequence of events for one user visit"""
    session_id = fake.uuid4()
    user_id = random.randint(1, 1000)  # Assuming 1000 unique users
    
    # Base time for this session
    base_time = datetime.now() - timedelta(days=random.randint(0, 30))
    base_time = base_time.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))
    
    # Decide whether this will be a full-funnel session or a partial one
    complete_funnel = random.random() < 0.15  # 15% of sessions go through the full funnel
    
    events = []
    current_time = base_time
    
    if complete_funnel:
        # Homepage visit
        event = generate_event(session_id, user_id, current_time)
        event['page'] = 'homepage'
        event['action'] = 'page_view'
        events.append(event)
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Category page visit
        event = generate_event(session_id, user_id, current_time)
        event['page'] = 'category_page'
        event['action'] = 'page_view'
        events.append(event)
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Product page visit
        event = generate_event(session_id, user_id, current_time)
        event['page'] = 'product_page'
        event['action'] = 'page_view'
        events.append(event)
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Add to cart action
        event = generate_event(session_id, user_id, current_time)
        event['page'] = 'product_page'
        event['action'] = 'add_to_cart'
        product_id = random.randint(1000, 9999)
        product_name = fake.word() + " " + random.choice(['Pro', 'Max', 'Ultra', 'Basic', 'Premium', 'Lite'])
        product_category = random.choice(PRODUCT_CATEGORIES)
        product_price = round(random.uniform(10, 500), 2)
        event['metadata'] = {
            'product_id': product_id,
            'product_name': product_name,
            'product_category': product_category,
            'product_price': product_price
        }
        events.append(event)
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Cart page visit
        event = generate_event(session_id, user_id, current_time)
        event['page'] = 'cart_page'
        event['action'] = 'page_view'
        events.append(event)
        current_time += timedelta(seconds=random.randint(5, 30))
        
        # Decide whether to checkout
        if random.random() < 0.75:  # 75% continue to checkout
            # Begin checkout
            event = generate_event(session_id, user_id, current_time)
            event['page'] = 'cart_page'
            event['action'] = 'begin_checkout'
            events.append(event)
            current_time += timedelta(seconds=random.randint(5, 30))
            
            # Checkout page visit
            event = generate_event(session_id, user_id, current_time)
            event['page'] = 'checkout_page'
            event['action'] = 'page_view'
            events.append(event)
            current_time += timedelta(seconds=random.randint(5, 30))
            
            # Payment page visit
            event = generate_event(session_id, user_id, current_time)
            event['page'] = 'payment_page'
            event['action'] = 'page_view'
            events.append(event)
            current_time += timedelta(seconds=random.randint(5, 30))
            
            # Decide whether to purchase
            if random.random() < 0.7:  # 70% of sessions that reach payment complete purchase
                event = generate_event(session_id, user_id, current_time)
                event['page'] = 'payment_page'
                event['action'] = 'purchase'
                
                order_id = random.randint(100000, 999999)
                products = []
                num_products = random.randint(1, 4)
                order_total = 0
                for _ in range(num_products):
                    product_price = round(random.uniform(10, 500), 2)
                    product = {
                        'product_id': random.randint(1000, 9999),
                        'product_name': fake.word() + " " + random.choice(['Pro', 'Max', 'Ultra', 'Basic', 'Premium', 'Lite']),
                        'product_category': random.choice(PRODUCT_CATEGORIES),
                        'product_price': product_price,
                        'quantity': random.randint(1, 3)
                    }
                    order_total += product['product_price'] * product['quantity']
                    products.append(product)
                
                event['metadata'] = {
                    'order_id': order_id,
                    'order_total': round(order_total, 2),
                    'products': products
                }
                events.append(event)
                current_time += timedelta(seconds=random.randint(5, 30))
                
                # Order confirmation page
                event = generate_event(session_id, user_id, current_time)
                event['page'] = 'order_confirmation'
                event['action'] = 'page_view'
                events.append(event)
    else:
        # Generate a random session with 1-7 events
        num_events = np.random.choice([1, 2, 3, 4, 5, 6, 7], p=[0.3, 0.25, 0.2, 0.1, 0.08, 0.05, 0.02])
        
        current_time = base_time
        for _ in range(num_events):
            event = generate_event(session_id, user_id, current_time)
            events.append(event)
            
            # Add a random time increment between events (1-120 seconds)
            current_time += timedelta(seconds=random.randint(1, 120))
    
    return events

def generate_and_save_events(num_sessions=100, filename='clickstream_data.csv'):
    """Generate clickstream events and save to CSV file"""
    all_events = []
    for _ in range(num_sessions):
        session_events = generate_session()
        all_events.extend(session_events)
    
    # Convert to DataFrame
    df_events = pd.DataFrame(all_events)
    
    # Handle JSON metadata by converting it to string
    df_events['metadata'] = df_events['metadata'].apply(json.dumps)
    
    # Save to CSV
    df_events.to_csv(filename, index=False)
    print(f"Generated {len(df_events)} events across {num_sessions} sessions")
    print(f"Data saved to {filename}")
    
    return df_events

def generate_and_append_events(num_sessions=10, filename='clickstream_data.csv'):
    """Generate new events and append to existing file (for real-time simulation)"""
    all_events = []
    for _ in range(num_sessions):
        session_events = generate_session()
        all_events.extend(session_events)
    
    # Convert to DataFrame
    df_new_events = pd.DataFrame(all_events)
    
    # Handle JSON metadata by converting it to string
    df_new_events['metadata'] = df_new_events['metadata'].apply(json.dumps)
    
    # Append to existing file or create new if it doesn't exist
    if os.path.exists(filename):
        df_new_events.to_csv(filename, index=False, mode='a', header=False)
    else:
        df_new_events.to_csv(filename, index=False)
    
    print(f"Added {len(df_new_events)} new events across {num_sessions} sessions")
    return df_new_events

def run_real_time_data_generator(interval_seconds=10, num_sessions_per_batch=5):
    """Run a continuous data generator to simulate real-time data"""
    print(f"Starting real-time data generation every {interval_seconds} seconds...")
    
    try:
        while True:
            # Generate and append new data
            generate_and_append_events(num_sessions=num_sessions_per_batch)
            
            # Sleep for interval seconds
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Data generation stopped by user.")

if __name__ == "__main__":
    # Initial data generation
    if not os.path.exists('clickstream_data.csv'):
        generate_and_save_events(num_sessions=500, filename='clickstream_data.csv')
    
    # Run real-time data generator
    import argparse
    parser = argparse.ArgumentParser(description='Generate real-time e-commerce clickstream data')
    parser.add_argument('--interval', type=int, default=10, help='Interval in seconds between data generation batches')
    parser.add_argument('--batch-size', type=int, default=5, help='Number of sessions to generate in each batch')
    args = parser.parse_args()
    
    run_real_time_data_generator(interval_seconds=args.interval, num_sessions_per_batch=args.batch_size)
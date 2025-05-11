import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="🌸 My Daily Activities",
    page_icon="🌸",
    layout="wide"
)

# Define activities (kid-friendly options)
activities = [
    "Playing", "Reading", "Drawing", "Dancing", "Singing",
    "Math", "Science", "Story Time", "Outdoor Play", "Puzzle",
    "Craft", "Coding", "Yoga", "Music", "Painting",
    "Gardening", "Cooking", "Cleaning", "Helping", "TV Time",
    "Sleeping", "Eating", "Bathing", "Traveling", "Other Fun"
]

# File path for data storage
DATA_FILE = "daily_check.csv"

# Function to load data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=[
            'date', 'Activity 1', 'Activity 1 proportion',
            'Activity 2', 'Activity 2 proportion',
            'Activity 3', 'Activity 3 proportion', 'Note'
        ])
    
    # Convert date column to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df

# Function to save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Function to get time periods
def get_time_period_data(df, period):
    today = datetime.now().date()
    
    if period == "Last Week":
        start_date = today - timedelta(days=7)
    elif period == "Last Month":
        start_date = today - timedelta(days=30)
    elif period == "Last 6 Months":
        start_date = today - timedelta(days=180)
    elif period == "Last Year":
        start_date = today - timedelta(days=365)
    else:  # All Data
        return df
    
    return df[df['date'] >= start_date]

# Function to calculate activity percentages
def calculate_percentages(df):
    activity_totals = {}
    
    for i in range(1, 4):
        for _, row in df.iterrows():
            activity = row[f'Activity {i}']
            proportion = row[f'Activity {i} proportion']
            activity_totals[activity] = activity_totals.get(activity, 0) + proportion
    
    total_time = sum(activity_totals.values()) or 1  # Avoid division by zero
    return {k: (v / total_time * 100) for k, v in activity_totals.items()}

# Main App
st.title("🌸 My Daily Activities")

# Section 1: Activity Summary
st.header("Activity Summary")

# Time period selection
time_period = st.selectbox(
    "Show activities from:",
    ["All Data", "Last Week", "Last Month", "Last 6 Months", "Last Year"],
    index=0
)

# Load and filter data
df = load_data()
filtered_df = get_time_period_data(df, time_period)

# Show activity percentages
percentages = calculate_percentages(filtered_df)
if percentages:
    st.subheader("Time Spent on Activities")
    for activity, percent in sorted(percentages.items(), key=lambda x: -x[1]):
        if percent >= 1:  # Only show activities with at least 1%
            st.progress(int(percent), text=f"{activity}: {percent:.1f}%")
else:
    st.info("No activity data available yet!")

# Section 2: Daily Entry
st.header("Daily Entry")

# Date picker
selected_date = st.date_input(
    "Select Date:",
    value=datetime.now().date() - timedelta(days=1),
    max_value=datetime.now().date() - timedelta(days=1),
    key="date_picker"
)

# Check for existing entry
existing_entry = df[df['date'] == selected_date]

# Initialize form state
if 'form' not in st.session_state:
    st.session_state.form = {
        'activities': [activities[0], activities[1], activities[2]],
        'proportions': [33, 33, 34],
        'note': ''
    }

# Load existing entry if found
if not existing_entry.empty:
    entry = existing_entry.iloc[0]
    st.session_state.form = {
        'activities': [
            entry['Activity 1'],
            entry['Activity 2'],
            entry['Activity 3']
        ],
        'proportions': [
            entry['Activity 1 proportion'],
            entry['Activity 2 proportion'],
            entry['Activity 3 proportion']
        ],
        'note': entry.get('Note', '')
    }

# Activity entry form
with st.form("daily_form"):
    st.subheader("Today's Activities")
    
    proportions = []
    for i in range(3):
        col1, col2 = st.columns([3, 1])
        with col1:
            activity = st.selectbox(
                f"Activity {i+1}",
                activities,
                index=activities.index(st.session_state.form['activities'][i]),
                key=f'act_{i}'
            )
        with col2:
            max_val = 100 - sum(proportions) if i < 2 else 100 - sum(proportions)
            proportion = st.slider(
                "Percentage",
                min_value=0,
                max_value=max_val,
                value=st.session_state.form['proportions'][i],
                key=f'prop_{i}'
            )
            proportions.append(proportion)
    
    # Note field
    note = st.text_area(
        "Notes (max 500 characters, any language):",
        value=st.session_state.form['note'],
        max_chars=500
    )
    
    # Form buttons
    col1, col2 = st.columns(2)
    with col1:
        save_btn = st.form_submit_button("💾 Save My Day")
    with col2:
        reset_btn = st.form_submit_button("🔄 Reset Form")

# Handle form submission
if save_btn:
    # Create/update entry
    new_entry = {
        'date': selected_date,
        'Activity 1': st.session_state.act_0,
        'Activity 1 proportion': st.session_state.prop_0,
        'Activity 2': st.session_state.act_1,
        'Activity 2 proportion': st.session_state.prop_1,
        'Activity 3': st.session_state.act_2,
        'Activity 3 proportion': st.session_state.prop_2,
        'Note': note if note.strip() else existing_entry.get('Note', '').iloc[0] if not existing_entry.empty else ''
    }
    
    # Update DataFrame
    if not existing_entry.empty:
        df.loc[df['date'] == selected_date, list(new_entry.keys())] = list(new_entry.values())
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save data
    save_data(df)
    st.success("Saved successfully! Great job today! 👏")
    
if reset_btn:
    st.session_state.form = {
        'activities': [activities[0], activities[1], activities[2]],
        'proportions': [33, 33, 34],
        'note': ''
    }
    st.rerun()

# Add some styling
st.markdown("""
<style>
    [data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stProgress > div > div > div > div {
        background-color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)
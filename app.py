import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import pytz

# Set page configuration
st.set_page_config(page_title="Daily Check App", page_icon="🌸", layout="wide")

# Set timezone to Indian Standard Time
ist = pytz.timezone('Asia/Kolkata')

# Define activities (you can modify this list as needed)
activities = [
    "Playing", "Reading", "Drawing", "Dancing", "Singing",
    "Math Practice", "Science Learning", "Story Time", "Outdoor Play", "Puzzle",
    "Craft", "Coding", "Yoga", "Music", "Painting",
    "Gardening", "Cooking", "Cleaning", "Helping", "Watching",
    "Sleeping", "Eating", "Bathing", "Traveling", "Other"
]

# GitHub file path
GITHUB_FILE_PATH = "Monitoring/daily_check.csv"

# Function to load data from GitHub
@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data():
    try:
        if os.path.exists(GITHUB_FILE_PATH):
            df = pd.read_csv(GITHUB_FILE_PATH)
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(GITHUB_FILE_PATH), exist_ok=True)
            # Create empty DataFrame with correct columns
            df = pd.DataFrame(columns=[
                'date', 'Activity 1', 'Activity 1 proportion',
                'Activity 2', 'Activity 2 proportion',
                'Activity 3', 'Activity 3 proportion', 'Note'
            ])
            df.to_csv(GITHUB_FILE_PATH, index=False)
        
        # Convert date column to datetime and sort
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            'date', 'Activity 1', 'Activity 1 proportion',
            'Activity 2', 'Activity 2 proportion',
            'Activity 3', 'Activity 3 proportion', 'Note'
        ])

# Function to save data to GitHub
def save_data(df):
    try:
        # Sort by date before saving
        df = df.sort_values('date')
        df.to_csv(GITHUB_FILE_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Function to filter data based on time period
def filter_data(df, time_period):
    today = datetime.now(ist).date()
    
    if time_period == "Last Week":
        start_date = today - timedelta(days=7)
    elif time_period == "Last Month":
        start_date = today - timedelta(days=30)
    elif time_period == "Last 6 Months":
        start_date = today - timedelta(days=180)
    elif time_period == "Last Year":
        start_date = today - timedelta(days=365)
    else:  # All Data
        return df
    
    return df[df['date'].dt.date >= start_date]

# Function to create pie chart with Plotly
def create_pie_chart(df):
    if df.empty:
        st.warning("No data available for the selected time period.")
        return
    
    # Combine all activity proportions
    proportions = {}
    for i in range(1, 4):
        activity_col = f'Activity {i}'
        proportion_col = f'Activity {i} proportion'
        
        for _, row in df.iterrows():
            activity = row[activity_col]
            proportion = row[proportion_col]
            
            if activity in proportions:
                proportions[activity] += proportion
            else:
                proportions[activity] = proportion
    
    # Convert to DataFrame and sort
    pie_data = pd.DataFrame.from_dict(proportions, orient='index', columns=['value'])
    pie_data = pie_data.sort_values('value', ascending=False)
    
    # Filter out values < 1% of total
    total = pie_data['value'].sum()
    pie_data = pie_data[pie_data['value'] / total * 100 >= 1]
    
    # Limit to top 10 if more than 10 entries
    if len(pie_data) > 10:
        pie_data = pie_data.head(10)
        others = pd.DataFrame({'value': [total - pie_data['value'].sum()]}, index=['Others'])
        pie_data = pd.concat([pie_data, others])
    
    # Create pie chart with Plotly
    if not pie_data.empty:
        fig = px.pie(
            pie_data,
            values='value',
            names=pie_data.index,
            title='Activity Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial',
            hovertemplate='%{label}: %{percent}'
        )
        fig.update_layout(
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data to display (all values are less than 1% of total).")

# Upper Section
st.title("🌸 Daily Check App")
st.subheader("Activity Distribution")

# Time period selection
time_period = st.selectbox(
    "Select Time Period:",
    ["All Data", "Last Week", "Last Month", "Last 6 Months", "Last Year"],
    index=0
)

# Load data and filter
df = load_data()
filtered_df = filter_data(df, time_period)

# Display pie chart
create_pie_chart(filtered_df)

# Lower Section
st.subheader("Daily Entry")

# Date picker (only past dates allowed)
today = datetime.now(ist).date()
selected_date = st.date_input(
    "Select Date:",
    value=today - timedelta(days=1),
    max_value=today - timedelta(days=1),
    key="date_picker"
)

# Check if entry exists for selected date
existing_entry = df[df['date'].dt.date == selected_date]

# Initialize session state for form values
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'activity1': activities[0],
        'activity2': activities[1],
        'activity3': activities[2],
        'slider1': 33,
        'slider2': 33,
        'slider3': 34,
        'note': ''
    }

# If entry exists, load values
if not existing_entry.empty:
    entry = existing_entry.iloc[0]
    st.session_state.form_values = {
        'activity1': entry['Activity 1'],
        'activity2': entry['Activity 2'],
        'activity3': entry['Activity 3'],
        'slider1': entry['Activity 1 proportion'],
        'slider2': entry['Activity 2 proportion'],
        'slider3': entry['Activity 3 proportion'],
        'note': entry.get('Note', '')
    }
elif st.session_state.get('form_submitted', False):
    # Reset form after submission
    st.session_state.form_values = {
        'activity1': activities[0],
        'activity2': activities[1],
        'activity3': activities[2],
        'slider1': 33,
        'slider2': 33,
        'slider3': 34,
        'note': ''
    }
    st.session_state.form_submitted = False

# Slider update functions
def update_slider1():
    max_val = 100 - st.session_state.slider2
    st.session_state.slider1 = min(st.session_state.slider1, max_val)
    st.session_state.slider3 = 100 - st.session_state.slider1 - st.session_state.slider2

def update_slider2():
    max_val = 100 - st.session_state.slider1
    st.session_state.slider2 = min(st.session_state.slider2, max_val)
    st.session_state.slider3 = 100 - st.session_state.slider1 - st.session_state.slider2

# Activity forms
with st.form("daily_entry_form"):
    # Activity 1
    st.markdown("**Activity 1**")
    col1, col2 = st.columns([3, 2])
    with col1:
        activity1 = st.selectbox(
            "Select Activity 1:",
            activities,
            index=activities.index(st.session_state.form_values['activity1']),
            key='activity1'
        )
    with col2:
        slider1 = st.slider(
            "Proportion:",
            min_value=0,
            max_value=100,
            value=st.session_state.form_values['slider1'],
            key='slider1',
            on_change=update_slider1
        )
    
    # Activity 2
    st.markdown("**Activity 2**")
    col1, col2 = st.columns([3, 2])
    with col1:
        activity2 = st.selectbox(
            "Select Activity 2:",
            activities,
            index=activities.index(st.session_state.form_values['activity2']),
            key='activity2'
        )
    with col2:
        slider2 = st.slider(
            "Proportion:",
            min_value=0,
            max_value=100 - slider1,
            value=st.session_state.form_values['slider2'],
            key='slider2',
            on_change=update_slider2
        )
    
    # Activity 3 (automatically calculated)
    remaining = 100 - slider1 - slider2
    st.markdown("**Activity 3**")
    col1, col2 = st.columns([3, 2])
    with col1:
        activity3 = st.selectbox(
            "Select Activity 3:",
            activities,
            index=activities.index(st.session_state.form_values['activity3']),
            key='activity3'
        )
    with col2:
        # Display only, not editable
        st.slider(
            "Proportion:",
            min_value=0,
            max_value=100,
            value=remaining,
            key='slider3_display',
            disabled=True
        )
    
    # Note field with character limit
    note = st.text_area(
        "Note (Max 500 characters, supports Indian languages):",
        value=st.session_state.form_values['note'],
        max_chars=500,
        key='note'
    )
    
    # Form buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit_button = st.form_submit_button("Save Entry")
    with col2:
        load_button = st.form_submit_button("Load Entry")

# Handle form submission
if submit_button:
    # Create new entry
    new_entry = {
        'date': selected_date,
        'Activity 1': activity1,
        'Activity 1 proportion': slider1,
        'Activity 2': activity2,
        'Activity 2 proportion': slider2,
        'Activity 3': activity3,
        'Activity 3 proportion': remaining,
        'Note': note if note.strip() else existing_entry.get('Note', '').iloc[0] if not existing_entry.empty else ''
    }
    
    # Update DataFrame
    if not existing_entry.empty:
        # Update existing entry
        df.loc[df['date'].dt.date == selected_date, list(new_entry.keys())] = list(new_entry.values())
    else:
        # Add new entry
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save data
    if save_data(df):
        st.success("Entry saved successfully!")
        st.session_state.form_submitted = True
        st.experimental_rerun()

if load_button:
    if not existing_entry.empty:
        st.success("Entry loaded successfully!")
    else:
        st.warning("No entry found for selected date.")
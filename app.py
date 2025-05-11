import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz

# Set page configuration
st.set_page_config(page_title="Daily Check App", page_icon="🌸", layout="wide")

# Set timezone to Indian Standard Time
ist = pytz.timezone('Asia/Kolkata')

# Define activities (kid-friendly options)
activities = [
    "Playing", "Reading", "Drawing", "Dancing", "Singing",
    "Math", "Science", "Story Time", "Outdoor Play", "Puzzle",
    "Craft", "Coding", "Yoga", "Music", "Painting",
    "Gardening", "Cooking", "Cleaning", "Helping", "TV Time",
    "Sleeping", "Eating", "Bathing", "Traveling", "Other Fun"
]

# GitHub file path
GITHUB_FILE_PATH = "Monitoring/daily_check.csv"

# Function to load data
@st.cache_data(ttl=600)
def load_data():
    try:
        if os.path.exists(GITHUB_FILE_PATH):
            df = pd.read_csv(GITHUB_FILE_PATH)
        else:
            os.makedirs(os.path.dirname(GITHUB_FILE_PATH), exist_ok=True)
            df = pd.DataFrame(columns=[
                'date', 'Activity 1', 'Activity 1 proportion',
                'Activity 2', 'Activity 2 proportion',
                'Activity 3', 'Activity 3 proportion', 'Note'
            ])
            df.to_csv(GITHUB_FILE_PATH, index=False)
        
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            'date', 'Activity 1', 'Activity 1 proportion',
            'Activity 2', 'Activity 2 proportion',
            'Activity 3', 'Activity 3 proportion', 'Note'
        ])

# Function to save data
def save_data(df):
    try:
        df.sort_values('date').to_csv(GITHUB_FILE_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Function to filter data by time period
def filter_data(df, time_period):
    today = datetime.now(ist).date()
    periods = {
        "Last Week": 7,
        "Last Month": 30,
        "Last 6 Months": 180,
        "Last Year": 365
    }
    if time_period in periods:
        return df[df['date'].dt.date >= (today - timedelta(days=periods[time_period]))]
    return df

# Function to display activity summary
def show_activity_summary(df):
    if df.empty:
        st.warning("No data available for the selected time period.")
        return
    
    # Calculate activity proportions
    activity_data = {}
    for i in range(1, 4):
        for _, row in df.iterrows():
            activity = row[f'Activity {i}']
            proportion = row[f'Activity {i} proportion']
            activity_data[activity] = activity_data.get(activity, 0) + proportion
    
    # Prepare data for display
    total = sum(activity_data.values())
    summary = pd.DataFrame({
        'Activity': activity_data.keys(),
        'Percentage': [round(val/total*100, 1) for val in activity_data.values()],
        'Time Spent': [f"{val}%" for val in activity_data.values()]
    }).sort_values('Percentage', ascending=False)
    
    # Filter small percentages and limit to top 10
    summary = summary[summary['Percentage'] >= 1].head(10)
    
    if summary.empty:
        st.warning("No activities with significant time spent.")
    else:
        st.dataframe(
            summary[['Activity', 'Time Spent', 'Percentage']],
            column_config={
                "Activity": "Activity",
                "Time Spent": "Time Spent (%)",
                "Percentage": st.column_config.ProgressColumn(
                    "Percentage",
                    format="%f%%",
                    min_value=0,
                    max_value=100
                )
            },
            hide_index=True,
            use_container_width=True
        )

# Upper Section
st.title("🌸 My Daily Activities")
st.subheader("Activity Summary")

# Time period selection
time_period = st.selectbox(
    "Show activities from:",
    ["All Data", "Last Week", "Last Month", "Last 6 Months", "Last Year"],
    index=0
)

# Load and display data
df = load_data()
show_activity_summary(filter_data(df, time_period))

# Lower Section
st.subheader("Today's Activities")

# Date picker (only past dates)
today = datetime.now(ist).date()
selected_date = st.date_input(
    "Select Date:",
    value=today - timedelta(days=1),
    max_value=today - timedelta(days=1),
    key="date_picker"
)

# Check for existing entry
existing_entry = df[df['date'].dt.date == selected_date]

# Initialize form values
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'activities': [activities[0], activities[1], activities[2]],
        'proportions': [33, 33, 34],
        'note': ''
    }

# Load existing entry if found
if not existing_entry.empty:
    entry = existing_entry.iloc[0]
    st.session_state.form_values = {
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
elif st.session_state.get('form_submitted', False):
    st.session_state.form_values = {
        'activities': [activities[0], activities[1], activities[2]],
        'proportions': [33, 33, 34],
        'note': ''
    }
    st.session_state.form_submitted = False

# Activity form
with st.form("daily_form"):
    # Activity inputs
    proportions = []
    for i in range(3):
        st.markdown(f"**Activity {i+1}**")
        col1, col2 = st.columns([3, 2])
        with col1:
            activity = st.selectbox(
                f"Choose activity {i+1}:",
                activities,
                index=activities.index(st.session_state.form_values['activities'][i]),
                key=f'activity_{i}'
            )
        with col2:
            max_val = 100 - sum(proportions) if i < 2 else 100 - sum(proportions)
            proportion = st.slider(
                "Time spent (%):",
                min_value=0,
                max_value=max_val,
                value=st.session_state.form_values['proportions'][i],
                key=f'slider_{i}'
            )
            proportions.append(proportion)
    
    # Note input
    note = st.text_area(
        "Notes (supports all languages, max 500 characters):",
        value=st.session_state.form_values['note'],
        max_chars=500,
        key='note'
    )
    
    # Form buttons
    col1, col2 = st.columns(2)
    with col1:
        save_btn = st.form_submit_button("💾 Save My Day")
    with col2:
        load_btn = st.form_submit_button("🔍 Load My Day")

# Handle form submission
if save_btn:
    new_entry = {
        'date': selected_date,
        'Activity 1': st.session_state.activity_0,
        'Activity 1 proportion': st.session_state.slider_0,
        'Activity 2': st.session_state.activity_1,
        'Activity 2 proportion': st.session_state.slider_1,
        'Activity 3': st.session_state.activity_2,
        'Activity 3 proportion': st.session_state.slider_2,
        'Note': note if note.strip() else existing_entry.get('Note', '').iloc[0] if not existing_entry.empty else ''
    }
    
    if not existing_entry.empty:
        df.loc[df['date'].dt.date == selected_date, list(new_entry.keys())] = list(new_entry.values())
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    if save_data(df):
        st.success("Saved successfully! Great job today! 👏")
        st.session_state.form_submitted = True
        st.rerun()

if load_btn:
    if not existing_entry.empty:
        st.success("Found your day! Here's what you did.")
    else:
        st.warning("No activities found for this date. Ready to add new ones!")

# Add some fun emojis and colors
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #FF69B4;
    }
    [data-testid="stForm"] {
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
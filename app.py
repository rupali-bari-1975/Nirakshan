import streamlit as st
import pandas as pd
import io
import sys
from datetime import datetime, timedelta, date

# Configuration
st.set_page_config(page_title="Activity Tracker", page_icon="🌸", layout="wide")

# Try to import matplotlib with error handling
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.warning("Pie charts are disabled because matplotlib is not available.")

# Constants
DATA_FILE = "activity_data.csv"
ACTIVITY_LIST = [
    "Playing", "Drawing", "Reading", "Cooking", "Dancing", 
    "Singing", "Research", "Traveling", "Swimming", "Cycling",
    "Painting", "Crafting", "Gardening", "Watching TV", "Puzzle Solving",
    "Building Blocks", "Story Telling", "Photography", "Yoga", "Meditation",
    "Science Experiments", "Music Practice", "Language Learning", "Math Practice", "Writing"
]

# Initialize data file if it doesn't exist
def init_data_file():
    columns = [
        "Date", 
        "Activity 1", "Activity 1 proportion", 
        "Activity 2", "Activity 2 proportion", 
        "Activity 3", "Activity 3 proportion", 
        "Note"
    ]
    try:
        df = pd.read_csv(DATA_FILE)
        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = "" if col == "Note" else 0
        df.to_csv(DATA_FILE, index=False)
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(DATA_FILE, index=False)

# Load data from CSV
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df.sort_values('Date')
    except:
        return pd.DataFrame()

# Save data to CSV
def save_data(df):
    df = df.sort_values('Date')
    df.to_csv(DATA_FILE, index=False)
    return df

# Pie chart function with proper spacing
def create_pie_chart(df, time_period):
    if not MATPLOTLIB_AVAILABLE:
        st.warning("Pie charts are disabled because matplotlib is not available.")
        return None
        
    now = datetime.now().date()
    
    if time_period == "last week":
        start_date = now - timedelta(days=7)
    elif time_period == "last month":
        start_date = now - timedelta(days=30)
    elif time_period == "last 2 months":
        start_date = now - timedelta(days=60)
    elif time_period == "last 6 months":
        start_date = now - timedelta(days=180)
    elif time_period == "last year":
        start_date = now - timedelta(days=365)
    else:  # all records
        start_date = df['Date'].min() if not df.empty else now
    
    # Convert both to datetime.date for comparison
    filtered_df = df[df['Date'] >= start_date] if not df.empty else pd.DataFrame()
    
    if filtered_df.empty:
        st.warning("No data available for the selected time period.")
        return None
    
    # Combine all activity proportions
    activities = []
    
    for i in range(1, 4):
        activity_col = f"Activity {i}"
        prop_col = f"Activity {i} proportion"
        
        temp_df = filtered_df[[activity_col, prop_col]].copy()
        temp_df.columns = ['Activity', 'Proportion']
        activities.append(temp_df)
    
    combined = pd.concat(activities)
    activity_sum = combined.groupby('Activity')['Proportion'].sum().reset_index()
    activity_sum = activity_sum[activity_sum['Proportion'] > 0]
    
    if activity_sum.empty:
        st.warning("No activity data available.")
        return None
    
    # Sort and limit to top 10
    activity_sum = activity_sum.sort_values('Proportion', ascending=False)
    activity_sum = activity_sum.head(10)
    
    # Calculate percentages and filter out <1%
    total = activity_sum['Proportion'].sum()
    activity_sum['Percentage'] = (activity_sum['Proportion'] / total * 100).round(1)
    activity_sum = activity_sum[activity_sum['Percentage'] >= 1]
    
    if activity_sum.empty:
        st.warning("No activities with significant proportions.")
        return None
    
    # Create pie chart with proper spacing
    fig, ax = plt.subplots(figsize=(10, 10))
    colors = plt.cm.tab20.colors  # Bright colors
    
    wedges, texts, autotexts = ax.pie(
        activity_sum['Proportion'],
        labels=activity_sum['Activity'],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10},
        pctdistance=0.85,
        labeldistance=1.05
    )
    
    ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
    
    # Add title with proper spacing
    plt.title(f"Activity Distribution ({time_period})", fontsize=14, pad=20)
    plt.tight_layout(pad=3.0)
    
    return fig

# Function to update sliders with constraints
def update_sliders(changed_slider):
    # Get current values
    s1 = st.session_state.slider1
    s2 = st.session_state.slider2
    s3 = st.session_state.slider3
    
    # Calculate total and difference
    total = s1 + s2 + s3
    diff = total - 100
    
    if diff == 0:
        return  # No adjustment needed
    
    if changed_slider == 1:  # Slider 1 changed
        # First try to adjust slider3
        if s3 - diff >= 0 and s3 - diff <= 100:
            st.session_state.slider3 = s3 - diff
        else:
            # Then adjust slider2 with remaining difference
            remaining_diff = diff - (s3 - st.session_state.slider3)
            st.session_state.slider2 = s2 - remaining_diff
            # Ensure slider2 stays within bounds
            st.session_state.slider2 = max(0, min(100, st.session_state.slider2))
            # Recalculate slider3
            st.session_state.slider3 = 100 - st.session_state.slider1 - st.session_state.slider2
    
    elif changed_slider == 2:  # Slider 2 changed
        # First try to adjust slider3
        if s3 - diff >= 0 and s3 - diff <= 100:
            st.session_state.slider3 = s3 - diff
        else:
            # Then adjust slider1 with remaining difference
            remaining_diff = diff - (s3 - st.session_state.slider3)
            st.session_state.slider1 = s1 - remaining_diff
            # Ensure slider1 stays within bounds
            st.session_state.slider1 = max(0, min(100, st.session_state.slider1))
            # Recalculate slider3
            st.session_state.slider3 = 100 - st.session_state.slider1 - st.session_state.slider2
    
    # Final check to ensure all values are within bounds
    st.session_state.slider1 = max(0, min(100, st.session_state.slider1))
    st.session_state.slider2 = max(0, min(100, st.session_state.slider2))
    st.session_state.slider3 = max(0, min(100, st.session_state.slider3))
    
    # Final adjustment to ensure sum is exactly 100
    current_sum = st.session_state.slider1 + st.session_state.slider2 + st.session_state.slider3
    if current_sum != 100:
        st.session_state.slider3 += (100 - current_sum)

# Upper Section - Pie Chart
st.title("🌸 My Activity Tracker")
st.header("Activity Distribution")

# Time period selection
time_periods = ["all records", "last week", "last month", "last 2 months", "last 6 months", "last year"]
selected_period = st.selectbox("Select time period:", time_periods, index=0)

# Load data and display pie chart
df = load_data()
if MATPLOTLIB_AVAILABLE:
    pie_chart = create_pie_chart(df, selected_period)
    if pie_chart:
        st.pyplot(pie_chart)
    else:
        st.info("No data available to display the pie chart.")
else:
    st.info("Pie chart functionality is not available. Showing data table instead.")
    st.dataframe(df)

# Lower Section - Activity Tracking
st.header("Track Your Activities")

# Date picker (only past dates, default yesterday)
today = date.today()
yesterday = today - timedelta(days=1)
selected_date = st.date_input(
    "Select Date:", 
    value=yesterday,
    max_value=yesterday,
    help="Only past dates are allowed"
)

# Initialize session state for sliders if not already done
if 'slider1' not in st.session_state:
    st.session_state.slider1 = 50
if 'slider2' not in st.session_state:
    st.session_state.slider2 = 25
if 'slider3' not in st.session_state:
    st.session_state.slider3 = 25

# Initialize note in session state
if 'note' not in st.session_state:
    st.session_state.note = ""

# Activity selection and sliders
activity1 = st.selectbox("Activity 1:", ACTIVITY_LIST, index=0)
st.session_state.slider1 = st.slider(
    "Activity 1 Proportion:", 
    min_value=0, max_value=100, value=st.session_state.slider1, 
    key="slider1_key",
    on_change=update_sliders, args=(1,)
)

activity2 = st.selectbox("Activity 2:", ACTIVITY_LIST, index=1)
st.session_state.slider2 = st.slider(
    "Activity 2 Proportion:", 
    min_value=0, max_value=100, value=st.session_state.slider2, 
    key="slider2_key",
    on_change=update_sliders, args=(2,)
)

activity3 = st.selectbox("Activity 3:", ACTIVITY_LIST, index=2)
# Third slider is read-only (controlled by the other two)
st.session_state.slider3 = st.slider(
    "Activity 3 Proportion:", 
    min_value=0, max_value=100, value=st.session_state.slider3, 
    key="slider3_key",
    disabled=True
)

# Note textbox - properly bound to session state
note = st.text_area("Note:", value=st.session_state.note, max_chars=500, 
                   help="You can write in any Indian language", key="note_area")

# Buttons layout
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Submit Activity"):
        # Create new row or update existing one
        new_row = {
            "Date": selected_date,
            "Activity 1": activity1,
            "Activity 1 proportion": st.session_state.slider1,
            "Activity 2": activity2,
            "Activity 2 proportion": st.session_state.slider2,
            "Activity 3": activity3,
            "Activity 3 proportion": st.session_state.slider3,
            "Note": st.session_state.note
        }
        
        df = load_data()
        
        # Check if date already exists
        existing_index = df[df['Date'] == selected_date].index
        
        if not existing_index.empty:
            # Update existing row
            for col, value in new_row.items():
                df.at[existing_index[0], col] = value
            st.success(f"Updated activities for {selected_date}")
        else:
            # Add new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Added new activities for {selected_date}")
        
        # Save and reload data
        df = save_data(df)
        
        # Update pie chart
        if MATPLOTLIB_AVAILABLE:
            pie_chart = create_pie_chart(df, selected_period)
            if pie_chart:
                st.pyplot(pie_chart)

with col2:
    if st.button("Load Activity"):
        df = load_data()
        entry = df[df['Date'] == selected_date]
        
        if not entry.empty:
            entry = entry.iloc[0]
            
            # Update activity selections
            st.session_state.activity1 = entry["Activity 1"]
            st.session_state.activity2 = entry["Activity 2"]
            st.session_state.activity3 = entry["Activity 3"]
            
            # Update slider values
            st.session_state.slider1 = entry["Activity 1 proportion"]
            st.session_state.slider2 = entry["Activity 2 proportion"]
            st.session_state.slider3 = entry["Activity 3 proportion"]
            
            # Update note - this is critical for textbox loading
            st.session_state.note = entry["Note"] if pd.notna(entry["Note"]) else ""
            
            st.success(f"Loaded activities for {selected_date}")
            
            # Need to rerun to update UI
            st.rerun()
        else:
            st.warning(f"No entry found for {selected_date}")

with col3:
    # Download button
    df = load_data()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Records",
        data=csv,
        file_name="activity_records.csv",
        mime="text/csv"
    )

# Initialize data file if it doesn't exist
init_data_file()

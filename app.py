import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Child-friendly CSS
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #ff69b4; color: white; font-size: 18px; padding: 10px; }
    .stSelectbox, .stSlider, .stTextInput, .stDateInput { background-color: #e6e6fa; border-radius: 10px; padding: 10px; }
    h1, h2, h3 { color: #ff4500; font-family: 'Comic Sans MS', sans-serif; }
    .stNumberInput input { background-color: #fffacd; border: none; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for sliders
if 'slider1' not in st.session_state:
    st.session_state.slider1 = 50
if 'slider2' not in st.session_state:
    st.session_state.slider2 = 25
if 'slider3' not in st.session_state:
    st.session_state.slider3 = 25

# Activity list (modify as needed, up to 25)
activity_list = [
    "Playing", "Cooking", "Drawing", "Research", "Traveling", "Reading", "Singing", "Dancing",
    "Painting", "Writing", "Gardening", "Swimming", "Cycling", "Crafting", "Photography",
    "Hiking", "Yoga", "Gaming", "Sewing", "Knitting", "Fishing", "Bird Watching", "Stargazing",
    "Building", "Exploring"
]

# GitHub CSV URL (replace with your repository's raw URL)
CSV_URL = "https://raw.githubusercontent.com/yourusername/activity-tracker/main/data/activities.csv"

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])  # Drop rows with invalid dates
            return df.sort_values('Date')
        else:
            return pd.DataFrame(columns=['Date', 'Activity 1', 'Activity 1 proportion', 'Activity 2', 'Activity 2 proportion', 'Activity 3', 'Activity 3 proportion', 'Note'])
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}. Trying local file...")
        # Fallback to local CSV for testing
        local_csv = 'activities.csv'
        if os.path.exists(local_csv):
            try:
                df = pd.read_csv(local_csv)
                if not df.empty:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df = df.dropna(subset=['Date'])
                    return df.sort_values('Date')
            except Exception as local_e:
                st.error(f"Error loading local file: {local_e}")
        return pd.DataFrame(columns=['Date', 'Activity 1', 'Activity 1 proportion', 'Activity 2', 'Activity 2 proportion', 'Activity 3', 'Activity 3 proportion', 'Note'])

# Save dataset to GitHub (simulated locally; requires GitHub Actions or manual push for online)
def save_data(df):
    df = df.sort_values('Date')
    # Ensure Date is in a consistent string format for CSV
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df.to_csv('activities.csv', index=False)
    st.warning("Data saved locally. For GitHub, commit and push 'activities.csv' to your repository.")

# Upper Section: Pie Chart
st.title("My Fun Activity Tracker! 🎉")
st.header("How I Spend My Time 🥧")

time_options = ["Last Week", "Last Month", "Last 2 Months", "Last 6 Months", "Last Year", "All Records"]
time_selection = st.selectbox("Choose Time Period:", time_options, index=5)

df = load_data()
if not df.empty:
    today = datetime.today().date()
    if time_selection == "Last Week":
        start_date = today - timedelta(days=7)
    elif time_selection == "Last Month":
        start_date = today - timedelta(days=30)
    elif time_selection == "Last 2 Months":
        start_date = today - timedelta(days=60)
    elif time_selection == "Last 6 Months":
        start_date = today - timedelta(days=180)
    elif time_selection == "Last Year":
        start_date = today - timedelta(days=365)
    else:
        start_date = df['Date'].min().date() if not df['Date'].empty else today

    filtered_df = df[df['Date'].dt.date >= start_date]
    
    if not filtered_df.empty:
        # Aggregate proportions by activity
        activity_sums = {}
        for i in [1, 2, 3]:
            for _, row in filtered_df.iterrows():
                activity = row[f'Activity {i}']
                proportion = row[f'Activity {i} proportion']
                if activity in activity_sums:
                    activity_sums[activity] += proportion
                else:
                    activity_sums[activity] = proportion
        
        # Prepare data for pie chart
        labels = []
        sizes = []
        for activity, total in sorted(activity_sums.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (total / sum(activity_sums.values())) * 100
            if percentage >= 1:
                labels.append(activity)
                sizes.append(percentage)
        
        if sizes:
            fig, ax = plt.subplots()
            colors = plt.cm.Set3(range(len(labels)))  # Bright colors
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.write("Not enough data to show the pie chart.")
    else:
        st.write("No data for the selected time period.")
else:
    st.write("No data available yet. Add some activities below!")

# Spacer
st.markdown("<br><br>", unsafe_allow_html=True)

# Lower Section: Input Form
st.header("Add Your Activities! 🌟")

# Date Picker (past dates only)
yesterday = datetime.today().date() - timedelta(days=1)
selected_date = st.date_input("Pick a Date:", max_value=yesterday, value=yesterday)

# Activity Inputs
st.subheader("Activity 1")
activity1 = st.selectbox("Choose Activity 1:", activity_list, key="act1")

def update_sliders():
    total = st.session_state.slider1 + st.session_state.slider2
    if total > 100:
        excess = total - 100
        if st.session_state.get('last_slider', 'slider1') == 'slider1':
            # Adjust slider3 first, then slider2
            st.session_state.slider3 = max(0, st.session_state.slider3 - excess)
            if st.session_state.slider3 == 0 and excess > 0:
                st.session_state.slider2 = max(0, st.session_state.slider2 - (excess - st.session_state.slider3))
        else:
            # Adjust slider3 first, then slider1
            st.session_state.slider3 = max(0, st.session_state.slider3 - excess)
            if st.session_state.slider3 == 0 and excess > 0:
                st.session_state.slider1 = max(0, st.session_state.slider1 - (excess - st.session_state.slider3))
    else:
        st.session_state.slider3 = 100 - total

slider1 = st.slider("How much time for Activity 1? (%)", 0, 100, value=st.session_state.slider1, key="slider1", on_change=update_sliders)
st.session_state.last_slider = 'slider1'

st.subheader("Activity 2")
activity2 = st.selectbox("Choose Activity 2:", activity_list, key="actaction2")
slider2 = st.slider("How much time for Activity 2? (%)", 0, 100, value=st.session_state.slider2, key="slider2", on_change=update_sliders)
st.session_state.last_slider = 'slider2'

st.subheader("Activity 3")
activity3 = st.selectbox("Choose Activity 3:", activity_list, key="act3")
# Simulate read-only slider with number input
st.number_input("Activity 3 Time (%) (auto-adjusted):", 0, 100, value=st.session_state.slider3, disabled=True, key="slider3_display")

# Note Input
note = st.text_area("Note (e.g., in Gujarati or English, max 500 chars):", max_chars=500, height=100)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Activity")
with col2:
    load = st.button("Load Activity")
with col3:
    download = st.button("Download Records")

# Handle Submit
if submit:
    df = load_data()
    new_entry = {
        'Date': pd.to_datetime(selected_date),
        'Activity 1': activity1,
        'Activity 1 proportion': st.session_state.slider1,
        'Activity 2': activity2,
        'Activity 2 proportion': st.session_state.slider2,
        'Activity 3': activity3,
        'Activity 3 proportion': st.session_state.slider3,
        'Note': note
    }
    # Convert selected_date to datetime.date for comparison
    df_dates = pd.to_datetime(df['Date']).dt.date
    if selected_date in df_dates.values:
        df = df[df_dates != selected_date]
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(df)
    st.success("Activity saved!")

# Handle Load
if load:
    df = load_data()
    df_dates = pd.to_datetime(df['Date']).dt.date
    entry = df[df_dates == selected_date]
    if not entry.empty:
        st.session_state.act1 = entry['Activity 1'].iloc[0]
        st.session_state.slider1 = int(entry['Activity 1 proportion'].iloc[0])
        st.session_state.act2 = entry['Activity 2'].iloc[0]
        st.session_state.slider2 = int(entry['Activity 2 proportion'].iloc[0])
        st.session_state.act3 = entry['Activity 3'].iloc[0]
        st.session_state.slider3 = int(entry['Activity 3 proportion'].iloc[0])
        st.session_state.note = entry['Note'].iloc[0]
        st.experimental_rerun()
    else:
        st.error("Entry corresponding to this date is missing.")

# Handle Download
if download:
    df = load_data()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # Format for download
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="activities.csv",
        mime="text/csv",
        key="download_csv"
    )

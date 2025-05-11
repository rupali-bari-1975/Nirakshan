import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from github import Github
import io
import base64
import os

# Streamlit page configuration for child-friendly UI
st.set_page_config(page_title="My Activity Tracker", page_icon="🌈", layout="centered")
st.markdown("""
    <style>
    body {background-color: #f0f8ff;}
    .stApp {font-family: 'Comic Sans MS', cursive, sans-serif;}
    .stButton>button {background-color: #ff69b4; color: white; border-radius: 10px; font-size: 18px;}
    .stSelectbox, .stSlider, .stTextArea {background-color: #e6e6fa; border-radius: 10px; padding: 10px;}
    h1, h2, h3 {color: #ff4500; text-align: center;}
    .css-1d391kg {padding: 20px;}
    </style>
""", unsafe_allow_html=True)

# GitHub setup
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "Nirakshan"
CSV_FILE = "activity_records.csv"
g = Github(GITHUB_TOKEN)
repo = g.get_user().get_repo(REPO_NAME)

# Activity list (editable)
activity_list = [
    "Playing", "Cooking", "Drawing", "Research", "Traveling", "Reading", "Singing",
    "Dancing", "Painting", "Writing", "Gardening", "Cycling", "Swimming", "Crafting",
    "Photography", "Hiking", "Yoga", "Gaming", "Knitting", "Fishing", "Bird Watching",
    "Coding", "Baking", "Sculpting", "Volunteering"
]

# Function to read CSV from GitHub
def read_csv_from_github():
    try:
        content = repo.get_contents(CSV_FILE)
        csv_content = content.decoded_content.decode()
        df = pd.read_csv(io.StringIO(csv_content))
        return df
    except:
        # Initialize empty DataFrame if file doesn't exist or is empty
        columns = ["Date", "Activity_1", "Activity_1_proportion", "Activity_2",
                   "Activity_2_proportion", "Activity_3", "Activity_3_proportion", "Note"]
        return pd.DataFrame(columns=columns)

# Function to write CSV to GitHub
def write_csv_to_github(df):
    df = df.sort_values(by="Date").reset_index(drop=True)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    try:
        content = repo.get_contents(CSV_FILE)
        repo.update_file(content.path, "Update activity_records.csv", csv_content, content.sha)
    except:
        repo.create_file(CSV_FILE, "Create activity_records.csv", csv_content)

# Initialize session state for loaded values
if "loaded" not in st.session_state:
    st.session_state.loaded = False
    st.session_state.loaded_activity_1 = activity_list[0]
    st.session_state.loaded_slider_1 = 50
    st.session_state.loaded_activity_2 = activity_list[1]
    st.session_state.loaded_slider_2 = 25
    st.session_state.loaded_activity_3 = activity_list[2]
    st.session_state.loaded_slider_3 = 25
    st.session_state.loaded_note = ""

# Upper Section: Pie Chart
st.title("🌟 My Activity Pie Chart 🌟")
time_options = ["Last Week", "Last Month", "Last 2 Months", "Last 6 Months", "Last Year", "All Records"]
time_range = st.selectbox("📅 Choose Time Period", time_options, index=5)

# Load data
df = read_csv_from_github()
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    today = datetime.today().date()
    if time_range == "Last Week":
        start_date = today - timedelta(days=7)
    elif time_range == "Last Month":
        start_date = today - timedelta(days=30)
    elif time_range == "Last 2 Months":
        start_date = today - timedelta(days=60)
    elif time_range == "Last 6 Months":
        start_date = today - timedelta(days=180)
    elif time_range == "Last Year":
        start_date = today - timedelta(days=365)
    else:
        start_date = df["Date"].min().date()
    
    # Filter data
    mask = df["Date"].dt.date >= start_date
    filtered_df = df[mask]
    
    # Aggregate proportions
    activities = {}
    for i in [1, 2, 3]:
        for _, row in filtered_df.iterrows():
            activity = row[f"Activity_{i}"]
            proportion = row[f"Activity_{i}_proportion"]
            if activity and pd.notna(proportion):
                activities[activity] = activities.get(activity, 0) + proportion
    
    # Prepare pie chart data
    if activities:
        activity_df = pd.DataFrame(list(activities.items()), columns=["Activity", "Proportion"])
        activity_df = activity_df.sort_values(by="Proportion", ascending=False).head(10)
        total = activity_df["Proportion"].sum()
        activity_df["Percentage"] = (activity_df["Proportion"] / total * 100).round(2)
        activity_df = activity_df[activity_df["Percentage"] >= 1]
        
        # Plot pie chart
        plt.figure(figsize=(8, 6))
        colors = sns.color_palette("Set2", len(activity_df))
        plt.pie(activity_df["Percentage"], labels=activity_df["Activity"], autopct="%1.1f%%",
                startangle=140, colors=colors, textprops={'fontsize': 12})
        plt.title("My Activities", pad=30, fontsize=20, color="#ff4500")
        st.pyplot(plt)
    else:
        st.write("No activities found for this time period.")
else:
    st.write("No data available yet. Start adding activities below!")

# Lower Section: Activity Form
st.markdown("<hr>", unsafe_allow_html=True)
st.title("📝 Add or View My Activities 📝")

# Date picker (past dates only)
yesterday = datetime.today().date() - timedelta(days=1)
selected_date = st.date_input("📅 Pick a Date", value=yesterday, max_value=yesterday)

# Compute slider values to ensure sum = 100
if "temp_slider_1" not in st.session_state:
    st.session_state.temp_slider_1 = st.session_state.loaded_slider_1
if "temp_slider_2" not in st.session_state:
    st.session_state.temp_slider_2 = st.session_state.loaded_slider_2

# Activity inputs with loaded defaults
st.subheader("🎨 Activity 1")
activity_1 = st.selectbox("Choose Activity 1", activity_list, index=activity_list.index(st.session_state.loaded_activity_1), key="activity_1")
slider_1 = st.slider("How much time (%)?", 0, 100, st.session_state.temp_slider_1, key="slider_1")

st.subheader("🎭 Activity 2")
activity_2 = st.selectbox("Choose Activity 2", activity_list, index=activity_list.index(st.session_state.loaded_activity_2), key="activity_2")
slider_2 = st.slider("How much time (%)?", 0, 100, st.session_state.temp_slider_2, key="slider_2")

# Update temp values and compute slider_3
if slider_1 != st.session_state.temp_slider_1:
    st.session_state.temp_slider_1 = slider_1
    if slider_1 + st.session_state.temp_slider_2 > 100:
        st.session_state.temp_slider_2 = 100 - slider_1
    st.rerun()
elif slider_2 != st.session_state.temp_slider_2:
    st.session_state.temp_slider_2 = slider_2
    if st.session_state.temp_slider_1 + slider_2 > 100:
        st.session_state.temp_slider_1 = 100 - slider_2
    st.rerun()

# Compute slider_3
slider_3 = 100 - st.session_state.temp_slider_1 - st.session_state.temp_slider_2

st.subheader("🎶 Activity 3")
activity_3 = st.selectbox("Choose Activity 3", activity_list, index=activity_list.index(st.session_state.loaded_activity_3), key="activity_3")
st.slider("How much time (%)?", 0, 100, slider_3, key="slider_3", disabled=True)

# Note input
note = st.text_area("📜 Note (max 500 characters)", value=st.session_state.loaded_note or "", max_chars=500, height=100, key="note")

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit_button = st.button("Submit Activity")
with col2:
    load_button = st.button("Load Activity")
with col3:
    download_button = st.button("Download Records")

# Submit activity
if submit_button:
    new_data = {
        "Date": selected_date.strftime("%Y-%m-%d"),
        "Activity_1": activity_1,
        "Activity_1_proportion": slider_1,
        "Activity_2": activity_2,
        "Activity_2_proportion": slider_2,
        "Activity_3": activity_3,
        "Activity_3_proportion": slider_3,
        "Note": note
    }
    df = read_csv_from_github()
    df = df[df["Date"] != selected_date.strftime("%Y-%m-%d")]
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    write_csv_to_github(df)
    st.success("Activity saved successfully! 🌈")
    # Update loaded values
    st.session_state.loaded_activity_1 = activity_1
    st.session_state.loaded_slider_1 = slider_1
    st.session_state.loaded_activity_2 = activity_2
    st.session_state.loaded_slider_2 = slider_2
    st.session_state.loaded_activity_3 = activity_3
    st.session_state.loaded_slider_3 = slider_3
    st.session_state.loaded_note = note
    st.session_state.temp_slider_1 = slider_1
    st.session_state.temp_slider_2 = slider_2
    st.session_state.loaded = True

# Load activity
if load_button:
    df = read_csv_from_github()
    entry = df[df["Date"] == selected_date.strftime("%Y-%m-%d")]
    if not entry.empty:
        st.session_state.loaded_activity_1 = entry.iloc[0]["Activity_1"]
        st.session_state.loaded_slider_1 = int(entry.iloc[0]["Activity_1_proportion"])
        st.session_state.loaded_activity_2 = entry.iloc[0]["Activity_2"]
        st.session_state.loaded_slider_2 = int(entry.iloc[0]["Activity_2_proportion"])
        st.session_state.loaded_activity_3 = entry.iloc[0]["Activity_3"]
        st.session_state.loaded_slider_3 = int(entry.iloc[0]["Activity_3_proportion"])
        # Handle NaN or missing note
        st.session_state.loaded_note = str(entry.iloc[0]["Note"]) if pd.notna(entry.iloc[0]["Note"]) else ""
        st.session_state.temp_slider_1 = st.session_state.loaded_slider_1
        st.session_state.temp_slider_2 = st.session_state.loaded_slider_2
        st.session_state.loaded = True
        st.success("Activity loaded successfully! 🌟")
        st.rerun()
    else:
        st.error("Entry corresponding to this date is missing.")
        # Reset to defaults
        st.session_state.loaded_activity_1 = activity_list[0]
        st.session_state.loaded_slider_1 = 50
        st.session_state.loaded_activity_2 = activity_list[1]
        st.session_state.loaded_slider_2 = 25
        st.session_state.loaded_activity_3 = activity_list[2]
        st.session_state.loaded_slider_3 = 25
        st.session_state.loaded_note = ""
        st.session_state.temp_slider_1 = 50
        st.session_state.temp_slider_2 = 25
        st.session_state.loaded = False
        st.rerun()

# Download CSV
if download_button:
    df = read_csv_from_github()
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="activity_records.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from github import Github
import io
from datetime import datetime, timedelta
import uuid

# GitHub configuration
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "Nirakshan/activity_records.csv"
g = Github(GITHUB_TOKEN)
repo = g.get_repo("Nirakshan")

# Activity list (modifiable)
activity_list = [
    "Playing", "Cooking", "Drawing", "Research", "Traveling", "Reading", "Painting",
    "Singing", "Dancing", "Swimming", "Cycling", "Gardening", "Writing", "Hiking",
    "Photography", "Yoga", "Crafting", "Puzzle Solving", "Baking", "Sewing",
    "Knitting", "Fishing", "Bird Watching", "Stargazing", "Chess"
]

# Function to read CSV from GitHub
def read_csv_from_github():
    try:
        contents = repo.get_contents(REPO_NAME)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df
    except:
        # Create empty DataFrame if file doesn't exist
        return pd.DataFrame(columns=[
            "Date", "Activity_1", "Activity_1_proportion",
            "Activity_2", "Activity_2_proportion",
            "Activity_3", "Activity_3_proportion", "Note"
        ])

# Function to save CSV to GitHub
def save_csv_to_github(df):
    df = df.sort_values("Date")  # Sort by date
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    try:
        contents = repo.get_contents(REPO_NAME)
        repo.update_file(
            contents.path,
            f"Update {REPO_NAME}",
            csv_buffer.getvalue(),
            contents.sha
        )
    except:
        repo.create_file(
            REPO_NAME,
            f"Create {REPO_NAME}",
            csv_buffer.getvalue()
        )

# Function to create pie chart
def create_pie_chart(df, time_filter):
    # Filter data based on time period
    today = datetime.now().date()
    if time_filter == "Last Week":
        start_date = today - timedelta(days=7)
    elif time_filter == "Last Month":
        start_date = today - timedelta(days=30)
    elif time_filter == "Last 2 Months":
        start_date = today - timedelta(days=60)
    elif time_filter == "Last 6 Months":
        start_date = today - timedelta(days=180)
    elif time_filter == "Last Year":
        start_date = today - timedelta(days=365)
    else:  # All Records
        start_date = None

    if start_date:
        df = df[pd.to_datetime(df["Date"]) >= pd.to_datetime(start_date)]

    # Aggregate activity proportions
    activity_counts = {}
    for i in range(1, 4):
        col = f"Activity_{i}"
        prop_col = f"Activity_{i}_proportion"
        for _, row in df.iterrows():
            activity = row[col]
            proportion = row[prop_col]
            activity_counts[activity] = activity_counts.get(activity, 0) + proportion

    # Filter activities with >= 1% and limit to top 10
    total = sum(activity_counts.values())
    if total == 0:
        return None
    activity_percentages = {
        k: (v / total * 100) for k, v in activity_counts.items() if (v / total * 100) >= 1
    }
    sorted_activities = sorted(activity_percentages.items(), key=lambda x: x[1], reverse=True)[:10]
    if not sorted_activities:
        return None

    labels, sizes = zip(*sorted_activities)
    colors = plt.cm.Set3.colors[:len(labels)]  # Bright colors

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    plt.title("Activity Distribution", pad=20, fontsize=14, color="navy")
    return fig

# Streamlit app layout
st.set_page_config(page_title="Activity Tracker", page_icon="🌟", layout="centered")
st.title("🌈 Activity Tracker for My Star 🌈", anchor=False)
st.markdown("Track your fun activities with this colorful app! 🎉")

# Upper section: Pie chart
st.header("📊 Your Activity Chart", anchor=False)
time_filter = st.selectbox(
    "Select Time Period",
    ["All Records", "Last Week", "Last Month", "Last 2 Months", "Last 6 Months", "Last Year"],
    index=0
)
df = read_csv_from_github()
fig = create_pie_chart(df, time_filter)
if fig:
    st.pyplot(fig)
else:
    st.info("No data available for the selected period. Start adding activities below! 😊")

# Lower section: Activity input
st.header("✨ Add Your Activities", anchor=False)

# Date picker (past dates only)
yesterday = datetime.now().date() - timedelta(days=1)
selected_date = st.date_input(
    "Select Date",
    value=yesterday,
    max_value=yesterday,
    format="YYYY-MM-DD"
)

# Initialize session state for sliders
if "slider_1" not in st.session_state:
    st.session_state.slider_1 = 50
    st.session_state.slider_2 = 25
    st.session_state.slider_3 = 25

# Activity 1
st.subheader("🎮 Activity 1", anchor=False)
activity_1 = st.selectbox("Choose Activity 1", activity_list, key="activity_1")
slider_1 = st.slider(
    "Proportion (%)",
    min_value=0,
    max_value=100,
    value=st.session_state.slider_1,
    step=1,
    key="slider_1",
    on_change=lambda: st.session_state.update({
        "slider_3": max(0, 100 - st.session_state.slider_1 - st.session_state.slider_2),
        "slider_2": max(0, 100 - st.session_state.slider_1 - max(0, 100 - st.session_state.slider_1 - st.session_state.slider_2))
    })
)

# Activity 2
st.subheader("🍳 Activity 2", anchor=False)
activity_2 = st.selectbox("Choose Activity 2", activity_list, key="activity_2")
slider_2 = st.slider(
    "Proportion (%)",
    min_value=0,
    max_value=100,
    value=st.session_state.slider_2,
    step=1,
    key="slider_2",
    on_change=lambda: st.session_state.update({
        "slider_3": max(0, 100 - st.session_state.slider_1 - st.session_state.slider_2),
        "slider_1": max(0, 100 - st.session_state.slider_2 - max(0, 100 - st.session_state.slider_1 - st.session_state.slider_2))
    })
)

# Activity 3 (non-interactive slider)
st.subheader("🎨 Activity 3", anchor=False)
activity_3 = st.selectbox("Choose Activity 3", activity_list, key="activity_3")
slider_3 = st.slider(
    "Proportion (%)",
    min_value=0,
    max_value=100,
    value=100 - slider_1 - slider_2,
    step=1,
    key="slider_3",
    disabled=True
)

# Note textbox
st.subheader("📝 Note", anchor=False)
note = st.text_area(
    "Add a Note (max 500 characters, supports Gujarati and other Indian languages)",
    max_chars=500,
    height=100
)

# Buttons
col1, col2, col3 = st.columns([1, 1, 2])
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
    df = df[df["Date"] != selected_date.strftime("%Y-%m-%d")]  # Remove existing entry for date
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    save_csv_to_github(df)
    st.success("Activity saved successfully! 🎉")

# Load activity
if load_button:
    df = read_csv_from_github()
    entry = df[df["Date"] == selected_date.strftime("%Y-%m-%d")]
    if not entry.empty:
        st.session_state.activity_1 = entry["Activity_1"].iloc[0]
        st.session_state.slider_1 = entry["Activity_1_proportion"].iloc[0]
        st.session_state.activity_2 = entry["Activity_2"].iloc[0]
        st.session_state.slider_2 = entry["Activity_2_proportion"].iloc[0]
        st.session_state.activity_3 = entry["Activity_3"].iloc[0]
        st.session_state.slider_3 = entry["Activity_3_proportion"].iloc[0]
        st.session_state.note = entry["Note"].iloc[0]
        st.experimental_rerun()
    else:
        st.warning("Entry corresponding to this date is missing. 😔")

# Download CSV
if download_button:
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download activity_records.csv",
        data=csv_buffer.getvalue(),
        file_name="activity_records.csv",
        mime="text/csv"
    )

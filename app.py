import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from github import Github
import io
import base64
import streamlit.components.v1 as components

# Streamlit page config
st.set_page_config(page_title="My Activity Tracker", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color: #f0f8ff;}
    h1 {color: #ff69b4; font-family: Comic Sans MS;}
    h2 {color: #ff4500; font-family: Comic Sans MS;}
    .stButton>button {background-color: #90ee90; color: black; font-family: Comic Sans MS;}
    .stSlider>div>div>div {background-color: #ffd700;}
    .stSelectbox>div>div>select {background-color: #add8e6;}
    .stTextArea textarea {background-color: #e6e6fa;}
    </style>
    """,
    unsafe_allow_html=True
)

# GitHub setup
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
g = Github(GITHUB_TOKEN)
repo = g.get_repo("rupali-bari-1975/Nirakshan")
def get_csv_from_github():
    try:
        contents = repo.get_contents("activity_records.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df
    except:
        return pd.DataFrame(columns=["Date", "Activity_1", "Activity_1_proportion", 
                                     "Activity_2", "Activity_2_proportion", 
                                     "Activity_3", "Activity_3_proportion", "Note"])

def save_csv_to_github(df):
    df = df.sort_values("Date")
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    content = csv_buffer.getvalue()
    try:
        contents = repo.get_contents("activity_records.csv")
        repo.update_file(contents.path, "Update activity_records.csv", content, contents.sha)
    except:
        repo.create_file("activity_records.csv", "Create activity_records.csv", content)

# Activity list
activity_list = [
    "Playing", "Cooking", "Drawing", "Research", "Traveling", "Reading", "Singing", 
    "Dancing", "Painting", "Writing", "Gardening", "Swimming", "Cycling", "Hiking", 
    "Crafting", "Photography", "Yoga", "Meditation", "Gaming", "Baking", 
    "Knitting", "Fishing", "Bird Watching", "Stargazing", "Volunteering"
]

# Upper Section: Pie Chart
st.title("My Fun Activities! 🎉")
time_range = st.selectbox("Show activities for:", 
                          ["All Records", "Last Week", "Last Month", "Last 2 Months", 
                           "Last 6 Months", "Last Year"], index=0)

df = get_csv_from_github()
if not df.empty:
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
        start_date = pd.to_datetime(df["Date"]).min().date()

    if time_range != "All Records":
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[df["Date"] >= pd.to_datetime(start_date)]

    # Aggregate proportions
    activity_data = {}
    for i in [1, 2, 3]:
        temp = df.groupby(f"Activity_{i}")["Activity_%d_proportion" % i].sum()
        for act, prop in temp.items():
            activity_data[act] = activity_data.get(act, 0) + prop

    # Filter and limit to top 10
    total = sum(activity_data.values())
    if total > 0:
        activity_data = {k: (v / total * 100) for k, v in activity_data.items() if (v / total * 100) >= 1}
        activity_data = dict(sorted(activity_data.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Plot pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = plt.cm.Set3(range(len(activity_data)))
        wedges, texts, autotexts = ax.pie(
            activity_data.values(), labels=activity_data.keys(), autopct="%1.1f%%", 
            startangle=90, colors=colors
        )
        ax.axis("equal")
        plt.setp(autotexts, size=10, weight="bold", color="black")
        plt.setp(texts, size=12)
        st.pyplot(fig)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
else:
    st.write("No activities yet! Add some below! 🌟")

# Lower Section
st.header("Add Your Activities! 🌈")
yesterday = datetime.today().date() - timedelta(days=1)
selected_date = st.date_input("Pick a date:", value=yesterday, max_value=yesterday)

# Initialize session state for sliders
if "slider_1" not in st.session_state:
    st.session_state.slider_1 = 50
if "slider_2" not in st.session_state:
    st.session_state.slider_2 = 25
if "slider_3" not in st.session_state:
    st.session_state.slider_3 = 25

# Custom JavaScript for slider interaction
components.html(
    """
    <script>
    function updateSliders() {
        const slider1 = document.getElementById('slider1');
        const slider2 = document.getElementById('slider2');
        const slider3 = document.getElementById('slider3');
        
        slider1.oninput = function() {
            let val1 = parseInt(this.value);
            let val2 = parseInt(slider2.value);
            let val3 = 100 - val1 - val2;
            
            if (val3 < 0) {
                val2 = 100 - val1;
                val3 = 0;
            }
            slider2.value = val2;
            slider3.value = val3;
        };
        
        slider2.oninput = function() {
            let val2 = parseInt(this.value);
            let val1 = parseInt(slider1.value);
            let val3 = 100 - val1 - val2;
            
            if (val3 < 0) {
                val1 = 100 - val2;
                val3 = 0;
            }
            slider1.value = val1;
            slider3.value = val3;
        };
    }
    </script>
    """,
    height=0
)

# Activity Inputs
st.subheader("Activity 1")
act_1 = st.selectbox("Choose Activity 1:", activity_list, key="act_1")
slider_1 = st.slider("How much time? (%)", 0, 100, st.session_state.slider_1, key="slider1")
st.session_state.slider_1 = slider_1

st.subheader("Activity 2")
act_2 = st.selectbox("Choose Activity 2:", activity_list, key="act_2")
slider_2 = st.slider("How much time? (%)", 0, 100, st.session_state.slider_2, key="slider2")
st.session_state.slider_2 = slider_2

st.subheader("Activity 3")
act_3 = st.selectbox("Choose Activity 3:", activity_list, key="act_3")
slider_3 = st.slider("How much time? (%)", 0, 100, 100 - slider_1 - slider_2, disabled=True, key="slider3")
st.session_state.slider_3 = slider_3

# Note Textbox
st.subheader("Note")
note = st.text_area("Write a note (max 500 characters):", max_chars=500, height=100)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Activity")
with col2:
    load = st.button("Load Activity")
with col3:
    download = st.button("Download Records")

# Submit Activity
if submit:
    df = get_csv_from_github()
    new_entry = {
        "Date": selected_date.strftime("%Y-%m-%d"),
        "Activity_1": act_1,
        "Activity_1_proportion": slider_1,
        "Activity_2": act_2,
        "Activity_2_proportion": slider_2,
        "Activity_3": act_3,
        "Activity_3_proportion": slider_3,
        "Note": note
    }
    if selected_date.strftime("%Y-%m-%d") in df["Date"].values:
        df.loc[df["Date"] == selected_date.strftime("%Y-%m-%d")] = pd.Series(new_entry)
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_csv_to_github(df)
    st.success("Activity saved! 🎈")

# Load Activity
if load:
    df = get_csv_from_github()
    date_str = selected_date.strftime("%Y-%m-%d")
    if date_str in df["Date"].values:
        entry = df[df["Date"] == date_str].iloc[0]
        st.session_state.act_1 = entry["Activity_1"]
        st.session_state.slider_1 = int(entry["Activity_1_proportion"])
        st.session_state.act_2 = entry["Activity_2"]
        st.session_state.slider_2 = int(entry["Activity_2_proportion"])
        st.session_state.act_3 = entry["Activity_3"]
        st.session_state.slider_3 = int(entry["Activity_3_proportion"])
        st.session_state.note = entry["Note"]
        st.experimental_rerun()
    else:
        st.warning("Entry for this date is missing! 😔")

# Download CSV
if download:
    df = get_csv_to_github()
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="activity_records.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

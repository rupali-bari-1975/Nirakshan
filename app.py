import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import io

# Set page config
st.set_page_config(page_title="Activity Tracker", layout="wide")

# Custom colors for the pie chart
COLORS = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', 
    '#FF9F40', '#8AC249', '#EA5F89', '#00BFFF', '#FFD700'
]

# Activity list (you can modify this as needed)
activity_list = [
    "Playing", "Cooking", "Drawing", "Research", "Traveling",
    "Reading", "Dancing", "Singing", "Studying", "Sleeping",
    "Watching TV", "Gardening", "Cycling", "Swimming", "Painting",
    "Writing", "Coding", "Meditating", "Exercising", "Shopping",
    "Photography", "Music", "Crafting", "Baking", "Walking"
]

# Initialize or load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('activity_records.csv', parse_dates=['Date'])
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df.sort_values('Date').reset_index(drop=True)
    except:
        df = pd.DataFrame(columns=[
            'Date', 'Activity 1', 'Activity 1 proportion',
            'Activity 2', 'Activity 2 proportion',
            'Activity 3', 'Activity 3 proportion', 'Note'
        ])
    return df

def save_data(df):
    df = df.sort_values('Date').reset_index(drop=True)
    df.to_csv('activity_records.csv', index=False)
    return df

# Function to create pie chart
def create_pie_chart(df, time_period):
    # Filter data based on time period
    today = date.today()
    if time_period == 'last week':
        start_date = today - timedelta(days=7)
    elif time_period == 'last month':
        start_date = today - timedelta(days=30)
    elif time_period == 'last 2 months':
        start_date = today - timedelta(days=60)
    elif time_period == 'last 6 months':
        start_date = today - timedelta(days=180)
    elif time_period == 'last year':
        start_date = today - timedelta(days=365)
    else:  # all records
        start_date = df['Date'].min() if not df.empty else today
    
    filtered_df = df[df['Date'] >= start_date] if time_period != 'all records' else df
    
    # Prepare data for pie chart
    activities = []
    proportions = []
    
    # Collect all activities and their proportions
    for i in range(1, 4):
        col_act = f'Activity {i}'
        col_prop = f'Activity {i} proportion'
        activities.extend(filtered_df[col_act].tolist())
        proportions.extend(filtered_df[col_prop].tolist())
    
    if not activities:
        st.warning("No data available for the selected time period.")
        return
    
    # Create a summary dataframe
    summary = pd.DataFrame({'Activity': activities, 'Proportion': proportions})
    summary = summary.groupby('Activity')['Proportion'].sum().reset_index()
    summary = summary.sort_values('Proportion', ascending=False)
    
    # Combine small proportions into "Others"
    total = summary['Proportion'].sum()
    summary['Percentage'] = summary['Proportion'] / total * 100
    others = summary[summary['Percentage'] < 1]
    
    if not others.empty:
        main = summary[summary['Percentage'] >= 1]
        others_sum = others['Proportion'].sum()
        others_percentage = others_sum / total * 100
        if not main.empty:
            main = pd.concat([main, pd.DataFrame({
                'Activity': ['Others'],
                'Proportion': [others_sum],
                'Percentage': [others_percentage]
            })])
        summary = main
    
    # Limit to top 10 entries
    summary = summary.head(10)
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    patches, texts, autotexts = ax.pie(
        summary['Proportion'],
        labels=summary['Activity'],
        autopct='%1.1f%%',
        colors=COLORS[:len(summary)],
        startangle=90,
        pctdistance=0.85
    )
    
    # Make labels more readable
    for text in texts:
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    plt.title(f'Activity Distribution ({time_period.capitalize()})', pad=20)
    
    st.pyplot(fig)

# Main app
def main():
    df = load_data()
    
    st.title("🌈 My Activity Tracker")
    
    # Upper section - Pie chart
    with st.container():
        st.header("Activity Summary")
        time_period = st.selectbox(
            "Select time period:",
            ["all records", "last week", "last month", "last 2 months", "last 6 months", "last year"],
            index=0
        )
        create_pie_chart(df, time_period)
    
    # Lower section - Activity input
    with st.container():
        st.header("Daily Activity Entry")
        
        # Date picker (default to yesterday, only past dates allowed)
        yesterday = date.today() - timedelta(days=1)
        selected_date = st.date_input(
            "Select Date:",
            value=yesterday,
            max_value=yesterday
        )
        
        # Initialize session state for slider values if not exists
        if 'slider1' not in st.session_state:
            st.session_state.slider1 = 50
            st.session_state.slider2 = 25
            st.session_state.slider3 = 25
        
        # Function to update sliders
        def update_sliders(primary_slider, secondary_slider, fixed_slider, changed_slider):
            total = st.session_state.slider1 + st.session_state.slider2 + st.session_state.slider3
            diff = total - 100
            
            if diff != 0:
                if changed_slider == primary_slider:
                    # First try to adjust fixed_slider
                    if st.session_state[fixed_slider] - diff >= 0:
                        st.session_state[fixed_slider] -= diff
                    else:
                        remaining_diff = diff - st.session_state[fixed_slider]
                        st.session_state[fixed_slider] = 0
                        st.session_state[secondary_slider] -= remaining_diff
                elif changed_slider == secondary_slider:
                    # First try to adjust fixed_slider
                    if st.session_state[fixed_slider] - diff >= 0:
                        st.session_state[fixed_slider] -= diff
                    else:
                        remaining_diff = diff - st.session_state[fixed_slider]
                        st.session_state[fixed_slider] = 0
                        st.session_state[primary_slider] -= remaining_diff
        
        # Activity 1
        st.subheader("Activity 1")
        act1 = st.selectbox("Select Activity 1:", activity_list, key='act1')
        st.session_state.slider1 = st.slider(
            "Proportion:", 0, 100, st.session_state.slider1, key='slider1',
            on_change=update_sliders,
            args=('slider1', 'slider2', 'slider3', 'slider1')
        )
        
        # Activity 2
        st.subheader("Activity 2")
        act2 = st.selectbox("Select Activity 2:", activity_list, key='act2')
        st.session_state.slider2 = st.slider(
            "Proportion:", 0, 100, st.session_state.slider2, key='slider2',
            on_change=update_sliders,
            args=('slider2', 'slider1', 'slider3', 'slider2')
        )
        
        # Activity 3 (read-only slider)
        st.subheader("Activity 3")
        act3 = st.selectbox("Select Activity 3:", activity_list, key='act3')
        st.session_state.slider3 = st.slider(
            "Proportion:", 0, 100, st.session_state.slider3, key='slider3',
            disabled=True
        )
        
        # Note field
        note = st.text_area("Note (in any Indian language):", max_chars=500, height=100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Submit button
            if st.button("Submit Activity"):
                # Check if date already exists
                mask = df['Date'] == selected_date
                if mask.any():
                    # Update existing record
                    df.loc[mask, [
                        'Activity 1', 'Activity 1 proportion',
                        'Activity 2', 'Activity 2 proportion',
                        'Activity 3', 'Activity 3 proportion', 'Note'
                    ]] = [
                        act1, st.session_state.slider1,
                        act2, st.session_state.slider2,
                        act3, st.session_state.slider3, note
                    ]
                else:
                    # Add new record
                    new_record = pd.DataFrame([{
                        'Date': selected_date,
                        'Activity 1': act1,
                        'Activity 1 proportion': st.session_state.slider1,
                        'Activity 2': act2,
                        'Activity 2 proportion': st.session_state.slider2,
                        'Activity 3': act3,
                        'Activity 3 proportion': st.session_state.slider3,
                        'Note': note
                    }])
                    df = pd.concat([df, new_record], ignore_index=True)
                
                df = save_data(df)
                st.success("Activity submitted successfully!")
        
        with col2:
            # Load button
            if st.button("Load Activity"):
                mask = df['Date'] == selected_date
                if mask.any():
                    record = df[mask].iloc[0]
                    st.session_state.act1 = record['Activity 1']
                    st.session_state.act2 = record['Activity 2']
                    st.session_state.act3 = record['Activity 3']
                    st.session_state.slider1 = record['Activity 1 proportion']
                    st.session_state.slider2 = record['Activity 2 proportion']
                    st.session_state.slider3 = record['Activity 3 proportion']
                    st.session_state.note = record['Note']
                    st.experimental_rerun()
                else:
                    st.warning("No entry found for this date.")
        
        with col3:
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Records",
                data=csv,
                file_name='activity_records.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()

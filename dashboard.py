import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page configuration
st.set_page_config(page_title="Bike Sharing Analysis Dashboard", layout="wide")

@st.cache_data
def load_data():
    hour_data = pd.read_csv("data/hour.csv")
    day_data = pd.read_csv("data/day.csv")
    return hour_data, day_data

# Load the data
hour_data, day_data = load_data()

# Map values to readable labels
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weather_mapping = {
    1: 'Clear/Few Clouds',
    2: 'Mist/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Heavy Rain/Snow'
}

hour_data['season'] = hour_data['season'].map(season_mapping)
hour_data['weathersit'] = hour_data['weathersit'].map(weather_mapping)
day_data['season'] = day_data['season'].map(season_mapping)
day_data['weathersit'] = day_data['weathersit'].map(weather_mapping)

# Extract year for filtering
hour_data['year'] = pd.to_datetime(hour_data['dteday']).dt.year
day_data['year'] = pd.to_datetime(day_data['dteday']).dt.year

# Define color palette
palette = ["#C6E7FF", "#D4F6FF", "#FBFBFB", "#FFDDAE"]

# Title and Description
st.title("Bike Sharing Data Analysis Dashboard")

# Sidebar Filters
st.sidebar.title("Filters")
selected_season = st.sidebar.multiselect(
    "Select Season",
    options=hour_data['season'].unique(),
    default=hour_data['season'].unique()
)
selected_weather = st.sidebar.multiselect(
    "Select Weather Condition",
    options=hour_data['weathersit'].unique(),
    default=hour_data['weathersit'].unique()
)
selected_year = st.sidebar.multiselect(
    "Select Year",
    options=hour_data['year'].unique(),
    default=hour_data['year'].unique()
)

# Filtered Data
filtered_hour_data = hour_data[
    (hour_data['season'].isin(selected_season)) &
    (hour_data['weathersit'].isin(selected_weather)) &
    (hour_data['year'].isin(selected_year))
]
filtered_day_data = day_data[
    (day_data['season'].isin(selected_season)) &
    (day_data['weathersit'].isin(selected_weather)) &
    (day_data['year'].isin(selected_year))
]

# Calculate scorecard metrics
avg_rentals_per_day = filtered_day_data['cnt'].mean()
avg_rentals_per_hour = filtered_hour_data['cnt'].mean()
avg_users_per_day = filtered_day_data[['casual', 'registered']].sum(axis=1).mean()
avg_users_per_hour = filtered_hour_data[['casual', 'registered']].sum(axis=1).mean()

# Scorecard Section
st.header("Scorecard Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg. Rentals/Day", f"{avg_rentals_per_day:.2f}")
col2.metric("Avg. Rentals/Hour", f"{avg_rentals_per_hour:.2f}")
col3.metric("Avg. Users/Day", f"{avg_users_per_day:.2f}")
col4.metric("Avg. Users/Hour", f"{avg_users_per_hour:.2f}")

# Layout: Main Content
st.header("Visualizations and Insights")

# Question 1: Seasonal Effect on Rentals
st.subheader("Seasonal Effect on Bicycle Rentals")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(x="season", y="cnt", data=filtered_day_data, ci=None, palette=palette, ax=ax1)
    ax1.set_title("Average Rentals by Season (Daily Data)", fontsize=12)
    ax1.set_xlabel("Season")
    ax1.set_ylabel("Average Rentals")
    st.pyplot(fig1)

with row1_col2:
    season_hourly = filtered_hour_data.groupby("season")["cnt"].mean().reset_index()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.lineplot(x="season", y="cnt", data=season_hourly, marker="o", palette=palette, ax=ax2)
    ax2.set_title("Average Rentals by Season (Hourly Data)", fontsize=12)
    ax2.set_xlabel("Season")
    ax2.set_ylabel("Average Rentals")
    st.pyplot(fig2)

# Question 2: Weather vs Rentals
st.subheader("Impact of Weather on Rentals")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.boxplot(x="weathersit", y="cnt", data=filtered_day_data, palette=palette, ax=ax3)
    ax3.set_title("Rentals by Weather Condition (Daily Data)", fontsize=12)
    ax3.set_xlabel("Weather Condition")
    ax3.set_ylabel("Rental Count")
    st.pyplot(fig3)

with row2_col2:
    weather_hourly = filtered_hour_data.groupby("weathersit")["cnt"].mean().reset_index()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    sns.barplot(x="weathersit", y="cnt", data=weather_hourly, palette=palette, ax=ax4)
    ax4.set_title("Average Rentals by Weather Condition (Hourly Data)", fontsize=12)
    ax4.set_xlabel("Weather Condition")
    ax4.set_ylabel("Average Rentals")
    st.pyplot(fig4)

# Question 3: Hourly Patterns
# Hourly Rentals: Working Days vs Holidays
st.header("Hourly Rentals: Working Days vs Holidays")
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=filtered_hour_data, x='hr', y='cnt', hue='workingday', ax=ax, ci=None)
ax.set_title("Hourly Rentals: Working Days vs Holidays")
ax.set_xlabel("Hour")
ax.set_ylabel("Number of Rentals")
st.pyplot(fig)

# Heatmap of Hourly Rentals
st.header("Heatmap of Hourly Rentals")
pivot_data = filtered_hour_data.pivot_table(index='hr', columns='weekday', values='cnt', aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot_data, cmap="YlGnBu", annot=True, fmt=".1f", ax=ax)
ax.set_title("Heatmap of Hourly Rentals")
ax.set_xlabel("Weekday")
ax.set_ylabel("Hour")
st.pyplot(fig)

# Question 4: Casual vs Registered Users
st.subheader("Hourly Casual vs Registered Users")
row4_col1, row4_col2 = st.columns(2)

# Calculate average users by type and hour grouped by working day
casual_registered_summary = filtered_hour_data.groupby(['workingday', 'hr'])[['casual', 'registered']].mean().reset_index()

# Visualization in Streamlit
with row4_col1:
    st.markdown("**Hourly User Patterns by Type (Casual vs Registered)**")

    # Create a figure and axes for the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Loop through user types and working day categories for plotting
    for user_type in ['casual', 'registered']:
        for working_day in [0, 1]:  # 0 for holiday, 1 for working day
            subset = casual_registered_summary[casual_registered_summary['workingday'] == working_day]
            ax.plot(
                subset['hr'],
                subset[user_type],
                marker='o',
                label=f'{user_type.capitalize()} - {"Holiday" if working_day == 0 else "Working Day"}'
            )

    # Add titles and labels
    ax.set_title("Hourly Patterns of Casual vs Registered Users", fontsize=14)
    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Average User Count", fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.legend(title="User Type / Day Type", fontsize=10)
    ax.grid()

    # Display the plot in Streamlit
    st.pyplot(fig)

with row4_col2:
    st.markdown("**Cumulative Rentals by User Type**")
    fig8, ax8 = plt.subplots(figsize=(6, 4))
    cumulative_user_pattern = filtered_hour_data.groupby(["workingday"])[["casual", "registered"]].sum().reset_index()
    cumulative_user_pattern = pd.melt(cumulative_user_pattern, id_vars=["workingday"], var_name="User Type", value_name="Total Count")
    sns.barplot(data=cumulative_user_pattern, x="workingday", y="Total Count", hue="User Type", palette="viridis", ax=ax8)
    ax8.set_title("Cumulative Rentals by User Type", fontsize=12)
    ax8.set_xlabel("Working Day (0 = Holiday, 1 = Working Day)")
    ax8.set_ylabel("Total Rentals")
    ax8.legend(title="User Type")
    st.pyplot(fig8)

# Closing Remarks
st.markdown("**Insights Summary:**")
st.markdown("""
1. **Seasonal Impact on Bicycle Rentals**  
   - The Fall season records the highest average rentals due to stable, comfortable weather, with a consistent rental trend throughout the week, favored by both casual and registered users.
2. **Weather Impact on Bicycle Rentals**  
   - Clear or partly cloudy weather leads to the highest rentals, while bad weather (heavy rain, snow, or fog) causes a significant drop in rentals. Warm temperatures support higher rentals, while high humidity and strong winds are negatively correlated with rentals.
3. **Rental Patterns Based on Time (Workingday vs Holiday)**  
   - On working days, rental peaks occur during rush hours (07:00–09:00 and 17:00–19:00), reflecting bike usage for commuting. On holidays, the peak is between 11:00–16:00, indicating recreational bike usage.
4. **Casual vs Registered Users**  
   - Registered users dominate rentals on working days, especially during peak hours. Casual users are more active on weekends or holidays, with peak rentals occurring midday to afternoon, suggesting they use bikes more for recreational purposes.
""")
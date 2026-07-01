import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_css():
    with open("dashboard/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

st.html("""
<div class="hero">
    <h1>Netflix Data Analysis Dashboard</h1>
    <p>
        Explore Netflix movies and TV shows through 
        interactive visualizations and business insights.
    </p>
    <div class="tech">
        Python • Pandas • NumPy • Matplotlib • Seaborn • Streamlit
    </div>
</div>
""")

df = pd.read_csv("Data/netflix.csv")

genres = (
    df["listed_in"]
    .str.split(", ")
    .explode()
    .dropna()
    .sort_values()
    .unique()
)

genre_options = ["All"] + list(genres)

selected_genre = st.sidebar.selectbox(
    "Genre",
    genre_options
)

# Clean data for filters
df["country"] = df["country"].fillna("Unknown")
df["listed_in"] = df["listed_in"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Unknown")

st.sidebar.markdown("## Dashboard Filters")
st.sidebar.markdown("---")

type_options = ["All"] + sorted(df["type"].unique().tolist())

selected_type = st.sidebar.selectbox(
    "Type",
    type_options
)

country_options = ["All"] + sorted(df["country"].unique().tolist())

selected_country = st.sidebar.selectbox(
    "Country",
    country_options
)

rating_options = ["All"] + sorted(df["rating"].unique().tolist())

selected_rating = st.sidebar.selectbox(
    "Rating",
    rating_options
)

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())

selected_year = st.sidebar.slider(
    "Release Year",
    min_year,
    max_year,
    (min_year, max_year)
)

filtered_df = df.copy()

if selected_genre != "All":
    filtered_df = filtered_df[
        filtered_df["listed_in"].str.contains(selected_genre, na=False)
    ]
if selected_type != "All":
    filtered_df = filtered_df[
        filtered_df["type"] == selected_type
    ]

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

if selected_rating != "All":
    filtered_df = filtered_df[
        filtered_df["rating"] == selected_rating
    ]

filtered_df = filtered_df[
    (filtered_df["release_year"] >= selected_year[0]) &
    (filtered_df["release_year"] <= selected_year[1])
]

col1, col2, col3, col4 = st.columns(4)

total_titles = len(df)
movies = (df["type"] == "Movie").sum()
tv_shows = (df["type"] == "TV Show").sum()
countries = (
    df["country"]
    .dropna()
    .str.split(", ")
    .explode()
    .nunique()
)

col1, col2, col3, col4 = st.columns(4)

st.html(f"""
<div class="kpi-container">

    <div class="kpi-card">
        <div class="kpi-title">🎬 Total Titles</div>
        <div class="kpi-value">{total_titles:,}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">🎥 Movies</div>
        <div class="kpi-value">{movies:,}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">📺 TV Shows</div>
        <div class="kpi-value">{tv_shows:,}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">🌍 Countries</div>
        <div class="kpi-value">{countries:,}</div>
    </div>

</div>
""")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# LOAD CSS
def load_css():
    with open("dashboard/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# HERO SECTION
st.html("""
<div class="hero">
    <h1>Netflix Data Analysis Dashboard</h1>
    <p>
        Explore Netflix movies and TV shows through 
        interactive visualizations and business insights.
    </p>
</div>
""")

# LOAD DATA
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

# DATA PREPARATION
df["country"] = df["country"].fillna("Unknown")
df["listed_in"] = df["listed_in"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Unknown")

# SIDEBAR FILTERS
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

# APPLY FILTERS
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

if filtered_df.empty:
    st.warning("No titles match the selected filters. Please choose different filters.")
    st.stop()

# KPI CALCULATIONS
total_titles = len(filtered_df)

movies = (filtered_df["type"] == "Movie").sum()

tv_shows = (filtered_df["type"] == "TV Show").sum()

countries = (
    filtered_df["country"]
    .str.split(", ")
    .explode()
    .nunique()
)

col1, col2, col3, col4 = st.columns(4)

# CHART DATA
top_countries = (
    filtered_df["country"]
    .str.split(", ")
    .explode()
    .value_counts()
    .head(10)
)

top_genres = (
    filtered_df["listed_in"]
    .str.split(", ")
    .explode()
    .value_counts()
    .head(10)
)

year_counts = (
    filtered_df["release_year"]
    .value_counts()
    .sort_index()
)

rating_counts = (
    filtered_df["rating"]
    .value_counts()
)

director_counts = (
    filtered_df["director"]
    .dropna()
    .str.split(", ")
    .explode()
    .value_counts()
    .head(10)
)

movie_duration = (
    filtered_df[filtered_df["type"] == "Movie"]["duration"]
    .str.replace(" min", "", regex=False)
)

movie_duration = pd.to_numeric(
    movie_duration,
    errors="coerce"
).dropna()

month_order = [
    "January","February","March","April",
    "May","June","July","August",
    "September","October","November","December"
]

month_counts = (
    filtered_df["date_added"]
    .dropna()
    .str.split()
    .str[0]
    .value_counts()
    .reindex(month_order)
)

# KPI CARDS
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

# DASHBOARD CHARTS
col1, col2, col3 = st.columns(3)

# Movies
with col1:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Movies vs TV Shows
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    sns.countplot(
        data=filtered_df,
        x="type",
        hue="type",
        palette="viridis",
        legend=False,
        ax=ax
    )

    ax.set_title("Distribution of Movies and TV Shows", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("Count")

    for container in ax.containers:
        ax.bar_label(container, fontsize=8)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)
# Countries
with col2:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Top Countries
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    sns.barplot(
        x=top_countries.values,
        y=top_countries.index,
        hue=top_countries.index,
        palette="viridis",
        legend=False,
        ax=ax
    )

    ax.set_title("Top Countries", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("")

    for container in ax.containers:
        ax.bar_label(container, fontsize=7)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)
# Genres
with col3:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Top Genres
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    sns.barplot(
        x=top_genres.values,
        y=top_genres.index,
        hue=top_genres.index,
        palette="viridis",
        legend=False,
        ax=ax
    )

    ax.set_title("Top Genres", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("")

    for container in ax.containers:
        ax.bar_label(container, fontsize=7)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

# Ratings
with col4:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Ratings Distribution
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    sns.barplot(
        x=rating_counts.values,
        y=rating_counts.index,
        hue=rating_counts.index,
        palette="viridis",
        legend=False,
        ax=ax
    )

    ax.set_title("Ratings", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("")

    for container in ax.containers:
        ax.bar_label(container, fontsize=7)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)
# Growth
with col5:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Netflix Growth
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    sns.lineplot(
        x=year_counts.index,
        y=year_counts.values,
        marker="o",
        ax=ax
    )

    ax.set_title("Release Year", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("Titles")

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)
# Duration
with col6:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Movie Duration
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(4,3))

    ax.hist(
        movie_duration,
        bins=25,
        edgecolor="black"
    )

    ax.axvline(
        movie_duration.mean(),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Average = {movie_duration.mean():.0f} min"
    )

    ax.set_title("Movie Duration", fontsize=11)
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Movies")

    ax.legend(fontsize=7)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

col7, col8 = st.columns(2)

# Month Added
with col7:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Month Added
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(5,3))

    sns.lineplot(
        x=month_counts.index,
        y=month_counts.values,
        marker="o",
        linewidth=2,
        ax=ax
    )

    ax.set_title("Content Added by Month", fontsize=11)

    plt.xticks(rotation=45)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)
# Directors
with col8:

    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">
            Top Directors
        </div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(5,3))

    sns.barplot(
        x=director_counts.values,
        y=director_counts.index,
        hue=director_counts.index,
        palette="viridis",
        legend=False,
        ax=ax
    )

    ax.set_title("Top Directors", fontsize=11)
    ax.set_xlabel("")
    ax.set_ylabel("")

    for container in ax.containers:
        ax.bar_label(container, fontsize=7)

    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

#FOOTER
st.markdown("---")

st.markdown("""
<div class="footer">
    <p><strong>Created by Hiba Eman</strong></p>
    <p>
        Built with Python • Pandas • NumPy • Matplotlib • Seaborn • Streamlit
    </p>
    <p>© 2026 Netflix Data Analysis Dashboard</p>
</div>
""", unsafe_allow_html=True)

hide_style = """
    <style>
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)
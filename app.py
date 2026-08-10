import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
db_url = os.getenv("DATABASE_URL")

# Page config
st.set_page_config(page_title="Tech Skills Monitor", layout="wide", initial_sidebar_state="collapsed")

# Connect to DB
@st.cache_resource
def get_engine():
    return create_engine(db_url)

engine = get_engine()

# ========== QUERIES ==========

# Query: Top 10 skills by job count
@st.cache_data(ttl=3600)
def get_top_skills(limit=10):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT skill_name, COUNT(DISTINCT job_id) as job_count
            FROM job_skills
            GROUP BY skill_name
            ORDER BY job_count DESC
            LIMIT {limit}
        """))
        return pd.DataFrame(result.fetchall(), columns=['skill_name', 'job_count'])

# Query: Skills with job counts
@st.cache_data(ttl=3600)
def get_skills_counts():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
              js.skill_name,
              COUNT(DISTINCT js.job_id) as job_count
            FROM job_skills js
            GROUP BY js.skill_name
            ORDER BY job_count DESC
        """))
        return pd.DataFrame(result.fetchall(), columns=['skill_name', 'job_count'])

# Query: Get all unique skills
@st.cache_data(ttl=3600)
def get_all_skills():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT skill_name
            FROM job_skills
            ORDER BY skill_name
        """))
        return [row[0] for row in result.fetchall()]

# Query: Get all categories
@st.cache_data(ttl=3600)
def get_all_categories():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT category
            FROM skills
            WHERE category IS NOT NULL
            ORDER BY category
        """))
        return [row[0] for row in result.fetchall()]

# Query: Get all tags
@st.cache_data(ttl=3600)
def get_all_tags():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT unnest(tags) as tag
            FROM skills
            ORDER BY tag
        """))
        return sorted([row[0] for row in result.fetchall()])

# Query: Get metadata
@st.cache_data(ttl=3600)
def get_metadata():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
              COUNT(DISTINCT job_id) as total_jobs,
              MAX(skill_extraction_date) as last_ingestion
            FROM jobs
            WHERE skill_extraction_date IS NOT NULL
        """))
        row = result.fetchone()
        return {
            'total_jobs': row[0] or 0,
            'last_ingestion': row[1]
        }

# Query: Skills co-occurring with a selected skill
@st.cache_data(ttl=3600)
def get_cooccurring_skills(selected_skill):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT js2.skill_name, COUNT(DISTINCT js2.job_id) as job_count
            FROM job_skills js1
            JOIN job_skills js2 ON js1.job_id = js2.job_id
            WHERE js1.skill_name = '{selected_skill}'
            AND js2.skill_name != '{selected_skill}'
            GROUP BY js2.skill_name
            ORDER BY job_count DESC
            LIMIT 15
        """))
        return pd.DataFrame(result.fetchall(), columns=['skill_name', 'job_count'])

# Query: Skills by category
@st.cache_data(ttl=3600)
def get_skills_by_category(category):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT js.skill_name, COUNT(DISTINCT js.job_id) as job_count
            FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            WHERE s.category = '{category}'
            GROUP BY js.skill_name
            ORDER BY job_count DESC
            LIMIT 15
        """))
        return pd.DataFrame(result.fetchall(), columns=['skill_name', 'job_count'])

# Query: Tag co-occurrence (tags that appear with selected tags)
@st.cache_data(ttl=3600)
def get_tag_cooccurrence(tags_list):
    if not tags_list:
        return pd.DataFrame(columns=['tag', 'co_occurrence_count'])

    tags_placeholder = ','.join([f"'{tag}'" for tag in tags_list])
    exclude_tags = ','.join([f"'{tag}'" for tag in tags_list])

    with engine.connect() as conn:
        result = conn.execute(text(f"""
            WITH tags_expanded AS (
              SELECT
                js.job_id,
                unnest(s.tags) as tag
              FROM job_skills js
              JOIN skills s ON js.skill_id = s.skill_id
              WHERE s.tags && ARRAY[{tags_placeholder}]::text[]
            )
            SELECT
              tag,
              COUNT(DISTINCT job_id) as co_occurrence_count
            FROM tags_expanded
            WHERE tag NOT IN ({exclude_tags})
            GROUP BY tag
            ORDER BY co_occurrence_count DESC
            LIMIT 20
        """))
        return pd.DataFrame(result.fetchall(), columns=['tag', 'co_occurrence_count'])

# ========== LAYOUT ==========

# Process banner (centered)
col_title = st.columns([1])[0]
st.markdown("<h1 style='text-align: center;'>📊 Tech Skills Monitor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Track what skills employers actually demand in data roles</i></p>", unsafe_allow_html=True)


# Process flow diagram
process_text = "|| HTML Job Offers (Indeed)  ||  ----> || Parse html files (BeautifulSoup) || ----> || Store (Supabase) || ---->  || Extract Skills (Regex)  ||  ---->  || Data Visuals (Streamlit) ||"
st.caption(process_text)


# Display Metadata
metadata = get_metadata()
last_ingestion_str = metadata['last_ingestion'].strftime('%Y-%m-%d %H:%M') if metadata['last_ingestion'] else 'Never'
metadata_text = f"**Data source:** Indeed.com | **Jobs ingested:** {metadata['total_jobs']} | **Last ingestion:** {last_ingestion_str}"
st.caption(metadata_text)


# SECTION 1: Top 10 Skills (Centered, Full Width)
st.subheader("🔥 Top 10 Most Demanded Skills")

skills_df = get_top_skills(10)

if len(skills_df) > 0:
    fig_top = go.Figure()
    fig_top.add_trace(go.Bar(
        y=skills_df['skill_name'],
        x=skills_df['job_count'],
        orientation='h',
        marker=dict(
            color=skills_df['job_count'],
            colorscale='Blues',
            showscale=False,
        ),
        text=skills_df['job_count'],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Jobs: %{x}<extra></extra>',
    ))

    fig_top.update_layout(
        xaxis_title='Number of Jobs',
        yaxis_title='',
        height=350,
        margin=dict(l=150, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False,
    )
    fig_top.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)')

    st.plotly_chart(fig_top, use_container_width=True)

# SECTION 2: Skills Treemap
st.divider()
st.subheader("🌳 Skills Distribution")

skills_df = get_skills_counts()

if len(skills_df) > 0:
    # Build treemap structure: root node → skills only (no tags)
    labels = ['Skills'] + skills_df['skill_name'].tolist()
    parents = [''] + ['Skills'] * len(skills_df)
    values = [1] + skills_df['job_count'].tolist()  # Root value = 1 to minimize its space

    fig_treemap = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colorscale='Blues',
            cmid=skills_df['job_count'].median(),
        ),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
        textposition='middle center',
    ))

    fig_treemap.update_layout(
        height=700,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        showlegend=False,
    )

    st.plotly_chart(fig_treemap, use_container_width=True)
else:
    st.info("No skills data available")

# SECTION 3: Skill Selector
st.divider()
st.subheader("🔗 Skills by Skill Co-occurrence")

all_skills = get_all_skills()
selected_skill = st.selectbox("Select a skill:", all_skills, key='skill_selector')

if selected_skill:
    cooc_df = get_cooccurring_skills(selected_skill)

    if len(cooc_df) > 0:
        # Reverse order so most common appears at top
        cooc_df = cooc_df.iloc[::-1].reset_index(drop=True)

        fig_cooc = go.Figure()
        fig_cooc.add_trace(go.Bar(
            y=cooc_df['skill_name'],
            x=cooc_df['job_count'],
            orientation='h',
            marker=dict(color='rgba(70, 130, 180, 0.8)'),
            text=cooc_df['job_count'],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Jobs: %{x}<extra></extra>',
        ))

        fig_cooc.update_layout(
            title=f"Skills that appear with {selected_skill}",
            xaxis_title='Number of Jobs',
            yaxis_title='',
            height=400,
            margin=dict(l=150, r=20, t=60, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11),
            showlegend=False,
        )
        fig_cooc.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)')

        st.plotly_chart(fig_cooc, use_container_width=True)
    else:
        st.info("No co-occurring skills found")

# SECTION 4: Category Selector
st.divider()
st.subheader("📂 Skills by Category")

all_categories = get_all_categories()
selected_category = st.selectbox("Select a category:", all_categories, key='category_selector')

if selected_category:
    cat_df = get_skills_by_category(selected_category)

    if len(cat_df) > 0:
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            y=cat_df['skill_name'],
            x=cat_df['job_count'],
            orientation='h',
            marker=dict(color='rgba(60, 179, 113, 0.8)'),
            text=cat_df['job_count'],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Jobs: %{x}<extra></extra>',
        ))

        fig_cat.update_layout(
            title=f"Skills in {selected_category} category",
            xaxis_title='Number of Jobs',
            yaxis_title='',
            height=400,
            margin=dict(l=150, r=20, t=60, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11),
            showlegend=False,
        )
        fig_cat.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)')

        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No skills found in this category")

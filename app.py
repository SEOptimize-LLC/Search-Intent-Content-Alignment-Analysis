import streamlit as st
import pandas as pd
import time
from utils.data_processing import load_gsc_data, load_crawl_data, merge_data
from utils.serp_analysis import fetch_serp_data, extract_serp_features
from utils.content_scraping import scrape_content
from utils.llm_analysis import analyze_intent_with_llm

st.set_page_config(page_title="Search Intent & Content Alignment Analyzer", layout="wide")

st.title("Search Intent & Content Alignment Analyzer")
st.markdown("""
This tool automates the analysis of your content's alignment with search intent.
1. Upload your **GSC Performance Report** (Pages, Queries, Clicks, Impressions, Position).
2. Upload your **Screaming Frog Internal HTML Report**.
3. The tool will fetch live SERP data, scrape your content, and use AI to audit alignment.
""")

# --- Sidebar: Configuration ---
st.sidebar.header("Configuration")

# API Keys (from Secrets or Input)
try:
    serper_api_key = st.secrets["SERPER_API_KEY"]
except:
    serper_api_key = st.sidebar.text_input("Serper.dev API Key", type="password")

try:
    firecrawl_api_key = st.secrets["FIRECRAWL_API_KEY"]
except:
    firecrawl_api_key = st.sidebar.text_input("Firecrawl API Key", type="password")

# Model Selection
model_provider = st.sidebar.selectbox("Select AI Provider", ["OpenAI", "Anthropic", "Google", "xAI"])

if model_provider == "OpenAI":
    model_options = ["gpt-4o", "gpt-4-turbo"]
    try:
        llm_api_key = st.secrets["OPENAI_API_KEY"]
    except:
        llm_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
elif model_provider == "Anthropic":
    model_options = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"]
    try:
        llm_api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        llm_api_key = st.sidebar.text_input("Anthropic API Key", type="password")
elif model_provider == "Google":
    model_options = ["gemini-1.5-pro", "gemini-1.5-flash"]
    try:
        llm_api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        llm_api_key = st.sidebar.text_input("Google API Key", type="password")
elif model_provider == "xAI":
    model_options = ["grok-beta"] # Placeholder model name
    try:
        llm_api_key = st.secrets["XAI_API_KEY"]
    except:
        llm_api_key = st.sidebar.text_input("xAI API Key", type="password")

selected_model = st.sidebar.selectbox("Select Model", model_options)

# --- Main Content: File Uploads ---
col1, col2 = st.columns(2)

with col1:
    gsc_file = st.file_uploader("Upload GSC Report (CSV/Excel)", type=['csv', 'xlsx'])

with col2:
    crawl_file = st.file_uploader("Upload Crawl Report (CSV/Excel)", type=['csv', 'xlsx'])

if gsc_file and crawl_file:
    st.info("Files uploaded. Processing data...")
    
    gsc_df = load_gsc_data(gsc_file)
    crawl_df = load_crawl_data(crawl_file)
    
    if gsc_df is not None and crawl_df is not None:
        merged_df = merge_data(gsc_df, crawl_df)
        
        if merged_df is not None:
            st.success(f"Successfully merged data! Found {len(merged_df)} URLs.")
            
            # Filter options
            min_impressions = st.slider("Minimum Impressions Filter", 0, 1000, 100)
            filtered_df = merged_df[merged_df['Impressions'] >= min_impressions].copy()
            
            st.dataframe(filtered_df.head())
            
            if st.button("Start Analysis"):
                if not (serper_api_key and firecrawl_api_key and llm_api_key):
                    st.error("Please provide all necessary API keys.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    total_rows = len(filtered_df)
                    
                    for index, row in filtered_df.iterrows():
                        status_text.text(f"Analyzing {index + 1}/{total_rows}: {row['URL']}")
                        
                        # 1. Fetch SERP Data
                        query = row['Top queries']
                        serp_data = fetch_serp_data(query, serper_api_key)
                        
                        # 2. Scrape Content
                        content = scrape_content(row['URL'], firecrawl_api_key)
                        
                        # 3. LLM Analysis
                        analysis = analyze_intent_with_llm(row, serp_data, content, selected_model, llm_api_key)
                        
                        # Combine results
                        row_result = row.to_dict()
                        row_result.update(analysis)
                        results.append(row_result)
                        
                        progress_bar.progress((index + 1) / total_rows)
                        
                    # Final DataFrame
                    final_df = pd.DataFrame(results)
                    
                    st.success("Analysis Complete!")
                    st.dataframe(final_df)
                    
                    # Download Button
                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Analysis Report",
                        csv,
                        "intent_analysis_report.csv",
                        "text/csv",
                        key='download-csv'
                    )
        else:
            st.error("Failed to merge data. Please check column names.")
    else:
        st.error("Error loading files.")

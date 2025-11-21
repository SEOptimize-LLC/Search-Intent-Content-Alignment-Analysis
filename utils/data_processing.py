import pandas as pd
import io

def normalize_columns(df):
    """
    Normalizes column names to standard formats.
    Specifically looks for URL-like columns and renames them to 'URL'.
    """
    df.columns = [c.strip() for c in df.columns]
    
    url_variations = ['Address', 'Landing Page', 'Page', 'url', 'link', 'Permalink']
    
    for col in df.columns:
        if col.lower() == 'url':
            return df # Already has URL column
        for var in url_variations:
            if col.lower() == var.lower():
                df.rename(columns={col: 'URL'}, inplace=True)
                return df
    return df

def load_gsc_data(file):
    """
    Loads GSC data from a CSV or Excel file.
    Expects columns like 'Top queries', 'Impressions', 'Clicks', 'CTR', 'Position'.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        df = normalize_columns(df)
        return df
    except Exception as e:
        return None, str(e)

def load_crawl_data(file):
    """
    Loads Screaming Frog (or similar) crawl data.
    Expects columns like 'Address', 'H1-1', 'Title 1', 'Word Count', etc.
    """
    try:
        if file.name.endswith('.csv'):
            # Screaming Frog CSVs often skip the first row or have specific headers
            # We'll try standard read first
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        df = normalize_columns(df)
        return df
    except Exception as e:
        return None, str(e)

def merge_data(gsc_df, crawl_df):
    """
    Merges GSC and Crawl data on the 'URL' column.
    """
    if 'URL' not in gsc_df.columns:
        return None, "GSC data missing 'URL' column (or equivalent)."
    if 'URL' not in crawl_df.columns:
        return None, "Crawl data missing 'URL' column (or equivalent)."
    
    # Ensure URLs are strings and stripped
    gsc_df['URL'] = gsc_df['URL'].astype(str).str.strip()
    crawl_df['URL'] = crawl_df['URL'].astype(str).str.strip()
    
    # Merge
    merged_df = pd.merge(gsc_df, crawl_df, on='URL', how='left')
    
    return merged_df
import pandas as pd
import io

def normalize_columns(df):
    """
    Normalizes column names to standard formats.
    Specifically looks for URL-like columns and renames them to 'URL'.
    """
    df.columns = [c.strip() for c in df.columns]
    
    url_variations = ['Address', 'Landing Page', 'Page', 'url', 'link', 'Permalink']
    
    # Map for other common GSC columns
    column_mapping = {
        'impressions': 'Impressions',
        'total impressions': 'Impressions',
        'clicks': 'Clicks',
        'total clicks': 'Clicks',
        'ctr': 'CTR',
        'average ctr': 'CTR',
        'position': 'Position',
        'average position': 'Position',
        'avg. pos': 'Position',
        'avg. position': 'Position',
        'top queries': 'Top queries',
        'query': 'Top queries',
        'queries': 'Top queries',
        'keyword': 'Top queries',
        'keywords': 'Top queries'
    }

    new_columns = {}
    for col in df.columns:
        col_lower = col.lower()
        
        # Check for URL variations
        if col_lower == 'url':
            new_columns[col] = 'URL'
            continue
            
        found_url = False
        for var in url_variations:
            if col_lower == var.lower():
                new_columns[col] = 'URL'
                found_url = True
                break
        if found_url:
            continue

        # Check for other mappings
        if col_lower in column_mapping:
            new_columns[col] = column_mapping[col_lower]
    
    if new_columns:
        df.rename(columns=new_columns, inplace=True)
    
    # Drop empty "Unnamed" columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
    return df

def clean_numeric_columns(df):
    """
    Cleans numeric columns by removing commas and converting to float/int.
    """
    numeric_cols = ['Impressions', 'Clicks', 'CTR', 'Position']
    
    for col in numeric_cols:
        if col in df.columns:
            # Remove commas, %, and handle "No data"
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('%', '')
                df[col] = df[col].replace('No data', pd.NA)
            
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def load_gsc_data(file):
    """
    Loads GSC data from a CSV or Excel file.
    Expects columns like 'Top queries', 'Impressions', 'Clicks', 'CTR', 'Position'.
    """
    try:
        if file.name.endswith('.csv'):
            # List of encodings to try
            encodings = ['utf-8', 'utf-16', 'latin-1']
            
            for encoding in encodings:
                try:
                    file.seek(0)
                    # Try reading with default comma separator
                    df = pd.read_csv(file, encoding=encoding, on_bad_lines='skip')
                    
                    if len(df.columns) <= 1:
                        # If only one column, try semicolon separator
                        file.seek(0)
                        df = pd.read_csv(file, sep=';', encoding=encoding, on_bad_lines='skip')
                    
                    # If we successfully read a dataframe with columns, break
                    if len(df.columns) > 1:
                        break
                except:
                    continue
            else:
                # If all encodings fail, try python engine as last resort
                file.seek(0)
                df = pd.read_csv(file, engine='python', on_bad_lines='skip')

        else:
            df = pd.read_excel(file)
            
        df = normalize_columns(df)
        df = clean_numeric_columns(df)
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
    
    # Drop conflicting performance columns from crawl data to avoid _x/_y suffixes
    # We prioritize GSC data for these metrics
    conflicting_cols = ['Impressions', 'Clicks', 'CTR', 'Position', 'Top queries']
    cols_to_drop = [col for col in conflicting_cols if col in crawl_df.columns]
    if cols_to_drop:
        crawl_df = crawl_df.drop(columns=cols_to_drop)
    
    # Merge
    merged_df = pd.merge(gsc_df, crawl_df, on='URL', how='left')
    
    return merged_df
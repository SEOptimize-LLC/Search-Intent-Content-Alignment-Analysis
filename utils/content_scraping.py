import requests
import json
import time

def scrape_content(url, api_key):
    """
    Scrapes content using Firecrawl API.
    """
    api_url = "https://api.firecrawl.dev/v0/scrape"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": True
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', {}).get('markdown', '')
            else:
                return f"Error: {data.get('error', 'Unknown error')}"
        elif response.status_code == 429:
            return "Error: Rate limit exceeded"
        else:
            return f"Error: HTTP {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def batch_scrape(urls, api_key, delay=1):
    """
    Scrapes a list of URLs with a delay to respect rate limits.
    """
    results = {}
    for url in urls:
        content = scrape_content(url, api_key)
        results[url] = content
        time.sleep(delay)
    return results
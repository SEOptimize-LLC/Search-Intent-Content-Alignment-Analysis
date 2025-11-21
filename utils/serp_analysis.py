import requests
import json

def fetch_serp_data(query, api_key):
    """
    Fetches SERP data from Serper.dev.
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": 10,
        "gl": "us", # Default to US, could be parameterized
        "hl": "en"
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def extract_serp_features(serp_data):
    """
    Extracts key features from the SERP response to help determine intent.
    """
    features = []
    
    if "error" in serp_data:
        return ["Error fetching SERP"]

    if "answerBox" in serp_data:
        features.append("Featured Snippet")
    
    if "peopleAlsoAsk" in serp_data:
        features.append("People Also Ask")
        
    if "knowledgeGraph" in serp_data:
        features.append("Knowledge Graph")
        
    if "shopping" in serp_data:
        features.append("Shopping Carousel")
        
    if "places" in serp_data:
        features.append("Local Pack")
        
    if "images" in serp_data:
        features.append("Image Pack")
        
    if "videos" in serp_data:
        features.append("Video Carousel")
        
    organic = serp_data.get("organic", [])
    
    # Check for review stars in organic results (Commercial Investigation signal)
    has_reviews = any("rating" in result for result in organic[:5])
    if has_reviews:
        features.append("Review Stars")

    return features

def get_top_competitors(serp_data, limit=3):
    """
    Returns the URLs of the top organic competitors.
    """
    if "error" in serp_data:
        return []
        
    organic = serp_data.get("organic", [])
    return [result.get("link") for result in organic[:limit]]
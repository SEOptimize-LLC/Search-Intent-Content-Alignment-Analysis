import openai
import json

def analyze_intent_with_llm(row, serp_data, content, model_choice, api_key):
    """
    Analyzes intent and content alignment using the selected LLM via OpenRouter.
    """
    
    prompt = f"""
    You are a Senior SEO Strategist. Analyze the following data to determine search intent and content alignment.

    **Target URL:** {row.get('URL', 'N/A')}
    **Top Query:** {row.get('Top queries', 'N/A')}
    **Current Position:** {row.get('Position', 'N/A')}
    **CTR:** {row.get('CTR', 'N/A')}
    
    **SERP Data (Top Results & Features):**
    {json.dumps(serp_data, indent=2)}

    **Page Content (Markdown):**
    {content[:3000]}... (truncated)

    **Task:**
    1. Determine the **Target Intent (Hypothesis)** based on the query.
    2. Determine the **Actual SERP Intent** based on the SERP results (e.g., Know Simple, Know Complex, Do, Commercial Investigation).
    3. Identify the **Content Format** required by the SERP (e.g., Listicle, Product Page, Calculator).
    4. Assess **SERP Feature Presence** (what features are triggering?).
    5. Recommend an **Action Status** (Keep, Optimize, Consolidate, Prune).
    
    **Output Format:**
    Return ONLY a JSON object with these keys:
    {{
        "Target Intent (Hypothesis)": "...",
        "Actual SERP Intent": "...",
        "Content Format": "...",
        "SERP Feature Presence": "...",
        "Action Status": "...",
        "Analysis Notes": "Brief explanation of the decision."
    }}
    """

    try:
        # OpenRouter uses the OpenAI SDK structure
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": "You are an SEO expert. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            extra_headers={
                "HTTP-Referer": "https://streamlit.io/", # Optional: For OpenRouter rankings
                "X-Title": "Search Intent Analyzer", # Optional: For OpenRouter rankings
            }
        )
        
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "Target Intent (Hypothesis)": "Error",
            "Actual SERP Intent": "Error",
            "Content Format": "Error",
            "SERP Feature Presence": "Error",
            "Action Status": "Error",
            "Analysis Notes": str(e)
        }
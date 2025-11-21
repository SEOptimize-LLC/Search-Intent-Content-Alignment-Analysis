import openai
import anthropic
import google.generativeai as genai
import json

def analyze_intent_with_llm(row, serp_data, content, model_choice, api_key):
    """
    Analyzes intent and content alignment using the selected LLM.
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
        if "gpt" in model_choice:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)

        elif "claude" in model_choice:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model_choice,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Extract JSON from Claude's response (which might contain text)
            content_text = response.content[0].text
            start = content_text.find('{')
            end = content_text.rfind('}') + 1
            return json.loads(content_text[start:end])

        elif "gemini" in model_choice:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            response = model.generate_content(prompt)
            # Clean up markdown code blocks if present
            text = response.text.replace('```json', '').replace('```', '')
            return json.loads(text)
            
        # Placeholder for xAI (Grok) - assuming OpenAI-compatible API structure
        elif "grok" in model_choice:
             # xAI API structure is often similar to OpenAI, but endpoint differs.
             # For now, we'll treat it as a generic OpenAI-compatible client if base_url was provided,
             # but since we don't have a specific SDK, we'll skip or mock.
             # User asked to include it, so we'll add a placeholder or use OpenAI client with base_url if known.
             # Assuming standard OpenAI client for now with specific model name.
             client = openai.OpenAI(
                 api_key=api_key, 
                 base_url="https://api.x.ai/v1" 
             )
             response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
             return json.loads(response.choices[0].message.content)

        else:
            return {"error": "Unsupported model selected"}

    except Exception as e:
        return {
            "Target Intent (Hypothesis)": "Error",
            "Actual SERP Intent": "Error",
            "Content Format": "Error",
            "SERP Feature Presence": "Error",
            "Action Status": "Error",
            "Analysis Notes": str(e)
        }
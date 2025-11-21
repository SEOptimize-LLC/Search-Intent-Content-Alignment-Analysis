# Search Intent & Content Alignment Analyzer

This Streamlit application automates the process of auditing your content against search intent. It combines data from Google Search Console (GSC) and Screaming Frog, fetches live SERP data, scrapes your content, and uses advanced LLMs (via OpenRouter) to provide actionable recommendations.

## Features

*   **Data Merging:** Automatically merges GSC performance data with Screaming Frog crawl data.
*   **Live SERP Analysis:** Uses Serper.dev to fetch real-time search results and features.
*   **Content Scraping:** Uses Firecrawl to extract clean markdown content from your URLs.
*   **AI-Powered Audit:** Leverages **OpenRouter** to access top-tier models like GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, and more for intent analysis.
*   **Actionable Output:** Generates a downloadable CSV with specific recommendations (Keep, Optimize, Consolidate, Prune).

## Setup & Installation

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

## Configuration (Secrets)

To run this app, you need to configure your API keys. You can do this via the Streamlit sidebar inputs OR by creating a `.streamlit/secrets.toml` file in the project root for automatic loading.

**Example `.streamlit/secrets.toml`:**

```toml
SERPER_API_KEY = "your_serper_key"
FIRECRAWL_API_KEY = "your_firecrawl_key"
OPENROUTER_API_KEY = "your_openrouter_key"
```

## Usage Guide

1.  **Export GSC Data:**
    *   Go to Google Search Console > Performance.
    *   Select "Pages", "Queries", "Clicks", "Impressions", "CTR", "Position".
    *   Export as CSV/Excel.
2.  **Export Crawl Data:**
    *   Crawl your site with Screaming Frog.
    *   Export the "Internal HTML" report.
3.  **Upload & Analyze:**
    *   Upload both files to the app.
    *   Select your preferred AI model from the OpenRouter list (or enter a custom ID).
    *   Click "Start Analysis".
4.  **Review & Act:**
    *   Download the final report.
    *   Filter by "Action Status" to prioritize your work.

## Project Structure

*   `app.py`: Main Streamlit application.
*   `utils/`: Helper modules for data processing, SERP analysis, scraping, and LLM logic.
*   `requirements.txt`: Python dependencies.
# CartSavvy — AI Shopping Comparison Agent 🛒

CartSavvy is an agentic AI solution that searches, normalizes, and compares product listings across Pakistani e-commerce platforms (Daraz, Telemart, PriceOye, Dvago, Foodpanda, etc.).

## 🚀 Deployment on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New App**, select your GitHub repository and set `app.py` as the Main file path.
4. Go to **Advanced settings** -> **Secrets** and add:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
SERPER_API_KEY = "your_serper_api_key_here" # Optional for live web search

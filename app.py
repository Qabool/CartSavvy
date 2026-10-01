import os
import streamlit as st
from PIL import Image
from crew import run_cartsavvy_crew

# Page Config
st.set_page_config(
    page_title="CartSavvy — AI Shopping Comparison Agent",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling incorporating Brand Palette: #0F6E56, #1D9E75, #FAC775
st.markdown("""
    <style>
    .main-header {
        color: #0F6E56;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #1D9E75;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .summary-card {
        background-color: #F7FAF9;
        border-left: 5px solid #1D9E75;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .badge-value {
        background-color: #FAC775;
        color: #0F6E56;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .stButton>button {
        background-color: #0F6E56 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100%;
        height: 48px;
    }
    .stButton>button:hover {
        background-color: #1D9E75 !important;
    }
    </style>
""", unsafe_allow_html=True)

# API Secret Setup for Groq
if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
    os.environ["GROQ_API_KEY"] = groq_key
    os.environ["OPENAI_API_KEY"] = groq_key  # Backup for OpenAI wrapper compatibility
if "SERPER_API_KEY" in st.secrets:
    os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

# Sidebar - Search Controls
with st.sidebar:
# NEW (Compatible with Streamlit 2026+):
    logo_path = "assets/cartsavvy_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width="stretch")
    else:
        st.title("🛒 CartSavvy")
    
    st.markdown("### Search Preferences")
    city = st.selectbox("Delivery City", ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Faisalabad", "Multan"])
    category = st.selectbox("Category", ["Electronics", "Mobile Phones", "Grocery", "Pharmacy", "Fashion", "Home Appliances"])
    budget_max = st.number_input("Max Budget (PKR)", min_value=0, value=100000, step=5000)
    condition = st.radio("Condition", ["New", "Refurbished", "Any"], index=0)
    
    st.divider()
    st.caption("CartSavvy AI Agent v1.0 | Powered by CrewAI & Gemini")

# Header Section
st.markdown("<h1 class='main-header'>Compare Smart. Buy Right.</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Agentic AI shopping assistant for Pakistani e-commerce platforms</p>", unsafe_allow_html=True)

# Search Input
query = st.text_input("What are you looking for today?", placeholder="e.g., Samsung Galaxy A55 128GB, Dvago Panadol 500mg, or Foodpanda groceries")

if st.button("Find Best Value Deal") and query:
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Missing Gemini API Key. Please add `GEMINI_API_KEY` to your Streamlit secrets.")
    else:
        user_inputs = {
            "query": query,
            "delivery_city": city,
            "category": category,
            "budget_max": budget_max,
            "condition": condition
        }

        with st.spinner("AI agents searching Daraz, Telemart, PriceOye, and local stores..."):
            try:
                data = run_cartsavvy_crew(user_inputs)
                
                # Render AI Summary
                st.markdown("### 🤖 AI Shopping Recommendation")
                summary = data.get("ai_summary", {})
                st.markdown(f"""
                <div class="summary-card">
                    <b>💡 Best Value Pick:</b> {summary.get('best_value', 'N/A')}<br>
                    <b>💰 Lowest Price:</b> {summary.get('best_price', 'N/A')}<br>
                    <b>⚡ Fastest Delivery:</b> {summary.get('fastest_delivery', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

                # Render Warnings if any
                warnings = data.get("warnings", [])
                if warnings:
                    for warn in warnings:
                        st.warning(f"⚠️ {warn}")

                # Render Results Table/Cards
                st.markdown("### 📊 Side-by-Side Comparison")
                results = data.get("results", [])

                if results:
                    cols = st.columns(len(results))
                    for idx, item in enumerate(results):
                        with cols[idx if idx < len(cols) else 0]:
                            st.markdown(f"#### {item.get('platform')}")
                            st.caption(item.get("product_title"))
                            
                            score = item.get('best_value_score', 80)
                            st.markdown(f"Value Score: <span class='badge-value'>{score}/100</span>", unsafe_allow_html=True)
                            
                            st.metric("Total Landed Cost", f"PKR {item.get('total_cost', 0):,}")
                            st.write(f"**Item Price:** PKR {item.get('discounted_price', 0):,}")
                            st.write(f"**Delivery Fee:** PKR {item.get('shipping_fee', 0):,}")
                            st.write(f"**Delivery:** {item.get('delivery_estimate')}")
                            st.write(f"**Seller Rating:** ⭐ {item.get('seller_rating')}")
                            st.write(f"**Warranty:** {item.get('warranty')}")
                            
                            st.link_button(f"View on {item.get('platform')}", item.get("product_url", "#"))
                else:
                    st.info("No explicit listings found matching criteria. Try broadening your query.")

            except Exception as e:
                st.error(f"Error processing your query: {str(e)}")

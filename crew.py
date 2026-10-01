import os
import json
from crewai import Agent, Task, Crew, Process, LLM
from tools import LocalEcommerceSearchTool

def run_cartsavvy_crew(user_input: dict) -> dict:
    # Set up Gemini LLM via CrewAI's native LLM wrapper
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
# NEW (Compatible with Google Gemini API & CrewAI):
    llm = LLM(
        model="gemini/gemini-3.8-flash",
        api_key=gemini_api_key,
        temperature=0.2
    )

    search_tool = LocalEcommerceSearchTool()

    # Agent 1: Product Research & Retrieval Agent
    retriever_agent = Agent(
        role="Pakistani E-Commerce Research Specialist",
        goal="Find and fetch product listings for '{query}' across platforms in Pakistan like Daraz, Telemart, PriceOye, and Dvago.",
        backstory=(
            "You are an expert e-commerce research agent specialized in navigating Pakistani online markets. "
            "You accurately extract item specs, prices in PKR, seller trust ratings, and delivery terms."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    # Agent 2: Comparison & Recommendation Agent
    analyzer_agent = Agent(
        role="CartSavvy Best-Value Analyst",
        goal="Analyze prices, shipping fees, seller ratings, and warranty to calculate Best-Value scores and generate comparison outputs.",
        backstory=(
            "You are a savvy shopping advisor for Pakistani consumers. You calculate the true landed cost (Price + Shipping), "
            "evaluate seller authenticity, flag potential fake discounts, and rank options strictly by user utility."
        ),
        llm=llm,
        verbose=True
    )

    # Task 1: Fetch listings
    research_task = Task(
        description=(
            "Search for the product: '{query}'. "
            "Target delivery city: {delivery_city}. "
            "Budget constraint: {budget_max} PKR. "
            "Fetch listings using the Local E-Commerce Search Tool."
        ),
        expected_output="Raw normalized JSON list containing product listings from at least 3 platforms.",
        agent=retriever_agent
    )

    # Task 2: Synthesize structured JSON output
    analysis_task = Task(
        description=(
            "Analyze the retrieved listings for '{query}' and return a structured JSON response with the following keys:\n"
            "1. 'ai_summary': A clear plain-language recommendation covering best price, fastest delivery, and best overall value.\n"
            "2. 'results': A list of objects containing:\n"
            "   - 'platform', 'product_title', 'listed_price', 'discounted_price', 'shipping_fee', 'total_cost', "
            "     'delivery_estimate', 'seller_rating', 'warranty', 'authenticity_badge', 'best_value_score' (0-100), 'product_url'\n"
            "3. 'warnings': Array of warning strings (e.g., missing warranty, high shipping fee, unverified seller).\n"
            "Respond ONLY with valid JSON inside a ```json``` code block."
        ),
        expected_output="Valid JSON string matching the CartSavvy response specification.",
        agent=analyzer_agent,
        context=[research_task]
    )

    crew = Crew(
        agents=[retriever_agent, analyzer_agent],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )

    raw_result = crew.kickoff(inputs=user_input)
    
    # Extract JSON string from raw output
    result_text = str(raw_result)
    try:
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text.strip()
        return json.loads(json_str)
    except Exception:
        return {
            "ai_summary": {
                "best_price": "Multiple platforms evaluated",
                "fastest_delivery": "Depends on local stock",
                "best_value": "See itemized listings below"
            },
            "results": [],
            "warnings": ["AI response parsed with fallback rules. Please review raw results."]
        }

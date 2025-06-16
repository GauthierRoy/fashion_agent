import re
from dotenv import load_dotenv
import os
import requests
from markdownify import markdownify
from requests.exceptions import RequestException
from smolagents import (
    tool,
    CodeAgent,
    ToolCallingAgent,
    WebSearchTool,
    # ManagedAgent,
    LiteLLMModel,
)
from pydantic import BaseModel, HttpUrl, Field, ValidationError

#from helpers import ask_user
from agent_conseiller import AgentAdvisor
from price_searcher import get_prices_from_list_product
from agent_product_sheet import ProductSheetAgent
from user_interface import confirm_with_user


def verify_whether_user_likes_product(product_info: str) -> str:
    """Asks the user if they like the product.

    Args:
        product_info: The product to ask the user about.
    Returns:
        True if the user likes the product, False otherwise.
    """
    answer = input(f"Do you like this product? {product_info}\n(yes/no): ")
    return answer.lower().strip()


def main():
    """Main function to run the fashion agent."""

    # 1. Load environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("FATAL: ANTHROPIC_API_KEY environment variable not set.")
        return
    load_dotenv(dotenv_path="fashion_agent/.env")
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # 2. Initialize the LiteLLMModel with the specified model and API key
    model = LiteLLMModel(model="claude-3-haiku-20240307", api_key=api_key)

    # 3. Initialize the agents
    advisor_agent = AgentAdvisor(
        model=model,
        api_key=api_key,
    )

    product_sheet_agent = ProductSheetAgent(model=model, max_results=5)

    # User information
    infos = {
        "name": "jean",
        "age": "36",
        "location": "Paris",
        "size": "m",
        "occasions": "something casual",
        "preferences": "blue, comfortable, and stylish",
        "budget": "40 euro",
    }


    

    print("Starting fashion recommendation pipeline...")

    # Pipeline execution
    max_iterations = 1
    for iteration in range(max_iterations):
        # print(f"\n--- Iteration {iteration + 1} ---")

        # Step 1: Get advice from AgentAdvisor
        print("Step 1: Getting fashion advice...")
        advisor_prompt = f"""Based on the user information:
        Name: {infos["name"]}
        Age: {infos["age"]}
        Location: {infos["location"]}
        Size: {infos["size"]}
        Occasions: {infos["occasions"]}
        Preferences: {infos["preferences"]}
        Budget: {infos["budget"]}
        
        Provide fashion advice and specific product recommendations that would suit this user.
        """

        advisor_output = advisor_agent.run_dialogue()


        product_sheet_output = product_sheet_agent.generate_product_sheets(advisor_output)
        print(f"Product sheet: {product_sheet_output}")

        #Step 3: Get prices for the recommended products
        print("\nStep 3: Finding prices...")
        prices_output = get_prices_from_list_product(product_sheet_output)
        print(f"Price information: {prices_output}")

        #prices_output = [{'name': 'Bulk Unisex T-Shirts Eversoft Cotton Regular Fit', 'price': 36.24, 'url': HttpUrl('https://www.amazon.com/bulk-tshirts-unisex-multiple-sizes/s?k=bulk+tshirts+unisex+multiple+sizes')}]

        print(prices_output)

        urls, feedback = confirm_with_user([str(p['url']) for p in prices_output], 
                          [p['price'] for p in prices_output], 
                          [p['name'] for p in prices_output],
                          [0 for _ in prices_output])


if __name__ == "__main__":
    main()

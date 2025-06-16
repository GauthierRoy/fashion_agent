import os
import asyncio
from typing import Type, List, Dict, Any
from dotenv import load_dotenv

from pydantic import BaseModel, HttpUrl, Field, ValidationError

# Using the corrected import paths
from smolagents import CodeAgent, LiteLLMModel, WebSearchTool, tool, Tool

# --- 1. Pydantic Data Class Definitions (Data Contracts) ---


class ProductNew(BaseModel):
    """Input model: Describes a product we need to search for."""

    name: str
    brand: str
    size: int
    color: str | None = None


class ProductPriceInfo(BaseModel):
    """Output model: The required structure for the final, validated data."""

    name: str = Field(
        description="The full, official name of the product found online."
    )
    price: float = Field(description="The price in euros.")
    url: HttpUrl = Field(
        description="A direct, valid URL to the product's purchase page."
    )


# --- 2. Helper Function: The Tool Factory ---
# This is not a tool itself, but a factory used by our main tool.


def create_pydantic_validator_tool(model_class: Type[BaseModel]) -> Tool:
    """
    A factory that creates a simplified validation Tool for a Pydantic class.
    This version lets the tool raise a Pydantic ValidationError directly upon failure.
    """

    class DynamicValidatorTool(Tool):
        name = f"validate_{model_class.__name__}_tool"

        description = (
            f"Validates a data dictionary against the '{model_class.__name__}' schema. "
            f"On success, it returns the validated data. "
            f"On failure, it will raise a detailed ValidationError that you must use to correct the data."
            f"Example use: {model_class.__name__}(data_to_validate={{{', '.join(model_class.model_fields.keys())}}})"
            f" to validate a dictionary against the {model_class.__name__} model."
        )

        inputs = {
            "data_to_validate": {
                "type": "object",
                "description": f"A Python dictionary to validate against the {model_class.__name__} model.",
            }
        }

        # The output on success is the validated dictionary
        output_type = "object"

        def forward(self, data_to_validate: dict):
            """
            Directly attempts to instantiate the model.
            If validation fails, Pydantic raises a ValidationError, which the agent will catch.
            """
            # No try/except block. Simpler and more direct.
            instance = model_class(**data_to_validate)
            # On success, return the validated data as a dictionary.
            return instance.model_dump()

    return DynamicValidatorTool()


# --- 3. The Orchestrator Tool ---
# Defined as a standalone  function, as you requested.


@tool
def get_prices_from_list_product(products_to_find: list[dict]) -> list[dict]:
    """A tool that takes a list of dict (ProductNew) and finds the best price for each one.

    Args:
        products_to_find: A list of dictionaries representing products to search for. Each dictionary must conform to the ProductNew schema (name, brand, size, color).

    Returns:
        A list of dictionaries, each containing the found product details.
    """
    print("products_to_find:", products_to_find)
    print(f"--- TOOL: Starting  search for {len(products_to_find)} products... ---")

    product_validator_tool = create_pydantic_validator_tool(ProductPriceInfo)

    # Configure the "worker" agent that will be used for each sub-task.
    # Using the specified model as requested.
    claude_model = LiteLLMModel(model_id="claude-3-5-haiku-latest", temperature=0.0)
    worker_agent = CodeAgent(
        model=claude_model, tools=[WebSearchTool(), product_validator_tool]
    )

    # use result = code_agent.run(prompt)
    results = []
    for product in products_to_find:
        print(f"--- TOOL: Processing product: {product['name']} ---")

        # Create a prompt for the worker agent
        prompt = f"""
        You are an expert shopping assistant.

        1.  **Search**: Use the 'web_search' tool to find a {product["name"]} in {product["color"] or "any color"}, size {product["size"]}.
        2.  **Extract Information**: From the results, find the best price for the product, add the direct purchase URL, and reuse the product name given.
        3.  **Validate Your Findings**: Use the '{product_validator_tool.name}' tool to validate the data you extracted.
        4.  **Final Answer**: Once the validation tool succeeds, its output is your final answer. Provide only that output.

        Begin.
        """
        result = worker_agent.run(prompt)
        results.append(result)

    return [result for result in results if result is not None]


# --- 4. Example Usage: A "Manager Agent" Using the Tool ---


# def main():
#     load_dotenv()
#     if not os.getenv("ANTHROPIC_API_KEY"):
#         print("FATAL: ANTHROPIC_API_KEY environment variable not set.")
#         return

#     # This is the "Manager Agent". Its only job is to delegate tasks.
#     # Note that its tool list contains our powerful new orchestrator function.
#     manager_agent = CodeAgent(
#         model=LiteLLMModel(model_id="claude-3-5-haiku-latest", temperature=0.0),
#         tools=[get_prices_from_list_product],  # The function is passed directly
#     )

#     # The list of products we want the manager to process.
#     products = [
#         ProductNew(
#             name="Chuck Taylor All-Star '70", brand="Converse", size=42, color="noire"
#         ),
#         ProductNew(name="Air Force 1 '07", brand="Nike", size=43, color="white"),
#     ]
#     # The agent needs the data in its prompt, typically as a string.
#     # products_as_dicts = [p.model_dump() for p in products]

#     manager_prompt = f"""
#     You are a high-level manager. Your job is to process a list of products to find their prices.
#     You have one tool available to you that can handle this entire complex task.

#     Use your tool to find pricing information for the following list of products:
#     {products}

#     Execute the tool and return its final output directly.
#     Return a list of ProductPriceInfo objects, each containing the product name, price, and URL.
#     ProductPriceInfo is defined as follows:
#     Example use: {ProductPriceInfo.__name__}(data_to_validate={{{", ".join(ProductPriceInfo.model_fields.keys())}}})

#     """

#     print("---  MANAGER AGENT: Starting its job... ---")
#     final_result_list = manager_agent.run(manager_prompt)

#     print("\n--- ✅ MANAGER AGENT: Job complete. Final Output: ---")
#     print(final_result_list)

#     # Final check to prove the output is valid
#     try:
#         validated_final_output = [ProductPriceInfo(**p) for p in final_result_list]
#         print(
#             "\n--- Final output successfully validates against the ProductPriceInfo schema ---"
#         )
#     except Exception as e:
#         print(f"Final output failed validation: {e}")


# main()

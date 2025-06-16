from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool, Tool
from typing import List, Dict, Any, Union
import json
import os
import dotenv

dotenv.load_dotenv()


class LLMJudgeTool(Tool):
    name = "llm_judge_scorer"
    description = "Score a single product using LLM judge"
    inputs = {
        "product": {"type": "string", "description": "Single product to score"},
        "criteria": {"type": "string", "description": "Criteria for scoring"},
    }
    output_type = "string"

    def __init__(self, model=None):
        super().__init__()
        self.model = model

    def forward(self, product: str, criteria: str) -> str:
        import json

        prompt = f"""Score this product 0-100 based on the criteria.
Criteria: {criteria}
Product: {product}

Consider:
- How well the product matches the style, season, and occasion
- Material compatibility with criteria
- Color match with preferences
- Overall suitability

Return only a single number (0-100): """

        try:
            if self.model:
                messages = [{"role": "user", "content": prompt}]
                response = self.model(messages)
                print(f"LLM response: {response}")

                # Extract single score from response
                import re

                # Look for a number (0-100)
                score_match = re.search(r"\b(\d{1,3})\b", str(response))
                if score_match:
                    score = min(100, max(0, int(score_match.group(1))))
                else:
                    score = 70  # Default score

                return str(score)
            else:
                return "60"
        except Exception as e:
            print(f"LLM judge error: {e}")
            return "60"


class ProductSheetAgent(CodeAgent):
    """Agent for generating product sheets based on product descriptions"""

    def __init__(self, model: LiteLLMModel, max_results=5):
        # Initialize tools
        tools = [
            DuckDuckGoSearchTool(),  # Internet search
            LLMJudgeTool(model=model),  # Custom scoring tool
        ]

        # name and description for the agent
        self.name = "ProductSheetAgent"
        self.description = (
            "An agent that generates product sheets based on user criteria. "
            "It searches for products online, scores them based on user preferences, "
            "and formats them into standardized product sheets."
        )

        # Store tools separately for direct access
        self.judge_tool = LLMJudgeTool(model=model)
        self.max_results = max_results

        super().__init__(
            tools=tools,
            model=model,
            name=self.name,
            description=self.description,
        )

    def generate_product_sheets(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main pipeline method to generate product sheets

        Args:
            criteria: Dictionary with keys: type, style, season, budget (range), material (list), colors (list), brands (list), occasion

        Returns:
            List of product sheets with brand, size, name, color, matching_score
        """
        # Step 1: Receive and validate criteria
        validated_criteria = self._validate_criteria(criteria)

        # Step 2: Search for corresponding products
        search_results = self._search_products(validated_criteria)

        # Step 3: Calculate scores for each product
        scored_products = self._calculate_scores(search_results, validated_criteria)

        # Step 4: Format as product sheets
        product_sheets = self._format_product_sheets(scored_products)

        return product_sheets

    def _validate_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize input criteria"""

        #if criteria is a string, try to parse it as JSON 
        

        validated = {}

        # Required fields with default values
        validated["type"] = criteria.get("type", "")
        validated["style"] = criteria.get("style", "")
        validated["season"] = criteria.get("season", "")
        validated["occasion"] = criteria.get("occasion", False)

        # Budget - convert to range if needed
        budget = criteria.get("budget", [0, float("inf")])
        if isinstance(budget, list) and len(budget) == 2:
            validated["budget_min"] = budget[0]
            validated["budget_max"] = budget[1]
        else:
            validated["budget_min"] = 0
            validated["budget_max"] = float("inf")

        # Lists - ensure they are lists
        validated["materials"] = criteria.get("material", [])
        if not isinstance(validated["materials"], list):
            validated["materials"] = [validated["materials"]]

        validated["colors"] = criteria.get("colors", [])
        if not isinstance(validated["colors"], list):
            validated["colors"] = [validated["colors"]]

        validated["brands"] = criteria.get("brands", [])
        if not isinstance(validated["brands"], list):
            validated["brands"] = [validated["brands"]]
        print(f"Validated criteria: {json.dumps(validated, indent=2)}")
        return validated

    def _search_products(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for products using multiple sources"""
        all_results = []
        print("Building search queries based on criteria...")

        # Build multiple search queries for different combinations
        search_queries = self._build_search_queries(criteria)
        ddg_tool = DuckDuckGoSearchTool()  # Internet search tool

        forum_tool = None
        press_tool = None

        # for tool in self.tools:
        #     if hasattr(tool, 'name'):
        #         if tool.name == "web_search":  # DuckDuckGoSearchTool
        #             ddg_tool = tool
        #         elif tool.name == "forum_search":
        #             forum_tool = tool
        #         elif tool.name == "press_search":
        #             press_tool = tool

        print("searching for products:")

        # TODO do for all queries, not just first 3
        print(f"Search queries: {search_queries}")

        query = search_queries[0]  # For testing, use only the first query

        try:
            # internet_results = self.run(f"Search for '{query}' using web search")
            internet_results = ddg_tool.forward(query=query)
            print(f"Internet search results for '{query}': {internet_results}")

            all_results.extend(self._parse_search_results(internet_results))
        except Exception as e:
            print(f"Internet search error: {e}")

        # Remove duplicates based on product name or URL
        unique_results = self._remove_duplicates(all_results)

        return unique_results

    def _calculate_scores(
        self, products: List[Dict[str, Any]], criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate matching scores using LLM judge tool, scoring one product at a time"""
        print("Calculating matching scores for products...")

        scored_products = []

        for i, product in enumerate(products):
            print(
                f"Scoring product {i + 1}/{len(products)}: {product.get('name', 'Unknown')}"
            )

            try:
                # Score single product - updated to use 'product' parameter
                score_str = self.judge_tool.forward(
                    product=str(product), criteria=str(criteria)
                )
                product["matching_score"] = int(score_str)

            except Exception as e:
                print(f"Error scoring product {product.get('name', 'Unknown')}: {e}")
                product["matching_score"] = 70

            scored_products.append(product)

        # Filter out products with very low scores and sort by score
        return sorted(
            [p for p in scored_products if p["matching_score"] > 5],
            key=lambda x: x["matching_score"],
            reverse=True,
        )

    def _format_product_sheets(
        self, products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Format products into standardized product sheets"""
        product_sheets = []

        for product in products:
            sheet = {
                "brand": product.get("brand", "Unknown"),
                "size": product.get("size", "Unknown"),
                "name": product.get("name", "Unknown"),
                "color": product.get("color", "Unknown"),
                #"matching_score": product.get("matching_score", 0.0),
            }
            product_sheets.append(sheet)

        return product_sheets[:20]

    def _build_search_queries(self, criteria: Dict[str, Any]) -> List[str]:
        """Build multiple search queries from criteria"""
        queries = []
        base_query = criteria["type"]

        # Base query with type and style
        if criteria["style"]:
            styles = [s.strip() for s in criteria["style"].split(",")]
            for style in styles:
                query_parts = [base_query, style]

                # Add season if specified
                if criteria["season"]:
                    query_parts.append(criteria["season"])

                queries.append(" ".join(query_parts))

        # Add color-specific queries
        if criteria["colors"]:
            for color in criteria["colors"]:
                color_query = [base_query, color]
                if criteria["season"]:
                    color_query.append(criteria["season"])
                queries.append(" ".join(color_query))

        # If no queries generated, use basic query
        if not queries:
            queries = [base_query]

        print(f"Generated search queries: {queries}")
        return list(set(queries))

    def _remove_duplicates(
        self, products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate products based on name and brand"""
        seen = set()
        unique_products = []

        for product in products:
            identifier = f"{product.get('name', '')}-{product.get('brand', '')}"
            if identifier not in seen:
                seen.add(identifier)
                unique_products.append(product)

        return unique_products

    def _parse_search_results(self, results: Any) -> List[Dict[str, Any]]:
        """Parse internet search results one by one using LLM capabilities"""

        # Convert results to string if needed
        if not isinstance(results, str):
            results_str = str(results)
        else:
            results_str = results

        print(f"Parsing search results: {results_str[:200]}...")

        # First, split the results into individual items
        individual_results = self._split_search_results(results_str)

        all_products = []

        # Process each result individually
        for i, single_result in enumerate(individual_results):
            print(f"Processing result {i + 1}/{len(individual_results)}")

            extraction_prompt = f"""
    Extract fashion product information from this search result and return ONLY a Python dictionary.

    If this contains a fashion product, return a dictionary with these keys:
    - name: product name
    - brand: brand name or "Unknown"  
    - color: color or "Various"
    - size: size or "Various"
    - price: price in euros (number) or 50 if unknown
    - material: material or "Mixed"
    - type: product category

    Return ONLY the dictionary, nothing else. Example:
    {{"name": "Product Name", "brand": "Brand", "color": "Color", "size": "Size", "price": 50, "material": "Material", "type": "type"}}

    If no fashion product found, return an empty dictionary: {{}}

    Search result: {single_result}
    """

            try:
                # Use the agent's run method for each individual result
                extraction_response = self.run(extraction_prompt, max_steps=5)
                print(
                    f"Agent extraction response for result {i + 1}: {extraction_response}"
                )

                # The response should already be a dictionary
                if isinstance(extraction_response, dict):
                    product = self._validate_single_product(extraction_response)
                else:
                    # Try to parse if it's a string representation
                    product = self._safe_eval_single_response(extraction_response)

                if product and product.get("name"):  # Only add if valid product found
                    all_products.append(product)
                    print(
                        f"Successfully extracted product: {product.get('name', 'Unknown')}"
                    )
                    # for testing we stop after 2 products
                    if len(all_products) >= self.max_results:
                        break

                else:
                    print(f"No product found in result {i + 1}")

            except Exception as e:
                print(f"Error processing result {i + 1}: {e}")
                continue

        print(f"Successfully extracted {len(all_products)} products total")
        return all_products

    def _extract_final_answer(self, response: str) -> Dict[str, Any]:
        """Extract the final answer from agent response"""
        try:
            import re
            import ast

            # Look for final_answer() call in the response
            pattern = r"final_answer\((\{.*?\})\)"
            match = re.search(pattern, response, re.DOTALL)

            if match:
                dict_str = match.group(1)
                product = ast.literal_eval(dict_str)
                return self._validate_single_product(product)

            return {}

        except Exception as e:
            print(f"Error extracting final answer: {e}")
            return {}

    def _split_search_results(self, results_str: str) -> List[str]:
        """Split search results into individual items"""
        try:
            # Try to intelligently split results based on common patterns

            # Split by common delimiters that indicate separate results
            # This is a simple approach - you might need to adjust based on your search tool's output format

            # First try splitting by double newlines (common in search results)
            if "\n\n" in results_str:
                individual_results = [
                    result.strip()
                    for result in results_str.split("\n\n")
                    if result.strip()
                ]

            # If no double newlines, try splitting by single newlines and group by patterns
            elif "\n" in results_str:
                lines = [
                    line.strip() for line in results_str.split("\n") if line.strip()
                ]

                # Group lines that seem to belong to the same result
                individual_results = []
                current_result = []

                for line in lines:
                    # Check if this line starts a new result (common patterns)
                    if (
                        line.startswith("http")
                        or line.startswith("Title:")
                        or line.startswith("•")
                        or line.startswith("-")
                        or len(line) > 50
                    ):  # Likely a title or description
                        if current_result:
                            individual_results.append("\n".join(current_result))
                            current_result = []

                    current_result.append(line)

                # Add the last result
                if current_result:
                    individual_results.append("\n".join(current_result))

            else:
                # If no clear separators, treat as one result
                individual_results = [results_str]

            # Filter out very short results that are unlikely to contain product info
            individual_results = [
                result for result in individual_results if len(result) > 20
            ]

            print(f"Split into {len(individual_results)} individual results")
            return individual_results

        except Exception as e:
            print(f"Error splitting results: {e}")
            return [results_str]  # Fallback to original string

    def _safe_eval_single_response(
        self, response: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Safely evaluate LLM response as a single Python dictionary"""
        try:
            import ast
            import re

            # If response is already a dict, validate and return it
            if isinstance(response, dict):
                return self._validate_single_product(response)

            # Clean the response (string case)
            response = response.strip()

            # Remove any markdown code blocks if present
            response = re.sub(r"```python\s*", "", response)
            response = re.sub(r"```\s*", "", response)

            # Handle empty response
            if response in ["{}", "", "None", "null"]:
                return {}

            # Try to find dictionary pattern
            dict_match = re.search(r"\{.*\}", response, re.DOTALL)
            if dict_match:
                dict_str = dict_match.group(0)

                # Use ast.literal_eval for safe evaluation
                product = ast.literal_eval(dict_str)

                if isinstance(product, dict):
                    return self._validate_single_product(product)

            return {}

        except Exception as e:
            print(f"Error parsing single LLM response: {e}")
            return {}

    def _validate_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize a single product dictionary"""
        if not product or not isinstance(product, dict):
            return {}

        # Ensure required fields exist with defaults
        validated_product = {
            "name": product.get("name", "Unknown Product"),
            "brand": product.get("brand", "Unknown"),
            "color": product.get("color", "Various"),
            "size": product.get("size", "Various"),
            "price": self._safe_convert_price(product.get("price", 50)),
            "material": product.get("material", "Mixed"),
            "type": product.get("type", "clothing"),
        }

        # Only return if we have a meaningful name
        if validated_product["name"] in ["Unknown Product", "", None]:
            return {}

        return validated_product

    def _safe_convert_price(self, price_value: Any) -> int:
        """Safely convert price to integer"""
        try:
            if isinstance(price_value, (int, float)):
                return int(price_value)
            elif isinstance(price_value, str):
                # Extract numeric value from string
                import re

                price_match = re.search(r"(\d+)", price_value)
                if price_match:
                    return int(price_match.group(1))
            return 50  # Default price
        except:
            return 50

    def _parse_forum_results(self, results: Any) -> List[Dict[str, Any]]:
        """Parse forum search results"""
        # Mock some results for testing
        return [
            {
                "name": "Casual Chic Dress",
                "brand": "Forum Recommended",
                "color": "Pastel Pink",
                "size": "S",
                "price": 65,
                "material": "Linen",
                "type": "dress",
            }
        ]

    def _parse_press_results(self, results: Any) -> List[Dict[str, Any]]:
        """Parse press article results"""
        # Mock some results for testing
        return [
            {
                "name": "Designer Summer Dress",
                "brand": "Press Featured",
                "color": "Light Green",
                "size": "L",
                "price": 85,
                "material": "Light Silk",
                "type": "dress",
            }
        ]


anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
model_id = "claude-3-haiku-20240307"


"""
HOW TO USE:

agent = ProductSheetAgent(model_id=model_id, max_results=5)
criteria = {
    "type": "shirt",
    "style": "casual",
    "season": "summer",
    "budget": [30, 100],
    "material": ["cotton"],
    "colors": ["light", "pastel"],
    "brands": [],
    "occasion": True
}

product_sheets = agent.generate_product_sheets(criteria)
print(json.dumps(product_sheets, indent=2))

"""

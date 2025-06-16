# Fashion Agent

A comprehensive AI-powered fashion recommendation system that helps users find clothing products based on their preferences, budget, and style requirements.
It was developed the 06/16 during Agents Hackathon by Hugging Face, Anthropic & Unaite.

## 🌟 Features

- **Conversational Style Advisor**: Interactive chatbot that understands your fashion preferences
- **Product Sheet Generation**: Automated search and compilation of fashion products
- **Price Comparison**: Real-time price searching across multiple platforms
- **Visual Product Selection**: Web-based interface for browsing and selecting products
- **Image Extraction**: Automatic product image extraction from retailer websites

## 🏗️ Architecture

The system consists of several specialized agents:

- **`AgentAdvisor`**: Conversational agent for gathering user preferences
- **`ProductSheetAgent`**: Searches and generates standardized product sheets
- **[`Price Searcher`](src/price_searcher.py)**: Finds current prices and purchase URLs
- **[`User Interface`](src/user_interface.py)**: Web-based product selection interface

## 📋 Prerequisites

- Python 3.11+
- Chrome/Chromium browser (for Selenium web scraping)
- Anthropic API key

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/GauthierRoy/fashion_agent.git
   cd fashion_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a .env file in the root directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   api_key=your_anthropic_api_key_here
   ```

4. **Install Chrome WebDriver**
   Ensure Chrome WebDriver is installed and accessible in your PATH for Selenium functionality.

## 🎯 Usage

### Basic Usage

Run the main application:

```bash
python src/main.py
```

### Using Individual Components

#### 1. Style Consultation
```python
from src.agent_conseiller import AgentAdvisor
from src.anthropic_client import client

advisor = AgentAdvisor(model=client, api_key="your_api_key")
criteria = advisor.run_dialogue()
```

#### 2. Product Search
```python
from src.agent_product_sheet import ProductSheetAgent
from src.anthropic_client import client

agent = ProductSheetAgent(model=client, max_results=5)
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
```

#### 3. Price Finding
```python
from src.price_searcher import get_prices_from_list_product

products = [
    {"name": "Casual T-Shirt", "brand": "Nike", "size": 42, "color": "blue"}
]

prices = get_prices_from_list_product(products)
```

#### 4. User Interface
```python
from src.user_interface import confirm_with_user

urls = ["https://example.com/product1", "https://example.com/product2"]
prices = [29.99, 45.50]
names = ["Product 1", "Product 2"]

selected_urls, feedback = confirm_with_user(urls, prices, names)
```

## 📁 Project Structure

```
fashion_agent/
├── src/
│   ├── agent_conseiller.py       # Conversational style advisor
│   ├── agent_product_sheet.py    # Product search and sheet generation
│   ├── anthropic_client.py       # LLM client configuration
│   ├── fetch_and_extract_image.py # Image extraction utilities
│   ├── helpers.py                # Utility functions
│   ├── main.py                   # Main application entry point
│   ├── price_searcher.py         # Price comparison tool
│   ├── user_interface.py         # Web-based user interface
│   └── summary_tool/             # Additional summary tools
│       ├── anthropic_client.py
│       ├── fetch_and_extract_image.py
│       ├── summary_tool.py       # Flask-based image gallery
│       └── summary_tool_official.py # Matplotlib-based display
├── test.ipynb                    # Jupyter notebook for testing
├── price_searcher.ipynb          # Price searcher development notebook
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables
└── .gitignore
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API key | Yes |


## 🛠️ Development

### Adding New Features

1. **New Search Sources**: Extend `ProductSheetAgent` by adding new search methods
2. **UI Improvements**: Modify the HTML template in `user_interface.py`
3. **Additional LLM Models**: Update `anthropic_client.py`

## 📝 API Reference

### AgentAdvisor

Interactive fashion advisor that collects user preferences through conversation.

**Methods:**
- `run_dialogue()`: Starts interactive session, returns structured criteria

### ProductSheetAgent

Searches for fashion products and generates standardized product sheets.

**Methods:**
- `generate_product_sheets(criteria)`: Main pipeline method
- `_search_products(criteria)`: Searches multiple sources
- `_calculate_scores(products, criteria)`: Scores products using LLM

### Price Searcher

Finds current prices and purchase URLs for fashion products.

**Functions:**
- `get_prices_from_list_product(products)`: Returns price information for product list

### User Interface

Web-based interface for product selection and feedback.

**Functions:**
- `confirm_with_user(urls, prices, names)`: Displays products and collects user selection

## 🐛 Troubleshooting

### Common Issues

1. **Selenium WebDriver Issues**
   - Ensure Chrome/Chromium is installed
   - Check ChromeDriver version compatibility

2. **API Key Errors**
   - Verify your Anthropic API key is valid
   - Check the .env file is properly configured

3. **Port Conflicts**
   - The web interface uses port 5000 by default
   - Modify the port in `user_interface.py` if needed


## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude API
- [SmolagentsAI](https://github.com/huggingface/smolagents) for the agent framework
- [Flask](https://flask.palletsprojects.com/) for the web interface
- [Selenium](https://selenium.dev/) for web scraping capabilities

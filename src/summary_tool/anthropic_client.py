import anthropic
from dotenv import load_dotenv
from smolagents import LiteLLMModel
import os

load_dotenv()
api_key = os.getenv("api_key")

client = LiteLLMModel(
    model_id="claude-3-5-haiku-latest",
    temperature=0.1,
    api_key = api_key)

if __name__=="__main__":
    response = client.generate(
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ])
    print(response.content)
from smolagents import CodeAgent
import requests
from dotenv import load_dotenv
import os
import json
load_dotenv(dotenv_path="fashion_agent/.env")
API_KEY = os.getenv("ANTHROPIC_API_KEY")
url = "https://api.anthropic.com/v1/messages"


class AgentAdvisor(CodeAgent):
    def __init__(self, model, api_key):
        self.name = "AgentAdvisor"
        self.description = "An AI shopping advisor that helps users find clothing based on their preferences."
        self.api_key = API_KEY
        self.url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        super().__init__(
            tools=[], model=model, name=self.name, description=self.description
        )
        self.prompt_templates["system_prompt"] = (
            "You are a smart shopping advisor and style consultant. "
            "Start by introducing yourself and asking questions to understand the user's clothing preferences. "
            "For each answer, you can give style advice or suggestions if relevant. "
            "Ask about the following criteria, one by one if needed: "
            "type (e.g., dress, pants), style (e.g., chic, streetwear, basic), season (e.g., summer), "
            "budget (format [min, max]), preferred materials, preferred colors, brands, second-hand acceptable (true if yes). "
            "If the user's answer is not directly related to a criterion, give advice or ask clarifying questions. "
            "When you have collected all the answers, STOP asking questions and output ONLY a JSON object with these keys and the user's answers. "
            "Do not explain or comment, just output the JSON object at the end."
        )

    def run_dialogue(self):
        history = [
            {
                "role": "assistant",
                "content": "Hello! I am your shopping advisor. What type of clothing are you looking for?",
            }
        ]
        while True:
            print(history[-1]["content"])
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "stop"]:
                print("Fin de la discussion.")
                break
            if not user_input:
                print("Merci d'entrer une réponse.")
                continue
            history.append({"role": "user", "content": user_input})

            messages = [{"role": "user", "content": self.system_prompt}] + history

            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 256,
                "messages": messages,
            }
            response = requests.post(self.url, headers=self.headers, json=data)
            resp_json = response.json()
            if "content" in resp_json and isinstance(resp_json["content"], list):
                assistant_message = resp_json["content"][0]["text"]
            else:
                print("Erreur ou format inattendu :", resp_json)
                break
            history.append({"role": "assistant", "content": assistant_message})

            if assistant_message.strip().startswith("{"):
                print("Final JSON:", assistant_message)
                raw_criteria = json.loads(assistant_message)
                
                # Transform to the required format
                criteria = {
                    "type": raw_criteria.get("type", ""),
                    "style": raw_criteria.get("style", ""),
                    "season": raw_criteria.get("season", ""),
                    "budget": raw_criteria.get("budget", []),
                    "material": raw_criteria.get("materials", []) if isinstance(raw_criteria.get("materials"), list) else [raw_criteria.get("materials", "")],
                    "colors": raw_criteria.get("colors", []) if isinstance(raw_criteria.get("colors"), list) else [raw_criteria.get("colors", "")],
                    "brands": raw_criteria.get("brands", []) if isinstance(raw_criteria.get("brands"), list) else [raw_criteria.get("brands", "")] if raw_criteria.get("brands") else [],
                    "occasion": raw_criteria.get("second-hand acceptable", True)
                }
                return criteria
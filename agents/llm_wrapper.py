import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()  


class AzureLLM:
    def __init__(self):
        self.endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        self.api_key = os.environ["AZURE_OPENAI_API_KEY"]
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        self.deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        resp = self.client.chat.completions.create(
            model=self.deployment,   # Azure uses deployment name here
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content
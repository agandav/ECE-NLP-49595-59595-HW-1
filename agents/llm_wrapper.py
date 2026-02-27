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

    def chat(
      self,
      messages: List[Dict[str, str]],
      temperature: float = 0.,
      max_tokens: int = 300,
      presence_penalty: float = 0.0,
      frequency_penalty: float = 0.4,
      ) -> str:
      resp = self.client.chat.completions.create(
         model=self.deployment,
         messages=messages,
         temperature=temperature,
         max_tokens=max_tokens,
         presence_penalty=presence_penalty,
         frequency_penalty=frequency_penalty,
      )
      return resp.choices[0].message.content
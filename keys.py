import os
from dotenv import load_dotenv

load_dotenv()

azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_region = os.getenv("AZURE_OPENAI_REGION")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
azure_key = os.getenv("AZURE_KEY")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_region = os.getenv("AZURE_REGION")
import os
from dotenv import load_dotenv

load_dotenv()

azure_openai_key        = os.getenv("_OPENAI_API_KEY")
azure_openai_endpoint   = os.getenv("_OPENAI_ENDPOINT")
azure_openai_api_version = os.getenv("_OPENAI_API_VERSION")
azure_openai_deployment  = os.getenv("_OPENAI_DEPLOYMENT")

azure_key    = os.getenv("AZURE_KEY")
azure_region = os.getenv("AZURE_REGION")
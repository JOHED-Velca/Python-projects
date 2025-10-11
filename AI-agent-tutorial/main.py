from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()  # Load environment variables from .env file

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

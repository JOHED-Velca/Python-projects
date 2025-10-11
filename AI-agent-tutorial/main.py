from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()  # Load environment variables from .env file

# Option 1: Use Anthropic (requires credits)
# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Option 2: Use OpenAI (requires OPENAI_API_KEY in .env file)
llm = ChatOpenAI(model="gpt-3.5-turbo")  # or "gpt-4" if you have access

response = llm.invoke("Write a poem about a lonely computer.")
print(response)
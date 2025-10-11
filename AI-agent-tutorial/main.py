from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()  # Load environment variables from .env file

# Option 1: Use Anthropic (requires credits) - Using cheapest Claude model
llm = ChatAnthropic(model="claude-3-haiku-20240307")  # Cheapest and fastest

# Other Claude options (uncomment to use):
# llm = ChatAnthropic(model="claude-3-sonnet-20240229")  # More capable, slightly more expensive
# llm = ChatAnthropic(model="claude-3-5-haiku-20241022")  # Newer haiku (if available)
# llm = ChatAnthropic(model="claude-3-opus-20240229")  # Most capable, most expensive

# Option 2: Use OpenAI (requires OPENAI_API_KEY in .env file)
# llm = ChatOpenAI(model="gpt-3.5-turbo")  # or "gpt-4" if you have access

response = llm.invoke("Write a poem about a lonely computer.")
print(response)
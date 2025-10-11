from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()  # Load environment variables from .env file

class ReserachResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatAnthropic(model="claude-3-haiku-20240307")  # Cheapest and fastest
parser = PydanticOutputParser(pydantic_object=ReserachResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a reserach assistant that will help generate a reserach paper.
            Answer the user query and use neccessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=[]
)

agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)

raw_response = agent_executor.invoke({"query": "What is the capital of France?"})

print(raw_response)

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
except Exception as e:
    print("Error parsing response", e, "Raw response:", raw_response)
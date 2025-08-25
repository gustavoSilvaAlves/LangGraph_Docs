from dotenv import load_dotenv
load_dotenv()

from langgraph.prebuilt import create_react_agent



def get_weather(city: str) -> str:
    """Obtenha a previsão do tempo para uma determinada cidade"""
    return f"Está sempre ensolarado em {city}!"


def get_transito(city: str) -> str:
    """Obtenha o fluxo de trânsito de uma determinada cidade"""
    return f"Está sempre trânsito em {city}!"

def get_policia(city: str) -> str:
    """Obetenha se a cidade tem policial"""
    return f"A cidade  {city} sempre tem policial"





agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[get_weather,get_transito,get_policia],
    prompt="You are a helpful assistant"
)

# Run the agent


print(agent.invoke(
    {"messages": [{"role": "user", "content": "Como está as chuvas em brasília??"}]}
))



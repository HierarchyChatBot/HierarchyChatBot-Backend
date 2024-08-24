# llm.py

from langgraph.graph import Graph

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json

def get_llm():
    # Specify the local language model
    local_llm = "gemma2"

    # Initialize the ChatOllama model with desired parameters
    return ChatOllama(
        model=local_llm, 
        format="json", 
        temperature=0)

# Clip the history to the last 16000 characters
def clip_history(history: str, max_chars: int = 16000) -> str:
    if len(history) > max_chars:
        return history[-max_chars:]
    return history

def ChatBot(question):
    # Define the prompt template
    template = """
        {question}
        you reply in {{ reply:"<content>" }}
    """

    prompt = PromptTemplate.from_template(clip_history(template))

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=question)

    llm = get_llm()

    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    data = json.loads(generation)
    reply = data.get("reply", "")

    return reply
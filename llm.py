# llm.py

from langgraph.graph import Graph

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json

# Specify the local language model
local_llm = "phi3"

# Initialize the ChatOllama model with desired parameters
llm = ChatOllama(model=local_llm, format="json", temperature=0)


def ChatBot(question):
    # Define the prompt template
    template = """
        {question}
        you reply in {{ reply:"<content>" }}
    """
    
    prompt = PromptTemplate.from_template(template)

    # Format the prompt with the input variable
    formatted_prompt = prompt.format(question=question)

    llm_chain = prompt | llm | StrOutputParser()
    generation = llm_chain.invoke(formatted_prompt)
    
    data = json.loads(generation)
    reply = data.get("reply", "")

    return reply
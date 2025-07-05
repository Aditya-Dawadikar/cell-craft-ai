from services.langchain_prompt import transform_prompt
from services.langchain_llm import llm

transform_chain = transform_prompt | llm
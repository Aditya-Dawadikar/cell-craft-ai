from services.langchain_prompt import transform_prompt
from services.langchain_summary_prompt import history_summary_prompt
from services.langchain_llm import llm

transform_chain = transform_prompt | llm
history_summary_chain = history_summary_prompt | llm
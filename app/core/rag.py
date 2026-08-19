from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_llm


ASKDOC_SYSTEM_PROMPT = """
You are AskDoc agent, a document assistant. Answer only based on given context. If the answer is not in the context say "I don't know". Cite the answer from context. Never cite information from other sources except the context. Answer shortly and to the point unless the user states otherwise.
"""

askdoc_template = ChatPromptTemplate.from_messages([
    ("system", ASKDOC_SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])

llm = get_llm()
# rag test
'''
rag_chain = askdoc_template | llm | StrOutputParser()
print(rag_chain.invoke({
    "context": "The company was founded in 2020. It has 50 employees. The CEO is Jane Smith.",
    "question": "Who is the CEO?"
}))
print()
print(rag_chain.invoke({
    "context": "The company was founded in 2020.",
    "question": "What is the company's revenue?"
}))
'''
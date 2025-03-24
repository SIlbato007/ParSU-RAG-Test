from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def setup_llm():
    """Initialize the LLM via HuggingFaceHub with specified parameters."""
    return HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        model_kwargs={
            "max_new_tokens": 512,
            "temperature": 0.5,
            "repetition_penalty": 1.1,
            "return_full_text": False
        }
    )

def setup_prompt_template():
    """Create a prompt template and output parser for the chain."""
    template = (
        "<|system|>\n"
        "You are a friendly AI Assistant for Partido State University that understands users extremely well and always responds professionally.\n"
        "Please be truthful and give direct answers. If the user query is not in CONTEXT, then ask again for clarification.\n"
        "You can't process any transaction you can only explain it.</s>\n"
        "CONTEXT: {context}</s>\n"
        "<|user|> {query} </s>\n"
        "<|assistant|>"
    )
    prompt = ChatPromptTemplate.from_template(template)
    output_parser = StrOutputParser()
    return prompt, output_parser

def assemble_chain(retriever, prompt, llm, output_parser):
    """Assemble the chain using retriever, prompt, LLM, and output parser."""
    return (
        {"context": retriever, "query": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )

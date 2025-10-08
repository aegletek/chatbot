import os
from dotenv import load_dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.vectorstores import Weaviate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import weaviate
from operator import itemgetter
from langchain_core.runnables import RunnableLambda

from ai.config import ENV_PATH
load_dotenv(dotenv_path=ENV_PATH)

# Setup Weaviate vector store
vectorstore = Weaviate(client, "YourIndexName", "text", embeddings)
retriever = vectorstore.as_retriever()

# Setup the compressor
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)


# Define the prompt template with history
template = """You are a helpful assistant for a government website. Your primary goal is to answer user questions based on the provided context and conversation history.

Use the following pieces of retrieved context and chat history to answer the question. If the context contains information about a specific document, form, or page, do not offer a direct download link. Instead, guide the user to the relevant webpage where they can find the information or document.

If you don't know the answer, just say that you don't know. Keep the answer concise and clear.

History: {chat_history}
Question: {question}
Context: {context}
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)

from langchain_core.runnables import RunnablePassthrough

# ... (imports and other setup remain the same)

# Create the RAG chain with history and context pass-through
rag_chain = (
    {
        "context": itemgetter("question") | compression_retriever,
        "question": itemgetter("question"),
        "chat_history": itemgetter("chat_history"),
    }
    | RunnablePassthrough.assign(
        answer=(
            prompt
            | llm
            | StrOutputParser()
        )
    )
)

if __name__ == "__main__":
    chat_history = []
    print("Chatbot is ready. Type 'quit', 'exit', or 'end' to end the session.")

    while True:
        try:
            question = input("You: ")
            if question.lower() in ["quit", "exit", "end"]:
                print("Ending chat session.")
                break

            # Format chat history for the prompt
            formatted_history = "\n".join(chat_history)

            # Invoke the chain to get both answer and context
            result = rag_chain.invoke({"question": question, "chat_history": formatted_history})
            answer = result["answer"]
            
            # Extract and log the sources for internal use
            sources = sorted(list(set(doc.metadata["source"] for doc in result["context"])))
            
            print(f"Bot: {answer}")
            if sources:
                print(f"[Sources: {', '.join(sources)}]")

            # Update history
            chat_history.append(f"Human: {question}")
            chat_history.append(f"AI: {answer}")

        except (KeyboardInterrupt, EOFError):
            print("\nEnding chat session.")
            break

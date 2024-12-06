# rag_service.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from config import EMBEDDING_MODEL, CHROMA_PATH, api_key

class RAGService:
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
         
        # Initialize the base model
        self.base_llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")
        
        # Initialize the vector store
        self.vectorstore = None

        # Initialize the prompt
        self.prompt_template = """
        You are a helpful assistant. Use the following pieces of context to answer the question at the end.
            Context: {context}
            Question: {question}
        """
        self.prompt = PromptTemplate.from_template(self.prompt_template) 


    def upload_pdf(self, pdf_path):
        # Load the PDF document
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50
        )
        texts = text_splitter.split_documents(documents)
        
        # Delete the previous collection if it exists
        try:
            Chroma.delete_collection(
                persist_directory=CHROMA_PATH, 
                collection_name="default_collection"
            )
        except:
            pass
        
        # Save the chunks to ChromaDB
        self.vectorstore = Chroma.from_documents(
            documents=texts, 
            embedding=self.embeddings,
            persist_directory=CHROMA_PATH
        )

    def base_query(self, query):
        # Generate a response using the base model
        return self.base_llm.invoke(query).content

    def rag_query(self, query):
        # Ensure the vector store is initialized
        if self.vectorstore is None:
            return "Upload the Document"
        
        # Create a Retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.base_llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 2}),
            chain_type_kwargs={"prompt": self.prompt}
        )
        
        # Run the query using RAG
        response = qa_chain.invoke({"query": query})
        return response["result"]

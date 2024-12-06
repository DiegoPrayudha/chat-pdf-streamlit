import streamlit as st
import os
from rag_service import RAGService
from streamlit_chat import message  # Import streamlit-chat

def main():
    st.title("Chat with PDF")
    
    # Initialize RAG Service
    if 'rag_service' not in st.session_state:
        st.session_state.rag_service = RAGService()
        st.session_state.messages = []  # To store the conversation
        st.session_state.is_rag_available = False
    
    # Sidebar for uploading a PDF
    with st.sidebar:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Select a PDF file", type="pdf")
        
        if uploaded_file is not None:
            # Save the file temporarily
            temp_path = "temp.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Upload to Chroma
            st.session_state.rag_service.upload_pdf(temp_path)
            st.success("PDF successfully uploaded!")
            st.session_state.is_rag_available = True
            
            # Remove the temporary file
            os.remove(temp_path)
    
    # Display previous conversation
    for i, chat in enumerate(st.session_state.messages):
        is_user = chat["role"] == "user"
        message(chat["content"], is_user=is_user, key=f"chat_{i}")
    
    # Input prompt
    prompt = st.text_input("Enter your question:", key="input", placeholder="Type your question here...")

    # Button to send the question
    if st.button("Submit Question"):
        if prompt.strip():
            # Add user input to the conversation
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get a response from the model
            if st.session_state.is_rag_available:
                response = st.session_state.rag_service.rag_query(prompt)
            else:
                response = st.session_state.rag_service.base_query(prompt)
            
            # Add chatbot response to the conversation
            st.session_state.messages.append({"role": "bot", "content": response})


if __name__ == "__main__":
    main()

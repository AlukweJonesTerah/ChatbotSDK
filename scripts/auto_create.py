import os
import json
import logging


def create_project_structure(api_key_file, expected_api_key):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(api_key_file, 'r') as file:
        api_key_data = json.load(file)
        api_key = api_key_data['key']

    if api_key == expected_api_key:
        root_folder = 'chatbots/mtafsiribot'
        os.makedirs(root_folder, exist_ok=True)
        logging.info('[itsKios-09]: running creating ${root_folder}.....')

        subfolders = ['model', 'static', 'template']
        for folder in subfolders:
            os.makedirs(os.path.join(root_folder, folder), exist_ok=True)
        logging.info('[itsKios-09]: running creating ${subfolders}.....')

        # Create the app.py file
        with open(os.path.join(root_folder, 'app.py'), 'w') as file:
            file.write("""import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
import os

# Sidebar contents
with st.sidebar:
    st.title('Common questions asked during pregnancy')
  
    # Path to your image file
    image_path = "image.jpg"

    # Display the image
    st.image(image_path, caption='Helping teen mothers figure out their way through pregnancy', use_column_width=True)
    st.markdown('''
    ## About
    EmpowerBot is an interactive chatbot application specifically designed to offer support and guidance to teen mothers throughout their pregnancy journey. This Streamlit-powered chatbot leverages cutting-edge technologies to provide comprehensive answers to a wide array of questions related to pregnancy.
                
    Built by [Chang'ach, Devis, Brenda, Faith, Lorraine]
    ''')


    add_vertical_space(5)
# Load environment variables from a .env file if present
load_dotenv()

# Retrieve the OpenAI API key from the environment
# openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_key = "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"
# Set the OpenAI API key
# os.environ["OPENAI_API_KEY"] = openai_api_key
def main():
    st.header("Pregnancy Chatbot💬")
    # Get the file path from the user
    file_path = "Common-Questions-in-Pregnancy-pdf.pdf"

    # Check if a file path is provided
    if file_path:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(text=text)

            # Extracting store name from the file path
            store_name = os.path.splitext(os.path.basename(file_path))[0]
            # st.write(f'{store_name}')

            if os.path.exists(f"{store_name}.pkl"):
                with open(f"{store_name}.pkl", "rb") as f:
                    VectorStore = pickle.load(f)
            else:
                embeddings = OpenAIEmbeddings()
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                with open(f"{store_name}.pkl", "wb") as f:
                    pickle.dump(VectorStore, f)


        # Initialize the chat messages history
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "assistant", "content": "Hello. How can I help?"}]

        # Prompt for user input and save
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            docs = VectorStore.similarity_search(query=prompt, k=3)

        # display the existing chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If last message is not from assistant, we need to generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            # Call LLM
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", max_tokens=1000)
                    chain = load_qa_chain(llm=llm, chain_type="stuff")
                    with get_openai_callback() as cb:
                        response = chain.run(input_documents=docs, question=prompt)

                    r = response
                    response = r
                    st.write(response)

            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)

if __name__ == '__main__':
    main()
                       """)
            with open(os.path.join(root_folder, '.env'), 'w') as file:
                file.write(""" Get the user api key from openai and save it here""")
        
            with open(os.path.join(root_folder, 'apikey.json'), 'w') as file:
                file.write(""" Get the user api key from openai and save it here""")


            with open(os.path.join(root_folder, 'readme.md'), 'w') as file:
                file.write(""" README.MD file, write the chatbot description here""")
        logging.info('[itsKios-09]: running creating .env.....')
        logging.info('[itsKios-09]: running creating apikey.json .....')
        logging.info('[itsKios-09]: running creating readme.md .....')



        return
    else:
        print('Error: API key does not match the expected key')



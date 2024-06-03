import streamlit as st
from gtts import gTTS
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmltemplates import css, bot_template, user_template





# extracting text from pdfs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

# Function to handle voice input
def handle_voice_input():
    r = sr.Recognizer()

    with st.spinner("Listening..."):
        with sr.Microphone() as source:
            audio = r.listen(source)

    try:
        user_question = r.recognize_google(audio)
        handle_userinput(user_question)
    except sr.UnknownValueError:
        st.warning("Sorry, could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
    finally:
        st.write("")  # Remove the "Speak something..." message

def handle_voice_output(bot_response):
    tts = gTTS(text=bot_response, lang='en')
    tts.save("bot_response.mp3")
    st.audio("bot_response.mp3", format="audio/mp3")
    


def main():
    load_dotenv()
    st.set_page_config(page_title="Symphony", page_icon="💡")
    st.markdown("""
    <style>
        .title-container {
            background-color: #8083F9;
            padding: -2px;
            border-radius: 62px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .title {
            font-family: serif;
            font-size: 48px;
            color: #fff;
            text-align: center;
            margin-bottom: 0;
        }
    </style>
    <div class="title-container">
        <h1 class="title">Symphony.IO</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    

 
    

    
    st.write(css, unsafe_allow_html=True)

    

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    welcome_text = "<span style='font-size:25px;font-weight: bold;'>✨ Curious about something in your document? Ask away and let the</span> <span class='symphony-hover' style='color:#ffd700;font-weight: bold; font-size:44px;'>Symphony</span> <span style='font-size:25px;font-weight: bold;'>reveal insights!</span>"
    

# ...

    styled_text = f"""
<div style="text-align:center; font-size:18px; font-weight:bold; color:#ffffff;">
  {welcome_text}
  <br>
  <style>
   .symphony-hover {{
   transition: color 0.3s ease-in-out, transform 0.2s ease-in-out;
   display: inline-block;
   }}
   .symphony-hover:hover {{
    color: #f4d03f;
    transform: translateY(-2px);
  }}
 </style>
</div>
"""


    st.markdown(styled_text, unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "📄Upload your PDF documents for analysis. Click 'Analyze'", accept_multiple_files=True)

        if st.button("Analyze"):
            if pdf_docs is None or len(pdf_docs) == 0:
                st.warning("⚠️ Please upload at least one PDF document.")
            else:
                with st.spinner("Analysizng"):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    vectorstore = get_vectorstore(text_chunks)
                    st.session_state.conversation = get_conversation_chain(vectorstore)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("Voice Interaction")

        # Informative and user-friendly tooltip with clear instructions:
        tooltip_text = """
        - **Speak:** Click to provide voice input instead of typing.
          - Ensure a microphone is connected and configured.
          - Speak clearly and concisely for better recognition.
        - **Listen:** Click to have the bot's responses read aloud.
          - Ensure speakers are connected and configured.
        """
        st.info(tooltip_text)

        voice_input_button = st.button("🎙️Speak", key="voice_input_button")
        voice_output_button = st.button("🔊 Listen", key="voice_output_button")
    
    

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    user_question = st.text_input("Got questions about your document?")

    if voice_output_button and st.session_state.chat_history:
        bot_response = st.session_state.chat_history[-1].content
        handle_voice_output(bot_response)

    if voice_input_button:
        handle_voice_input()

        

    

    st.markdown(
        """
        <style>
        .styled-arrow-button {
            background-color: #A9A9A9;
            border: none;
            color: white;
            padding: 3px 13px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 24px;
            margin-right: 10px;
            margin-top: -13px;
            cursor: pointer;
            border-radius: 16px;
            transition: transform 0.3s ease-in-out;
        }

        .styled-arrow-button:hover {
            background-color: #808080;
            transform: translateX(10px);
        }
        </style>
        """
        , unsafe_allow_html=True)

    st.markdown(
        """
        <button class="styled-arrow-button" onclick="generateResponse()">➜</button>
        <script>
            function generateResponse() {
                var response = {'content': 'This is a response from the bot!', 'role': 'bot'};
                st.session_state.chatHistory.push(response);
                st.rerun();
            }
        </script>
        """
        , unsafe_allow_html=True)

    if user_question:
        handle_userinput(user_question)

    # Add the last block of code here
    if "voice_output_enabled" in st.session_state and st.session_state.voice_output_enabled:
        bot_response = st.session_state.chat_history[-1].content
        st.write(bot_response, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .copyright {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #212121;
            color: #ffffff;
            text-align: center;
            padding: 5px;
            font-size: 12px;
        }
        </style>
        """
        , unsafe_allow_html=True)

    st.markdown(
        """
        <div class="copyright">
            &copy; 2024 YSC Symphony. All rights reserved.
        </div>
        """
        , unsafe_allow_html=True)

if __name__ == '__main__':
    main()

    
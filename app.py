import os

import streamlit as st
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_URL = os.getenv("FIREBASE_URL")

if not GEMINI_API_KEY:
    st.error("Missing GEMINI_API_KEY. Please add it to your .env file.")
    st.stop()

if not FIREBASE_URL:
    st.error("Missing FIREBASE_URL. Please add it to your .env file.")
    st.stop()

st.set_page_config(page_title="AI Study Assistant")

client = genai.Client(api_key=GEMINI_API_KEY)

st.title("AI Study Assistant")
st.write("Ask me any school question. ")

DATABASE_URL = FIREBASE_URL

response = requests.get(DATABASE_URL + "/messages.json")

profile = requests.get(DATABASE_URL + "/profile.json").json()
print(profile)

if profile is None:
    st.subheader("Create your profile")
    name = st.text_input("Enter your name: ")
    grade = st.text_input("Enter your grade")
    subject = st.text_input("Enter your favorite subject")

    if st.button("Save profile"):
        profile = {
            "name": name,
            "grade": grade,
            "favorite_subject": subject
        }

        requests.put(DATABASE_URL + "/profile.json", json = profile).json()

        st.success("Profile saved successfully!")
if response.json():
    st.session_state.messages = response.json()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask your question...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    prompt = f"""You are an AI Study Assistant.
                Student Name: {profile['name']}
                Grade: {profile['grade']}
                favorite Subject = {profile['favorite_subject']}
                Explain everything in simple language suitable for this student
            """

    recent_messages =  st.session_state.messages[-5:]

    for message in recent_messages:
        prompt += f"{message['role']} : {message['content']}"


    response = client.models.generate_content(
        model = "gemini-3-flash-preview",
        contents = prompt
    )

    answer = response.text

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    
    with st.chat_message("assistant"):
        st.write(answer)

    response = requests.put(DATABASE_URL + "/messages.json", json=st.session_state.messages)
    print(response.status_code)

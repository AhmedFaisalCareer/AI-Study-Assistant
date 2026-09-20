```python
import os

import streamlit as st
import requests
from google import genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_URL = os.getenv("FIREBASE_URL")


# Check API keys
if not GEMINI_API_KEY:
    st.error("Missing GEMINI_API_KEY. Please add it to your environment variables.")
    st.stop()

if not FIREBASE_URL:
    st.error("Missing FIREBASE_URL. Please add it to your environment variables.")
    st.stop()


# Page settings
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖"
)


# Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Firebase URL
DATABASE_URL = FIREBASE_URL.rstrip("/")


# --------------------------------------------------
# APP TITLE
# --------------------------------------------------

st.title("🤖 AI Study Assistant")
st.write("Ask me any school question.")


# --------------------------------------------------
# GET PROFILE
# --------------------------------------------------

try:
    profile_response = requests.get(
        DATABASE_URL + "/profile.json",
        timeout=10
    )

    profile = profile_response.json()

except Exception:
    profile = None


# --------------------------------------------------
# CREATE PROFILE
# --------------------------------------------------

if not isinstance(profile, dict):

    st.subheader("Create your profile")

    name = st.text_input("Enter your name")
    grade = st.text_input("Enter your grade")
    subject = st.text_input("Enter your favorite subject")

    if st.button("Save profile"):

        if not name or not grade or not subject:
            st.warning("Please fill in all the fields.")

        else:

            new_profile = {
                "name": name,
                "grade": grade,
                "favorite_subject": subject
            }

            try:

                save_profile = requests.put(
                    DATABASE_URL + "/profile.json",
                    json=new_profile,
                    timeout=10
                )

                if save_profile.ok:

                    st.success("Profile saved successfully!")

                    st.rerun()

                else:

                    st.error("Could not save your profile.")

            except Exception as error:

                st.error(f"Error saving profile: {error}")

    st.stop()


# --------------------------------------------------
# GET MESSAGES FROM FIREBASE
# --------------------------------------------------

try:

    messages_response = requests.get(
        DATABASE_URL + "/messages.json",
        timeout=10
    )

    firebase_messages = messages_response.json()

except Exception:

    firebase_messages = None


# --------------------------------------------------
# LOAD VALID MESSAGES
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


if isinstance(firebase_messages, list):

    valid_messages = []

    for message in firebase_messages:

        if (
            isinstance(message, dict)
            and message.get("role") in ["user", "assistant"]
            and isinstance(message.get("content"), str)
        ):

            valid_messages.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

    st.session_state.messages = valid_messages


elif isinstance(firebase_messages, dict):

    valid_messages = []

    for message in firebase_messages.values():

        if (
            isinstance(message, dict)
            and message.get("role") in ["user", "assistant"]
            and isinstance(message.get("content"), str)
        ):

            valid_messages.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

    st.session_state.messages = valid_messages


# --------------------------------------------------
# DISPLAY OLD MESSAGES
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input("Ask your question...")


if question:

    # Add user question
    user_message = {
        "role": "user",
        "content": question
    }

    st.session_state.messages.append(user_message)


    # Display user question
    with st.chat_message("user"):

        st.write(question)


    # --------------------------------------------------
    # GET STUDENT INFORMATION
    # --------------------------------------------------

    student_name = profile.get(
        "name",
        "Student"
    )

    student_grade = profile.get(
        "grade",
        "Not specified"
    )

    favorite_subject = profile.get(
        "favorite_subject",
        "Not specified"
    )


    # --------------------------------------------------
    # CREATE PROMPT
    # --------------------------------------------------

    prompt = f"""
You are an AI Study Assistant.

Student Name: {student_name}

Grade: {student_grade}

Favorite Subject: {favorite_subject}

Explain everything in simple language suitable for this student.

Help the student understand the topic clearly.
Use examples when useful.
Do not make the explanation unnecessarily difficult.

Recent conversation:
"""


    # Add recent messages
    recent_messages = st.session_state.messages[-5:]


    for message in recent_messages:

        prompt += f"""
{message["role"]}: {message["content"]}
"""


    # --------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text

    except Exception as error:

        answer = f"Sorry, I could not generate an answer right now.\n\nError: {error}"


    # --------------------------------------------------
    # ADD AI RESPONSE
    # --------------------------------------------------

    assistant_message = {
        "role": "assistant",
        "content": answer
    }


    st.session_state.messages.append(
        assistant_message
    )


    # --------------------------------------------------
    # DISPLAY AI RESPONSE
    # --------------------------------------------------

    with st.chat_message("assistant"):

        st.write(answer)


    # --------------------------------------------------
    # SAVE CHAT TO FIREBASE
    # --------------------------------------------------

    try:

        save_messages = requests.put(
            DATABASE_URL + "/messages.json",
            json=st.session_state.messages,
            timeout=10
        )

        if not save_messages.ok:

            st.warning("The answer was generated, but the chat could not be saved.")

    except Exception as error:

        st.warning(f"Could not save chat history: {error}")
```

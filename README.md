# AI Study Assistant

AI Study Assistant is a Streamlit web app that helps students ask school-related questions in simple language. It collects a student profile, stores chat history, and uses Google Gemini to generate helpful explanations tailored to the student.

## Features

- Create and save a student profile with name, grade, and favorite subject
- Chat with the assistant in a simple conversational interface
- Store messages and profile data in Firebase Realtime Database
- Generate answers using the Google Gemini API

## Requirements

- Python 3.10+
- A Google Gemini API key
- Access to the Firebase Realtime Database URL used by the app

## Installation

1. Create and activate a virtual environment (optional but recommended).
2. Install the dependencies:

bash
pip install -r requirements.txt


## Run the app

Start the Streamlit app with:

bash
streamlit run app.py


## Notes

The app currently uses a Firebase Realtime Database URL and a Google Gemini client directly inside the code. If you plan to reuse or deploy this project, consider moving sensitive values such as the API key and database URL to environment variables.

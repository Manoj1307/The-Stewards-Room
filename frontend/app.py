import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000/ask")

st.title("The Stewards Room")
st.caption("An AI assistant for Formula 1 regulations.")

question= st.chat_input("Enter your question")

if question:
    response= requests.post(API_URL, json={"question": question})
    answer = response.json()["answer"]
    st.chat_message("user").write(question)
    st.chat_message("assistant").write(answer)
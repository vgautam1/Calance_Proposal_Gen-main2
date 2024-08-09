from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import Ollama
import streamlit as st

def configure_llm(api, api_key, temp):
    if api == 'Ollama':
        model = st.sidebar.selectbox('Choose a model', ['llama3.1:latest', 'mistral', 'gemma2'])
        return Ollama(model=model, temperature=temp, base_url="http://localhost:11434")
    elif api == 'OpenRouter':
        model = st.sidebar.selectbox('Choose a model', ['openai/gpt-4o-mini', 'anthropic/claude-3.5-sonnet', 'meta-llama/llama-3.1-8b-instruct:free','meta-llama/llama-3.1-70b-instruct'])
        return ChatOpenRouter(model_name=model, temperature=temp, openai_api_key=api_key)
    elif api == 'OpenAI':
        model = st.sidebar.selectbox('Choose a model', ['gpt-4', 'gpt-3.5-turbo'])
        return ChatOpenAI(temperature=temp, openai_api_key=api_key, model_name=model)
    return None

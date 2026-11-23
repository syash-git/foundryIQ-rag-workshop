import os

import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]

st.set_page_config(page_title="IT Desk")
st.title("IT Desk")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_message := st.chat_input("Message IT Desk"):
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            with (
                DefaultAzureCredential() as credential,
                AIProjectClient(
                    endpoint=endpoint,
                    credential=credential,
                    allow_preview=True,
                ) as project_client,
            ):
                openai_client = project_client.get_openai_client(agent_name=agent_name)
                if st.session_state.conversation_id is None:
                    conversation = openai_client.conversations.create()
                    st.session_state.conversation_id = conversation.id

                response = openai_client.responses.create(
                    conversation=st.session_state.conversation_id,
                    input=[{"role": "user", "content": user_message}],
                )
                answer = response.output_text
                if not answer:
                    raise ValueError("The agent returned no text response.")
        st.markdown(answer)

    st.session_state.messages.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ])
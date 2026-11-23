# Module 4: Invoke The Agent With A Local Web App

The [IT Desk chat app](../src/rag_webapp.py) uses Streamlit for the UI and the existing Foundry SDK calls for the agent.

1. Complete Module 3 and sign in with `az login`.
2. Set `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_AGENT_NAME` in `.env`, then load the environment as described in setup. Use the same agent name as Module 3.
3. Run from the repository root:

   ```powershell
   python -m streamlit run .\src\rag_webapp.py --server.address localhost
   ```

Open `http://localhost:8501`. Each browser session keeps its own chat history and Foundry conversation across turns. Reloading the page starts a new chat. The UI runs locally; messages are sent to your Foundry agent. Request errors are displayed in the app.

[Previous: RAG Agent](module-03-rag-agent.md) | [Workshop overview](../README.md)
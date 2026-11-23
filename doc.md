README structure

Intro (max 150 words): 
Workshop introduced how to build a retrieval augemented generation application for IT help desk using Azure AI foundry. It cover fundemental concepts of Foundry IQ - knolwedge sources, and knowledge base, and shows how to build RAG agent that can answer questions on IT desk knowledge base articles.


1) Prreq
python, access to an azure subsription, any other thing you can think of 


2) setup
venv
intall all libs
az login



3) create .env file by copying, and referecing .env.example


Workshop Modules
Module 1)
Create knowledge source using  create-ks-blob-storage.py


Module 2)
Create knolwedge base using create-kb.py


Module 3)
Create a foundry agent for Retrieval Augmented Generation

Module 4)
Invoke the agent with a local web app



Create seperate MD files for each module

Module 1)
Create knowledge source using  create-ks-blob-storage.py
Show how the knowledge source is linked to blob storage.


Module 2)
Create knolwedge base using create-kb.py

Explain what it creates under the hood: AI search index, indexer, and skillset


Module 3)
Create a foundry agent for Retrieval Augmented Generation

Show how to go to the foundry portal and view the agnet


Module 4)
<do not implement it yet>


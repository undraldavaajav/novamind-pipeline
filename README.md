# NovaMind AI Marketing Pipeline

An automated marketing content pipeline that generates, distributes, and analyzes blog and newsletter content using Groq AI and HubSpot CRM.

## What it does

1. Takes a topic input and generates a blog post + 3 persona newsletters using Groq (Llama 3.3)
2. Creates contacts in HubSpot CRM segmented by persona and logs the campaign
3. Simulates engagement metrics and generates an AI performance summary

## Tech Stack
- AI Model: Groq API (Llama 3.3 70B)
- CRM: HubSpot API (Private App)
- Language: Python 3.13
- Storage: JSON files

## Personas
- Agency Owner: ROI-focused, business tone
- Freelance Designer: casual, practical tone  
- Marketing Manager: data-informed, professional tone

## Setup
1. Clone the repo
2. Create venv: python3 -m venv venv && source venv/bin/activate
3. Install: pip install groq requests python-dotenv
4. Create .env with GROQ_API_KEY and HUBSPOT_API_KEY
5. Run: python3 main.py "AI tools for creative agencies"

## Assumptions
- Engagement metrics are simulated around realistic baselines
- HubSpot contacts use mock test data
- Groq free tier used for all AI generation

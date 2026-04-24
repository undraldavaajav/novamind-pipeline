from dotenv import load_dotenv; import os; load_dotenv(); print(os.environ.get('GROQ_API_KEY', 'MISSING')[:8]); print(os.environ.get('HUBSPOT_API_KEY', 'MISSING')[:8])

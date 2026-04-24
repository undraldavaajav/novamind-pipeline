import os; from dotenv import load_dotenv; load_dotenv(); k=os.environ.get('HUBSPOT_API_KEY','MISSING'); print('Key starts with:', k[:15])

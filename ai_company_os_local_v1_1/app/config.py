from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
DATA_DIR=BASE_DIR/'data'; DATA_DIR.mkdir(exist_ok=True)
SECRETS_DIR=BASE_DIR/'secrets'; SECRETS_DIR.mkdir(exist_ok=True)
DB_PATH=DATA_DIR/'company.db'
GOOGLE_CREDENTIALS=SECRETS_DIR/'credentials.json'
GOOGLE_TOKEN=SECRETS_DIR/'token.json'
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
ANTHROPIC_API_KEY=os.getenv('ANTHROPIC_API_KEY','')
OPENAI_MODEL=os.getenv('OPENAI_MODEL','gpt-5.6-terra')
ANTHROPIC_MODEL=os.getenv('ANTHROPIC_MODEL','claude-sonnet-5')
GMAIL_POLL_MINUTES=max(1,int(os.getenv('GMAIL_POLL_MINUTES','5')))
CALENDAR_POLL_MINUTES=max(1,int(os.getenv('CALENDAR_POLL_MINUTES','5')))
IMPORTANT_NAME=os.getenv('IMPORTANT_NAME','').strip()

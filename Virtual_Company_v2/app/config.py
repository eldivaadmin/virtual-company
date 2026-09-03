from pathlib import Path
import os,json
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
DATA_DIR=BASE_DIR/'data'; DATA_DIR.mkdir(exist_ok=True)
SECRETS_DIR=BASE_DIR/'secrets'; SECRETS_DIR.mkdir(exist_ok=True)
DB_PATH=DATA_DIR/'company.db'
GOOGLE_CREDENTIALS=SECRETS_DIR/'credentials.json'
GOOGLE_ACCOUNTS_FILE=SECRETS_DIR/'google_accounts.json'
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
ANTHROPIC_API_KEY=os.getenv('ANTHROPIC_API_KEY','')
OPENAI_MODEL=os.getenv('OPENAI_MODEL','gpt-5.6')
ANTHROPIC_MODEL=os.getenv('ANTHROPIC_MODEL','claude-sonnet-4-5')
GMAIL_POLL_MINUTES=max(1,int(os.getenv('GMAIL_POLL_MINUTES','5')))
CALENDAR_POLL_MINUTES=max(1,int(os.getenv('CALENDAR_POLL_MINUTES','5')))
IMPORTANT_NAME=os.getenv('IMPORTANT_NAME','木塚直也').strip()
DEFAULT_GOOGLE_ACCOUNTS={
 'mail':['naoya.kizuka@gmail.com','xnetwork.lab@gmail.com'],
 'calendar':'lamp.kizuka@gmail.com'
}
def google_accounts():
    if GOOGLE_ACCOUNTS_FILE.exists():
        try:return json.loads(GOOGLE_ACCOUNTS_FILE.read_text(encoding='utf-8'))
        except Exception:pass
    return DEFAULT_GOOGLE_ACCOUNTS

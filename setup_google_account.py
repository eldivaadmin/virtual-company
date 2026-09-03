import argparse,json
from app.google_services import authorize_account
from app import config
p=argparse.ArgumentParser();p.add_argument('email');a=p.parse_args()
print(f'Google認証: {a.email}')
print('ブラウザで必ずこのGoogleアカウントを選択してください。')
ok=authorize_account(a.email)
print('OK' if ok else 'FAILED')

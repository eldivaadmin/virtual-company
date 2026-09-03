from app.google_services import authorize
print('Google OAuthを開始します。ブラウザが開いたら許可してください。')
print('OK' if authorize() else 'FAILED')

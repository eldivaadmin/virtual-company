from . import config
import shutil,subprocess,os

class ProviderNotConfigured(RuntimeError): pass

def _run(cmd,input_text,timeout=180):
    env=os.environ.copy()
    p=subprocess.run(cmd,input=input_text,text=True,capture_output=True,timeout=timeout,env=env)
    if p.returncode!=0: raise RuntimeError((p.stderr or p.stdout or 'CLI execution failed').strip())
    return p.stdout.strip()

def cli_status():
    return {'codex':bool(shutil.which('codex')),'claude':bool(shutil.which('claude')),'gemini':bool(shutil.which('gemini'))}

def ask_codex(system,prompt):
    if not shutil.which('codex'): raise ProviderNotConfigured('Codex CLIが見つかりません')
    return _run(['codex','exec','--skip-git-repo-check','-'],system+'\n\n依頼:\n'+prompt)

def ask_claude_cli(system,prompt):
    if not shutil.which('claude'): raise ProviderNotConfigured('Claude Codeが見つかりません')
    return _run(['claude','-p',system+'\n\n依頼:\n'+prompt])

def ask_gemini_cli(system,prompt):
    if not shutil.which('gemini'): raise ProviderNotConfigured('Gemini CLIが見つかりません')
    return _run(['gemini','-p',system+'\n\n依頼:\n'+prompt])

def ask_openai(system,prompt):
    if not config.OPENAI_API_KEY: raise ProviderNotConfigured('OpenAI API未設定')
    from openai import OpenAI
    r=OpenAI(api_key=config.OPENAI_API_KEY).responses.create(model=config.OPENAI_MODEL,instructions=system,input=prompt)
    return r.output_text

def ask_claude_api(system,prompt):
    if not config.ANTHROPIC_API_KEY: raise ProviderNotConfigured('Claude API未設定')
    import anthropic
    m=anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY).messages.create(model=config.ANTHROPIC_MODEL,max_tokens=1400,system=system,messages=[{'role':'user','content':prompt}])
    return ''.join(getattr(x,'text','') for x in m.content)

def route(provider,system,prompt):
    p=(provider or 'auto').lower()
    aliases={'openai':'codex','gpt':'codex','claude':'claude-cli','gemini':'gemini-cli'};p=aliases.get(p,p)
    if p=='codex': return ask_codex(system,prompt)
    if p=='claude-cli': return ask_claude_cli(system,prompt)
    if p=='gemini-cli': return ask_gemini_cli(system,prompt)
    if p=='openai-api': return ask_openai(system,prompt)
    if p=='claude-api': return ask_claude_api(system,prompt)
    errors=[]
    for name,fn in [('codex',ask_codex),('claude',ask_claude_cli),('gemini',ask_gemini_cli)]:
        try:return fn(system,prompt)
        except Exception as e:errors.append(name+': '+str(e))
    if config.OPENAI_API_KEY:
        try:return ask_openai(system,prompt)
        except Exception as e:errors.append('OpenAI API: '+str(e))
    if config.ANTHROPIC_API_KEY:
        try:return ask_claude_api(system,prompt)
        except Exception as e:errors.append('Claude API: '+str(e))
    raise ProviderNotConfigured('利用可能なローカルAI CLIがありません / '+' | '.join(errors))

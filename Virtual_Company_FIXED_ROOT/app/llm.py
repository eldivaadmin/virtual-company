from . import config

def ask_openai(system,prompt):
    if not config.OPENAI_API_KEY:return '[OpenAI未設定] '+prompt
    from openai import OpenAI
    client=OpenAI(api_key=config.OPENAI_API_KEY)
    r=client.responses.create(model=config.OPENAI_MODEL,instructions=system,input=prompt)
    return r.output_text

def ask_claude(system,prompt):
    if not config.ANTHROPIC_API_KEY:return '[Claude未設定] '+prompt
    import anthropic
    client=anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    m=client.messages.create(model=config.ANTHROPIC_MODEL,max_tokens=1400,system=system,messages=[{'role':'user','content':prompt}])
    return ''.join(getattr(x,'text','') for x in m.content)

def route(provider,system,prompt):
    if provider=='claude':return ask_claude(system,prompt)
    if provider=='openai':return ask_openai(system,prompt)
    if config.OPENAI_API_KEY:
        try:return ask_openai(system,prompt)
        except Exception:pass
    return ask_claude(system,prompt)

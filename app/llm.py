from . import config

class ProviderNotConfigured(RuntimeError):
    pass

def ask_openai(system,prompt):
    if not config.OPENAI_API_KEY:
        raise ProviderNotConfigured('OpenAI APIが未設定です。.env に OPENAI_API_KEY を設定してください。ChatGPTのログイン/Plus契約とは別設定です。')
    from openai import OpenAI
    client=OpenAI(api_key=config.OPENAI_API_KEY)
    r=client.responses.create(model=config.OPENAI_MODEL,instructions=system,input=prompt)
    return r.output_text

def ask_claude(system,prompt):
    if not config.ANTHROPIC_API_KEY:
        raise ProviderNotConfigured('Claude APIが未設定です。.env に ANTHROPIC_API_KEY を設定してください。')
    import anthropic
    client=anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    m=client.messages.create(model=config.ANTHROPIC_MODEL,max_tokens=1400,system=system,messages=[{'role':'user','content':prompt}])
    return ''.join(getattr(x,'text','') for x in m.content)

def route(provider,system,prompt):
    if provider=='claude':
        return ask_claude(system,prompt)
    if provider=='openai':
        return ask_openai(system,prompt)
    errors=[]
    if config.OPENAI_API_KEY:
        try:return ask_openai(system,prompt)
        except Exception as e:errors.append('OpenAI: '+str(e))
    if config.ANTHROPIC_API_KEY:
        try:return ask_claude(system,prompt)
        except Exception as e:errors.append('Claude: '+str(e))
    if errors:
        raise RuntimeError(' / '.join(errors))
    raise ProviderNotConfigured('AIプロバイダが未設定です。.env に OPENAI_API_KEY または ANTHROPIC_API_KEY を設定してください。')

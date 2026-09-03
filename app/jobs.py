from .db import add_event,ceo_report,set_agent_load
from .google_services import poll_gmail,upcoming_calendar,calendar_triggers,unreplied_threads
from . import config

def job_gmail():
    try:
        set_agent_load('secretary',45,88)
        rows=poll_gmail()
        waiting=unreplied_threads(max_results=40,days=14)
        if rows:add_event('秘書AI','status',f'{len(rows)}件の新着メールを確認')
        if waiting:
            add_event('秘書AI','mail_followup',f'未返信候補 {len(waiting)}件を検出',{'threads':waiting[:20]})
            ceo_report('秘書AI','未返信メール候補',f'{len(waiting)}件あります。\n'+ '\n'.join([f"・{x['subject']} / {x['from']} / {x['age_hours']}時間" for x in waiting[:10]]),'high' if any(x['age_hours']>=24 for x in waiting) else 'normal')
        set_agent_load('secretary',18,86)
    except Exception as e:
        set_agent_load('secretary',0,80);add_event('SYSTEM','error',f'Gmail確認エラー: {e}')

def job_calendar():
    try:
        set_agent_load('secretary',38,86)
        rows=upcoming_calendar();triggers=calendar_triggers()
        # Avoid noisy polling log; only log if there is an actual trigger.
        if triggers:add_event('秘書AI','calendar_alerts',f'予定アラート {len(triggers)}件を発報',{'events':triggers})
        set_agent_load('secretary',15,85)
    except Exception as e:
        set_agent_load('secretary',0,80);add_event('SYSTEM','error',f'Calendar確認エラー: {e}')

def install_jobs(scheduler):
    # Calendar is more time-sensitive than mail. Poll every minute regardless of slower env setting.
    scheduler.add_job(job_gmail,'interval',minutes=config.GMAIL_POLL_MINUTES,id='gmail',replace_existing=True,max_instances=1,next_run_time=__import__('datetime').datetime.now()+__import__('datetime').timedelta(seconds=3))
    scheduler.add_job(job_calendar,'interval',minutes=1,id='calendar',replace_existing=True,max_instances=1,next_run_time=__import__('datetime').datetime.now()+__import__('datetime').timedelta(seconds=5))

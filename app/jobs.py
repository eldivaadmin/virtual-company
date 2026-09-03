from .db import add_event
from .google_services import poll_gmail,upcoming_calendar,calendar_triggers
from . import config

def job_gmail():
    try:
        rows=poll_gmail()
        if rows:add_event('秘書AI','status',f'{len(rows)}件の新着メールを確認')
    except Exception as e:add_event('SYSTEM','error',f'Gmail確認エラー: {e}')

def job_calendar():
    try:
        rows=upcoming_calendar()
        add_event('秘書AI','calendar',f'24時間以内の予定 {len(rows)}件を確認',{'events':rows})
        calendar_triggers()
    except Exception as e:add_event('SYSTEM','error',f'Calendar確認エラー: {e}')

def install_jobs(scheduler):
    scheduler.add_job(job_gmail,'interval',minutes=config.GMAIL_POLL_MINUTES,id='gmail',replace_existing=True,max_instances=1,next_run_time=__import__('datetime').datetime.now()+__import__('datetime').timedelta(seconds=3))
    scheduler.add_job(job_calendar,'interval',minutes=config.CALENDAR_POLL_MINUTES,id='calendar',replace_existing=True,max_instances=1,next_run_time=__import__('datetime').datetime.now()+__import__('datetime').timedelta(seconds=5))

import subprocess, platform
from apscheduler.schedulers.background import BackgroundScheduler
from .tts import speak

scheduler = BackgroundScheduler()
scheduler.start()

def notify(msg):
    if platform.system()=="Darwin":
        try:
            subprocess.run(["osascript","-e",f'display notification "{msg}" with title "Study Assistant"'])
        except:
            pass
    speak(msg)

def schedule(run_dt, msg, jid=None):
    jid = jid or str(run_dt.timestamp())
    scheduler.add_job(lambda:notify(msg), 'date', run_date=run_dt, id=jid)
    return jid

# Alias for backward compatibility
def schedule_reminder(run_dt, msg, jid=None):
    return schedule(run_dt, msg, jid)

def list_jobs():
    return [(j.id, j.next_run_time) for j in scheduler.get_jobs()]

def remove_job(jid):
    """Remove a scheduled job by ID"""
    try:
        scheduler.remove_job(jid)
        return True
    except:
        return False

def stop_scheduler():
    """Stop the scheduler (called on app close)"""
    try:
        scheduler.shutdown(wait=False)
    except:
        pass
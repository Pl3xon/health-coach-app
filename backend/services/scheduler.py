import asyncio
import time
from datetime import datetime, timezone, timedelta
from services.storage import list_users
from services.manager import (
    get_renpho_client, get_google_fit_client, save_gf_tokens_for_user,
    get_yazio_client, save_yazio_tokens_for_user,
)

TZ = timezone(timedelta(hours=2))
_running = False


async def refresh_all_users():
    global _running
    if _running:
        return
    _running = True
    try:
        users = list_users()
        now = datetime.now(TZ).strftime("%H:%M:%S")
        print(f"[Scheduler] Starte Token-Refresh fuer {len(users)} User(s) um {now}")

        for user in users:
            uid = user["id"]

            renpho = get_renpho_client(uid)
            if renpho:
                try:
                    renpho.login()
                    print(f"[Scheduler] {uid}: Renpho OK")
                except Exception as e:
                    print(f"[Scheduler] {uid}: Renpho Fehler: {e}")

            gf = get_google_fit_client(uid)
            if gf and gf.refresh_token:
                try:
                    if gf.refresh_access_token():
                        save_gf_tokens_for_user(uid, gf)
                        print(f"[Scheduler] {uid}: Google Fit Token Refresh OK")
                    else:
                        print(f"[Scheduler] {uid}: Google Fit Refresh fehlgeschlagen")
                except Exception as e:
                    print(f"[Scheduler] {uid}: Google Fit Fehler: {e}")

            yazio = get_yazio_client(uid)
            if yazio and yazio.refresh_token:
                try:
                    if yazio._refresh():
                        save_yazio_tokens_for_user(uid, yazio)
                        print(f"[Scheduler] {uid}: Yazio Token Refresh OK")
                    else:
                        print(f"[Scheduler] {uid}: Yazio Refresh fehlgeschlagen")
                except Exception as e:
                    print(f"[Scheduler] {uid}: Yazio Fehler: {e}")

        print(f"[Scheduler] Refresh abgeschlossen fuer {len(users)} User(s)")
    finally:
        _running = False


def _seconds_until_next_55():
    now = datetime.now(TZ)
    target = now.replace(minute=55, second=0, microsecond=0)
    if target <= now:
        target += timedelta(hours=1)
    return (target - now).total_seconds()


async def _loop():
    wait = _seconds_until_next_55()
    print(f"[Scheduler] Naechster Refresh in {int(wait)}s (um XX:55)")
    await asyncio.sleep(wait)
    while True:
        await refresh_all_users()
        await asyncio.sleep(3600)


_scheduler_task = None


def start_scheduler():
    global _scheduler_task
    if _scheduler_task is None:
        _scheduler_task = asyncio.ensure_future(_loop())
        print("[Scheduler] Gestartet")


def stop_scheduler():
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        _scheduler_task = None
        print("[Scheduler] Gestoppt")

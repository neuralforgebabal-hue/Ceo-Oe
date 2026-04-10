"""
CEO AI OS - Telegram Alerts & Monitoring
Sends system alerts and reports via Telegram Bot.
"""
import httpx
from typing import Optional
from core.config import settings
from core.logger import get_logger

logger = get_logger("monitoring.telegram")

TELEGRAM_API = "https://api.telegram.org"


async def send_message(text: str, chat_id: Optional[str] = None, parse_mode: str = "HTML") -> bool:
    """Send a message via Telegram Bot API."""
    token = settings.TELEGRAM_BOT_TOKEN
    cid = chat_id or settings.TELEGRAM_CHAT_ID

    if not token or not cid:
        logger.debug("Telegram not configured, skipping alert")
        return False

    url = f"{TELEGRAM_API}/bot{token}/sendMessage"
    payload = {"chat_id": cid, "text": text, "parse_mode": parse_mode}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info("Telegram alert sent")
                return True
            logger.warning(f"Telegram API error: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


async def alert_scan_complete(project_count: int):
    msg = (
        f"🤖 <b>CEO AI OS — Scan Complete</b>\n\n"
        f"📁 Projects found: <b>{project_count}</b>\n"
        f"✅ Database updated\n"
        f"🔗 Dashboard: <a href='http://localhost:3000'>Open Dashboard</a>"
    )
    await send_message(msg)


async def alert_agent_done(agent_name: str, project_name: str, summary: str):
    msg = (
        f"⚡ <b>{agent_name.upper()} Agent Complete</b>\n\n"
        f"📦 Project: <code>{project_name}</code>\n"
        f"📋 {summary[:200]}"
    )
    await send_message(msg)


async def alert_security_critical(project_name: str, vuln_count: int):
    msg = (
        f"🚨 <b>SECURITY ALERT</b>\n\n"
        f"📦 Project: <code>{project_name}</code>\n"
        f"⚠️ Critical vulnerabilities: <b>{vuln_count}</b>\n"
        f"🔍 Run Security Agent for full report"
    )
    await send_message(msg)


async def alert_project_generated(project_name: str, template: str, path: str):
    msg = (
        f"🛠 <b>New Project Generated</b>\n\n"
        f"📦 Name: <code>{project_name}</code>\n"
        f"📐 Template: {template}\n"
        f"📂 Path: <code>{path}</code>"
    )
    await send_message(msg)

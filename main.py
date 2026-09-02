# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐑𝐔𝐍𝐍𝐄𝐑 — 𝐅𝐔𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐃𝐈𝐓𝐈𝐎𝐍     ║
╠══════════════════════════════════════════════════════════════╣
║  • Credit System + Subscriptions                           ║
║  • Session Strings (Telethon/Pyrogram)                    ║
║  • File Upload + Approval System                          ║
║  • Run/Stop/Logs/Speed/Status                             ║
║  • Premium Emojis + Colourful Buttons                     ║
║  • Force-Join Channels                                    ║
║  • Host Approval Toggle                                   ║
║  • Ban File System                                        ║
║  • Broadcast System                                       ║
║  • Admin Panel                                            ║
║  • Referral System                                        ║
║  • Auto Pip Install + NPM Support                         ║
║  • Developer: @SUNRAKUV2                                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import json
import re
import select
import threading
import subprocess
import shutil
import tempfile
import zipfile
import hashlib
import sqlite3
import logging
import atexit
import functools
import io
import html
from datetime import datetime, timedelta
from pathlib import PurePosixPath
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import psutil
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
#  ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set!")
    sys.exit(1)

bot = TeleBot(BOT_TOKEN)

# ============================================================
#  CONFIGURATION
# ============================================================
OWNER_ID = int(os.getenv("OWNER_ID") or 8641613327)
ADMIN_IDS = {OWNER_ID}
YOUR_USERNAME = "@SunrakuV2"
UPDATE_CHANNEL = "https://t.me/ANISHPY"
FORCE_JOIN_CHANNELS = {}

# Folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'bot_data.db')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Limits
FREE_USER_LIMIT = 2
SUBSCRIBED_USER_LIMIT = 10
ADMIN_LIMIT = 20
OWNER_LIMIT = float('inf')

# ============================================================
#  PREMIUM EMOJI SYSTEM
# ============================================================
def to_small_caps(text):
    """Convert text to small caps with bold first letters."""
    normal_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    normal_lower = "abcdefghijklmnopqrstuvwxyz"
    small_caps_letters = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    bold_upper = "".join(chr(0x1D400 + i) for i in range(26))
    bold_lower = "".join(chr(0x1D41A + i) for i in range(26))
    small_table = str.maketrans(normal_upper + normal_lower, small_caps_letters + small_caps_letters)
    bold_table = str.maketrans(normal_upper + normal_lower, bold_upper + bold_lower)
    result = []
    at_start = True
    for ch in text:
        if ch.isalpha():
            if at_start:
                result.append(ch.translate(bold_table))
                at_start = False
            else:
                result.append(ch.translate(small_table))
        else:
            result.append(ch)
            at_start = True
    return "".join(result)

# Premium emoji IDs (Telegram Premium)
PREMIUM_EMOJI_IDS = {
    "⭐": "6267008582294705964",
    "🔥": "6267000941547885720",
    "💎": "6267186570034419608",
    "👑": "6266969287638913443",
    "🚀": "6266955436369385728",
    "🌟": "6267298050205553492",
    "✨": "6264907690451932671",
    "💫": "6269340869795518262",
    "🌈": "6066548336737917783",
    "🎯": "6066782648678749894",
    "🏆": "6066712498977904768",
    "🎨": "6066407805407991485",
    "🔮": "6066624550932585300",
    "⚡": "6066563631116459003",
    "💡": "6066589340790690901",
    "🎪": "6066750659762329304",
    "🎭": "6066594589240727141",
    "🎪": "6066572714972289937",
    "🎠": "6066364172835232055",
    "🎢": "6066397518961317139",
    "🎡": "6066423731146726364",
    "🎪": "6066505155136722830",
    "🎨": "6064369667332380317",
    "🎭": "6260206664062867939",
    "🎪": "6111669364774147851",
    "🎠": "4936256830130095259",
    "🎢": "6264879695855095980",
    "🎡": "6262365842906811952",
    "🎨": "6264848742025793313",
    "🎭": "6262751500905222205",
    "🎪": "6264519360983863801",
    "🎠": "6262427454212673646",
    "🎢": "6262518748037516781",
    "🎡": "6262755628368794467",
    "🎨": "6264974477193384574",
    "🎭": "6262421892230025751",
    "🎪": "6111520380948582356",
    "🎠": "5999068164225242555",
    "🎢": "5999151980512024620",
    "🎡": "6001533441093408240",
    "🎨": "6001589602085771497",
}

def premium_emoji(emoji):
    """Convert normal emoji to premium emoji using Telegram premium IDs."""
    if emoji in PREMIUM_EMOJI_IDS:
        return f'<tg-emoji emoji-id="{PREMIUM_EMOJI_IDS[emoji]}">{emoji}</tg-emoji>'
    return emoji

def premium_text(text):
    """Convert all emojis in text to premium emojis."""
    for emoji, eid in PREMIUM_EMOJI_IDS.items():
        if emoji in text:
            text = text.replace(emoji, f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>')
    return text

def premium_border(repeat=15):
    """Create a premium border."""
    return premium_text("✨" * repeat)

# ============================================================
#  DATABASE SETUP
# ============================================================
def init_db():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_files
                 (user_id INTEGER, file_name TEXT, file_type TEXT,
                  PRIMARY KEY (user_id, file_name))''')
    c.execute('''CREATE TABLE IF NOT EXISTS active_users
                 (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS authorized_users
                 (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS force_join_channels
                 (channel TEXT PRIMARY KEY, display_name TEXT, active INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned_files
                 (file_hash TEXT PRIMARY KEY, file_name TEXT, file_content BLOB,
                  banned_by INTEGER, banned_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_sessions
                 (user_id INTEGER PRIMARY KEY, session_string TEXT, api_id TEXT,
                  api_hash TEXT, phone TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_credits
                 (user_id INTEGER PRIMARY KEY, credits INTEGER DEFAULT 0)''')
    c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
    conn.commit()
    conn.close()

init_db()

# ============================================================
#  DATA LOADING
# ============================================================
user_subscriptions = {}
user_files = {}
user_credits = {}
active_users = set()
admin_ids = {OWNER_ID}
authorized_users = set()
banned_file_hashes = set()
bot_locked = False
PASSWORD_ENABLED = False
BOT_PASSWORD = None
HOST_APPROVAL_ENABLED = False
pending_approvals = {}
referral_claimed = set()

def load_data():
    global admin_ids, active_users, user_subscriptions, user_credits, authorized_users, banned_file_hashes
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    
    c.execute('SELECT user_id, expiry FROM subscriptions')
    for uid, expiry in c.fetchall():
        try:
            user_subscriptions[uid] = {'expiry': datetime.fromisoformat(expiry)}
        except:
            pass
    
    c.execute('SELECT user_id, file_name, file_type FROM user_files')
    for uid, fname, ftype in c.fetchall():
        if uid not in user_files:
            user_files[uid] = []
        user_files[uid].append((fname, ftype))
    
    c.execute('SELECT user_id FROM active_users')
    active_users.update(uid for (uid,) in c.fetchall())
    
    c.execute('SELECT user_id FROM admins')
    admin_ids.update(uid for (uid,) in c.fetchall())
    
    c.execute('SELECT user_id FROM authorized_users')
    authorized_users.update(uid for (uid,) in c.fetchall())
    
    c.execute('SELECT user_id, credits FROM user_credits')
    for uid, credits in c.fetchall():
        user_credits[uid] = credits
    
    c.execute('SELECT file_hash FROM banned_files')
    banned_file_hashes.update(h for (h,) in c.fetchall())
    
    conn.close()

load_data()
# Token changes are persisted, but the environment variable remains the preferred source.
try:
    _saved_token = None
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as _conn:
        _row = _conn.execute("SELECT value FROM bot_settings WHERE key = ?", ("bot_token",)).fetchone()
        _saved_token = _row[0] if _row else None
    if _saved_token and not os.getenv("BOT_TOKEN"):
        BOT_TOKEN = _saved_token
        bot.token = BOT_TOKEN
except Exception as _exc:
    logger.warning("Could not load saved token: %s", _exc)

# ============================================================
#  DATABASE OPERATIONS
# ============================================================
DB_LOCK = threading.Lock()

def html_escape(value):
    return html.escape(str(value), quote=False)


def is_admin(user_id):
    return user_id == OWNER_ID or user_id in admin_ids


def is_authorized(user_id):
    return (not PASSWORD_ENABLED) or is_admin(user_id) or user_id in authorized_users


def check_force_join(user_id):
    """Return missing force-join channels. Requires the bot to be able to inspect each channel."""
    missing = []
    for channel, display_name in list(FORCE_JOIN_CHANNELS.items()):
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                missing.append((channel, display_name))
        except Exception as exc:
            logger.warning("Force-join check failed for %s: %s", channel, exc)
            # Do not lock users out when the bot cannot inspect a channel.
    return missing


def save_setting(key, value):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            conn.commit()
        finally:
            conn.close()


def make_join_markup(missing):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel, display_name in missing:
        url = channel if channel.startswith("http") else f"https://t.me/{channel.lstrip('@')}"
        markup.add(InlineKeyboardButton(f"📢 Join {display_name}", url=url))
    markup.add(InlineKeyboardButton("✅ Check Again", callback_data="check_join"))
    return markup


def guard_user(message_or_call):
    """Common access guard. Returns True when access is allowed."""
    user_id = getattr(message_or_call.from_user, "id", None)
    if user_id is None:
        return False
    if user_id == OWNER_ID or user_id in admin_ids:
        return True
    if bot_locked:
        if hasattr(message_or_call, "message"):
            bot.answer_callback_query(message_or_call.id, "🔒 Bot is locked.", show_alert=True)
        else:
            bot.reply_to(message_or_call, "🔒 Bot is locked.")
        return False
    if PASSWORD_ENABLED and user_id not in authorized_users:
        prompt = "🔐 Password protection is enabled. Send /auth <password> to continue."
        if hasattr(message_or_call, "message"):
            bot.answer_callback_query(message_or_call.id, "🔐 Authorization required.", show_alert=True)
        else:
            bot.reply_to(message_or_call, prompt)
        return False
    missing = check_force_join(user_id)
    if missing:
        markup = make_join_markup(missing)
        if hasattr(message_or_call, "message"):
            bot.answer_callback_query(message_or_call.id, "📢 Join required.", show_alert=True)
            bot.send_message(message_or_call.message.chat.id, "📢 Please join the required channel(s) first.", reply_markup=markup)
        else:
            bot.reply_to(message_or_call, "📢 Please join the required channel(s) first.", reply_markup=markup)
        return False
    return True


def normalize_filename(name):
    """Keep uploads inside the per-user folder and remove unsafe path components."""
    name = os.path.basename(str(name).replace("\\", "/")).strip()
    if not name or name in (".", ".."):
        raise ValueError("Invalid filename")
    if len(name) > 120:
        root, ext = os.path.splitext(name)
        name = root[:120-len(ext)] + ext
    if not re.match(r"^[A-Za-z0-9._()@+\- \[\]]+$", name):
        raise ValueError("Filename contains unsupported characters")
    return name


def safe_zip_members(zf, destination):
    """Extract a zip without allowing path traversal or symlink-like entries."""
    destination = os.path.abspath(destination)
    members = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        raw = info.filename.replace("\\", "/")
        p = PurePosixPath(raw)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError(f"Unsafe ZIP path: {info.filename}")
        out = os.path.abspath(os.path.join(destination, *p.parts))
        if os.path.commonpath([destination, out]) != destination:
            raise ValueError(f"Unsafe ZIP path: {info.filename}")
        members.append((info, out))
    for info, out in members:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with zf.open(info, "r") as src_file, open(out, "wb") as dst_file:
            shutil.copyfileobj(src_file, dst_file)
    return [out for _, out in members]


def start_approval(run_func, run_args, user_id, file_name, chat_id):
    approval_id = hashlib.sha256(
        f"{user_id}:{file_name}:{time.time_ns()}:{random.random()}".encode()
    ).hexdigest()[:16]
    pending_approvals[approval_id] = {
        "run_func": run_func,
        "run_args": run_args,
        "uid": user_id,
        "file_name": file_name,
        "chat_id": chat_id,
        "created_at": time.time(),
    }
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("🟢 Approve", callback_data=f"apprv_{approval_id}"),
        InlineKeyboardButton("🔴 Reject", callback_data=f"rejct_{approval_id}")
    )
    for admin_id in list(admin_ids):
        try:
            bot.send_message(
                admin_id,
                f"🆕 <b>New Host Approval</b>\n\n"
                f"📄 File: <code>{html_escape(file_name)}</code>\n"
                f"👤 User: <code>{user_id}</code>",
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as exc:
            logger.warning("Could not notify admin %s: %s", admin_id, exc)
    return approval_id


def get_user_folder(user_id):
    folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def get_user_credits(user_id):
    return user_credits.get(user_id, 0)

def set_user_credits(user_id, credits):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO user_credits (user_id, credits) VALUES (?, ?)', (user_id, credits))
        conn.commit()
        user_credits[user_id] = credits
        conn.close()

def add_user_credits(user_id, amount):
    new_total = max(0, get_user_credits(user_id) + amount)
    set_user_credits(user_id, new_total)
    return new_total

def has_hostable_credits(user_id):
    if user_id == OWNER_ID or user_id in admin_ids:
        return True
    return get_user_credits(user_id) > 0

def save_user_file(user_id, file_name, file_type):
    if user_id not in user_files:
        user_files[user_id] = []
    user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
    user_files[user_id].append((file_name, file_type))
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                  (user_id, file_name, file_type))
        conn.commit()
        conn.close()

def remove_user_file(user_id, file_name):
    if user_id in user_files:
        user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            conn.close()

def add_active_user(user_id):
    if user_id not in active_users:
        active_users.add(user_id)
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            conn.close()

def save_subscription(user_id, expiry):
    expiry_str = expiry.isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
        conn.commit()
        user_subscriptions[user_id] = {'expiry': expiry}
        conn.close()

def save_user_session(user_id, session_string, api_id, api_hash, phone):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO user_sessions (user_id, session_string, api_id, api_hash, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (user_id, session_string, str(api_id), api_hash, phone, datetime.now().isoformat()))
        conn.commit()
        conn.close()

def get_user_session_string(user_id):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT session_string FROM user_sessions WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_run_env(user_id):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    session_string = get_user_session_string(user_id)
    if session_string:
        env["SESSION_STRING"] = session_string
        env["STRING_SESSION"] = session_string
    return env

# ============================================================
#  SCRIPT RUNNER
# ============================================================
bot_scripts = {}

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
    return False

def kill_process_tree(process_info):
    process = process_info.get('process')
    if process and process.pid:
        try:
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except:
                    child.kill()
            parent.terminate()
            parent.wait(timeout=2)
        except:
            pass

def monitor_process(script_key, process, log_file):
    try:
        rc = process.wait()
        logger.info("Script %s exited with code %s", script_key, rc)
    except Exception:
        pass
    finally:
        try:
            log_file.flush()
            log_file.close()
        except Exception:
            pass
        current = bot_scripts.get(script_key)
        if current and current.get("process") is process:
            bot_scripts.pop(script_key, None)


def run_script(script_path, script_owner_id, user_folder, file_name, message_obj):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='replace')
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=get_run_env(script_owner_id)
        )
        
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name,
            'script_owner_id': script_owner_id,
            'start_time': datetime.now(),
            'user_folder': user_folder,
            'type': 'py'
        }
        
        bot.reply_to(message_obj, f"✅ Python script `{file_name}` started!\n🆔 PID: {process.pid}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message_obj, f"❌ Failed to start script: {e}")

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='replace')
        
        process = subprocess.Popen(
            ['node', script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=get_run_env(script_owner_id)
        )
        
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name,
            'script_owner_id': script_owner_id,
            'start_time': datetime.now(),
            'user_folder': user_folder,
            'type': 'js'
        }
        
        bot.reply_to(message_obj, f"✅ JS script `{file_name}` started!\n🆔 PID: {process.pid}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message_obj, f"❌ Failed to start script: {e}")

def start_hosting(run_func, run_args, user_id, chat_id, file_name, message):
    if not has_hostable_credits(user_id):
        bot.send_message(chat_id, f"⚠️ Your credit has ended. Contact {YOUR_USERNAME} to buy more credits.", parse_mode='Markdown')
        return
    
    if HOST_APPROVAL_ENABLED and user_id not in admin_ids:
        start_approval(run_func, run_args, user_id, file_name, chat_id)
        bot.send_message(
            chat_id,
            f"⏳ Your file <code>{html_escape(file_name)}</code> is pending owner/admin approval.",
            parse_mode='HTML'
        )
        return
    
    if user_id == OWNER_ID or user_id in admin_ids:
        threading.Thread(target=run_func, args=run_args, daemon=True).start()
    else:
        credits = get_user_credits(user_id)
        if credits > 0:
            set_user_credits(user_id, credits - 1)
            threading.Thread(target=run_func, args=run_args, daemon=True).start()
            bot.send_message(chat_id, f"✅ <code>{html_escape(file_name)}</code> hosting started. 1 credit used. Remaining: <code>{credits - 1}</code>.", parse_mode='HTML')
        else:
            bot.send_message(chat_id, f"⚠️ No credits remaining. Contact {html_escape(YOUR_USERNAME)}.", parse_mode='HTML')

# ============================================================
#  MENU CREATION
# ============================================================
def create_main_menu_inline(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(to_small_caps('Updates Channel'), url=UPDATE_CHANNEL),
        InlineKeyboardButton('🟢 Upload File', callback_data='upload'),
        InlineKeyboardButton(to_small_caps('Check Files'), callback_data='check_files'),
        InlineKeyboardButton(to_small_caps('Bot Speed'), callback_data='speed'),
        InlineKeyboardButton(to_small_caps('Send Command'), callback_data='send_command'),
        InlineKeyboardButton(to_small_caps('Contact Owner'), url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'),
        InlineKeyboardButton(to_small_caps('My Credit'), callback_data='my_credit'),
        InlineKeyboardButton('🟢 Earn Credit', callback_data='earn_credit')
    ]
    markup.add(buttons[0])
    markup.add(buttons[1], buttons[2])
    markup.add(buttons[3], buttons[4])
    markup.add(buttons[5])
    markup.add(buttons[6], buttons[7])
    
    if user_id in admin_ids:
        admin_buttons = [
            InlineKeyboardButton(to_small_caps('Subscriptions'), callback_data='subscription'),
            InlineKeyboardButton(to_small_caps('Statistics'), callback_data='stats'),
            InlineKeyboardButton('🔴 Lock Bot', callback_data='lock_bot'),
            InlineKeyboardButton(to_small_caps('Broadcast'), callback_data='broadcast'),
            InlineKeyboardButton(to_small_caps('Admin Panel'), callback_data='admin_panel'),
            InlineKeyboardButton('🟢 Run All Scripts', callback_data='run_all_scripts')
        ]
        markup.add(admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(admin_buttons[4])
    
    return markup

def create_reply_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout = [
        ["📢 Updates Channel"],
        ["📤 Upload File", "📂 Check Files"],
        ["⚡ Bot Speed", "📞 Contact Owner"],
        ["💳 My Credit", "🟢 Earn Credit"],
        ["📱 Create Session", "📦 Install Pip"],
        ["🚫 Banned Files"]
    ]
    if user_id in admin_ids:
        layout = [
            ["📢 Updates Channel"],
            ["📤 Upload File", "📂 Check Files"],
            ["⚡ Bot Speed", "📊 Statistics"],
            ["💳 Subscriptions", "📢 Broadcast"],
            ["🔒 Lock Bot", "🟢 Run All Scripts"],
            ["👑 Admin Panel", "📞 Contact Owner"],
            ["🚫 Banned Files", "💳 My Credit"],
            ["🟢 Earn Credit", "📱 Create Session"]
        ]
    for row in layout:
        markup.add(*[KeyboardButton(text) for text in row])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running):
    markup = InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            InlineKeyboardButton(to_small_caps("Restart"), callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            InlineKeyboardButton(to_small_caps("Logs"), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            InlineKeyboardButton(to_small_caps("Logs"), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(InlineKeyboardButton(to_small_caps("Back"), callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 Add Admin', callback_data='add_admin'),
        InlineKeyboardButton('🔴 Remove Admin', callback_data='remove_admin')
    )
    markup.row(InlineKeyboardButton(to_small_caps('List Admins'), callback_data='list_admins'))
    markup.row(InlineKeyboardButton(to_small_caps('Change Token'), callback_data='change_token'))
    markup.row(
        InlineKeyboardButton(to_small_caps('Password'), callback_data='password_menu'),
        InlineKeyboardButton(to_small_caps('Channels'), callback_data='channel_menu')
    )
    markup.row(InlineKeyboardButton('🔴 Ban File', callback_data='ban_file_init'))
    markup.row(InlineKeyboardButton(to_small_caps('Banned List'), callback_data='banned_files_admin_list'))
    markup.row(InlineKeyboardButton(to_small_caps('Install Pip'), callback_data='install_pip_init'))
    markup.row(InlineKeyboardButton(to_small_caps('Credits'), callback_data='credit_menu'))
    markup.row(InlineKeyboardButton(to_small_caps('Reset Menu'), callback_data='reset_menu'))
    markup.row(InlineKeyboardButton(to_small_caps('Back'), callback_data='back_to_main'))
    return markup

def create_reset_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(to_small_caps('Reset Files'), callback_data='reset_files'),
        InlineKeyboardButton(to_small_caps('Reset Stop'), callback_data='reset_stop')
    )
    status = "🟢 ON" if HOST_APPROVAL_ENABLED else "🔴 OFF"
    markup.row(InlineKeyboardButton(f"Host Approval: {status}", callback_data="toggle_host_approval"))
    markup.row(InlineKeyboardButton(to_small_caps('Back'), callback_data='admin_panel'))
    return markup

def create_subscription_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 Add Subscription', callback_data='add_subscription'),
        InlineKeyboardButton('🔴 Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(InlineKeyboardButton(to_small_caps('Check Subscription'), callback_data='check_subscription'))
    markup.row(InlineKeyboardButton(to_small_caps('Back'), callback_data='back_to_main'))
    return markup

def create_password_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    status = "🟢 ON" if PASSWORD_ENABLED else "🔴 OFF"
    markup.row(InlineKeyboardButton(f'Status: {status}', callback_data='noop'))
    markup.row(
        InlineKeyboardButton('🟢 Turn ON', callback_data='password_on'),
        InlineKeyboardButton('🔴 Turn OFF', callback_data='password_off')
    )
    markup.row(InlineKeyboardButton(to_small_caps('Back'), callback_data='admin_panel'))
    return markup

def create_channel_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 Add Channel', callback_data='add_channel'),
        InlineKeyboardButton('🔴 Remove Channel', callback_data='remove_channel_list')
    )
    markup.row(InlineKeyboardButton(to_small_caps('Back'), callback_data='admin_panel'))
    return markup

# ============================================================
#  COMMAND HANDLERS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    add_active_user(user_id)
    
    if get_user_credits(user_id) == 0:
        add_user_credits(user_id, 3)
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    credit_str = "Unlimited" if (user_id == OWNER_ID or user_id in admin_ids) else str(get_user_credits(user_id))
    
    is_premium = user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now()
    status_text = "⭐ Premium" if is_premium else "🆓 Free User"
    
    welcome_msg = f"""
{premium_border()}
   {premium_text('🤖')} <b>𝐎𝐌𝐄𝐆𝐀 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐑𝐔𝐍𝐍𝐄𝐑</b> {premium_text('🤖')}
{premium_border()}

{premium_text('👋')} Hey <b>{message.from_user.first_name}</b>, glad to have you here!

{premium_text('🆔')} <b>User ID:</b> <code>{user_id}</code>
{premium_text('✳️')} <b>Status:</b> {status_text}
{premium_text('📁')} <b>Files:</b> <code>{current_files} / {limit_str}</code>
{premium_text('💳')} <b>Credits:</b> <code>{credit_str}</code>

{premium_text('🚀')} Host & run <b>Python</b> (<code>.py</code>) or <b>JS</b> (<code>.js</code>) scripts
{premium_text('📦')} Upload single files or <code>.zip</code> archives

{premium_text('👇')} <b>Tap a button below to get started!</b>
"""
    bot.reply_to(message, welcome_msg, reply_markup=create_reply_keyboard(user_id), parse_mode='HTML')

@bot.message_handler(commands=['auth'])
def auth_command(message):
    user_id = message.from_user.id
    if not PASSWORD_ENABLED or is_admin(user_id):
        bot.reply_to(message, "✅ Password protection is disabled or you are an admin.")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /auth <password>")
        return
    if parts[1] == BOT_PASSWORD:
        authorized_users.add(user_id)
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            try:
                conn.execute("INSERT OR IGNORE INTO authorized_users (user_id) VALUES (?)", (user_id,))
                conn.commit()
            finally:
                conn.close()
        bot.reply_to(message, "✅ Authorization successful.")
    else:
        bot.reply_to(message, "❌ Wrong password.")


@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    try:
        bot.clear_step_handler_by_chat_id(message.chat.id)
    except Exception:
        pass
    session_data.pop(message.from_user.id, None)
    bot.reply_to(message, "❌ Current operation cancelled.")


@bot.message_handler(commands=['status'])
def command_status(message):
    user_id = message.from_user.id
    stats = f"""
{premium_border()}
   {premium_text('📊')} <b>BOT STATISTICS</b>
{premium_border()}

👥 Total Users: <code>{len(active_users)}</code>
📂 Total Files: <code>{sum(len(f) for f in user_files.values())}</code>
🟢 Running Bots: <code>{len(bot_scripts)}</code>
🔒 Bot Status: <code>{'🔴 Locked' if bot_locked else '🟢 Unlocked'}</code>
💳 Your Credits: <code>{'Unlimited' if (user_id == OWNER_ID or user_id in admin_ids) else get_user_credits(user_id)}</code>
"""
    bot.reply_to(message, stats, parse_mode='HTML')

# ============================================================
#  TEXT BUTTON HANDLERS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📢 Updates Channel")
def updates_channel(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(to_small_caps('Updates Channel'), url=UPDATE_CHANNEL))
    bot.reply_to(message, f"{premium_text('📢')} Visit our Updates Channel:", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "📤 Upload File")
def upload_file(message):
    if not guard_user(message):
        return
    user_id = message.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files first.", parse_mode='HTML')
        return
    bot.reply_to(message, f"{premium_text('📤')} Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.", parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "📂 Check Files")
def check_files(message):
    if not guard_user(message):
        return
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.reply_to(message, f"{premium_text('📂')} Your files:\n\n(No files uploaded yet)", parse_mode='HTML')
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(files):
        is_running = is_bot_running(user_id, file_name)
        status = "🟢 Running" if is_running else "🔴 Stopped"
        markup.add(InlineKeyboardButton(f"{file_name} ({file_type}) - {status}", callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, f"{premium_text('📂')} Your files:\nClick to manage.", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "⚡ Bot Speed")
def bot_speed(message):
    if not guard_user(message):
        return
    start = time.time()
    msg = bot.reply_to(message, f"{premium_text('🏃')} Testing speed...", parse_mode='HTML')
    time.sleep(0.5)
    latency = round((time.time() - start) * 1000, 2)
    status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
    bot.edit_message_text(
        f"{premium_text('⚡')} Bot Speed & Status:\n\n⏱️ Latency: <code>{latency} ms</code>\n🚦 Status: <code>{status}</code>",
        msg.chat.id, msg.message_id, parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: msg.text == "📞 Contact Owner")
def contact_owner(message):
    if not guard_user(message):
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(to_small_caps('Contact Owner'), url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, f"{premium_text('📞')} CLICK TO CONTACT OWNER", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "💳 My Credit")
def my_credit(message):
    if not guard_user(message):
        return
    user_id = message.from_user.id
    if user_id == OWNER_ID or user_id in admin_ids:
        bot.reply_to(message, f"{premium_text('💳')} My Credit\nBalance: <code>Unlimited</code> (Owner/Admin)", parse_mode='HTML')
        return
    balance = get_user_credits(user_id)
    bot.reply_to(message, f"{premium_text('💳')} My Credit\nBalance: <code>{balance}</code> credits\n(1 credit = 24 hrs hosting)", parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "🟢 Earn Credit")
def earn_credit(message):
    if not guard_user(message):
        return
    user_id = message.from_user.id
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    markup = InlineKeyboardMarkup(row_width=1)
    share_text = "🚀 Host your Python/JS bots for free! Join using my link:"
    share_url = f"https://t.me/share/url?url={link}&text={share_text}"
    markup.add(InlineKeyboardButton('🟢 Share with Friends', url=share_url))
    markup.add(InlineKeyboardButton(to_small_caps('Back'), callback_data='back_to_main'))
    bot.reply_to(
        message,
        f"{premium_text('🟢')} <b>Earn Credit</b>\n\n"
        f"🔗 Your Referral Link:\n<code>{link}</code>\n\n"
        f"🟣 Share this — every friend who joins using it earns you <b>+1 credit</b>!\n"
        f"💳 Your current balance: <code>{'Unlimited' if (user_id == OWNER_ID or user_id in admin_ids) else get_user_credits(user_id)}</code> credits.",
        reply_markup=markup, parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: msg.text == "📱 Create Session")
def create_session(message):
    if not guard_user(message):
        return
    msg = bot.reply_to(
        message,
        f"{premium_text('📱')} Userbot Session Creator\n\n"
        "This logs into a Telegram account and gives you a session string "
        "that your uploaded userbot script can use.\n\n"
        "Send your <code>API_ID</code> (get it from my.telegram.org).\n"
        "<code>/cancel</code> to abort.",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, session_get_api_hash)

def session_get_api_hash(message):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        return
    try:
        api_id = int(message.text.strip())
    except:
        msg = bot.reply_to(message, "⚠️ API_ID must be a number. Send it again, or /cancel.")
        bot.register_next_step_handler(msg, session_get_api_hash)
        return
    msg = bot.reply_to(message, f"{premium_text('🔑')} Now send your <code>API_HASH</code>.\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, session_get_phone, api_id)

def session_get_phone(message, api_id):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        return
    api_hash = message.text.strip()
    msg = bot.reply_to(message, f"{premium_text('📞')} Send the phone number with country code (e.g. +919876543210).\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, session_send_code, api_id, api_hash)

def session_send_code(message, api_id, api_hash):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        return
    phone = message.text.strip()
    user_id = message.from_user.id
    wait_msg = bot.reply_to(message, f"{premium_text('⏳')} Sending OTP to that number...", parse_mode='HTML')
    try:
        from telethon.sync import TelegramClient
        from telethon.sessions import StringSession
        client = TelegramClient(StringSession(), api_id, api_hash)
        client.connect()
        sent = client.send_code_request(phone)
        session_data[user_id] = {
            'client': client, 'phone': phone, 'api_id': api_id,
            'api_hash': api_hash, 'phone_code_hash': sent.phone_code_hash
        }
        bot.edit_message_text(
            f"{premium_text('✅')} OTP sent! Enter the code you received.\n"
            "If Telegram shows it split like '1 2 3 4 5', just type it as <code>12345</code>.\n/cancel to abort.",
            wait_msg.chat.id, wait_msg.message_id, parse_mode='HTML'
        )
        bot.register_next_step_handler(message, session_verify_code, user_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error sending code: {e}", wait_msg.chat.id, wait_msg.message_id)

session_data = {}

def session_verify_code(message, user_id):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        session_data.pop(user_id, None)
        return
    entry = session_data.get(user_id)
    if not entry:
        bot.reply_to(message, "⚠️ Session expired. Start again.")
        return
    code = re.sub(r'\D', '', message.text or '')
    client = entry['client']
    try:
        from telethon.errors import SessionPasswordNeededError
        client.sign_in(entry['phone'], code, phone_code_hash=entry.get('phone_code_hash'))
        session_string = client.session.save()
        client.disconnect()
        save_user_session(user_id, session_string, entry['api_id'], entry['api_hash'], entry['phone'])
        session_data.pop(user_id, None)
        bot.reply_to(
            message,
            f"{premium_text('✅')} Session created and saved!\n\n"
            f"Your session string:\n<code>{session_string}</code>\n\n"
            "It's now available as <code>SESSION_STRING</code> environment variable.",
            parse_mode='HTML'
        )
    except SessionPasswordNeededError:
        msg = bot.reply_to(message, "🔒 Two-step verification enabled. Send the password.\n/cancel to abort.")
        bot.register_next_step_handler(msg, session_verify_password, user_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
        session_data.pop(user_id, None)

def session_verify_password(message, user_id):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        session_data.pop(user_id, None)
        return
    entry = session_data.get(user_id)
    if not entry:
        bot.reply_to(message, "⚠️ Session expired.")
        return
    password = message.text.strip()
    client = entry['client']
    try:
        client.sign_in(password=password)
        session_string = client.session.save()
        client.disconnect()
        save_user_session(user_id, session_string, entry['api_id'], entry['api_hash'], entry['phone'])
        session_data.pop(user_id, None)
        bot.reply_to(
            message,
            f"{premium_text('✅')} Session created and saved!\n\n"
            f"Your session string:\n<code>{session_string}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
        session_data.pop(user_id, None)

@bot.message_handler(func=lambda msg: msg.text == "📦 Install Pip")
def install_pip(message):
    if not guard_user(message):
        return
    msg = bot.reply_to(
        message,
        f"{premium_text('📦')} Send the pip package name to install on this bot's host (e.g. telethon, gTTS).\n/cancel to abort.",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_install_pip)

def process_install_pip(message):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Install cancelled.")
        return
    package_name = message.text.strip()
    if not re.match(r'^[A-Za-z0-9_\-\.\[\]=<>!,~+]+$', package_name):
        bot.reply_to(message, "⚠️ Invalid package name. Send it again, or /cancel.")
        return
    wait_msg = bot.reply_to(message, f"⏳ Installing <code>{package_name}</code>...", parse_mode='HTML')
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            capture_output=True, text=True, check=False, encoding='utf-8', errors='replace', timeout=300
        )
        if result.returncode == 0:
            tail = (result.stdout or "")[-800:]
            bot.edit_message_text(
                f"✅ Installed <code>{package_name}</code>.\n<code>{tail}</code>",
                wait_msg.chat.id, wait_msg.message_id, parse_mode='HTML'
            )
        else:
            tail = (result.stderr or result.stdout or "")[-800:]
            bot.edit_message_text(
                f"❌ Failed to install <code>{package_name}</code>.\n<code>{tail}</code>",
                wait_msg.chat.id, wait_msg.message_id, parse_mode='HTML'
            )
    except subprocess.TimeoutExpired:
        bot.edit_message_text(f"❌ Install timed out.", wait_msg.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", wait_msg.chat.id, wait_msg.message_id)

@bot.message_handler(func=lambda msg: msg.text == "🚫 Banned Files")
def banned_files(message):
    if not guard_user(message):
        return
    chat_id = message.chat.id
    banned = get_all_banned_files()
    if not banned:
        bot.reply_to(message, f"{premium_text('📂')} No files are currently banned.", parse_mode='HTML')
        return
    bot.reply_to(message, f"{premium_text('🚫')} Sending {len(banned)} banned file(s). These will auto-delete in 60 seconds.", parse_mode='HTML')
    sent_messages = []
    for file_name, file_content in banned:
        if not file_content:
            continue
        try:
            file_obj = io.BytesIO(file_content)
            file_obj.name = file_name or "banned_file"
            sent = bot.send_document(chat_id, file_obj)
            sent_messages.append(sent.message_id)
        except Exception as e:
            logger.error(f"Error sending banned file: {e}")
    
    def delete_after():
        time.sleep(60)
        for mid in sent_messages:
            try:
                bot.delete_message(chat_id, mid)
            except:
                pass
    if sent_messages:
        threading.Thread(target=delete_after, daemon=True).start()

# ============================================================
#  ADMIN COMMANDS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📊 Statistics")
def statistics(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    stats = f"""
{premium_border()}
   {premium_text('📊')} <b>BOT STATISTICS</b>
{premium_border()}

👥 Total Users: <code>{len(active_users)}</code>
📂 Total Files: <code>{sum(len(f) for f in user_files.values())}</code>
🟢 Running Bots: <code>{len(bot_scripts)}</code>
🔒 Bot Status: <code>{'🔴 Locked' if bot_locked else '🟢 Unlocked'}</code>
💳 Total Credits: <code>{sum(user_credits.values())}</code>
👑 Admins: <code>{len(admin_ids)}</code>
"""
    bot.reply_to(message, stats, parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "💳 Subscriptions")
def subscriptions_panel(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, f"{premium_text('💳')} Subscription Management", reply_markup=create_subscription_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "📢 Broadcast")
def broadcast_init(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    msg = bot.reply_to(message, f"{premium_text('📢')} Send message to broadcast to all active users.\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Broadcast cancelled.")
        return
    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video or message.document):
        bot.reply_to(message, "⚠️ Cannot broadcast empty message.")
        return
    target_count = len(active_users)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("🟢 Confirm", callback_data=f"confirm_broadcast_{message.message_id}"),
        InlineKeyboardButton("🔴 Cancel", callback_data="cancel_broadcast")
    )
    preview = broadcast_content[:1000] if broadcast_content else "(Media message)"
    bot.reply_to(
        message,
        f"⚠️ Confirm Broadcast:\n\n<code>{preview}</code>\n\nTo <b>{target_count}</b> users. Sure?",
        reply_markup=markup, parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: msg.text == "🔒 Lock Bot")
def lock_bot(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = not bot_locked
    save_setting("bot_locked", "1" if bot_locked else "0")
    status = "locked" if bot_locked else "unlocked"
    bot.reply_to(message, f"🔒 Bot has been {status}.")
    logger.warning(f"Bot {status} by {message.from_user.id}")

@bot.message_handler(func=lambda msg: msg.text == "🟢 Run All Scripts")
def run_all_scripts(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, "⏳ Starting all user scripts...")
    started = 0
    for uid, files in user_files.items():
        user_folder = get_user_folder(uid)
        for file_name, file_type in files:
            if not is_bot_running(uid, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, uid, user_folder, file_name, message)).start()
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, uid, user_folder, file_name, message)).start()
                        started += 1
                        time.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Error starting {file_name}: {e}")
    bot.reply_to(message, f"✅ Started {started} scripts.")

@bot.message_handler(func=lambda msg: msg.text == "👑 Admin Panel")
def admin_panel(message):
    if not guard_user(message):
        return
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, f"{premium_text('👑')} Admin Panel", reply_markup=create_admin_panel(), parse_mode='HTML')

# ============================================================
#  CALLBACK QUERY HANDLERS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    if check_force_join(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ You still need to join.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "✅ Membership verified.")
    bot.send_message(call.message.chat.id, "✅ You are verified. You can use the bot now.")


@bot.callback_query_handler(func=lambda call: call.data == "upload")
def upload_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.answer_callback_query(call.id, f"⚠️ File limit ({current_files}/{limit_str}) reached.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.reply_to(call.message, f"{premium_text('📤')} Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "check_files")
def check_files_callback(call):
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(files):
        is_running = is_bot_running(user_id, file_name)
        status = "🟢 Running" if is_running else "🔴 Stopped"
        markup.add(InlineKeyboardButton(f"{file_name} ({file_type}) - {status}", callback_data=f'file_{user_id}_{file_name}'))
    markup.add(InlineKeyboardButton(to_small_caps("Back"), callback_data='back_to_main'))
    try:
        bot.edit_message_text(
            f"{premium_text('📂')} Your files:\nClick to manage.",
            call.message.chat.id, call.message.message_id,
            reply_markup=markup, parse_mode='HTML'
        )
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('file_'))
def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ You can only manage your own files.", show_alert=True)
            return
        is_running = is_bot_running(script_owner_id, file_name)
        status = '🟢 Running' if is_running else '🔴 Stopped'
        file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), '?')
        bot.edit_message_text(
            f"⚙️ Controls for: <code>{file_name}</code> ({file_type}) of User <code>{script_owner_id}</code>\nStatus: {status}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def start_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, "⚠️ Already running.", show_alert=True)
            return
        file_path = os.path.join(get_user_folder(script_owner_id), file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, "⚠️ File missing.", show_alert=True)
            return
        file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), 'py')
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, get_user_folder(script_owner_id), file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, get_user_folder(script_owner_id), file_name, call.message)).start()
        bot.answer_callback_query(call.id, "✅ Starting...")
        time.sleep(1)
        is_running = is_bot_running(script_owner_id, file_name)
        status = '🟢 Running' if is_running else '🟡 Starting...'
        bot.edit_message_text(
            f"⚙️ Controls for: <code>{file_name}</code>\nStatus: {status}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def stop_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        bot.answer_callback_query(call.id, "✅ Stopped.")
        time.sleep(0.5)
        bot.edit_message_text(
            f"⚙️ Controls for: <code>{file_name}</code>\nStatus: 🔴 Stopped",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, False),
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('restart_'))
def restart_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        time.sleep(0.5)
        file_path = os.path.join(get_user_folder(script_owner_id), file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, "⚠️ File missing.", show_alert=True)
            return
        file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), 'py')
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, get_user_folder(script_owner_id), file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, get_user_folder(script_owner_id), file_name, call.message)).start()
        bot.answer_callback_query(call.id, "✅ Restarting...")
        time.sleep(1)
        is_running = is_bot_running(script_owner_id, file_name)
        status = '🟢 Running' if is_running else '🟡 Starting...'
        bot.edit_message_text(
            f"⚙️ Controls for: <code>{file_name}</code>\nStatus: {status}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        for path in [file_path, log_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        remove_user_file(script_owner_id, file_name)
        bot.answer_callback_query(call.id, "✅ Deleted.")
        bot.edit_message_text(
            f"🗑️ <code>{file_name}</code> deleted!",
            call.message.chat.id, call.message.message_id,
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('logs_'))
def logs_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, "⚠️ No logs found.", show_alert=True)
            return
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()[-3000:]
        bot.answer_callback_query(call.id)
        bot.reply_to(
            call.message,
            f"{premium_text('📜')} Logs for <code>{file_name}</code>:\n<code>{log_content or '(Empty)'}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "speed")
def speed_callback(call):
    start = time.time()
    bot.answer_callback_query(call.id)
    msg = bot.edit_message_text(f"{premium_text('🏃')} Testing speed...", call.message.chat.id, call.message.message_id, parse_mode='HTML')
    time.sleep(0.5)
    latency = round((time.time() - start) * 1000, 2)
    status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
    bot.edit_message_text(
        f"{premium_text('⚡')} Bot Speed & Status:\n\n⏱️ Latency: <code>{latency} ms</code>\n🚦 Status: <code>{status}</code>",
        call.message.chat.id, msg.message_id, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    credit_str = "Unlimited" if (user_id == OWNER_ID or user_id in admin_ids) else str(get_user_credits(user_id))
    is_premium = user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now()
    status_text = "⭐ Premium" if is_premium else "🆓 Free User"
    main_text = f"""
{premium_border()}
   {premium_text('🤖')} <b>𝐎𝐌𝐄𝐆𝐀 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐑𝐔𝐍𝐍𝐄𝐑</b> {premium_text('🤖')}
{premium_border()}

👋 Hey <b>{call.from_user.first_name}</b>!

🆔 User ID: <code>{user_id}</code>
✳️ Status: {status_text}
📁 Files: <code>{current_files} / {limit_str}</code>
💳 Credits: <code>{credit_str}</code>

👇 Tap a button below!
"""
    try:
        bot.edit_message_text(
            main_text,
            call.message.chat.id, call.message.message_id,
            reply_markup=create_main_menu_inline(user_id),
            parse_mode='HTML'
        )
    except:
        bot.send_message(call.message.chat.id, main_text, reply_markup=create_main_menu_inline(user_id), parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "send_command")
def send_command_callback(call):
    if not guard_user(call):
        return
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    running = [name for name, _ in files if is_bot_running(user_id, name)]
    if not running:
        bot.send_message(call.message.chat.id, "⚠️ No running scripts. Start a script first.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for name in running:
        markup.add(InlineKeyboardButton(f"🖥️ {name}", callback_data=f"cmdfile_{user_id}_{name}"))
    markup.add(InlineKeyboardButton(to_small_caps("Back"), callback_data="back_to_main"))
    bot.send_message(call.message.chat.id, "📨 Select a running script:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cmdfile_"))
def command_file_callback(call):
    try:
        _, uid_s, file_name = call.data.split("_", 2)
        uid = int(uid_s)
    except Exception:
        bot.answer_callback_query(call.id, "Invalid selection.", show_alert=True)
        return
    if call.from_user.id != uid and call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
        return
    if not is_bot_running(uid, file_name):
        bot.answer_callback_query(call.id, "⚠️ Script is not running.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"📨 Send command for <code>{html_escape(file_name)}</code>.\n/cancel to abort.", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_send_command, uid, file_name)


def process_send_command(message, uid, file_name):
    if message.text and message.text.strip().lower() == "/cancel":
        bot.reply_to(message, "❌ Cancelled.")
        return
    if message.from_user.id != uid and message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Permission denied.")
        return
    key = f"{uid}_{file_name}"
    info = bot_scripts.get(key)
    if not info or not is_bot_running(uid, file_name):
        bot.reply_to(message, "⚠️ Script is no longer running.")
        return
    command = message.text or ""
    if not command:
        bot.reply_to(message, "⚠️ Empty command.")
        return
    try:
        stdin = info["process"].stdin
        if stdin is None:
            raise RuntimeError("Script stdin is unavailable.")
        stdin.write(command + "\n")
        stdin.flush()
        bot.reply_to(message, f"✅ Command sent to <code>{html_escape(file_name)}</code>.", parse_mode="HTML")
    except Exception as exc:
        bot.reply_to(message, f"❌ Could not send command: <code>{html_escape(exc)}</code>", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "subscription")
def subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f"{premium_text('💳')} Subscription Management",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_subscription_menu(), parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    stats = f"""
{premium_border()}
   {premium_text('📊')} <b>BOT STATISTICS</b>
{premium_border()}

👥 Total Users: <code>{len(active_users)}</code>
📂 Total Files: <code>{sum(len(f) for f in user_files.values())}</code>
🟢 Running Bots: <code>{len(bot_scripts)}</code>
🔒 Bot Status: <code>{'🔴 Locked' if bot_locked else '🟢 Unlocked'}</code>
💳 Total Credits: <code>{sum(user_credits.values())}</code>
👑 Admins: <code>{len(admin_ids)}</code>
"""
    bot.edit_message_text(stats, call.message.chat.id, call.message.message_id, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "lock_bot")
def lock_bot_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    global bot_locked
    bot_locked = not bot_locked
    save_setting("bot_locked", "1" if bot_locked else "0")
    bot.answer_callback_query(call.id, "🔒 Bot locked." if bot_locked else "🔓 Bot unlocked.")
    logger.warning(f"Bot locked by {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def broadcast_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, f"{premium_text('📢')} Send message to broadcast.\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_broadcast)

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f"{premium_text('👑')} Admin Panel",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_admin_panel(), parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "run_all_scripts")
def run_all_scripts_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "⏳ Starting all...")
    started = 0
    for uid, files in user_files.items():
        user_folder = get_user_folder(uid)
        for file_name, file_type in files:
            if not is_bot_running(uid, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, uid, user_folder, file_name, call.message)).start()
                        started += 1
                        time.sleep(0.5)
                    except:
                        pass
    bot.reply_to(call.message, f"✅ Started {started} scripts.")

@bot.callback_query_handler(func=lambda call: call.data == "add_admin")
def add_admin_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "👑 Enter User ID to promote to Admin.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_admin)

def process_add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Owner only.")
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        new_admin = int(message.text.strip())
        if new_admin <= 0:
            raise ValueError
        if new_admin in admin_ids:
            bot.reply_to(message, f"⚠️ User <code>{new_admin}</code> is already admin.", parse_mode='HTML')
            return
        admin_ids.add(new_admin)
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (new_admin,))
            conn.commit()
            conn.close()
        bot.reply_to(message, f"✅ <code>{new_admin}</code> promoted to Admin.", parse_mode='HTML')
        try:
            bot.send_message(new_admin, f"🎉 You are now an Admin of {bot.get_me().first_name}!")
        except:
            pass
    except:
        bot.reply_to(message, "⚠️ Invalid User ID. Send a numeric ID.")

@bot.callback_query_handler(func=lambda call: call.data == "remove_admin")
def remove_admin_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "👑 Enter Admin User ID to remove.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_admin)

def process_remove_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Owner only.")
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        admin_id = int(message.text.strip())
        if admin_id == OWNER_ID:
            bot.reply_to(message, "⚠️ Cannot remove Owner.")
            return
        if admin_id not in admin_ids:
            bot.reply_to(message, f"⚠️ <code>{admin_id}</code> is not an admin.", parse_mode='HTML')
            return
        admin_ids.remove(admin_id)
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
            conn.commit()
            conn.close()
        bot.reply_to(message, f"✅ <code>{admin_id}</code> removed from Admins.", parse_mode='HTML')
        try:
            bot.send_message(admin_id, f"ℹ️ You are no longer an Admin of {bot.get_me().first_name}.")
        except:
            pass
    except:
        bot.reply_to(message, "⚠️ Invalid User ID.")

@bot.callback_query_handler(func=lambda call: call.data == "list_admins")
def list_admins_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    admin_list = "\n".join(f"👑 <code>{aid}</code> {'⭐ Owner' if aid == OWNER_ID else ''}" for aid in sorted(admin_ids))
    bot.edit_message_text(
        f"{premium_text('👑')} Admins:\n\n{admin_list}",
        call.message.chat.id, call.message.message_id,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "change_token")
def change_token_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "🔑 Enter new bot token (from BotFather).\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_change_token)

def process_change_token(message):
    if message.from_user.id != OWNER_ID:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    new_token = message.text.strip()
    if not re.match(r'^\d{6,}:[A-Za-z0-9_-]{30,}$', new_token):
        bot.reply_to(message, "⚠️ Invalid token format. Send again.")
        return
    # Update the active TeleBot instance and persist for the next restart.
    global BOT_TOKEN
    BOT_TOKEN = new_token
    bot.token = new_token
    save_setting("bot_token", new_token)
    bot.reply_to(message, "✅ Token updated for the running instance and saved. If polling does not reconnect cleanly, restart the bot.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "password_menu")
def password_menu_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f"{premium_text('🔐')} Password Protection",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_password_menu(), parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "password_on")
def password_on_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "🔑 Enter the password to set.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_set_password)

def process_set_password(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    global PASSWORD_ENABLED, BOT_PASSWORD
    BOT_PASSWORD = message.text.strip()
    PASSWORD_ENABLED = True
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)', ('password_enabled', '1'))
        c.execute('INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)', ('bot_password', BOT_PASSWORD))
        conn.commit()
        conn.close()
    bot.reply_to(message, "✅ Password protection is now ON.")

@bot.callback_query_handler(func=lambda call: call.data == "password_off")
def password_off_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    global PASSWORD_ENABLED, BOT_PASSWORD
    PASSWORD_ENABLED = False
    BOT_PASSWORD = None
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)', ('password_enabled', '0'))
        c.execute('DELETE FROM bot_settings WHERE key = ?', ('bot_password',))
        c.execute('DELETE FROM authorized_users')
        conn.commit()
        conn.close()
    bot.reply_to(call.message, "✅ Password protection is now OFF.")

@bot.callback_query_handler(func=lambda call: call.data == "channel_menu")
def channel_menu_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f"{premium_text('📢')} Force-Join Channel Management",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_channel_menu(), parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "add_channel")
def add_channel_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "📢 Send channel username (e.g. @channel) or link.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_channel)

def process_add_channel(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    channel = message.text.strip()
    channel = channel.replace('https://t.me/', '@').replace('t.me/', '@')
    if not channel.startswith('@'):
        channel = '@' + channel
    FORCE_JOIN_CHANNELS[channel] = channel
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO force_join_channels (channel, display_name, active) VALUES (?, ?, 1)',
                  (channel, channel))
        conn.commit()
        conn.close()
    bot.reply_to(message, f"✅ Added channel: {channel}")

@bot.callback_query_handler(func=lambda call: call.data == "remove_channel_list")
def remove_channel_list_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    if not FORCE_JOIN_CHANNELS:
        bot.reply_to(call.message, "📢 No channels added yet.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for ch in FORCE_JOIN_CHANNELS:
        markup.add(InlineKeyboardButton(f"❌ {ch}", callback_data=f'rmch_{ch}'))
    markup.add(InlineKeyboardButton(to_small_caps("Back"), callback_data='channel_menu'))
    bot.edit_message_text(
        f"{premium_text('📢')} Remove a channel:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('rmch_'))
def remove_channel_action_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    channel = call.data.replace('rmch_', '')
    FORCE_JOIN_CHANNELS.pop(channel, None)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM force_join_channels WHERE channel = ?', (channel,))
        conn.commit()
        conn.close()
    bot.answer_callback_query(call.id, f"✅ Removed {channel}")

@bot.callback_query_handler(func=lambda call: call.data == "toggle_host_approval")
def toggle_host_approval_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    global HOST_APPROVAL_ENABLED
    HOST_APPROVAL_ENABLED = not HOST_APPROVAL_ENABLED
    save_setting("host_approval_enabled", "1" if HOST_APPROVAL_ENABLED else "0")
    bot.answer_callback_query(call.id, "Updated.")
    try:
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id,
            reply_markup=create_channel_menu()
        )
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: call.data == "ban_file_init")
def ban_file_init_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "🚫 Send the file to ban.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_ban_file)

def process_ban_file(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    if not message.document:
        bot.reply_to(message, "⚠️ Send a file document.")
        return
    file_info = bot.get_file(message.document.file_id)
    file_content = bot.download_file(file_info.file_path)
    file_hash = hashlib.sha256(file_content).hexdigest()
    banned_file_hashes.add(file_hash)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO banned_files (file_hash, file_name, file_content, banned_by, banned_at) VALUES (?, ?, ?, ?, ?)',
                  (file_hash, message.document.file_name, sqlite3.Binary(file_content), message.from_user.id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    bot.reply_to(message, f"✅ File banned: {message.document.file_name}")

@bot.callback_query_handler(func=lambda call: call.data == "banned_files_admin_list")
def banned_files_admin_list_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    banned_files = get_all_banned_files_meta()
    if not banned_files:
        bot.reply_to(call.message, "📂 No banned files.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for fhash, fname in banned_files:
        short_id = fhash[:12]
        markup.add(InlineKeyboardButton(f"🚫 {fname[:20]}...", callback_data=f'unban_{short_id}'))
    markup.add(InlineKeyboardButton(to_small_caps("Back"), callback_data='admin_panel'))
    bot.edit_message_text(
        f"{premium_text('🚫')} Banned Files (tap to unban):",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode='HTML'
    )

def get_all_banned_files_meta():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT file_hash, file_name FROM banned_files')
    result = c.fetchall()
    conn.close()
    return result

def get_all_banned_files():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT file_name, file_content FROM banned_files')
    result = c.fetchall()
    conn.close()
    return result

@bot.callback_query_handler(func=lambda call: call.data.startswith('unban_'))
def unban_file_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    short_id = call.data.replace('unban_', '')
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT file_hash FROM banned_files WHERE file_hash LIKE ?', (short_id + '%',))
        row = c.fetchone()
        if row:
            c.execute('DELETE FROM banned_files WHERE file_hash = ?', (row[0],))
            banned_file_hashes.discard(row[0])
            conn.commit()
            bot.answer_callback_query(call.id, "✅ File unbanned.")
        else:
            bot.answer_callback_query(call.id, "⚠️ File not found.")
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data == "install_pip_init")
def install_pip_init_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, f"{premium_text('📦')} Send pip package name to install.\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_install_pip)

@bot.callback_query_handler(func=lambda call: call.data == "credit_menu")
def credit_menu_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "💳 Enter User ID to add credits.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_credits)

def process_add_credits(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        uid = int(message.text.strip())
        current = get_user_credits(uid)
        bot.reply_to(message, f"💳 User <code>{uid}</code> has <code>{current}</code> credits.\nHow many to add? (negative to deduct)", parse_mode='HTML')
        bot.register_next_step_handler(message, process_credit_amount, uid)
    except:
        bot.reply_to(message, "⚠️ Invalid User ID.")

def process_credit_amount(message, uid):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        amount = int(message.text.strip())
        new_total = add_user_credits(uid, amount)
        bot.reply_to(message, f"✅ <code>{uid}</code> now has <code>{new_total}</code> credits.", parse_mode='HTML')
        try:
            bot.send_message(uid, f"💳 Your credits have been updated. New balance: <code>{new_total}</code>", parse_mode='HTML')
        except:
            pass
    except:
        bot.reply_to(message, "⚠️ Invalid amount.")

@bot.callback_query_handler(func=lambda call: call.data == "reset_menu")
def reset_menu_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f"{premium_text('🔄')} Reset Menu",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_reset_menu(), parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "reset_files")
def reset_files_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("🟢 Confirm Delete All Files", callback_data="reset_files_confirm"),
        InlineKeyboardButton("🔴 Cancel", callback_data="reset_menu")
    )
    bot.edit_message_text(
        "⚠️ This will delete ALL uploaded files for ALL users.\nAre you sure?",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "reset_files_confirm")
def reset_files_confirm_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "🗑️ Deleting files...")
    deleted = 0
    for uid in list(user_files.keys()):
        user_folder = get_user_folder(uid)
        for file_name, _ in user_files.get(uid, []):
            file_path = os.path.join(user_folder, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted += 1
                except:
                    pass
            log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                except:
                    pass
            # Stop if running
            script_key = f"{uid}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                del bot_scripts[script_key]
    user_files.clear()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM user_files')
        conn.commit()
        conn.close()
    bot.reply_to(call.message, f"✅ Deleted {deleted} files.")

@bot.callback_query_handler(func=lambda call: call.data == "reset_stop")
def reset_stop_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("🟢 Confirm Stop All Scripts", callback_data="reset_stop_confirm"),
        InlineKeyboardButton("🔴 Cancel", callback_data="reset_menu")
    )
    bot.edit_message_text(
        "⚠️ This will stop ALL running scripts.\nAre you sure?",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "reset_stop_confirm")
def reset_stop_confirm_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner only.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "⏹️ Stopping all...")
    stopped = 0
    for script_key in list(bot_scripts.keys()):
        kill_process_tree(bot_scripts[script_key])
        del bot_scripts[script_key]
        stopped += 1
    bot.reply_to(call.message, f"✅ Stopped {stopped} scripts.")

@bot.callback_query_handler(func=lambda call: call.data == "my_credit")
def my_credit_callback(call):
    user_id = call.from_user.id
    if user_id == OWNER_ID or user_id in admin_ids:
        bot.answer_callback_query(call.id)
        bot.reply_to(call.message, f"{premium_text('💳')} My Credit\nBalance: <code>Unlimited</code> (Owner/Admin)", parse_mode='HTML')
        return
    balance = get_user_credits(user_id)
    bot.answer_callback_query(call.id)
    bot.reply_to(call.message, f"{premium_text('💳')} My Credit\nBalance: <code>{balance}</code> credits", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "earn_credit")
def earn_credit_callback(call):
    user_id = call.from_user.id
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    markup = InlineKeyboardMarkup(row_width=1)
    share_text = "🚀 Host your Python/JS bots for free! Join using my link:"
    share_url = f"https://t.me/share/url?url={link}&text={share_text}"
    markup.add(InlineKeyboardButton('🟢 Share with Friends', url=share_url))
    markup.add(InlineKeyboardButton(to_small_caps('Back'), callback_data='back_to_main'))
    bot.answer_callback_query(call.id)
    bot.reply_to(
        call.message,
        f"{premium_text('🟢')} <b>Earn Credit</b>\n\n"
        f"🔗 Your Referral Link:\n<code>{link}</code>\n\n"
        f"🟣 Share this — every friend who joins earns you *+1 credit*!\n"
        f"💳 Your balance: <code>{'Unlimited' if (user_id == OWNER_ID or user_id in admin_ids) else get_user_credits(user_id)}</code>",
        reply_markup=markup, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "add_subscription")
def add_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "💳 Enter User ID and days (e.g. `123456789 30`).\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_subscription)

def process_add_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    parts = message.text.strip().split()
    if len(parts) != 2:
        bot.reply_to(message, "⚠️ Format: `USER_ID DAYS`")
        return
    try:
        uid = int(parts[0])
        days = int(parts[1])
        expiry = datetime.now() + timedelta(days=days)
        save_subscription(uid, expiry)
        bot.reply_to(message, f"✅ Sub added for <code>{uid}</code> for {days} days.", parse_mode='HTML')
        try:
            bot.send_message(uid, f"🎉 Your subscription has been activated for {days} days!")
        except:
            pass
    except:
        bot.reply_to(message, "⚠️ Invalid input.")

@bot.callback_query_handler(func=lambda call: call.data == "remove_subscription")
def remove_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "💳 Enter User ID to remove subscription.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_subscription)

def process_remove_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        uid = int(message.text.strip())
        if uid in user_subscriptions:
            del user_subscriptions[uid]
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM subscriptions WHERE user_id = ?', (uid,))
                conn.commit()
                conn.close()
            bot.reply_to(message, f"✅ Sub removed for <code>{uid}</code>.", parse_mode='HTML')
            try:
                bot.send_message(uid, "ℹ️ Your subscription has been removed.")
            except:
                pass
        else:
            bot.reply_to(message, f"⚠️ <code>{uid}</code> has no active sub.", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Invalid User ID.")

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "💳 Enter User ID to check.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_check_subscription)

def process_check_subscription(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    try:
        uid = int(message.text.strip())
        if uid in user_subscriptions:
            expiry = user_subscriptions[uid].get('expiry')
            if expiry and expiry > datetime.now():
                days_left = (expiry - datetime.now()).days
                bot.reply_to(message, f"✅ <code>{uid}</code> has active sub. Expires: {expiry.strftime('%Y-%m-%d')} ({days_left} days left)", parse_mode='HTML')
            else:
                bot.reply_to(message, f"⚠️ <code>{uid}</code> has expired sub.", parse_mode='HTML')
                del user_subscriptions[uid]
        else:
            bot.reply_to(message, f"ℹ️ <code>{uid}</code> has no sub.", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Invalid User ID.")

# ============================================================
#  BROADCAST CALLBACKS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_broadcast_'))
def confirm_broadcast_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "🚀 Broadcasting...")
    original_msg_id = int(call.data.replace('confirm_broadcast_', ''))
    sent = 0
    failed = 0
    for uid in list(active_users):
        try:
            bot.forward_message(uid, call.message.chat.id, original_msg_id)
            sent += 1
            time.sleep(0.1)
        except:
            failed += 1
    bot.reply_to(call.message, f"✅ Broadcast sent to {sent} users. Failed: {failed}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id, "❌ Cancelled.")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "noop")
def noop_callback(call):
    bot.answer_callback_query(call.id)

# ============================================================
#  FILE UPLOAD HANDLER
# ============================================================
@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot is locked.")
        return
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(message, f"⚠️ File limit ({current_files}/{limit_str}) reached.")
        return
    
    doc = message.document
    file_name = doc.file_name
    if not file_name:
        bot.reply_to(message, "⚠️ No file name.")
        return
    
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip'] and user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Only .py, .js, .zip allowed.")
        return
    
    if doc.file_size > 20 * 1024 * 1024:
        bot.reply_to(message, "⚠️ File too large (Max 20MB).")
        return
    
    try:
        file_info = bot.get_file(doc.file_id)
        file_content = bot.download_file(file_info.file_path)
        
        # Check if file is banned
        file_hash = hashlib.sha256(file_content).hexdigest()
        if file_hash in banned_file_hashes:
            bot.reply_to(message, "🚫 This file has been banned and cannot be hosted.")
            return
        
        user_folder = get_user_folder(user_id)
        
        if file_ext == '.zip':
            # Extract zip
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, file_name)
                with open(zip_path, 'wb') as f:
                    f.write(file_content)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    extracted = safe_zip_members(zf, tmpdir)
                script_candidates = [
                    p for p in extracted
                    if os.path.splitext(p)[1].lower() in ('.py', '.js')
                ]
                preferred = ['main.py', 'bot.py', 'app.py', 'index.js', 'main.js']
                main_path = next(
                    (p for name in preferred for p in script_candidates
                     if os.path.basename(p).lower() == name),
                    script_candidates[0] if script_candidates else None
                )
                if main_path:
                    rel = os.path.relpath(main_path, tmpdir)
                    main_file = normalize_filename(os.path.basename(rel))
                    file_type = 'py' if main_file.lower().endswith('.py') else 'js'
                    dest_path = os.path.join(user_folder, main_file)
                    shutil.copy2(main_path, dest_path)
                    save_user_file(user_id, main_file, file_type)
                    bot.reply_to(message, f"✅ Extracted and saved: <code>{html_escape(main_file)}</code>", parse_mode='HTML')
                    if user_id in admin_ids or not HOST_APPROVAL_ENABLED:
                        start_hosting(
                            run_script if file_type == 'py' else run_js_script,
                            (dest_path, user_id, user_folder, main_file, message),
                            user_id, chat_id, main_file, message
                        )
                    else:
                        start_approval(
                            run_script if file_type == 'py' else run_js_script,
                            (dest_path, user_id, user_folder, main_file, message),
                            user_id, main_file, chat_id
                        )
                        bot.send_message(chat_id, "⏳ ZIP script is pending approval.")
                else:
                    bot.reply_to(message, "❌ No .py or .js file found in zip.")
        else:
            # Single file
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            file_type = 'py' if file_ext == '.py' else 'js'
            save_user_file(user_id, file_name, file_type)
            bot.reply_to(message, f"✅ File uploaded: {file_name}")
            
            # Auto-start if owner/admin or approval not needed
            if user_id in admin_ids or not HOST_APPROVAL_ENABLED:
                start_hosting(
                    run_script if file_type == 'py' else run_js_script,
                    (file_path, user_id, user_folder, file_name, message),
                    user_id, chat_id, file_name, message
                )
            else:
                start_approval(
                    run_script if file_type == 'py' else run_js_script,
                    (file_path, user_id, user_folder, file_name, message),
                    user_id, file_name, chat_id
                )
                bot.reply_to(message, "⏳ File uploaded and pending approval.")
                
    except Exception as e:
        bot.reply_to(message, f"❌ Upload error: {e}")
        logger.error(f"Upload error for {user_id}: {e}")

# ============================================================
#  APPROVAL CALLBACKS
# ============================================================
pending_approvals = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('apprv_'))
def approve_host_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    approval_id = call.data.replace('apprv_', '', 1)
    entry = pending_approvals.pop(approval_id, None)
    if not entry:
        bot.answer_callback_query(call.id, "⚠️ Request expired.")
        return
    bot.answer_callback_query(call.id, "✅ Approved.")
    try:
        uid = entry["uid"]
        file_name = entry["file_name"]
        chat_id = entry["chat_id"]
        # Charge one credit only when a non-admin request is actually approved.
        if uid not in admin_ids and uid != OWNER_ID:
            credits = get_user_credits(uid)
            if credits <= 0:
                bot.send_message(chat_id, f"❌ Approval granted, but user has no credits left for <code>{html_escape(file_name)}</code>.", parse_mode="HTML")
                bot.edit_message_text("❌ Approval failed: user has no credits.", call.message.chat.id, call.message.message_id)
                return
            set_user_credits(uid, credits - 1)
        threading.Thread(target=entry["run_func"], args=entry["run_args"], daemon=True).start()
        bot.send_message(chat_id, f"✅ Your file <code>{html_escape(file_name)}</code> has been approved and is now running.", parse_mode="HTML")
        bot.edit_message_text(f"✅ Approved: {html_escape(file_name)}", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as exc:
        logger.exception("Approval error")
        bot.reply_to(call.message, f"❌ Error: {html_escape(exc)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('rejct_'))
def reject_host_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    approval_id = call.data.replace('rejct_', '', 1)
    entry = pending_approvals.pop(approval_id, None)
    if not entry:
        bot.answer_callback_query(call.id, "⚠️ Request expired.")
        return
    bot.answer_callback_query(call.id, "❌ Rejected.")
    try:
        bot.send_message(
            entry["chat_id"],
            f"❌ Your file <code>{html_escape(entry['file_name'])}</code> was rejected.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    try:
        bot.edit_message_text(
            f"❌ Rejected: {html_escape(entry['file_name'])}",
            call.message.chat.id, call.message.message_id,
            parse_mode="HTML"
        )
    except Exception:
        pass


# ============================================================
#  CLEANUP
# ============================================================
def cleanup():
    logger.warning("Shutting down... Stopping all scripts.")
    for script_key, info in list(bot_scripts.items()):
        try:
            kill_process_tree(info)
        finally:
            bot_scripts.pop(script_key, None)
            try:
                info.get("log_file").close()
            except Exception:
                pass
atexit.register(cleanup)

# ============================================================
#  MAIN
# ============================================================
if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║      𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐑𝐔𝐍𝐍𝐄𝐑 — 𝐅𝐔𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐃𝐈𝐓𝐈𝐎𝐍     ║
╠══════════════════════════════════════════════════════════════╣
║  • Credit System + Subscriptions                           ║
║  • Session Strings (Telethon/Pyrogram)                    ║
║  • File Upload + Approval System                          ║
║  • Run/Stop/Logs/Speed/Status                             ║
║  • Premium Emojis + Colourful Buttons                     ║
║  • Force-Join Channels                                    ║
║  • Host Approval Toggle                                   ║
║  • Ban File System                                        ║
║  • Broadcast System                                       ║
║  • Admin Panel                                            ║
║  • Referral System                                        ║
║  • Auto Pip Install + NPM Support                         ║
║  • Developer: @SUNRAKUV2                                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    print(f"✅ Bot started: @{bot.get_me().username}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👥 Admins: {admin_ids}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30, skip_pending=True)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception("Polling error: %s", e)
            time.sleep(5)

# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐑𝐔𝐍𝐍𝐄𝐑 — 𝐅𝐔𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐃𝐈𝐓𝐈𝐎𝐍     ║
╠══════════════════════════════════════════════════════════════╣
║  • Credit System + Subscriptions                           ║
║  • Session Strings (Telethon/Pyrogram)                    ║
║  • File Upload + Approval System                          ║
║  • Run/Stop/Logs/Speed/Status                             ║
║  • View Logs + Send Input                                 ║
║  • AUTO INPUT FORWARDING                                  ║
║  • Premium Emojis + Serif Font Buttons                    ║
║  • Force-Join Channels                                    ║
║  • Host Approval Toggle                                   ║
║  • Ban File System                                        ║
║  • Broadcast System                                       ║
║  • Admin Panel                                            ║
║  • Referral System                                        ║
║  • Developer: @SUNRAKUV2                                  ║
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
#  PREMIUM EMOJI + SERIF FONT
# ============================================================
def serif(text):
    """Convert text to serif-style Unicode"""
    serif_map = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
        'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
        'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
        'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
        'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓',
        '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
    }
    return ''.join(serif_map.get(ch, ch) for ch in text)

def premium_text(text):
    """Add premium emoji style"""
    return text

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
user_inputs = {}  # 🔥 NEW: Track user inputs

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

# ============================================================
#  HELPER FUNCTIONS
# ============================================================
def html_escape(value):
    return html.escape(str(value), quote=False)

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in admin_ids

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
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO user_credits (user_id, credits) VALUES (?, ?)', (user_id, credits))
        user_credits[user_id] = credits

def add_user_credits(user_id, amount):
    new_total = max(0, get_user_credits(user_id) + amount)
    set_user_credits(user_id, new_total)
    return new_total

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

# ============================================================
#  SCRIPT RUNNER WITH INPUT FORWARDING
# ============================================================
bot_scripts = {}
script_logs = {}

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
        
        # 🔥 Start input listener thread
        def input_listener():
            while process.poll() is None:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    # Check if line contains input prompt
                    if 'input' in line.lower() or 'enter' in line.lower() or '?' in line:
                        # Send to user
                        try:
                            bot.send_message(
                                script_owner_id,
                                f"📨 <b>Input Required</b>\n\n"
                                f"<code>{line.strip()}</code>\n\n"
                                f"Reply to this message with your input.",
                                parse_mode='HTML'
                            )
                            # Store waiting input
                            user_inputs[script_owner_id] = {
                                'script_key': script_key,
                                'prompt': line.strip(),
                                'timestamp': time.time()
                            }
                        except:
                            pass
                except:
                    break
            log_file.close()
        
        threading.Thread(target=input_listener, daemon=True).start()
        
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
        
        # 🔥 JS input listener
        def input_listener():
            while process.poll() is None:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    if 'input' in line.lower() or 'enter' in line.lower() or '?' in line:
                        try:
                            bot.send_message(
                                script_owner_id,
                                f"📨 <b>Input Required</b>\n\n"
                                f"<code>{line.strip()}</code>\n\n"
                                f"Reply to this message with your input.",
                                parse_mode='HTML'
                            )
                            user_inputs[script_owner_id] = {
                                'script_key': script_key,
                                'prompt': line.strip(),
                                'timestamp': time.time()
                            }
                        except:
                            pass
                except:
                    break
            log_file.close()
        
        threading.Thread(target=input_listener, daemon=True).start()
        
        bot.reply_to(message_obj, f"✅ JS script `{file_name}` started!\n🆔 PID: {process.pid}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message_obj, f"❌ Failed to start script: {e}")

def get_run_env(user_id):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    session_string = get_user_session_string(user_id)
    if session_string:
        env["SESSION_STRING"] = session_string
        env["STRING_SESSION"] = session_string
    return env

def get_user_session_string(user_id):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT session_string FROM user_sessions WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_user_file(user_id, file_name, file_type):
    if user_id not in user_files:
        user_files[user_id] = []
    user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
    user_files[user_id].append((file_name, file_type))
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                     (user_id, file_name, file_type))

def remove_user_file(user_id, file_name):
    if user_id in user_files:
        user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
        with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
            conn.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def start_hosting(run_func, run_args, user_id, chat_id, file_name, message):
    # Run directly
    threading.Thread(target=run_func, args=run_args, daemon=True).start()

# ============================================================
#  MENU CREATION (SERIF FONT)
# ============================================================
def create_main_menu_inline(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(serif('Updates Channel'), url=UPDATE_CHANNEL),
        InlineKeyboardButton('🟢 ' + serif('Upload File'), callback_data='upload'),
        InlineKeyboardButton(serif('Check Files'), callback_data='check_files'),
        InlineKeyboardButton(serif('Bot Speed'), callback_data='speed'),
        InlineKeyboardButton(serif('Send Input'), callback_data='send_input'),
        InlineKeyboardButton(serif('View Logs'), callback_data='view_logs'),
        InlineKeyboardButton(serif('Contact Owner'), url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'),
        InlineKeyboardButton(serif('My Credit'), callback_data='my_credit'),
        InlineKeyboardButton(serif('Earn Credit'), callback_data='earn_credit')
    ]
    markup.add(buttons[0])
    markup.add(buttons[1], buttons[2])
    markup.add(buttons[3], buttons[4])
    markup.add(buttons[5], buttons[6])
    markup.add(buttons[7], buttons[8])
    
    if user_id in admin_ids:
        admin_buttons = [
            InlineKeyboardButton(serif('Subscriptions'), callback_data='subscription'),
            InlineKeyboardButton(serif('Statistics'), callback_data='stats'),
            InlineKeyboardButton('🔴 ' + serif('Lock Bot'), callback_data='lock_bot'),
            InlineKeyboardButton(serif('Broadcast'), callback_data='broadcast'),
            InlineKeyboardButton(serif('Admin Panel'), callback_data='admin_panel'),
            InlineKeyboardButton('🟢 ' + serif('Run All'), callback_data='run_all_scripts')
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
        ["⚡ Bot Speed", "📨 Send Input"],
        ["📜 View Logs", "📞 Contact Owner"],
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
            InlineKeyboardButton("🔴 " + serif('Stop'), callback_data=f'stop_{script_owner_id}_{file_name}'),
            InlineKeyboardButton(serif('Restart'), callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            InlineKeyboardButton("🗑️ " + serif('Delete'), callback_data=f'delete_{script_owner_id}_{file_name}'),
            InlineKeyboardButton(serif('Logs'), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
        markup.row(
            InlineKeyboardButton("📨 " + serif('Send Input'), callback_data=f'sendinput_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            InlineKeyboardButton("🟢 " + serif('Start'), callback_data=f'start_{script_owner_id}_{file_name}'),
            InlineKeyboardButton("🗑️ " + serif('Delete'), callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            InlineKeyboardButton(serif('Logs'), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 ' + serif('Add Admin'), callback_data='add_admin'),
        InlineKeyboardButton('🔴 ' + serif('Remove Admin'), callback_data='remove_admin')
    )
    markup.row(InlineKeyboardButton(serif('List Admins'), callback_data='list_admins'))
    markup.row(InlineKeyboardButton(serif('Change Token'), callback_data='change_token'))
    markup.row(
        InlineKeyboardButton(serif('Password'), callback_data='password_menu'),
        InlineKeyboardButton(serif('Channels'), callback_data='channel_menu')
    )
    markup.row(InlineKeyboardButton('🔴 ' + serif('Ban File'), callback_data='ban_file_init'))
    markup.row(InlineKeyboardButton(serif('Banned List'), callback_data='banned_files_admin_list'))
    markup.row(InlineKeyboardButton(serif('Install Pip'), callback_data='install_pip_init'))
    markup.row(InlineKeyboardButton(serif('Credits'), callback_data='credit_menu'))
    markup.row(InlineKeyboardButton(serif('Reset Menu'), callback_data='reset_menu'))
    markup.row(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    return markup

# ============================================================
#  COMMAND HANDLERS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    active_users.add(user_id)
    
    if get_user_credits(user_id) == 0:
        add_user_credits(user_id, 3)
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    credit_str = "Unlimited" if (user_id == OWNER_ID or user_id in admin_ids) else str(get_user_credits(user_id))
    
    is_premium = user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now()
    status_text = "⭐ Premium" if is_premium else "🆓 Free User"
    
    welcome_msg = f"""
🤖 <b>ULTIMATE RUNNER</b> 🤖

👋 Hey <b>{message.from_user.first_name}</b>!

🆔 User ID: <code>{user_id}</code>
✳️ Status: {status_text}
📁 Files: <code>{current_files} / {limit_str}</code>
💳 Credits: <code>{credit_str}</code>

👇 Tap a button below to get started!
"""
    bot.reply_to(message, welcome_msg, reply_markup=create_reply_keyboard(user_id), parse_mode='HTML')

# ============================================================
#  TEXT BUTTON HANDLERS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📢 Updates Channel")
def updates_channel(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(serif('Updates Channel'), url=UPDATE_CHANNEL))
    bot.reply_to(message, "📢 Visit our Updates Channel:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📤 Upload File")
def upload_file(message):
    user_id = message.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files first.", parse_mode='HTML')
        return
    bot.reply_to(message, "📤 Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.", parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "📂 Check Files")
def check_files(message):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.reply_to(message, "📂 Your files:\n\n(No files uploaded yet)", parse_mode='HTML')
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(files):
        is_running = is_bot_running(user_id, file_name)
        status = "🟢 Running" if is_running else "🔴 Stopped"
        markup.add(InlineKeyboardButton(f"{file_name} ({file_type}) - {status}", callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, "📂 Your files:\nClick to manage.", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "⚡ Bot Speed")
def bot_speed(message):
    start = time.time()
    msg = bot.reply_to(message, "🏃 Testing speed...")
    time.sleep(0.5)
    latency = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(
        f"⚡ Bot Speed & Status:\n\n⏱️ Latency: <code>{latency} ms</code>",
        msg.chat.id, msg.message_id, parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: msg.text == "📨 Send Input")
def send_input_button(message):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    running = [name for name, _ in files if is_bot_running(user_id, name)]
    if not running:
        bot.reply_to(message, "⚠️ No running scripts. Start a script first.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for name in running:
        markup.add(InlineKeyboardButton(f"📨 {name}", callback_data=f'sendinput_{user_id}_{name}'))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.reply_to(message, "📨 Select a running script to send input:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📜 View Logs")
def view_logs_button(message):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.reply_to(message, "📜 No files uploaded yet.")
        return
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(files):
        markup.add(InlineKeyboardButton(f"📜 {file_name}", callback_data=f'logs_{user_id}_{file_name}'))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.reply_to(message, "📜 Select a file to view logs:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📞 Contact Owner")
def contact_owner(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(serif('Contact Owner'), url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, "📞 CLICK TO CONTACT OWNER", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "💳 My Credit")
def my_credit(message):
    user_id = message.from_user.id
    if user_id == OWNER_ID or user_id in admin_ids:
        bot.reply_to(message, "💳 My Credit\nBalance: <code>Unlimited</code> (Owner/Admin)", parse_mode='HTML')
        return
    balance = get_user_credits(user_id)
    bot.reply_to(message, f"💳 My Credit\nBalance: <code>{balance}</code> credits\n(1 credit = 24 hrs hosting)", parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "🟢 Earn Credit")
def earn_credit(message):
    user_id = message.from_user.id
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    markup = InlineKeyboardMarkup(row_width=1)
    share_url = f"https://t.me/share/url?url={link}&text=🚀 Host your Python/JS bots for free! Join using my link:"
    markup.add(InlineKeyboardButton('🟢 Share with Friends', url=share_url))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.reply_to(
        message,
        f"🟢 <b>Earn Credit</b>\n\n"
        f"🔗 Your Referral Link:\n<code>{link}</code>\n\n"
        f"🟣 Share this — every friend who joins earns you <b>+1 credit</b>!\n"
        f"💳 Your current balance: <code>{'Unlimited' if (user_id == OWNER_ID or user_id in admin_ids) else get_user_credits(user_id)}</code> credits.",
        reply_markup=markup, parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: msg.text == "📱 Create Session")
def create_session(message):
    msg = bot.reply_to(
        message,
        "📱 Userbot Session Creator\n\n"
        "Send your <code>API_ID</code> (get it from my.telegram.org).\n"
        "<code>/cancel</code> to abort.",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, session_get_api_hash)

@bot.message_handler(func=lambda msg: msg.text == "📦 Install Pip")
def install_pip(message):
    msg = bot.reply_to(
        message,
        "📦 Send the pip package name to install (e.g. telethon, gTTS).\n/cancel to abort.",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_install_pip)

@bot.message_handler(func=lambda msg: msg.text == "🚫 Banned Files")
def banned_files(message):
    bot.reply_to(message, "🚫 Banned files feature active. Admin can ban/unban files.")

# ============================================================
#  ADMIN COMMANDS
# ============================================================
@bot.message_handler(func=lambda msg: msg.text == "📊 Statistics")
def statistics(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    stats = f"""
📊 <b>BOT STATISTICS</b>

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
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, "💳 Subscription Management", reply_markup=create_subscription_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda msg: msg.text == "📢 Broadcast")
def broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    msg = bot.reply_to(message, "📢 Send message to broadcast to all active users.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast)

@bot.message_handler(func=lambda msg: msg.text == "🔒 Lock Bot")
def lock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = not bot_locked
    save_setting("bot_locked", "1" if bot_locked else "0")
    status = "locked" if bot_locked else "unlocked"
    bot.reply_to(message, f"🔒 Bot has been {status}.")

@bot.message_handler(func=lambda msg: msg.text == "🟢 Run All Scripts")
def run_all_scripts(message):
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
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, "👑 Admin Panel", reply_markup=create_admin_panel(), parse_mode='HTML')

# ============================================================
#  SESSION HANDLERS
# ============================================================
session_data = {}

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
    msg = bot.reply_to(message, "🔑 Now send your <code>API_HASH</code>.\n/cancel to abort.", parse_mode='HTML')
    bot.register_next_step_handler(msg, session_get_phone, api_id)

def session_get_phone(message, api_id):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        return
    api_hash = message.text.strip()
    msg = bot.reply_to(message, "📞 Send the phone number with country code (e.g. +919876543210).\n/cancel to abort.")
    bot.register_next_step_handler(msg, session_send_code, api_id, api_hash)

def session_send_code(message, api_id, api_hash):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Session creation cancelled.")
        return
    phone = message.text.strip()
    user_id = message.from_user.id
    wait_msg = bot.reply_to(message, "⏳ Sending OTP to that number...")
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
            "✅ OTP sent! Enter the code you received.\n"
            "If Telegram shows it split like '1 2 3 4 5', just type it as <code>12345</code>.\n/cancel to abort.",
            wait_msg.chat.id, wait_msg.message_id, parse_mode='HTML'
        )
        bot.register_next_step_handler(message, session_verify_code, user_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error sending code: {e}", wait_msg.chat.id, wait_msg.message_id)

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
            f"✅ Session created and saved!\n\n"
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
            f"✅ Session created and saved!\n\n"
            f"Your session string:\n<code>{session_string}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
        session_data.pop(user_id, None)

def save_user_session(user_id, session_string, api_id, api_hash, phone):
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO user_sessions (user_id, session_string, api_id, api_hash, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                     (user_id, session_string, str(api_id), api_hash, phone, datetime.now().isoformat()))

def process_install_pip(message):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Install cancelled.")
        return
    package_name = message.text.strip()
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

def process_broadcast(message):
    if message.from_user.id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Broadcast cancelled.")
        return
    broadcast_content = message.text
    sent = 0
    failed = 0
    for uid in list(active_users):
        try:
            bot.send_message(uid, broadcast_content)
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    bot.reply_to(message, f"✅ Broadcast sent to {sent} users. Failed: {failed}")

def save_setting(key, value):
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)', (key, str(value)))

def create_subscription_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 ' + serif('Add Subscription'), callback_data='add_subscription'),
        InlineKeyboardButton('🔴 ' + serif('Remove Subscription'), callback_data='remove_subscription')
    )
    markup.row(InlineKeyboardButton(serif('Check Subscription'), callback_data='check_subscription'))
    markup.row(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    return markup

# ============================================================
#  🔥 INPUT FORWARDING — MAIN LOGIC
# ============================================================
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_user_input(message):
    user_id = message.from_user.id
    
    # 🔥 Check if user is waiting for input
    if user_id in user_inputs:
        input_data = user_inputs[user_id]
        script_key = input_data['script_key']
        
        if script_key in bot_scripts:
            process = bot_scripts[script_key]['process']
            try:
                if process.stdin:
                    process.stdin.write(message.text + '\n')
                    process.stdin.flush()
                    
                    # Send confirmation
                    bot.reply_to(
                        message,
                        f"✅ Input sent to script!\n\n"
                        f"📨 <code>{message.text[:100]}</code>",
                        parse_mode='HTML'
                    )
                    
                    # Remove from waiting
                    del user_inputs[user_id]
                    
                    # Log the input
                    logger.info(f"Input sent to {script_key}: {message.text[:50]}")
                else:
                    bot.reply_to(message, "❌ Script stdin is not available.")
            except Exception as e:
                bot.reply_to(message, f"❌ Failed to send input: {e}")
        else:
            bot.reply_to(message, "❌ Script is no longer running.")
            del user_inputs[user_id]
        return
    
    # 🔥 If not waiting for input, check if it's a command
    # (Other message handlers will handle commands)

# ============================================================
#  CALLBACK QUERY HANDLERS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    credit_str = "Unlimited" if (user_id == OWNER_ID or user_id in admin_ids) else str(get_user_credits(user_id))
    is_premium = user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now()
    status_text = "⭐ Premium" if is_premium else "🆓 Free User"
    main_text = f"""
🤖 <b>ULTIMATE RUNNER</b> 🤖

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
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "upload")
def upload_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📤 Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.", parse_mode='HTML')

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
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    try:
        bot.edit_message_text(
            "📂 Your files:\nClick to manage.",
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
            # Clean up input waiting
            for uid in list(user_inputs.keys()):
                if user_inputs[uid]['script_key'] == script_key:
                    del user_inputs[uid]
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
            for uid in list(user_inputs.keys()):
                if user_inputs[uid]['script_key'] == script_key:
                    del user_inputs[uid]
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
            for uid in list(user_inputs.keys()):
                if user_inputs[uid]['script_key'] == script_key:
                    del user_inputs[uid]
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
        bot.send_message(
            call.message.chat.id,
            f"📜 Logs for <code>{file_name}</code>:\n<code>{log_content or '(Empty)'}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sendinput_'))
def send_input_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if user_id != script_owner_id and user_id not in admin_ids:
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        if not is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, "⚠️ Script is not running.", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            f"📨 Send input for <code>{file_name}</code>.\n/cancel to abort.",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_send_input, script_owner_id, file_name)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

def process_send_input(message, script_owner_id, file_name):
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        return
    if message.from_user.id != script_owner_id and message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Permission denied.")
        return
    script_key = f"{script_owner_id}_{file_name}"
    if script_key not in bot_scripts:
        bot.reply_to(message, "⚠️ Script is not running.")
        return
    process = bot_scripts[script_key]['process']
    try:
        if process.stdin:
            process.stdin.write(message.text + '\n')
            process.stdin.flush()
            bot.reply_to(message, f"✅ Input sent to <code>{file_name}</code>.\n📨 <code>{message.text[:100]}</code>", parse_mode='HTML')
            logger.info(f"Manual input sent to {script_key}: {message.text[:50]}")
        else:
            bot.reply_to(message, "❌ Script stdin is not available.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to send input: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "send_input")
def send_input_callback_main(call):
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    running = [name for name, _ in files if is_bot_running(user_id, name)]
    if not running:
        bot.answer_callback_query(call.id, "⚠️ No running scripts.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for name in running:
        markup.add(InlineKeyboardButton(f"📨 {name}", callback_data=f'sendinput_{user_id}_{name}'))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.send_message(call.message.chat.id, "📨 Select a running script:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_logs")
def view_logs_callback_main(call):
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(files):
        markup.add(InlineKeyboardButton(f"📜 {file_name}", callback_data=f'logs_{user_id}_{file_name}'))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.send_message(call.message.chat.id, "📜 Select a file to view logs:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "speed")
def speed_callback(call):
    start = time.time()
    bot.answer_callback_query(call.id)
    time.sleep(0.3)
    latency = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(
        f"⚡ Bot Speed:\n\n⏱️ Latency: <code>{latency} ms</code>",
        call.message.chat.id, call.message.message_id, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "my_credit")
def my_credit_callback(call):
    user_id = call.from_user.id
    if user_id == OWNER_ID or user_id in admin_ids:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 My Credit\nBalance: <code>Unlimited</code> (Owner/Admin)", parse_mode='HTML')
        return
    balance = get_user_credits(user_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"💳 My Credit\nBalance: <code>{balance}</code> credits", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "earn_credit")
def earn_credit_callback(call):
    user_id = call.from_user.id
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    markup = InlineKeyboardMarkup(row_width=1)
    share_url = f"https://t.me/share/url?url={link}&text=🚀 Host your Python/JS bots for free! Join using my link:"
    markup.add(InlineKeyboardButton('🟢 Share with Friends', url=share_url))
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='back_to_main'))
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"🟢 <b>Earn Credit</b>\n\n"
        f"🔗 Your Referral Link:\n<code>{link}</code>\n\n"
        f"💳 Your balance: <code>{'Unlimited' if (user_id == OWNER_ID or user_id in admin_ids) else get_user_credits(user_id)}</code>",
        reply_markup=markup, parse_mode='HTML'
    )

# ============================================================
#  ADMIN CALLBACKS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "subscription")
def subscription_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "💳 Subscription Management",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_subscription_menu(), parse_mode='HTML'
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

def save_subscription(user_id, expiry):
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry.isoformat()))
    user_subscriptions[user_id] = {'expiry': expiry}

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
            with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
                conn.execute('DELETE FROM subscriptions WHERE user_id = ?', (uid,))
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

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    stats = f"""
📊 <b>BOT STATISTICS</b>

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

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def broadcast_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "📢 Send message to broadcast.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast)

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "👑 Admin Panel",
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
        with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
            conn.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (new_admin,))
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
        with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
            conn.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
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
        f"👑 Admins:\n\n{admin_list}",
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
    global BOT_TOKEN
    BOT_TOKEN = new_token
    bot.token = new_token
    save_setting("bot_token", new_token)
    bot.reply_to(message, "✅ Token updated for the running instance and saved.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "password_menu")
def password_menu_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "🔐 Password Protection",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_password_menu(), parse_mode='HTML'
    )

def create_password_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    status = "🟢 ON" if PASSWORD_ENABLED else "🔴 OFF"
    markup.row(InlineKeyboardButton(f'Status: {status}', callback_data='noop'))
    markup.row(
        InlineKeyboardButton('🟢 Turn ON', callback_data='password_on'),
        InlineKeyboardButton('🔴 Turn OFF', callback_data='password_off')
    )
    markup.row(InlineKeyboardButton(serif('Back'), callback_data='admin_panel'))
    return markup

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
    save_setting("password_enabled", "1")
    save_setting("bot_password", BOT_PASSWORD)
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
    save_setting("password_enabled", "0")
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('DELETE FROM bot_settings WHERE key = ?', ('bot_password',))
        conn.execute('DELETE FROM authorized_users')
    bot.reply_to(call.message, "✅ Password protection is now OFF.")

@bot.callback_query_handler(func=lambda call: call.data == "channel_menu")
def channel_menu_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "📢 Force-Join Channel Management",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_channel_menu(), parse_mode='HTML'
    )

def create_channel_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton('🟢 Add Channel', callback_data='add_channel'),
        InlineKeyboardButton('🔴 Remove Channel', callback_data='remove_channel_list')
    )
    markup.row(InlineKeyboardButton(serif('Back'), callback_data='admin_panel'))
    return markup

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
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO force_join_channels (channel, display_name, active) VALUES (?, ?, 1)',
                     (channel, channel))
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
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='channel_menu'))
    bot.edit_message_text(
        "📢 Remove a channel:",
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
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('DELETE FROM force_join_channels WHERE channel = ?', (channel,))
    bot.answer_callback_query(call.id, f"✅ Removed {channel}")

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
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('INSERT OR REPLACE INTO banned_files (file_hash, file_name, file_content, banned_by, banned_at) VALUES (?, ?, ?, ?, ?)',
                     (file_hash, message.document.file_name, sqlite3.Binary(file_content), message.from_user.id, datetime.now().isoformat()))
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
    markup.add(InlineKeyboardButton(serif('Back'), callback_data='admin_panel'))
    bot.edit_message_text(
        "🚫 Banned Files (tap to unban):",
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('unban_'))
def unban_file_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    short_id = call.data.replace('unban_', '')
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
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

@bot.callback_query_handler(func=lambda call: call.data == "install_pip_init")
def install_pip_init_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    msg = bot.reply_to(call.message, "📦 Send pip package name to install.\n/cancel to abort.")
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
        "🔄 Reset Menu",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_reset_menu(), parse_mode='HTML'
    )

def create_reset_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(serif('Reset Files'), callback_data='reset_files'),
        InlineKeyboardButton(serif('Reset Stop'), callback_data='reset_stop')
    )
    status = "🟢 ON" if HOST_APPROVAL_ENABLED else "🔴 OFF"
    markup.row(InlineKeyboardButton(f"Host Approval: {status}", callback_data="toggle_host_approval"))
    markup.row(InlineKeyboardButton(serif('Back'), callback_data='admin_panel'))
    return markup

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
            script_key = f"{uid}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                for uid2 in list(user_inputs.keys()):
                    if user_inputs[uid2]['script_key'] == script_key:
                        del user_inputs[uid2]
                del bot_scripts[script_key]
    user_files.clear()
    with sqlite3.connect(DATABASE_PATH, check_same_thread=False) as conn:
        conn.execute('DELETE FROM user_files')
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
        for uid in list(user_inputs.keys()):
            if user_inputs[uid]['script_key'] == script_key:
                del user_inputs[uid]
        del bot_scripts[script_key]
        stopped += 1
    bot.reply_to(call.message, f"✅ Stopped {stopped} scripts.")

@bot.callback_query_handler(func=lambda call: call.data == "toggle_host_approval")
def toggle_host_approval_callback(call):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    global HOST_APPROVAL_ENABLED
    HOST_APPROVAL_ENABLED = not HOST_APPROVAL_ENABLED
    save_setting("host_approval_enabled", "1" if HOST_APPROVAL_ENABLED else "0")
    bot.answer_callback_query(call.id, "Updated.")

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
        
        file_hash = hashlib.sha256(file_content).hexdigest()
        if file_hash in banned_file_hashes:
            bot.reply_to(message, "🚫 This file has been banned and cannot be hosted.")
            return
        
        user_folder = get_user_folder(user_id)
        
        if file_ext == '.zip':
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, file_name)
                with open(zip_path, 'wb') as f:
                    f.write(file_content)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    safe_zip_members(zf, tmpdir)
                script_candidates = [p for p in os.listdir(tmpdir) if os.path.splitext(p)[1].lower() in ('.py', '.js')]
                preferred = ['main.py', 'bot.py', 'app.py', 'index.js', 'main.js']
                main_file = next((p for name in preferred for p in script_candidates if p == name), script_candidates[0] if script_candidates else None)
                if main_file:
                    main_path = os.path.join(tmpdir, main_file)
                    file_type = 'py' if main_file.endswith('.py') else 'js'
                    dest_path = os.path.join(user_folder, main_file)
                    shutil.copy2(main_path, dest_path)
                    save_user_file(user_id, main_file, file_type)
                    bot.reply_to(message, f"✅ Extracted and saved: <code>{main_file}</code>", parse_mode='HTML')
                    if user_id in admin_ids or not HOST_APPROVAL_ENABLED:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(dest_path, user_id, user_folder, main_file, message)).start()
                        else:
                            threading.Thread(target=run_js_script, args=(dest_path, user_id, user_folder, main_file, message)).start()
                    else:
                        bot.reply_to(message, "⏳ ZIP script pending approval.")
                else:
                    bot.reply_to(message, "❌ No .py or .js file found in zip.")
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            file_type = 'py' if file_ext == '.py' else 'js'
            save_user_file(user_id, file_name, file_type)
            bot.reply_to(message, f"✅ File uploaded: {file_name}")
            
            if user_id in admin_ids or not HOST_APPROVAL_ENABLED:
                if file_type == 'py':
                    threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                else:
                    threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
            else:
                bot.reply_to(message, "⏳ File uploaded and pending approval.")
                
    except Exception as e:
        bot.reply_to(message, f"❌ Upload error: {e}")
        logger.error(f"Upload error for {user_id}: {e}")

def safe_zip_members(zf, destination):
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
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with zf.open(info, "r") as src_file, open(out, "wb") as dst_file:
            shutil.copyfileobj(src_file, dst_file)
    return True

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
║  • View Logs + Send Input                                 ║
║  • AUTO INPUT FORWARDING                                 ║
║  • Premium Emojis + Serif Font Buttons                    ║
║  • Force-Join Channels                                    ║
║  • Host Approval Toggle                                   ║
║  • Ban File System                                        ║
║  • Broadcast System                                       ║
║  • Admin Panel                                            ║
║  • Referral System                                        ║
║  • Developer: @SUNRAKUV2                                    ║
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

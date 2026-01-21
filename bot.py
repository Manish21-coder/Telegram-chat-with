import os
import pandas as pd
from telethon import TelegramClient, events, Button
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio

# --- CONFIGURATION ---
API_ID = "20076810"
API_HASH = "7091c0a629f422f0336fd89298ef9932"
BOT_TOKEN = "7633409724:AxAHTqXO9cbRyH3g_018Bb_YmYcwKQvygqOY"

# Folder where data will be stored
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USERS_FILE = os.path.join(DATA_FOLDER, "users.csv")
SUBS_FILE = os.path.join(DATA_FOLDER, "subscribers.csv")
LINKS_FILE = os.path.join(DATA_FOLDER, "links.csv")

bot = TelegramClient("VedantuBot", API_ID, API_HASH)
scheduler = AsyncIOScheduler()

# --- LOCAL DATABASE HELPERS ---
def initialize_csv(file_path, columns):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)
        print(f"Initialized {file_path}")

# Initialize files if they don't exist
initialize_csv(USERS_FILE, ["user_id", "username", "first_name", "last_name", "created_at"])
initialize_csv(SUBS_FILE, ["user_id", "username", "first_name", "last_name", "created_at"])
if not os.path.exists(LINKS_FILE):
    # Create a dummy links file so the code doesn't crash
    pd.DataFrame(columns=["date", "link"]).to_csv(LINKS_FILE, index=False)

# --- BOT LOGIC ---

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await insert_user(event)
    buttons = [
        [Button.inline("📩 Daily NEET Material", data="daily_neet_material")],
        [Button.inline("📖 NEET Syllabus", data="syllabus")],
        [Button.inline("📅 Study Plan", data="study_plan"), Button.inline("🧠 Revision", data="revision")],
        [Button.inline("📝 PYQ Test", data="pyq_test"), Button.inline("🧪 Mock Test", data="mock_test")],
        [Button.inline("❓ Join Free Quiz", data="quiz"), Button.inline("📚 Courses", data="courses")],
        [Button.url("🏥 Medical Colleges List", "https://vdnt.in/Fs292")],
        [Button.inline("📝 Important Questions", data="important_questions")]
    ]
    await bot.send_message(event.chat_id, "🔬 **Welcome to Vedantu NEET Bot!**\nPick a resource to start:", buttons=buttons)

async def send_message_with_back(chat_id, text, buttons):
    buttons.append([Button.inline("🔙 Back to Main Menu", data="main_menu")])
    await bot.send_message(chat_id, text, buttons=buttons, parse_mode="markdown")

async def insert_user(event):
    user = await event.get_sender()
    df = pd.read_csv(USERS_FILE)
    if user.id not in df["user_id"].values:
        new_user = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": datetime.now()
        }
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        df.to_csv(USERS_FILE, index=False)

@bot.on(events.CallbackQuery(data=b'subscribe'))
async def subscribe(event):
    user = await event.get_sender()
    df = pd.read_csv(SUBS_FILE)
    if user.id not in df["user_id"].values:
        new_sub = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": datetime.now()
        }
        df = pd.concat([df, pd.DataFrame([new_sub])], ignore_index=True)
        df.to_csv(SUBS_FILE, index=False)
        msg = "✅ Success! You will now receive daily NEET resources."
    else:
        msg = "ℹ️ You are already subscribed!"
    await send_message_with_back(event.chat_id, msg, [])

# --- DAILY SCHEDULER TASK ---
async def send_daily_resource():
    print(f"Running daily task at {datetime.now()}")
    if not os.path.exists(LINKS_FILE) or not os.path.exists(SUBS_FILE):
        return

    links_df = pd.read_csv(LINKS_FILE)
    subs_df = pd.read_csv(SUBS_FILE)
    today_str = str(datetime.today().date())

    # Find the link for today
    today_data = links_df[links_df["date"] == today_str]
    
    if not today_data.empty:
        link = today_data.iloc[0]["link"]
        buttons = [[Button.url("🚀 Open Today's Resource", link)]]
        
        for _, row in subs_df.iterrows():
            try:
                await bot.send_message(int(row["user_id"]), f"☀️ **Good Morning {row['first_name']}!**\nHere is your daily resource:", buttons=buttons)
            except Exception as e:
                print(f"Could not send to {row['user_id']}: {e}")
    else:
        print("No link found for today in links.csv")

# --- OTHER HANDLERS (Syllabus, Quiz, etc.) ---
@bot.on(events.CallbackQuery(data="main_menu"))
async def back_to_start(event):
    await start(event)

@bot.on(events.CallbackQuery(data=b'daily_neet_material'))
async def daily_neet_material(event):
    await send_message_with_back(event.chat_id, "Get daily study guides and master essential formulas!", [[Button.inline("Subscribe for Daily Updates", b"subscribe")]])

# Add your other button handlers (syllabus, revision, etc.) here...

# --- MAIN EXECUTION ---
scheduler.add_job(send_daily_resource, trigger="cron", hour=5, minute=0) # 5 AM

async def main():
    scheduler.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is live...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
from telethon import TelegramClient, events, Button
import pandas as pd
from download_from_gdrive import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio


API_ID = "20076810"
API_HASH = "7091c0a629f422f0336fd89298ef9932"
BOT_TOKEN = "7633409724:AxAHTqXO9cbRyH3g_018Bb_YmYcwKQvygqOY"

bot = TelegramClient("VedantuBot", API_ID, API_HASH)
scheduler = AsyncIOScheduler()
gdrive_service = get_drive_service()


# Start command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    chat_id = event.chat_id
    await insert_user(event)
    await bot.send_message(
        chat_id,
        "🔬 **Crack NEET with VedantuNEETBot!** 🤖\n"
        "Your study buddy to help you score higher! 📈📚\n\n"
        "I’ll help you:\n"
        "✅ Practice with fun quizzes & mock tests\n"
        "✅ Revise daily with mind maps & study plans\n"
        "✅ Learn expert tips and notes\n"
        "✅ Join top NEET courses made just for you!\n\n"
        "👇 **Ready to begin? Tap a button to start:**",
        buttons=[
            [Button.inline("📩 Daily NEET Test, Notes & Much More", data="daily_neet_material")],
            [Button.inline("📖 Get NEET Syllabus", data="syllabus")],
            [Button.inline("📅 Daily Study Plan", data="study_plan"), Button.inline("🧠 Revision & Mind Maps", data="revision")],
            [Button.inline("📘 Must-Solves + Rank Predictor", data="must_solve")],
            [Button.inline("📝 Take FREE PYQ Test", data="pyq_test"), Button.inline("🧪 Free NEET Mock Test", data="mock_test")],
            [Button.inline("🎓 Expert Tips & Study Guides", data="study_guides")],
            [Button.inline("❓ Join Free Quiz", data="quiz"), Button.inline("📚 Explore NEET Courses", data="courses")],
            [Button.url("🏥 Detailed List of Medical Colleges in India", "https://vdnt.in/Fs292")],
            [Button.inline("📝 Important Questions", data="important_questions")]
        ],
        parse_mode="markdown"
    )

# Separate methods for each button with a "Back to Main Menu" button

async def send_message_with_back(chat_id, text, buttons):
    buttons.append([Button.inline("🔙 Back to Main Menu", data="main_menu")])
    buttons.append([Button.inline("📚 Explore NEET Courses", data="courses")])
    await bot.send_message(chat_id, text, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(data=b"important_questions"))
async def important_questions(event):
    message = "**Here are your important questions**"
    buttons = [
        [Button.url("500 Most difficult questions", "https://vdnt.in/Fw6Nx")],
        [Button.url("FREE 500 Most Important PYQs", "https://vdnt.in/Fw71E")],
        [Button.url("All India Rank & College Predictor", "https://www.vedantu.com/neet/rank-predictor")],
        [Button.url("NEET 2024 Free Answer Keys", "https://docs.google.com/document/d/1FLrfDeqowXhm4oNA04ac3pDI5QX4AcLG2uzkAEsNuBo/edit")]
    ]
    await send_message_with_back(event.chat_id, message, buttons)

@bot.on(events.CallbackQuery(data=b'daily_neet_material'))
async def daily_neet_material(event):
    message = f"""
📖 Daily NEET Resources ! 📩
💡 Supercharge your prep with expert-selected daily study resources! Pick what you need and stay on track.
📖 Daily Study Guide – Get expert-curated tips & strategies for smarter prep.
🧮 Formula of the Day – Master essential formulas effortlessly.
🎥 Concept Video of the Day – Understand tricky topics with expert breakdowns.
📄 Chapter-Specific Notes – Get concise, high-value revision notes.
📝 Mock Test of the Day – Test yourself with daily practice questions.
⏳ Consistent practice leads to top scores! Get your daily NEET boost now!
"""
    buttons = [
        [Button.inline("Subscribe", b"subscribe")],
    ]
    await send_message_with_back(event.chat_id, message, buttons)


async def send_file():
    print("job is called")
    links_file = find_file_id("links.csv", gdrive_service)
    subs_file = find_file_id("subscribers.csv", gdrive_service)

    if links_file is None or subs_file is None:
        raise Exception

    download_file(links_file, "links.csv", gdrive_service)
    download_file(subs_file, "subscribers.csv", gdrive_service)

    links_df = pd.read_csv("links.csv")
    subs_df = pd.read_csv("subscribers.csv")

    today_link = links_df[links_df["date"] == str(datetime.today().date())]["link"][0]

    def get_message(first_name): return f"**Good Morning {first_name}!** \n\nHere is your daily neet resource for today: "

    buttons = [
        [Button.url("Click on this Link", today_link)]
    ]
    for idx in subs_df.index:
        id = subs_df.loc[idx, "user_id"]
        fn = subs_df.loc[idx, "first_name"]
        await bot.send_message(entity=int(id), message=get_message(fn), buttons=buttons)


def get_user_details(id, user):
    return {
        "user_id": [id],
        "username": [user.username],
        "first_name": [user.first_name],
        "last_name": [user.last_name],
        "created_at": [datetime.now()]
    }

async def insert_user(event):
    user = await event.get_sender()
    user_id = event.sender_id
    user_details = get_user_details(user_id, user)

    file_id = find_file_id("users.csv", gdrive_service)

    if not (file_id is None):
        download_file(file_id, "users.csv", gdrive_service)
        df = pd.read_csv("users.csv")
        if not (user_id in df["user_id"].to_list()):
            df = pd.concat([df, pd.DataFrame(user_details)], ignore_index=True)
        else:
            print("user already in users.csv")
    else:
        raise Exception
    
    df.to_csv("users.csv", index=False)

    upload_file(file_id, "users.csv", gdrive_service)

    return

@bot.on(events.CallbackQuery(data=b'subscribe'))
async def insert_subscriber(event):
    user = await event.get_sender()
    user_id = event.sender_id
    user_details = get_user_details(user_id, user)

    file_id = find_file_id("subscribers.csv", gdrive_service)

    if not (file_id is None):
        download_file(file_id, "subscribers.csv", gdrive_service)
        df = pd.read_csv("subscribers.csv")
        if not (user_id in df["user_id"].to_list()):
            df = pd.concat([df, pd.DataFrame(user_details)], ignore_index=True)
        else:
            print("user already subscribed")
    else:
        raise Exception

    df.to_csv("subscribers.csv", index=False)

    upload_file(file_id, "subscribers.csv", gdrive_service)

    if not (user_id in df["user_id"].to_list()):
        message = "Nice! you have subscribed now. From now on, you will recieve a daily resource for your NEET preparation."
    else:
        message = "You are already a subscriber! You will continue to recieve a daily resource for your NEET preparation."

    await send_message_with_back(event.chat_id, message, [])

@bot.on(events.CallbackQuery(data="syllabus"))
async def syllabus(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "🎯 **NEET starts here. Master the syllabus.**", [
        [Button.url("📘 Physics", "https://vdnt.in/Fw1Xt")],
        [Button.url("📗 Chemistry", "https://vdnt.in/FvZN8")],
        [Button.url("📕 Biology", "https://vdnt.in/FvZMz")],
    ])


@bot.on(events.CallbackQuery(data="study_plan"))
async def study_plan(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "🎯 **NEET Study Plan – Start Now, Score More!**", [
        [Button.url("📘 Best Timetable for Droppers", "https://www.vedantu.com/blog/best-neet-timetable-for-droppers")],
        [Button.url("⏳ Prepare for NEET in 1 Month", "https://www.vedantu.com/blog/how-to-prepare-for-neet-in-1-month")],
        [Button.url("🎯 Score 500+ in One Month", "https://www.vedantu.com/blog/how-to-score-more-than-500-in-the-neet-exam-in-one-month")],
        [Button.url("🔁 Revise Smart in 30 Days", "https://www.vedantu.com/blog/how-to-revise-for-neet-ug-exam-in-one-month")],
        [Button.url("📈 Boost Physics in 1 Month", "https://www.vedantu.com/blog/how-do-i-improve-neet-physics-in-1-month-before-the-exam")],
        [Button.url("🧪 Crack Chemistry in 30 Days", "https://www.vedantu.com/blog/how-to-prepare-for-neet-chemistry-in-just-30-days")]
    ])


@bot.on(events.CallbackQuery(data="revision"))
async def revision(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "🧠 **Quick Revision Made Easy!*\nUse Mind Maps & Revision Books to revise smart and save time! ⏱️**", [
        [Button.url("📘 Biology Mind Maps", "https://content-youtube.vedantu.com/youtube/PROD/pdf/ec8aa62e-800f-4d85-8639-917a1c284825-1717055789353-4102613408973661.pdf")],
        [Button.url("📗 Chemistry Revision Book", "https://content-youtube.vedantu.com/youtube/PROD/pdf/10af1ec7-9c3f-4d94-b0f1-52f9152ddb43-1717056108132-4102613408973661.pdf")],
        [Button.url("📕 Physics Revision Book", "https://content-youtube.vedantu.com/youtube/PROD/pdf/84596137-8536-471e-8123-6b7bf21900ac-1717056254045-4102613408973661.pdf")],
    ])


@bot.on(events.CallbackQuery(data="must_solve"))
async def must_solve(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "📘 **NEET Must-Solves + Rank Predictor!**", [
        [Button.url("🔹 500 Most Wrong Questions", "https://vdnt.in/Fw6Nx")],
        [Button.url("🔹 500 Most Important PYQs", "https://vdnt.in/Fw71E")],
        [Button.url("🔹 Rank & College Predictor", "https://www.vedantu.com/neet/rank-predictor")],
        [Button.url("🔹 NEET 2024 Answer Key", "https://docs.google.com/document/d/1FLrfDeqowXhm4oNA04ac3pDI5QX4AcLG2uzkAEsNuBo/edit")],
    ])


@bot.on(events.CallbackQuery(data="pyq_test"))
async def pyq_test(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "📝 **Take a FREE NEET PYQ Mock Test!**", [
        [Button.url("🔹 Question Paper 2024", "https://drive.google.com/file/d/18UfjtpByntcMybUsBe3dYb3qTQKoWAc2/view?pli=1")],
        [Button.url("🔹 Question Paper 2023", "https://vdnt.in/FrXmb")],
        [Button.url("🔹 Question Paper 2022", "https://vdnt.in/FrXny")],
        [Button.url("🔹 Question Paper 2021", "https://vdnt.in/FrXpB")],
        [Button.url("🔹 Question Paper 2020", "https://vdnt.in/FrXqy")],
        [Button.url("🔹 Question Paper 2019", "https://vdnt.in/FrXr1")],
        [Button.url("🔹 Question Paper 2018", "https://www.vedantu.com/neet/neet-question-paper-2018")],
        [Button.url("🔹 Question Paper 2017", "https://www.vedantu.com/neet/neet-question-paper-2017")],
        [Button.url("🔹 Question Paper 2016", "https://www.vedantu.com/neet/neet-question-paper-2016")],
        [Button.url("🔹 Question Paper 2015", "https://www.vedantu.com/neet/neet-question-paper-2015")],
        [Button.url("🎥 NEET UG 2024: Video Analysis", "https://docs.google.com/document/d/1GaECHoiis_rHJgx8yIS262H5m-V2xVNWa4GQpPMBRbg/edit")],
        [Button.url("✅ NEET UG 2024: Free Answer Key", "https://docs.google.com/document/d/1FLrfDeqowXhm4oNA04ac3pDI5QX4AcLG2uzkAEsNuBo/edit")],
    ])

@bot.on(events.CallbackQuery(data="mock_test"))
async def mock_test(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "🧪 **Free NEET Mock Tests – Practice Anytime, Anywhere!**", [
        [Button.url("🔹 NEET Replica Test", "https://courses.vedantu.com/neet-replica-final-test2024/")],
        [Button.url("🔹 8 in 1 Mock Tests", "https://courses.vedantu.com/aimt/")],
    ])

@bot.on(events.CallbackQuery(data=b'study_guides'))
async def send_study_guide(event):
    message = ("📖 **Expert Tips & Study Guides – Study Smarter, Score Higher!**\n"
               "🎓 Crack NEET with pro-level strategies! Get expert-curated tips, guides, and insights from toppers & mentors to maximize your success.\n\n"
               "📌 **Select Your Guide:**")
    
    buttons = [
        [Button.url("🎯 How to Prepare for NEET in 1 Month?", "https://dummy-link.com")],
        [Button.url("📈 How to Score More Than 500 in the NEET Exam in One Month", "https://dummy-link.com")],
        [Button.url("📚 List of All Important NEET Topics & Explanation", "https://dummy-link.com")],
        [Button.url("🔑 NEET Important Concepts: Key Topics for Success", "https://dummy-link.com")],
        [Button.url("⏳ NEET 2025 – Things to Do Before the Exam", "https://dummy-link.com")],
        [Button.url("📖 Study Material for NEET 2024", "https://dummy-link.com")],
        [Button.url("❓ 70+ Important FAQs on NEET 2025", "https://dummy-link.com")],
        [Button.url("⚡ Physics Most Important Chapters for NEET", "https://dummy-link.com")],
        [Button.url("🏆 15 NEET Topper Strategies to Score Good Marks", "https://dummy-link.com")],
        [Button.url("📆 How to Prepare for NEET in 1 Month?", "https://dummy-link.com")],
        [Button.url("📌 Most Important Chapters for NEET", "https://dummy-link.com")],
        [Button.url("🎯 NEET Preparation Tips to Score Well", "https://dummy-link.com")],
    ]
    await send_message_with_back(event.chat_id, message, buttons)

@bot.on(events.CallbackQuery(data="quiz"))
async def quiz(event):
    chat_id = event.chat_id
    await send_message_with_back(chat_id, "❓ **Join Free NEET Quiz!**", [
        [Button.inline("Physics 🔬", b"quiz_physics")],
        [Button.inline("Chemistry 🧪", b"quiz_chemistry")],
        [Button.inline("Biology 🌱", b"quiz_biology")],
    ])


@bot.on(events.CallbackQuery(data=b"quiz_physics"))
async def physics_quiz(event):
    message = "🔬 **Physics Quizzes - Test Your Knowledge!**"
    buttons = [
        [Button.url("Kinematics Quiz", "https://www.vedantu.com/quiz/kinematics-quiz")],
        [Button.url("Laws of Motion Quiz", "https://www.vedantu.com/quiz/laws-of-motion-quiz")],
        [Button.url("Work, Energy, and Power Quiz", "https://www.vedantu.com/quiz/work-energy-and-power-quiz")],
        [Button.url("Gravitation Quiz", "https://www.vedantu.com/quiz/gravitation-quiz")],
        [Button.url("Thermodynamics Quiz", "https://www.vedantu.com/quiz/thermodynamics-quiz")],
        [Button.url("Electrostatics Quiz", "https://www.vedantu.com/quiz/electrostatics-quiz")],
        [Button.url("Current Electricity Quiz", "https://www.vedantu.com/quiz/current-electricity-quiz")],
        [Button.url("Optics Quiz", "https://www.vedantu.com/quiz/optics-quiz")],
    ]
    await send_message_with_back(event.chat_id, message, buttons)

@bot.on(events.CallbackQuery(data=b"quiz_chemistry"))
async def chemistry_quiz(event):
    message = "🧪 **Chemistry Quizzes - Challenge Yourself!**"
    buttons = [
        [Button.url("Structure of Atom Quiz", "https://www.vedantu.com/quiz/structure-of-atom-quiz")],
        [Button.url("Chemical Bonding Quiz", "https://www.vedantu.com/quiz/chemical-bonding-and-molecular-structure-quiz")],
        [Button.url("Thermodynamics Quiz", "https://www.vedantu.com/quiz/thermodynamics-quiz")],
        [Button.url("Equilibrium Quiz", "https://www.vedantu.com/quiz/equilibrium-quiz")],
        [Button.url("Redox Reactions Quiz", "https://www.vedantu.com/quiz/redox-reactions-quiz")],
        [Button.url("Organic Chemistry Quiz", "https://www.vedantu.com/quiz/organic-chemistry-basic-principles-and-techniques-quiz")],
        [Button.url("Hydrocarbons Quiz", "https://www.vedantu.com/quiz/hydrocarbons-quiz")],
        [Button.url("Polymers Quiz", "https://www.vedantu.com/quiz/polymers-quiz")],
    ]
    await send_message_with_back(event.chat_id, message, buttons)

@bot.on(events.CallbackQuery(data=b"quiz_biology"))
async def biology_quiz(event):
    message = "🌱 **Biology Quizzes - Explore Life Sciences!**"
    buttons = [
        [Button.url("Diversity in Living World Quiz", "https://www.vedantu.com/quiz/diversity-in-living-world-quiz")],
        [Button.url("Cell Structure and Function Quiz", "https://www.vedantu.com/quiz/cell-structure-and-function-quiz")],
        [Button.url("Plant Physiology Quiz", "https://www.vedantu.com/quiz/plant-physiology-quiz")],
        [Button.url("Genetics and Evolution Quiz", "https://www.vedantu.com/quiz/genetics-and-evolution-quiz")],
        [Button.url("Ecology and Environment Quiz", "https://www.vedantu.com/quiz/ecology-and-environment-quiz")],
    ]
    await send_message_with_back(event.chat_id, message, buttons)

@bot.on(events.CallbackQuery(data="courses"))
async def courses(event):
    chat_id = event.chat_id
    await send_message_with_back(
        chat_id, 
        "📚 **NEET Mastery Begins Now – Learn Better, Score Higher!**\n"
        "Hey Future Doctors! 👩‍⚕️👨‍⚕️ It’s time to turn your dream into a rank.\n\n"
        "💡 Here’s What You’ll Get:\n"
        "🎯 LIVE interactive classes with top teachers who know NEET inside-out\n"
        "❓ 24/7 instant doubt-solving—get help anytime\n"
        "📦 Printed study material delivered to your home\n"
        "👨‍🏫 Regular Parent-Teacher Meetings to track progress\n"
        "🏆 Vedantu Improvement Promise – We’re committed to your success\n"
        "📖 Ready to stay ahead with the best NEET prep?\n",
    [
        [Button.url("🎯 Join Now", "https://vdnt.in/short?q=GRVYu")],
    ])

# Back to Main Menu
@bot.on(events.CallbackQuery(data="main_menu"))
async def main_menu(event):
    await start(event)

scheduler.add_job(func=send_file, trigger="cron", hour=5, minute=0)

async def main():
    scheduler.start()
    print("Scheduler started...")

    # Start Telegram bot in parallel
    await bot.start(BOT_TOKEN)
    
    print("Bot is running...")
    await bot.run_until_disconnected()

asyncio.run(main())

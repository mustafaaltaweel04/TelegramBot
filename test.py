import os
import schedule
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

habits = {}
notes_a = ""
notes_b = ""

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'telegrambot-446110-a2d4fc0d2e83.json' 
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
docs_service = build('docs', 'v1', credentials=credentials)

DOC_ID = '1nWWx7og3xeGlqeE6J6FAXPA8xxNSaZwaNpb8UAI0ZfE' 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Habit Tracker Bot!\nUse /addhabit <habit> to add a habit.")

async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit = " ".join(context.args)
    if habit:
        habits[habit] = {"status": "Not Started", "time": None}
        await update.message.reply_text(f"Habit added: {habit}")
    else:
        await update.message.reply_text("Please specify a habit to add.")

async def delete_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit = " ".join(context.args)
    if habit in habits:
        del habits[habit]
        await update.message.reply_text(f"Habit deleted: {habit}")
    else:
        await update.message.reply_text("Habit not found.")

async def check_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit = " ".join(context.args)
    if habit in habits:
        habits[habit]["status"] = "Done"
        habits[habit]["time"] = datetime.datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Habit marked as done: {habit}")
    else:
        await update.message.reply_text("Habit not found.")

async def add_note_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global notes_a
    notes_a = " ".join(context.args)
    await update.message.reply_text("Note added for today.")

async def add_note_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global notes_b
    notes_b = " ".join(context.args)
    await update.message.reply_text("Note added for A's performance.")

async def add_extra_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit = " ".join(context.args)
    if habit:
        habits[habit] = {"status": "Not Started", "time": None}
        await update.message.reply_text(f"Extra task added: {habit}")
    else:
        await update.message.reply_text("Please specify a task to add.")

def generate_daily_report():
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    day_number = (now - datetime.datetime.strptime("2024-01-01", "%Y-%m-%d")).days + 1
    content = f"Date: {date_string}\nDay: {day_number}\n\nHabits:\n"

    for habit, data in habits.items():
        content += f"- {habit}: {data['status']} at {data['time']}\n"

    content += f"\nA's Notes: {notes_a}\nB's Notes: {notes_b}\n\n"

    requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
    docs_service.documents().batchUpdate(documentId=DOC_ID, body={"requests": requests}).execute()

schedule.every().day.at("22:00").do(generate_daily_report)

async def run_schedule():
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    app = ApplicationBuilder().token("7762777348:AAExXUL2de2VQHIUZ13AVIVXMnwr188xseE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addhabit", add_habit))
    app.add_handler(CommandHandler("deletehabit", delete_habit))
    app.add_handler(CommandHandler("checkhabit", check_habit))
    app.add_handler(CommandHandler("notea", add_note_a))
    app.add_handler(CommandHandler("noteb", add_note_b))
    app.add_handler(CommandHandler("addtask", add_extra_task))

    app.run_polling()

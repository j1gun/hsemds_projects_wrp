# JobQuest RPG Bot - MVP with local logging

import random
import datetime
import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

# --- States ---
WELCOME, RULES, ETHICS, QUEST, TEST, COMPLETE = range(6)

# --- Sample Quest Data ---
QUESTS = [
    {
        "name": "Get to know Jira",
        "reward": "+5 CorpCoins",
        "link": "https://jira.com",
        "description": "🛠 Jira is the battlefield where tasks are born and deadlines are conquered. Here you will create, track, and complete tickets like a true project warrior."
    },
    {
        "name": "Read the NDA",
        "reward": "+5 CorpCoins",
        "link": "https://example.com",
        "description": "📜 The NDA is a scroll of invisibility. By signing it, you vow to protect corporate secrets like an ancient archivist."
    },
    {
        "name": "Access Confluence",
        "reward": "+5 CorpCoins",
        "link": "https://confluence.com",
        "description": "📚 Confluence is the library of company knowledge. Here lie ancient manuals, guides, and the wisdom of senior developers."
    },
    {
        "name": "Save GitLab Repository",
        "reward": "+5 CorpCoins",
        "link": "https://gitlab.com",
        "description": "💾 GitLab is the forge of code. Add the repository to begin your journey of development and commits."
    },
    {
        "name": "Subscribe to our Habr Blog",
        "reward": "+5 CorpCoins",
        "link": "https://habr.com",
        "description": "📰 Habr is a source of corporate inspiration. Subscribing will help you stay on top of trends and remember: knowledge is power."
    },
    {
        "name": "Final BOSS: Knowledge Check",
        "reward": "+10 CorpCoins",
        "link": "https://example.com/boss",
        "description": "🐉 The final test will reveal how ready you are for adventure in our company. Don’t worry about mistakes — every hero learns through trials. Try again if you don’t succeed the first time!"
    }
]

# --- User Data ---
import os

user_progress = {}

def load_user_ids():
    try:
        with open("user_ids.csv", "r", encoding="utf-8") as file:
            for line in file:
                tg_id, uid = line.strip().split(",")
                user_progress[int(tg_id)] = {
                    "uid": int(uid),
                    "current_quest": 0,
                    "completed": [],
                    "timestamps": [],
                }
    except FileNotFoundError:
        pass

def save_user_id(tg_id, uid):
    if not os.path.exists("user_ids.csv") or f"{tg_id}," not in open("user_ids.csv", "r", encoding="utf-8").read():
        with open("user_ids.csv", "a", encoding="utf-8") as file:
            line = f"{tg_id},{uid}\n"
            file.write(line)

# --- Logging ---
def log_action(user_id, uid, action):
    timestamp = datetime.datetime.now().isoformat()
    with open("onboarding_log.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, user_id, uid, action])

# --- Onboarding Steps ---

async def welcome_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "WELCOME")
    await query.edit_message_text(
        '''📨 Welcome aboard! This bot will help you navigate your first steps in the company through quests.

Click the button below to view the onboarding rules.'''
    )
    await query.message.reply_text(
        "⬇️ Click the button below to continue:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("View Rules", callback_data="rules")]])
    )
    return RULES

async def rules_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "RULES")
    await query.edit_message_text(
        '''📘 Onboarding Rules:

1. Follow the quest sequence.
2. Keep this bot chat open.
3. Enjoy the ride!

Now let's take a look at our corporate values.''')
    await query.message.reply_text(
        "⬇️ Click the button below to continue:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Corporate Values", callback_data="ethics")]])
    )
    return ETHICS

async def ethics_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "ETHICS")
    await query.edit_message_text(
        '''🧭 Corporate Values:

✅ Respect your colleagues
✅ Meet your deadlines
✅ Maintain a healthy work-life balance

Ready for your first quest?''')
    await query.message.reply_text(
        "⬇️ Click the button below to begin:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("To the Quests!", callback_data="quest")]])
    )
    return QUEST

# --- Quest Handler ---

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)
    await query.answer()

    if not user_data:
        await query.edit_message_text("Please start with the /start command.")
        await query.message.reply_text(
            "🏁 Choose where to go next:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Jira", url="https://jira.com")],
                    [InlineKeyboardButton("Confluence", url="https://confluence.com")],
                    [InlineKeyboardButton("GitLab", url="https://gitlab.com")],
                    [InlineKeyboardButton("Habr", url="https://habr.com")],
                    [InlineKeyboardButton("Write to HR", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")]
                ])
            )
        return ConversationHandler.END

    index = user_data["current_quest"]
    if index == len(QUESTS) - 1:
        await query.edit_message_text(
            '''🐉 FINAL BOSS: Test Your Knowledge!

Which service is used to store and organize company knowledge?''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("GitLab", callback_data="test_gitlab")],
                [InlineKeyboardButton("Confluence", callback_data="test_confluence")],
                [InlineKeyboardButton("Jira", callback_data="test_jira")]
            ])
        )
        return TEST

    if index >= len(QUESTS):
        await query.edit_message_text("🎉 You’ve completed all quests! You are now a certified onboarding hero!")
        return ConversationHandler.END

    quest = QUESTS[index]
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_START: {quest['name']}")

    await query.edit_message_text(
        f'''🗺️ Quest: {quest['name']}

{quest['description']}

🎁 Reward: {quest['reward']}''',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go to Task", url=quest["link"])],
            [InlineKeyboardButton("I did it!", callback_data="complete")]
        ])
    )
    return COMPLETE


async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)
    await query.answer()

    if not user_data:
        await query.edit_message_text("Please start with the /start command.")
        return ConversationHandler.END

    index = user_data["current_quest"]
    quest = QUESTS[index]
    user_data["completed"].append(quest["name"])
    user_data["current_quest"] += 1
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_COMPLETE: {quest['name']}")

    await query.edit_message_text(
        "✅ Quest completed! Ready for the next one?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quest", callback_data="quest")]])
    )
    return QUEST

# --- Final Boss Test Handler ---

async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)

    questions = [
        {
            "question": "Which service is used to store and organize company knowledge?",
            "options": ["GitLab", "Confluence", "Jira"],
            "answer": "confluence"
        },
        {
            "question": "What is an NDA?",
            "options": ["Lunch agreement", "Secret document", "Software license"],
            "answer": "secret document"
        },
        {
            "question": "Where will you track your tasks?",
            "options": ["Notion", "Confluence", "Jira"],
            "answer": "jira"
        },
        {
            "question": "What can you buy with CorpCoins?",
            "options": ["Company shares", "Merch & stickers", "Vacation tickets"],
            "answer": "merch & stickers"
        }
    ]

    if user_id not in context.user_data:
        context.user_data[user_id] = {"test_index": 0}

    index = context.user_data[user_id]["test_index"]
    question = questions[index]
    selected = query.data.replace("test_", "").strip().lower()
    correct = question["answer"].strip().lower()

    if selected == correct:
        context.user_data[user_id]["test_index"] += 1
        if context.user_data[user_id]["test_index"] >= len(questions):
            user_data["completed"].append("Final BOSS: Knowledge Check")
            user_data["current_quest"] += 1
            user_data["timestamps"].append(datetime.datetime.now().isoformat())
            log_action(user_id, user_data["uid"], "QUEST_COMPLETE: Final BOSS")

            await query.edit_message_text(
                '''🏆 Congratulations! You’ve defeated the Final Boss and completed your onboarding! You earn +10 CorpCoins! 🎉

You crushed it without breaking a sweat — HR will sing legends of your speedrun.''')
            return ConversationHandler.END
        else:
            next_q = questions[context.user_data[user_id]["test_index"]]
            await query.edit_message_text(
                f"🧠 {next_q['question']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(opt, callback_data=f"test_{opt}") for opt in next_q['options']]
                ])
            )
            return TEST
    else:
        await query.edit_message_text(
            f'''❌ Incorrect! Try again, brave one! 🧠

Question: {question['question']} (your answer was: {selected})''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"test_{opt}") for opt in question['options']]
            ])
        )
        return TEST

# --- Main App ---

def main():
    app = ApplicationBuilder().token("7586450115:AAFkjkPVk-YVl1lFFlpIDJI4gnlcTxvpK0Q").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [CallbackQueryHandler(welcome_step, pattern="^welcome$")],
            RULES: [CallbackQueryHandler(rules_step, pattern="^rules$")],
            ETHICS: [CallbackQueryHandler(ethics_step, pattern="^ethics$")],
            QUEST: [CallbackQueryHandler(quest, pattern="^quest$")],
            COMPLETE: [CallbackQueryHandler(complete, pattern="^complete$")],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(test_handler, pattern="^test_.*$"))

    app.run_polling()

# --- Start Command ---
load_user_ids()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if user.id not in user_progress:
        uid = random.randint(100000, 999999)
        user_progress[user.id] = {
            "uid": uid,
            "current_quest": 0,
            "completed": [],
            "timestamps": [],
        }
        save_user_id(user.id, uid)
    uid = user_progress[user.id]["uid"]
    log_action(user.id, uid, "START")
    await update.message.reply_text(
        f"Hello, {user.first_name}! Welcome to JobQuest RPG! 🎮\n\nYour ID: {uid}\n\nThis bot will help you go through onboarding in a fun and fast way. For each quest completed, you earn CorpCoins — an internal company currency. Use them to get exclusive merch, stickers, and other fun stuff!\n\nClick the button below to start.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="welcome")]])
    )
    return WELCOME


if __name__ == '__main__':
    main()

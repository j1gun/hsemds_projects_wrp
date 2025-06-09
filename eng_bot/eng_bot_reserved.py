import random
import datetime
import csv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

WELCOME, RULES, ETHICS, QUEST, TEST, COMPLETE = range(6)

QUESTS = [
    {
        "name": "Get to know Jira",
        "reward": "+5 CorpCoins",
        "link": "https://jira.com",
        "description": "🛠 Jira is the battlefield where tasks are born and deadlines are conquered. Here you will create, track, and complete tickets like a true project warrior.",
        "image": "img/jira.png"
    },
    {
        "name": "Read the NDA",
        "reward": "+5 CorpCoins",
        "link": "https://example.com",
        "description": "📜 The NDA is a scroll of invisibility. By signing it, you vow to protect corporate secrets like an ancient archivist.",
        "image": "img/nda.png"
    },
    {
        "name": "Access Confluence",
        "reward": "+5 CorpCoins",
        "link": "https://confluence.com",
        "description": "📚 Confluence is the library of company knowledge. Here lie ancient manuals, guides, and the wisdom of senior developers.",
        "image": "img/confluence.png"
    },
    {
        "name": "Save GitLab Repository",
        "reward": "+5 CorpCoins",
        "link": "https://gitlab.com",
        "description": "💾 GitLab is the forge of code. Add the repository to begin your journey of development and commits.",
        "image": "img/gitlab.png"
    },
    {
        "name": "Subscribe to our Habr Blog",
        "reward": "+5 CorpCoins",
        "link": "https://habr.com",
        "description": "📰 Habr is a source of corporate inspiration. Subscribing will help you stay on top of trends and remember: knowledge is power.",
        "image": "img/habr.png"
    },
    {
        "name": "Final BOSS: Knowledge Check",
        "reward": "+10 CorpCoins",
        "link": "https://example.com/boss",
        "description": "🐉 The final test will reveal how ready you are for adventure in our company. Don’t worry about mistakes — every hero learns through trials. Try again if you don’t succeed the first time!",
        "image": "img/boss.png"
    }
]

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
            file.write(f"{tg_id},{uid}\n")

def log_action(user_id, uid, action):
    timestamp = datetime.datetime.now().isoformat()
    with open("onboarding_log.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, user_id, uid, action])

# Universal photo sender
async def send_photo_with_caption(chat, image_path, caption, reply_markup=None):
    with open(image_path, "rb") as img:
        await chat.send_photo(
            photo=img,
            caption=caption,
            reply_markup=reply_markup
        )

async def welcome_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await send_photo_with_caption(
        query.message.chat,
        "img/welcome.png",
        "📨 Welcome aboard! This bot will help you navigate your first steps in the company through quests.\n\nClick the button below to view the onboarding rules.",
        InlineKeyboardMarkup([[InlineKeyboardButton("View Rules", callback_data="rules")]])
    )
    await query.message.delete()
    return RULES

async def rules_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await send_photo_with_caption(
        query.message.chat,
        "img/rules.png",
        "📘 Onboarding Rules:\n\n1. Follow the quest sequence.\n2. Keep this bot chat open.\n3. Enjoy the ride!\n\nNow let's take a look at our corporate values.",
        InlineKeyboardMarkup([[InlineKeyboardButton("Corporate Values", callback_data="ethics")]])
    )
    await query.message.delete()
    return ETHICS

async def ethics_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await send_photo_with_caption(
        query.message.chat,
        "img/ethics.png",
        "🧭 Corporate Values:\n\n✅ Respect your colleagues\n✅ Meet your deadlines\n✅ Maintain a healthy work-life balance\n\nReady for your first quest?",
        InlineKeyboardMarkup([[InlineKeyboardButton("To the Quests!", callback_data="quest")]])
    )
    await query.message.delete()
    return QUEST

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
        await query.message.reply_photo(open("img/boss.png", "rb"))
        await query.message.reply_text(
            '''🐉 FINAL BOSS: Test Your Knowledge!\n\nWhich service is used to store and organize company knowledge?''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("GitLab", callback_data="test_gitlab")],
                [InlineKeyboardButton("Confluence", callback_data="test_confluence")],
                [InlineKeyboardButton("Jira", callback_data="test_jira")]
            ])
        )
        await query.delete_message()
        return TEST

    if index >= len(QUESTS):
        await query.message.reply_text("🎉 You’ve completed all quests! You are now a certified onboarding hero!")
        return ConversationHandler.END

    quest = QUESTS[index]
    if quest.get("image"):
        await query.message.reply_photo(open(quest["image"], "rb"))
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_START: {quest['name']}")

    await query.message.reply_text(
        f'''🗺️ Quest: {quest['name']}\n\n{quest['description']}\n\n🎁 Reward: {quest['reward']}''',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go to Task", url=quest["link"])],
            [InlineKeyboardButton("I did it!", callback_data="complete")]
        ])
    )
    await query.delete_message()
    return COMPLETE



async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)
    await query.answer()

    if not user_data:
        await query.message.reply_text("Please start with the /start command.")
        await query.delete_message()
        return ConversationHandler.END

    index = user_data["current_quest"]
    quest = QUESTS[index]
    user_data["completed"].append(quest["name"])
    user_data["current_quest"] += 1
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_COMPLETE: {quest['name']}")

    await query.message.reply_photo(open("img/campfire.png", "rb"))
    await query.message.reply_text(
        "✅ Quest completed! Ready for the next one?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quest", callback_data="quest")]])
    )
    await query.delete_message()
    return QUEST


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

    if "test_index" not in context.user_data:
        context.user_data["test_index"] = 0

    idx = context.user_data["test_index"]
    question = questions[idx]
    selected = query.data.replace("test_", "").strip().lower()
    correct = question["answer"].strip().lower()

    if selected == correct:
        context.user_data["test_index"] += 1
        if context.user_data["test_index"] >= len(questions):
            user_data["completed"].append("Final BOSS: Knowledge Check")
            user_data["current_quest"] += 1
            user_data["timestamps"].append(datetime.datetime.now().isoformat())
            log_action(user_id, user_data["uid"], "QUEST_COMPLETE: Final BOSS")
            await send_photo_with_caption(
                query.message.chat,
                "img/win.png",
                "🏆 Congratulations! You’ve defeated the Final Boss and completed your onboarding! You earn +10 CorpCoins! 🎉\n\nYou crushed it without breaking a sweat — HR will sing legends of your speedrun."
            )
            await send_photo_with_caption(
                query.message.chat,
                "img/menu.png",
                "🏁 Choose where to go next:",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("Jira", url="https://jira.com")],
                    [InlineKeyboardButton("Confluence", url="https://confluence.com")],
                    [InlineKeyboardButton("GitLab", url="https://gitlab.com")],
                    [InlineKeyboardButton("Habr", url="https://habr.com")],
                    [InlineKeyboardButton("Write to HR", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")]
                ])
            )
            await query.message.delete()
            context.user_data["test_index"] = 0
            return ConversationHandler.END
        else:
            next_q = questions[context.user_data["test_index"]]
            await send_photo_with_caption(
                query.message.chat,
                "img/boss.png",
                f"🧠 {next_q['question']}",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton(opt, callback_data=f"test_{opt}") for opt in next_q['options']]
                ])
            )
            await query.message.delete()
            return TEST
    else:
        await query.message.edit_text(
            f'''❌ Incorrect! Try again, brave one! 🧠\n\nQuestion: {question['question']} (your answer was: {selected})''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"test_{opt}") for opt in question['options']]
            ])
        )
        return TEST

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
    await send_photo_with_caption(
        update.message.chat,
        "img/welcome.png",
        f"Hello, {user.first_name}! Welcome to JobQuest RPG! 🎮\n\nYour ID: {uid}\n\nThis bot will help you go through onboarding in a fun and fast way. For each quest completed, you earn CorpCoins — an internal company currency. Use them to get exclusive merch, stickers, and other fun stuff!\n\nClick the button below to start.",
        InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="welcome")]])
    )
    return WELCOME

if __name__ == '__main__':
    main()

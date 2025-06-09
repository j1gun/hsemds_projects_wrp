import random
import datetime
import csv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler
)

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
PHOTO_TRACKER = {}  # user_id: last_sent_photo_id

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

async def delete_last_photo(user_id, context, chat_id):
    msg_id = PHOTO_TRACKER.get(user_id)
    if msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        PHOTO_TRACKER[user_id] = None

async def send_quest_photo_and_text(user_id, context, chat_id, image_path, text, reply_markup=None):
    await delete_last_photo(user_id, context, chat_id)
    with open(image_path, "rb") as img:
        msg = await context.bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption=text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    PHOTO_TRACKER[user_id] = msg.message_id

async def welcome_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "WELCOME")
    await send_quest_photo_and_text(
        user_id, context, query.message.chat_id,
        "img/welcome.png",
        "📨 Welcome aboard! This bot will help you navigate your first steps in the company through quests.\n\nClick the button below to view the onboarding rules.",
        InlineKeyboardMarkup([[InlineKeyboardButton("View Rules", callback_data="rules")]])
    )
    return RULES

async def rules_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "RULES")
    await send_quest_photo_and_text(
        user_id, context, query.message.chat_id,
        "img/rules.png",
        "📘 Onboarding Rules:\n\n1. Follow the quest sequence.\n2. Keep this bot chat open.\n3. Enjoy the ride!\n\nNow let's take a look at our corporate values.",
        InlineKeyboardMarkup([[InlineKeyboardButton("Corporate Values", callback_data="ethics")]])
    )
    return ETHICS

async def ethics_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    uid = user_progress[user_id]["uid"]
    log_action(user_id, uid, "ETHICS")
    await send_quest_photo_and_text(
        user_id, context, query.message.chat_id,
        "img/ethics.png",
        "🧭 Corporate Values:\n\n✅ Respect your colleagues\n✅ Meet your deadlines\n✅ Maintain a healthy work-life balance\n\nReady for your first quest?",
        InlineKeyboardMarkup([[InlineKeyboardButton("To the Quests!", callback_data="quest")]])
    )
    return QUEST

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)
    chat_id = query.message.chat_id

    if not user_data:
        await query.message.reply_text(
            "Please start with the /start command.\n🏁 Choose where to go next:",
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

    # Boss level
    if index == len(QUESTS) - 1:
        await send_quest_photo_and_text(
            user_id, context, chat_id,
            QUESTS[index]["image"],
            "🐉 FINAL BOSS: Test Your Knowledge!\n\nWhich service is used to store and organize company knowledge?",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("GitLab", callback_data="test_gitlab")],
                [InlineKeyboardButton("Confluence", callback_data="test_confluence")],
                [InlineKeyboardButton("Jira", callback_data="test_jira")]
            ])
        )

        context.user_data[user_id] = {"test_index": 0}
        return TEST

    # Финальное меню
    if index >= len(QUESTS):
        await send_quest_photo_and_text(
            user_id, context, chat_id,
            "img/menu.png",
            "🎉 You’ve completed all quests! You are now a certified onboarding hero!",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("Jira", url="https://jira.com")],
                [InlineKeyboardButton("Confluence", url="https://confluence.com")],
                [InlineKeyboardButton("GitLab", url="https://gitlab.com")],
                [InlineKeyboardButton("Habr", url="https://habr.com")],
                [InlineKeyboardButton("Write to HR", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")]
            ])
        )

        return ConversationHandler.END

    quest = QUESTS[index]
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_START: {quest['name']}")
    await send_quest_photo_and_text(
        user_id, context, chat_id,
        quest["image"],
        f"🗺️ Quest: {quest['name']}\n\n{quest['description']}\n\n🎁 Reward: {quest['reward']}",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("Go to Task", url=quest["link"])],
            [InlineKeyboardButton("I did it!", callback_data="complete")]
        ])
    )
    return COMPLETE

async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = user_progress.get(user_id)
    chat_id = query.message.chat_id

    if not user_data:
        await query.message.reply_text("Please start with the /start command.")

        return ConversationHandler.END

    index = user_data["current_quest"]
    quest = QUESTS[index]
    user_data["completed"].append(quest["name"])
    user_data["current_quest"] += 1
    user_data["timestamps"].append(datetime.datetime.now().isoformat())
    log_action(user_id, user_data["uid"], f"QUEST_COMPLETE: {quest['name']}")

    # Показываем костёр (campfire) при завершении квеста
    await send_quest_photo_and_text(
        user_id, context, chat_id,
        "img/campfire.png",
        "✅ Quest completed! Ready for the next one?",
        InlineKeyboardMarkup([[InlineKeyboardButton("Next Quest", callback_data="quest")]])
    )
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
    # Индекс вопроса только для текущего пользователя!
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

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=open("img/win.png", "rb"),
                caption="🏆 Congratulations! You've defeated the Final Boss and completed your onboarding! You earn +10 CorpCoins! 🎉\n\nYou crushed it without breaking a sweat — HR will sing legends of your speedrun."
            )

            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=open("img/menu.png", "rb")
            )

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🏁 Choose where to go next:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Jira", url="https://jira.com")],
                    [InlineKeyboardButton("Confluence", url="https://confluence.com")],
                    [InlineKeyboardButton("GitLab", url="https://gitlab.com")],
                    [InlineKeyboardButton("Habr", url="https://habr.com")],
                    [InlineKeyboardButton("Write to HR", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")]
                ])
            )


            # Возвращаем END, чтобы ConversationHandler закончился, но меню останется работать как отдельные URL-кнопки
            return ConversationHandler.END

        else:
            next_q = questions[context.user_data[user_id]["test_index"]]
            await send_quest_photo_and_text(
                user_id, context, query.message.chat_id,
                "img/boss.png",
                f"🧠 {next_q['question']}",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton(opt, callback_data=f"test_{opt}") for opt in next_q['options']]
                ])
            )

            return TEST
    else:
        await send_quest_photo_and_text(
            user_id, context, query.message.chat_id,
            "img/boss.png",
            f'''❌ Incorrect! Try again, brave one! 🧠

        Question: {question['question']} (your answer was: {selected})''',
            InlineKeyboardMarkup([
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
    load_user_ids()
    app.run_polling()

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
    await send_quest_photo_and_text(
        user.id, context, update.effective_chat.id,
        "img/welcome.png",
        f"Hello, {user.first_name}! Welcome to JobQuest RPG! 🎮\n\nYour ID: {uid}\n\nThis bot will help you go through onboarding in a fun and fast way. For each quest completed, you earn CorpCoins — an internal company currency. Use them to get exclusive merch, stickers, and other fun stuff!\n\nClick the button below to start.",
        InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="welcome")]])
    )
    return WELCOME

if __name__ == '__main__':
    main()

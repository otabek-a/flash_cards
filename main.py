from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
import wikipediaapi
from googletrans import Translator
from tinydb import TinyDB, Query
import time
import random
import requests
from salom import sardor

chat = TinyDB('id.json')
otash = TinyDB('topic.json')

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyTelegramBot/1.0 (contact: example@email.com)", 
    language="en"
)

def get_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            return definition
        except KeyError:
            return "❌ No definition found."
    else:
        return "🚫 Error: Could not fetch data."

async def help_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    a = sardor()
    await update.message.reply_text(a)

async def words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_key = [['➕ Add Words ✍️'],
                 ['📜 Show All Words 📚', '🌍 Show All Translations 🌐'],
                 ['❌ Exit 🚪', '🗑️ Delete Topic 🧹']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    await update.message.reply_text("🧠💬 Please choose one of the options below ⬇️:", reply_markup=key)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗑️ If you want to delete a topic, just send me like this 👉 !topic_name 💥")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_key = [['🏁 Begin 🏃‍♂️', '📊 Show Result 📈'],     
                 ['❌ Exit 🚪']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    await update.message.reply_text("🎯💡 Choose one of the options below ⬇️:", reply_markup=key)

async def begin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_key = [['🧠 eng -- uzb', '🧠 uzb -- eng'],     
                 ['📘 definition -- eng'], ['❌ Exit 🚪']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    await update.message.reply_text("📢 Send me topic name like: #eng/topic_name ⬇️")

async def add_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Send topic and word like this: topic_name*word ✍️")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Student = Query()
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    existing_user = chat.search(Student.chat_id == chat_id)
    if not existing_user:
        chat.insert({'chat_id': chat_id})

    relpy_key = [['📚 Words 🏫', '👨‍🏫 TEST 🎓']]
    key = ReplyKeyboardMarkup(relpy_key)

    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    user_username = update.message.from_user.username
    if user_username:
        await update.message.reply_text(f"👋 Hello, @{user_username}! Please choose a button below. 📲 if you need help pls send /help", reply_markup=key)
    else:
        user_first_name = update.message.from_user.first_name
        await update.message.reply_text(f"👋 Hello, {user_first_name}! Please choose a button below. 📲 if you need help pls send /help", reply_markup=key)

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            topic TEXT,
            word TEXT,
            definition TEXT,
            uzbek TEXT
        )
    """)

async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE, text):
    try:
        word = text
        definition = get_definition(word)
        user_id = update.message.from_user.id
        table_name = 'a' + str(user_id)
        matn = text.split('*')
        topic_name = matn[0]
        word = matn[1]
        translator = Translator()
        result = translator.translate(word, src='en', dest='uz')
        page = wiki_wiki.page(word)
        if not page.exists():
            await update.message.reply_text(f"❌ No definition found for '{word}'.")
            return
        summary = page.summary
        sentences = summary.split('. ')
        short_definition = '. '.join(sentences[:2])
        clean_definition = short_definition.replace(word, "This term").replace(word.capitalize(), "This term")
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {table_name} (topic, word, definition, uzbek)
            VALUES (?, ?, ?, ?)
        """, (topic_name, word, clean_definition, result.text))
        conn.commit()
        await update.message.reply_text(f"✅ Topic '{topic_name}' created and word '{word}' added successfully! 🎉")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def show_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)

    cursor.execute(f"SELECT topic, word, definition FROM {table_name}")
    rows = cursor.fetchall()
    topics = {}
    for topic, word, definition in rows:
        if topic not in topics:
            topics[topic] = []
        topics[topic].append((word, definition))
    if not topics:
        await update.message.reply_text("❌ You don't have any words saved yet.")
        return
    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n📚 {i}. **Topic:** _{topic}_ ({len(words)} words):\n"
        for j, (word, definition) in enumerate(words, 1):
            message += f"    {j}) {word} — {definition} 📖\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    await update.message.reply_text(message)

async def eng(update: Update, context: ContextTypes.DEFAULT_TYPE, text):
    text = text.strip().lower()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE topic = ?", (text,))
    result = cursor.fetchall()
    otash.insert({'name': text})
    if len(result) >= 1:
        await update.message.reply_text(f"✅ Topic \"{text}\" found with {len(result)} words.\n🧪 Test will begin! Send your answer sheet after finishing 🛑")
        for count in [5, 4, 3, 2, 1]:
            time.sleep(1)
            await update.message.reply_text(f"⏳ {count}")
        await update.message.reply_text(f"🚀 Starting test for '{text}'! 💥")
        cursor.execute(f"SELECT word FROM {table_name} WHERE topic = ?", (text,))
        rows = cursor.fetchall()
        word_list = [i[0] for i in rows]
        i = 1
        matn = f'📘 Topic: {text}\n\n'
        while len(word_list) > 0:
            word = random.choice(word_list)
            matn += f"❓ Q{i}: What does '{word}' mean in English?\n"
            word_list.remove(word)
            i += 1
        await update.message.reply_text(matn)
    else:
        await update.message.reply_text(f"⚠️ Topic not found: {text} ❌")

async def show_uzbek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    cursor.execute(f"SELECT topic, word, uzbek FROM {table_name}")
    rows = cursor.fetchall()
    topics = {}
    for topic, word, uzbek in rows:
        if topic not in topics:
            topics[topic] = []
        topics[topic].append((word, uzbek))
    if not topics:
        await update.message.reply_text("❌ No translations found.")
        return
    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n🌐 {i}. **Topic:** _{topic}_ ({len(words)} words):\n"
        for j, (word, uzbek) in enumerate(words, 1):
            message += f"    {j}) {word} — {uzbek} 🇺🇿\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    await update.message.reply_text(message)

async def delete_data(update: Update, context: ContextTypes.DEFAULT_TYPE, text):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE topic = ?", (text,))
    result = cursor.fetchall()
    if len(result) >= 1:
        await update.message.reply_text(f"🗑️ Deleted topic \"{text}\" with {len(result)} words ❌")
        cursor.execute(f"DELETE FROM {table_name} WHERE topic = ?", (text,))
        conn.commit()
    else:
        await update.message.reply_text(f"⚠️ Topic not found: {text} ❌")

async def show_result(text, update: Update):
    text = text.strip().lower()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    data = otash.all()
    last_name = data[-1].get('name') if data else "unknown"
    cursor.execute(f"SELECT uzbek FROM {table_name} WHERE topic = ?", (last_name,))
    rows = cursor.fetchall()
    uzbek_words = [row[0] for row in rows] if rows else []
    user_words = text.replace('answer', '').strip(',').split(',')
    correct = 0
    incorrect = 0
    max_length = max(len(user_words), len(uzbek_words))
    for i in range(max_length):
        user_word = user_words[i] if i < len(user_words) else None
        uzbek_word = uzbek_words[i] if i < len(uzbek_words) else None
        if user_word and uzbek_word and user_word.strip().lower() == uzbek_word.strip().lower():
            correct += 1 
        else:
            incorrect += 1 
    await update.message.reply_text(f"✅ Correct: {correct}, ❌ Incorrect: {incorrect}")

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_answer = context.user_data.get('last_answer')
    if last_answer:
        await show_result(last_answer, update)
    else:
        await update.message.reply_text("❗ No 'answer' found yet.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text.startswith('answer'):
        context.user_data['last_answer'] = text
    elif text.startswith('!'):
        await delete_data(update, context, text.replace('!', ''))
    elif text.startswith('*123'):
        msg = text[4:].strip()
        if not msg:
            await update.message.reply_text("⚠️ Message cannot be empty! 📢")
            return
        for user in chat.all():
            try:
                await context.bot.send_message(chat_id=user['chat_id'], text=f"📢 Admin Message: {msg}")
            except Exception as e:
                print(f"Error: {e}")
        await update.message.reply_text("✅ Sent to all users! 📩")
    elif text.startswith('#'):
        topic=text.replace('#','').strip()
        await eng(update, context, topic)
    elif '*' in text:
        await add_word(update, context, text)

def main() -> None:
    application = Application.builder().token("7981798770:AAGbSqQmu-Z4JJ5kD8P-wFwIIWaUvWmCOV4").build()

    application.add_handler(CommandHandler("help", help_data))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check))
    
    application.add_handler(MessageHandler(filters.Regex('^📊 Show Result 📈$'), show))
    application.add_handler(MessageHandler(filters.Regex('^📚 Words 🏫$'), words))
    application.add_handler(MessageHandler(filters.Regex('^👨‍🏫 TEST 🎓$'), test))
    application.add_handler(MessageHandler(filters.Regex('^🗑️ Delete Topic 🧹$'), delete))
    application.add_handler(MessageHandler(filters.Regex('^🏁 Begin 🏃‍♂️$'), begin_test))
    application.add_handler(MessageHandler(filters.Regex('^🌍 Show All Translations 🌐$'), show_uzbek))
    application.add_handler(MessageHandler(filters.Regex('^➕ Add Words ✍️$'), add_data))
    application.add_handler(MessageHandler(filters.Regex('^❌ Exit 🚪$'), start))
    application.add_handler(MessageHandler(filters.Regex('^📜 Show All Words 📚$'), show_words))

    application.run_polling()

if __name__ == "__main__":
    main()
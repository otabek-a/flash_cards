from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update, ReplyKeyboardMarkup
import sqlite3
import wikipediaapi
from googletrans import Translator
from tinydb import TinyDB,Query
import time
import random
chat = TinyDB('id.json')
otash=TinyDB('topic.json')
import requests
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
            return "No definition found."
    else:
        return "Error: Could not fetch data."



conn = sqlite3.connect("students.db") 
cursor = conn.cursor()

def words(update, context):
    reply_key = [[ '➕ Add Words ✍️'],
                 ['📜 Show All Words 📚', '🌍 Show All Translations 🌐'],
                 ['❌ Exit 🚪','🗑️ Delete Topic 🧹']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    update.message.reply_text("🧠💬 Please choose one of the options below ⬇️:", reply_markup=key)

def delete(update,context):
    update.message.reply_text("🗑️ If you want to delete a topic, just send me like that 👉 !topic_name 💥")

def test(update, context):
    reply_key = [['🏁 Begin 🏃‍♂️', '📊 Show Result 📈'],     
                 ['❌ Exit 🚪']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    update.message.reply_text("🎯💡 Please choose one of the options below ⬇️:", reply_markup=key)

def begin_test(update,context):
    reply_key = [['🧠 eng -- uzb ', '🧠 uzb -- eng '],     
                 ['📘 definition -- eng '],['❌ Exit 🚪']]
    key = ReplyKeyboardMarkup(reply_key, resize_keyboard=True)
    update.message.reply_text("📢 Please send me topic name after you want quiz. For example: #eng/topic_name ⬇️")



def add_data(update, context):
    update.message.reply_text("📝 Please send the topic name and word in the following format: topic_name*word ✍️")

def start(update, context):
    Student = Query()
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    existing_user = chat.search(Student.chat_id == chat_id)

    if not existing_user:
        chat.insert({'chat_id': chat_id})

    relpy_key =[['📚 Words 🏫', '👨‍🏫 TEST 🎓']]
    key = ReplyKeyboardMarkup(relpy_key)
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    user_username = update.message.from_user.username
    if user_username:
        update.message.reply_text(f"👋 Hello, @{user_username}! To start using this bot, please choose one of the buttons below. 📲", reply_markup=key)
    else:
        user_first_name = update.message.from_user.first_name
        update.message.reply_text(f"👋 Hello, {user_first_name}! To start using this bot, please choose one of the buttons below. 📲", reply_markup=key)

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

def add_word(update, context, text):
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
            update.message.reply_text(f"❌ Sorry, no definition found for '{word}'.")
            return
        summary = page.summary
        sentences = summary.split('. ')
        short_definition = '. '.join(sentences[:1])
        clean_definition = short_definition.replace(word, "This term").replace(word.capitalize(), "This term")
        conn = sqlite3.connect("students.db") 
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {table_name} (topic, word, definition, uzbek)
            VALUES (?, ?, ?, ?)
        """, (topic_name, word, clean_definition, result.text))
        conn.commit() 
        update.message.reply_text(f"✅ '{topic_name}' topic created and word '{word}' added successfully! 🎉")
    except Exception as e:
        update.message.reply_text(f"❌ Error occurred: {e}")

def show_words(update, context):
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
        update.message.reply_text("❌ You don't have any words saved yet.")
        return

    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n📚 {i}. **Topic Name:** _{topic}_ ({len(words)} words):\n"
        for j, (word, definition) in enumerate(words, 1):
            message += f"    {j}) {word} — {definition} 📖\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    update.message.reply_text(message, parse_mode='Markdown')
def eng(update, context, text):
    
    text = text.strip().lower()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM {table_name} WHERE topic = ?", (text,))
    result = cursor.fetchall()
    otash.insert({'name':text})
    if len(result) >= 1:
        update.message.reply_text(f"✅ I found this topic \"{text}\" with {len(result)} words\n🧪 Your test will begin! and pls send your answr sheet after answer word 🛑")
        for count in [5, 4, 3, 2, 1]:
            time.sleep(1)
            update.message.reply_text(f"⏳ {count}")
        update.message.reply_text(f"🚀 Let's begin your test for '{text}'! 💥")
        cursor.execute(f"SELECT word FROM {table_name} WHERE topic = ?", (text,))
        rows = cursor.fetchall()
        word_list = [i[0] for i in rows]
        i=1
        matn=f'             Topic {text}\n'
        while len(word_list) > 0:
              
             word = random.choice(word_list)
             matn+=(f"Qustion:{i}, What does '{word}' mean in english? \n")
             word_list.remove(word)
             i+=1
            
        update.message.reply_text(matn)
        
    else:
        update.message.reply_text(f"⚠️ I cannot find this topic: {text} ❌")

def show_uzbek(update, context):
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
        update.message.reply_text("❌ You don't have any words saved yet.")
        return

    message = ""
    for i, (topic, words) in enumerate(topics.items(), 1):
        message += f"\n📚 {i}. **Topic Name:** _{topic}_ ({len(words)} words):\n"
        for j, (word, uzbek) in enumerate(words, 1):
            message += f"    {j}) {word} — {uzbek} 🇺🇿\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"

    update.message.reply_text(message, parse_mode='Markdown')

def delete_data(update,context,text):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE topic = ?", (text,))
    result = cursor.fetchall()

    if len(result) >= 1:
        update.message.reply_text(f"🗑️ Deleted topic \"{text}\" with {len(result)} words ❌")
        cursor.execute(f"DELETE FROM {table_name} WHERE topic = ?", (text,))
        conn.commit()
    else:
        update.message.reply_text(f"⚠️ I cannot find this topic: {text} ❌")




def show_result(text, update):
    # Foydalanuvchidan kelgan matnni olish va tayyorlash
    text = text.strip().lower()
    user_id = update.message.from_user.id
    table_name = 'a' + str(user_id)
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Foydalanuvchidan oxirgi "name"ni olish
    data = otash.all()
    last_name = data[-1].get('name') if data else "Nomaʼlum"

    # Ma'lumotlar bazasidan so'zlarni olish
    cursor.execute(f"SELECT uzbek FROM {table_name} WHERE topic = ?", (last_name,))
    rows = cursor.fetchall()
    uzbek_words = [row[0] for row in rows] if rows else []
    
    # Foydalanuvchi kiritgan so'zlarni ajratish
    user_words = text.replace('answer', '').strip(',').split(',')
    
    # To'g'ri va noto'g'ri javoblarni hisoblash
    correct = 0
    incorrect = 0
    
    
    max_length = max(len(user_words), len(uzbek_words))
    
    for i in range(max_length):
        # Agar i-chi element mavjud bo'lsa, mosligini tekshirish
        user_word = user_words[i] if i < len(user_words) else None
        uzbek_word = uzbek_words[i] if i < len(uzbek_words) else None
        
        if user_word and uzbek_word and user_word.strip().lower() == uzbek_word.strip().lower():
            correct += 1  # Agar so'zlar teng bo'lsa
        else:
            incorrect += 1  # Agar so'zlar teng bo'lmasa
    
    update.message.reply_text(f"To'g'ri javoblar: {correct}, Noto'g'ri javoblar: {incorrect}")

def check(update, context):
    text = update.message.text.lower().strip()

    if text.startswith('answer'):
        context.user_data['last_answer'] = text

    elif text.startswith('!'):
        text = text.replace('!', '')
        delete_data(update, context, text)

    elif text.startswith('*123'):
        message_to_send = text[4:].strip()
        if not message_to_send:
            update.message.reply_text("⚠️ Message cannot be empty! 📢")
            return
        for user in chat.all():
            try:
                context.bot.send_message(chat_id=user['chat_id'], text=f"📢 Message from Admin: {message_to_send}")
            except Exception as e:
                print(f"Error: {e}")
        update.message.reply_text("✅ Message sent to all users! 🚀")

    elif text.startswith('#'):
        parts = text[1:].split('/')
        if len(parts) == 2:
            lang, topic = parts
            if lang == 'eng':
                eng(update, context, topic)

    elif '*' in text:
        add_word(update, context, text)

def show(update, context):
    last_answer = context.user_data.get('last_answer')
    if last_answer:
        result = show_result(last_answer,update)
        
    else:
        update.message.reply_text("Hech qanday 'answer' topilmadi.")

updater = Updater('7981798770:AAGbSqQmu-Z4JJ5kD8P-wFwIIWaUvWmCOV4', use_context=True)
dispatcher = updater.dispatcher


dispatcher.add_handler(MessageHandler(Filters.text( '📊 Show Result 📈'), show))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text('📚 Words 🏫'), words))
dispatcher.add_handler(MessageHandler(Filters.text('👨‍🏫 TEST 🎓'), test))
dispatcher.add_handler(MessageHandler(Filters.text('🗑️ Delete Topic 🧹'), delete))
dispatcher.add_handler(MessageHandler(Filters.text('🏁 Begin 🏃‍♂️'), begin_test))
dispatcher.add_handler(MessageHandler(Filters.text('🌍 Show All Translations 🌐'), show_uzbek))
dispatcher.add_handler(MessageHandler(Filters.text('➕ Add Words ✍️'), add_data))
dispatcher.add_handler(MessageHandler(Filters.text('❌ Exit 🚪'), start))
dispatcher.add_handler(MessageHandler(Filters.text('📜 Show All Words 📚'), show_words))
dispatcher.add_handler(MessageHandler(Filters.text, check))

updater.start_polling()
updater.idle()

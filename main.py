import telebot
from telebot import types

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

# Хранилище завдань пам'яті бота 
USER_TASKS = {}

QUIZ = [
    {
        "question": "1/3. Яку мову найчастіше використовують для ботів?",
        "options": ["Java", "Python", "C++"],
        "right": "Python"
    },
    {
        "question": "2/3. Що з цього НЕ є типом даних у Python?",
        "options": ["Integer", "String", "Notebook"],
        "right": "Notebook"
    },
    {
        "question": "3/3. Як розшифровується КПІ?",
        "options": ["Київський політехнічний інститут", "Критичні показники"],
        "right": "Київський політехнічний інститут"
    }
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📋 Мої завдання"), types.KeyboardButton("➕ Додати завдання"))
    markup.add(types.KeyboardButton("📝 Пройти тест"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привіт! Оберіть дію:", reply_markup=main_menu())

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    user_id = message.chat.id
    
    if message.text == "📋 Мої завдання":
        tasks = USER_TASKS.get(user_id, [])
        if not tasks:
            bot.send_message(user_id, "У вас поки немає завдань!")
        else:
            text = "📋 **Ваші завдання:**\n\n"
            for i, task in enumerate(tasks, 1):
                text += f"{i}. {task}\n"
            bot.send_message(user_id, text, parse_mode="Markdown")
            
    elif message.text == "➕ Додати завдання":
        msg = bot.send_message(user_id, "Введіть текст завдання:")
        bot.register_next_step_handler(msg, save_new_task)
        
    elif message.text == "📝 Пройти тест":
        start_quiz(user_id, 0, 0)

def save_new_task(message):
    user_id = message.chat.id
    task_text = message.text
    
    if user_id not in USER_TASKS:
        USER_TASKS[user_id] = []
    
    USER_TASKS[user_id].append(task_text)
    bot.send_message(user_id, f"✅ Завдання «{task_text}» додано!", reply_markup=main_menu())

def start_quiz(chat_id, q_index, score):
    if q_index >= len(QUIZ):
        bot.send_message(chat_id, f"🏁 **Тест завершено!**\nПравильних відповідей: {score} з {len(QUIZ)}")
        return

    question_data = QUIZ[q_index]
    markup = types.InlineKeyboardMarkup()
    for option in question_data["options"]:
        markup.add(types.InlineKeyboardButton(text=option, callback_data=f"q_{q_index}_{score}_{option}"))
        
    bot.send_message(chat_id, question_data["question"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('q_'))
def handle_quiz_answer(call):
    data_parts = call.data.split('_')
    q_index = int(data_parts[1])
    score = int(data_parts[2])
    user_answer = call.data.replace(f"q_{q_index}_{score}_", "")

    bot.answer_callback_query(call.id)
    
    if user_answer == QUIZ[q_index]["right"]:
        score += 1
        bot.send_message(call.message.chat.id, "🟢 Правильно!")
    else:
        bot.send_message(call.message.chat.id, f"🔴 Невірно!")
        
    start_quiz(call.message.chat.id, q_index + 1, score)

if __name__ == '__main__':
    bot.infinity_polling()
import telebot
from telebot import types

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

# Сховище завдань (Зошит) у пам'яті бота 
USER_TASKS = {}

#квіз
QUIZ = [
    {
        "question": "📓 1/3. Скільки секунд є у людини, щоб вписати причину смерті після імені?",
        "options": ["40 секунд", "60 секунд", "5 хвилин"],
        "right_index": 0  # "40 секунд"
    },
    {
        "question": "🍎 2/3. Які фрукти найбільше обожнює бог смерті Рюк?",
        "options": ["Банани", "Апельсини", "Яблука"],
        "right_index": 2  # "Яблука"
    },
    {
        "question": "🎓 3/3. Хто є головним ворогом Лайта Ягамі в розслідуванні?",
        "options": ["Поліція КПІ", "Детектив L", "Рюук"],
        "right_index": 1  # "Детектив L"
    }
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📓 Зошит завдань"), types.KeyboardButton("➕ Вписати завдання"))
    markup.add(types.KeyboardButton("👁️ Угода з Богом Смерті (Тест)"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        f"Привіт, {message.from_user.first_name}. Я твій бог смерті. Які завдання запишемо в зошит сьогодні?", 
        reply_markup=main_menu()
    )

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    user_id = message.chat.id
    
    if message.text == "📓 Зошит завдань":
        tasks = USER_TASKS.get(user_id, [])
        if not tasks:
            bot.send_message(user_id, "Твій зошит поки що порожній. Жодного завдання не записано.")
        else:
            text = "📓 **Записані в зошит завдання:**\n\n"
            for i, task in enumerate(tasks, 1):
                text += f"{i}. {task}\n"
            bot.send_message(user_id, text, parse_mode="Markdown")
            
    elif message.text == "➕ Вписати завдання":
        msg = bot.send_message(user_id, "Введіть назву завдання, яке потрібно виконати:")
        bot.register_next_step_handler(msg, save_new_task)
        
    elif message.text == "👁️ Угода з Богом Смерті (Тест)":
        start_quiz(user_id, 0, 0)

def save_new_task(message):
    user_id = message.chat.id
    task_text = message.text
    
    if user_id not in USER_TASKS:
        USER_TASKS[user_id] = []
    
    USER_TASKS[user_id].append(task_text)
    bot.send_message(user_id, f"✒️ Завдання «{task_text}» успішно вписано в зошит!", reply_markup=main_menu())

def start_quiz(chat_id, q_index, score):
    if q_index >= len(QUIZ):
        bot.send_message(chat_id, f"🏁 **Іспит завершено!**\nТвій результат: {score} з {len(QUIZ)} правильних відповідей. Рюк задоволений.")
        return

    question_data = QUIZ[q_index]
    markup = types.InlineKeyboardMarkup()
    
    # Замість тексту передаємо в callback_data тільки ІНДЕКС варіанту (0, 1 або 2)
    for i, option in enumerate(question_data["options"]):
        markup.add(types.InlineKeyboardButton(text=option, callback_data=f"q_{q_index}_{score}_{i}"))
        
    bot.send_message(chat_id, question_data["question"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('q_'))
def handle_quiz_answer(call):
    data_parts = call.data.split('_')
    q_index = int(data_parts[1])
    score = int(data_parts[2])
    opt_index = int(data_parts[3]) 

    bot.answer_callback_query(call.id)
    
    # Порівнюємо індекс натиснутої кнопки
    if opt_index == QUIZ[q_index]["right_index"]:
        score += 1
        bot.send_message(call.message.chat.id, "🟢 Абсолютно вірно!")
    else:
        bot.send_message(call.message.chat.id, "🔴 Неправильно! Бог смерті розчарований.")
        
    start_quiz(call.message.chat.id, q_index + 1, score)

if __name__ == '__main__':
    bot.infinity_polling()

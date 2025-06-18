import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters
)

logging.basicConfig(level=logging.INFO)

waiting_users = []
active_chats = {}

user_data = {}  # user_id: {"gender": "male"/"female", "age": int, "partner_gender": str, "partner_age_range": (min_age, max_age)}

def get_pronoun(gender):
    if gender == "male":
        return "Він"
    elif gender == "female":
        return "Вона"
    else:
        return "Він/Вона"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        await update.message.reply_text("Ви вже в чаті.")
        return
    if user_id in waiting_users:
        await update.message.reply_text("Очікуйте на співрозмовника.")
        return
    
    keyboard = [
        [InlineKeyboardButton("Чоловіча", callback_data="gender_male"),
         InlineKeyboardButton("Жіноча", callback_data="gender_female")]
    ]
    await update.message.reply_text(
        f"Вітаю! Оберіть вашу стать. В черзі зараз: {len(waiting_users)} осіб.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def gender_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    gender = None
    if query.data == "gender_male":
        gender = "male"
    elif query.data == "gender_female":
        gender = "female"

    user_data[user_id] = {"gender": gender, "age": None, "partner_gender": None, "partner_age_range": None}

    await query.edit_message_text("Введіть, будь ласка, ваш вік (числом від 18 до 99):")

async def age_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data or user_data[user_id]["age"] is not None:
        await update.message.reply_text("Ви вже в процесі або в чаті. Напишіть /start для початку.")
        return
    
    text = update.message.text
    if not text.isdigit() or not (18 <= int(text) <= 99):
        await update.message.reply_text("Введіть коректний вік від 18 до 99 (числом).")
        return

    age = int(text)
    user_data[user_id]["age"] = age

    keyboard = [
        [InlineKeyboardButton("Чоловіча", callback_data="partner_gender_male"),
         InlineKeyboardButton("Жіноча", callback_data="partner_gender_female"),
         InlineKeyboardButton("Будь-яка", callback_data="partner_gender_any")]
    ]
    await update.message.reply_text(
        "Оберіть стать співрозмовника, з яким хочете поспілкуватися:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def partner_gender_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    partner_gender = None
    if query.data == "partner_gender_male":
        partner_gender = "male"
    elif query.data == "partner_gender_female":
        partner_gender = "female"
    elif query.data == "partner_gender_any":
        partner_gender = "any"

    user_data[user_id]["partner_gender"] = partner_gender

    keyboard = [
        [InlineKeyboardButton("18-19", callback_data="age_range_18_19"),
         InlineKeyboardButton("20-29", callback_data="age_range_20_29")],
        [InlineKeyboardButton("30-39", callback_data="age_range_30_39"),
         InlineKeyboardButton("40-49", callback_data="age_range_40_49")],
        [InlineKeyboardButton("50-59", callback_data="age_range_50_59"),
         InlineKeyboardButton("60-99", callback_data="age_range_60_99")]
    ]

    await query.edit_message_text(
        "Оберіть діапазон віку співрозмовника:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def partner_age_range_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data  # наприклад "age_range_20_29"
    parts = data.split('_')
    min_age = int(parts[2])
    max_age = int(parts[3])

    user_data[user_id]["partner_age_range"] = (min_age, max_age)

    if user_id not in waiting_users and user_id not in active_chats:
        waiting_users.append(user_id)

    partner_id = None
    for candidate_id in waiting_users:
        if candidate_id == user_id:
            continue
        c_data = user_data.get(candidate_id)
        if not c_data:
            continue

        if user_data[user_id]["partner_gender"] != "any" and c_data["gender"] != user_data[user_id]["partner_gender"]:
            continue

        if c_data.get("partner_gender") not in (user_data[user_id]["gender"], "any"):
            continue

        min_age_c, max_age_c = user_data[user_id]["partner_age_range"]
        age_c = c_data.get("age")
        if age_c is None or not (min_age_c <= age_c <= max_age_c):
            continue

        min_age_u, max_age_u = c_data.get("partner_age_range", (18, 99))
        age_u = user_data[user_id]["age"]
        if age_u is None or not (min_age_u <= age_u <= max_age_u):
            continue

        partner_id = candidate_id
        break

    if partner_id:
        waiting_users.remove(user_id)
        waiting_users.remove(partner_id)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        p_gender = user_data[partner_id]["gender"]
        p_age = user_data[partner_id]["age"]
        p_pronoun = get_pronoun(p_gender)

        u_gender = user_data[user_id]["gender"]
        u_age = user_data[user_id]["age"]
        u_pronoun = get_pronoun(u_gender)

        end_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Завершити розмову", callback_data="end_chat")]]
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=f"🔗 Ви з'єднані з анонімом!\n{p_pronoun}, {p_age} років.",
            reply_markup=end_button
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text=f"🔗 Ви з'єднані з анонімом!\n{u_pronoun}, {u_age} років.",
            reply_markup=end_button
        )
    else:
        await query.edit_message_text(
            f"⏳ Очікуємо іншого користувача... В черзі зараз: {len(waiting_users)}"
        )

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    partner_id = active_chats.pop(user_id, None)
    if partner_id:
        active_chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="❌ Користувач завершив розмову.")
    if user_id in waiting_users:
        waiting_users.remove(user_id)
    if user_id in user_data:
        del user_data[user_id]
    await query.edit_message_text("🚪 Ви завершили розмову.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = active_chats.pop(user_id, None)
    if partner_id:
        active_chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="❌ Користувач вийшов з чату.")
    if user_id in waiting_users:
        waiting_users.remove(user_id)
    if user_id in user_data:
        del user_data[user_id]
    await update.message.reply_text("🚪 Ви вийшли з чату.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = active_chats.get(user_id)
    if partner_id:
        try:
            await context.bot.send_message(chat_id=partner_id, text=update.message.text)
        except Exception:
            await update.message.reply_text("❌ Неможливо доставити повідомлення.")
    else:
        await update.message.reply_text("⚠️ Ви ще не в чаті. Напишіть /start.")

def main():
    import os
    TOKEN = os.getenv("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gender_choice, pattern=r"gender_.*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, age_received))
    app.add_handler(CallbackQueryHandler(partner_gender_choice, pattern=r"partner_gender_.*"))
    app.add_handler(CallbackQueryHandler(partner_age_range_choice, pattern=r"age_range_.*"))
    app.add_handler(CallbackQueryHandler(end_chat, pattern="end_chat"))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()

if __name__ == "__main__":
    main()

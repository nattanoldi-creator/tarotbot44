import logging
import random
import requests
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7289635708:AAFzdbjE3tYhF0VR9Hv8uCE72vcpvJ4V0ws"

# 🎴 Полная колода Таро (78 карт) — Старшие и Младшие Арканы
TAROT_DECK = [
    # ========== СТАРШИЕ АРКАНЫ ==========
    {
        "name": "0. Шут",
        "upright": "Новые начинания, спонтанность, невинность, вера в себя.",
        "reversed": "Безрассудство, рискованное поведение, неопытность, плохое решение.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/43/RWS_Tarot_00_Fool.jpg"
    },
    {
        "name": "1. Маг",
        "upright": "Сила воли, творчество, мастерство, манипуляции.",
        "reversed": "Обман, манипуляции, неумение использовать ресурсы.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg"
    },
    {
        "name": "2. Верховная Жрица",
        "upright": "Интуиция, тайны, подсознание, духовное знание.",
        "reversed": "Секреты, подавленные чувства, отключение от интуиции.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg"
    },
    {
        "name": "3. Императрица",
        "upright": "Плодородие, материнство, природа, изобилие.",
        "reversed": "Зависимость, пустота, пренебрежение заботой о себе.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_03_Empress.jpg"
    },
    {
        "name": "4. Император",
        "upright": "Власть, структура, контроль, отцовство.",
        "reversed": "Тирания, жесткость, нестабильность, отсутствие дисциплины.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg"
    },
    {
        "name": "5. Иерофант",
        "upright": "Традиции, духовные учения, институты, наставник.",
        "reversed": "Бунт против традиций, ложный учитель, догматизм.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/26/RWS_Tarot_05_Hierophant.jpg"
    },
    {
        "name": "6. Влюбленные",
        "upright": "Любовь, гармония, выбор, отношения.",
        "reversed": "Разлад, несовместимость, плохой выбор, предательство.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_06_Lovers.jpg"
    },
    {
        "name": "7. Колесница",
        "upright": "Победа, воля, движение вперед, контроль.",
        "reversed": "Потеря контроля, поражение, отсутствие направления.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_07_Chariot.jpg"
    },
    {
        "name": "8. Сила",
        "upright": "Мужество, терпение, внутренняя сила, мягкость.",
        "reversed": "Слабость, сомнения, агрессия, отсутствие самоконтроля.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg"
    },
    {
        "name": "9. Отшельник",
        "upright": "Поиск истины, уединение, мудрость, самоанализ.",
        "reversed": "Одиночество, изоляция, потеря связи, цинизм.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0d/RWS_Tarot_09_Hermit.jpg"
    },
    {
        "name": "10. Колесо Фортуны",
        "upright": "Циклы, судьба, перемены, удача.",
        "reversed": "Плохая удача, сопротивление переменам, застой.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/09/RWS_Tarot_10_Wheel_of_Fortune.jpg"
    },
    {
        "name": "11. Справедливость",
        "upright": "Баланс, карма, правда, ответственность.",
        "reversed": "Несправедливость, предвзятость, нечестность, избегание последствий.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/03/RWS_Tarot_11_Justice.jpg"
    },
    {
        "name": "12. Повешенный",
        "upright": "Жертва, новый взгляд, пауза, смирение.",
        "reversed": "Стагнация, сопротивление, эгоизм, нетерпение.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/29/RWS_Tarot_12_Hanged_Man.jpg"
    },
    {
        "name": "13. Смерть",
        "upright": "Конец, трансформация, переход, обновление.",
        "reversed": "Страх перемен, цепляние за прошлое, застой.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d8/RWS_Tarot_13_Death.jpg"
    },
    {
        "name": "14. Умеренность",
        "upright": "Баланс, терпение, алхимия, гармония.",
        "reversed": "Дисбаланс, крайности, отсутствие гармонии.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/RWS_Tarot_14_Temperance.jpg"
    },
    {
        "name": "15. Дьявол",
        "upright": "Привязанности, искушение, материализм, порабощение.",
        "reversed": "Освобождение, разрыв зависимостей, просветление.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg"
    },
    {
        "name": "16. Башня",
        "upright": "Разрушение, кризис, внезапные перемены, просветление.",
        "reversed": "Избегание катастрофы, отсрочка неизбежного, частичный крах.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/RWS_Tarot_16_Tower.jpg"
    },
    {
        "name": "17. Звезда",
        "upright": "Надежда, вдохновение, исцеление, свет в конце тоннеля.",
        "reversed": "Потеря надежды, отчаяние, пессимизм.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6d/RWS_Tarot_17_Star.jpg"
    },
    {
        "name": "18. Луна",
        "upright": "Иллюзии, страхи, подсознание, обман.",
        "reversed": "Выход из иллюзий, преодоление страхов, ясность.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/RWS_Tarot_18_Moon.jpg"
    },
    {
        "name": "19. Солнце",
        "upright": "Радость, успех, ясность, жизненная сила.",
        "reversed": "Временное угасание, печаль, задержка успеха.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/2e/RWS_Tarot_19_Sun.jpg"
    },
    {
        "name": "20. Суд",
        "upright": "Возрождение, пробуждение, призвание, решение.",
        "reversed": "Сомнения в себе, отсутствие ясности, страх перемен.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/03/RWS_Tarot_20_Judgement.jpg"
    },
    {
        "name": "21. Мир",
        "upright": "Завершение, гармония, путешествие, целостность.",
        "reversed": "Незавершенность, препятствия, отсутствие закрытия.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/44/RWS_Tarot_21_World.jpg"
    },

    # ========== МЛАДШИЕ АРКАНЫ: ЖЕЗЛЫ ==========
    *[{
        "name": f"{i}. {['Туз', 'Двойка', 'Тройка', 'Четверка', 'Пятерка', 'Шестерка', 'Семерка', 'Восьмерка', 'Девятка', 'Десятка', 'Паж', 'Рыцарь', 'Королева', 'Король'][i-1]} Жезлов",
        "upright": "Энергия, страсть, действие, предприимчивость.",
        "reversed": "Задержка, конфликты, потеря мотивации.",
        "image_url": f"https://upload.wikimedia.org/wikipedia/commons/{'a/a8' if i == 1 else 'f/f6' if i == 2 else 'd/d7' if i == 3 else 'c/c7' if i == 4 else 'd/d8' if i == 5 else 'e/e5' if i == 6 else 'd/d7' if i == 7 else 'f/f0' if i == 8 else 'b/b5' if i == 9 else 'e/e7' if i == 10 else 'd/d5' if i == 11 else 'f/f5' if i == 12 else 'c/c5' if i == 13 else 'b/bd'}/RWS_Tarot_{str(i).zfill(2)}_of_Wands{'' if i <= 10 else '_Page' if i == 11 else '_Knight' if i == 12 else '_Queen' if i == 13 else '_King'}.jpg"
    } for i in range(1, 15)],

    # ========== МЛАДШИЕ АРКАНЫ: КУБКИ ==========
    *[{
        "name": f"{i}. {['Туз', 'Двойка', 'Тройка', 'Четверка', 'Пятерка', 'Шестерка', 'Семерка', 'Восьмерка', 'Девятка', 'Десятка', 'Паж', 'Рыцарь', 'Королева', 'Король'][i-1]} Кубков",
        "upright": "Эмоции, любовь, отношения, интуиция.",
        "reversed": "Подавленные чувства, разочарование, одиночество.",
        "image_url": f"https://upload.wikimedia.org/wikipedia/commons/{'3/33' if i == 1 else 'd/d5' if i == 2 else '3/31' if i == 3 else '6/6b' if i == 4 else '5/5c' if i == 5 else '3/31' if i == 6 else 'c/c3' if i == 7 else 'c/c7' if i == 8 else 'a/a7' if i == 9 else '6/6a' if i == 10 else 'f/f3' if i == 11 else 'f/f4' if i == 12 else '3/37' if i == 13 else '1/18'}/RWS_Tarot_{str(i).zfill(2)}_of_Cups{'' if i <= 10 else '_Page' if i == 11 else '_Knight' if i == 12 else '_Queen' if i == 13 else '_King'}.jpg"
    } for i in range(1, 15)],

    # ========== МЛАДШИЕ АРКАНЫ: МЕЧИ ==========
    *[{
        "name": f"{i}. {['Туз', 'Двойка', 'Тройка', 'Четверка', 'Пятерка', 'Шестерка', 'Семерка', 'Восьмерка', 'Девятка', 'Десятка', 'Паж', 'Рыцарь', 'Королева', 'Король'][i-1]} Мечей",
        "upright": "Мысли, конфликты, решимость, ясность.",
        "reversed": "Жестокость, путаница, несправедливость.",
        "image_url": f"https://upload.wikimedia.org/wikipedia/commons/{'c/cb' if i == 1 else 'd/d7' if i == 2 else 'a/a5' if i == 3 else '0/0c' if i == 4 else '5/5e' if i == 5 else '6/6c' if i == 6 else 'b/bd' if i == 7 else 'c/c1' if i == 8 else '5/5c' if i == 9 else 'a/a0' if i == 10 else 'f/f4' if i == 11 else 'c/c9' if i == 12 else '3/35' if i == 13 else 'd/d5'}/RWS_Tarot_{str(i).zfill(2)}_of_Swords{'' if i <= 10 else '_Page' if i == 11 else '_Knight' if i == 12 else '_Queen' if i == 13 else '_King'}.jpg"
    } for i in range(1, 15)],

    # ========== МЛАДШИЕ АРКАНЫ: ПЕНТАКЛИ ==========
    *[{
        "name": f"{i}. {['Туз', 'Двойка', 'Тройка', 'Четверка', 'Пятерка', 'Шестерка', 'Семерка', 'Восьмерка', 'Девятка', 'Десятка', 'Паж', 'Рыцарь', 'Королева', 'Король'][i-1]} Пентаклей",
        "upright": "Финансы, работа, материальный мир, стабильность.",
        "reversed": "Финансовые трудности, нестабильность, жадность.",
        "image_url": f"https://upload.wikimedia.org/wikipedia/commons/{'e/e3' if i == 1 else 'f/fd' if i == 2 else 'd/d7' if i == 3 else 'd/d1' if i == 4 else 'c/c9' if i == 5 else '3/3a' if i == 6 else 'c/c7' if i == 7 else 'f/f1' if i == 8 else 'a/a7' if i == 9 else 'f/f3' if i == 10 else 'f/f1' if i == 11 else 'f/f3' if i == 12 else 'b/b0' if i == 13 else 'd/d3'}/RWS_Tarot_{str(i).zfill(2)}_of_Pentacles{'' if i <= 10 else '_Page' if i == 11 else '_Knight' if i == 12 else '_Queen' if i == 13 else '_King'}.jpg"
    } for i in range(1, 15)],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие и кнопка 'Вытянуть карту'"""
    keyboard = [[InlineKeyboardButton("🎴 Вытянуть карту Таро", callback_data='draw')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🔮 *Добро пожаловать в Таро-Бот!*\n\n"
        "Я помогу тебе получить послание Вселенной.\n"
        "Каждая карта может выпасть *прямо* или *перевёрнуто* — и это меняет её значение.\n\n"
        "👇 Нажми кнопку, чтобы начать."
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def draw_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатие кнопки и отправляет случайную карту с учётом ориентации"""
    query = update.callback_query
    await query.answer()

    # Выбираем случайную карту
    card = random.choice(TAROT_DECK)

    # Определяем, прямая или перевёрнутая
    is_reversed = random.choice([True, False])
    orientation = "перевёрнутая" if is_reversed else "прямая"
    meaning = card["reversed"] if is_reversed else card["upright"]

    # Загружаем изображение
    try:
        response = requests.get(card["image_url"], timeout=10)
        if response.status_code != 200:
            raise Exception("Image not found")
        image = BytesIO(response.content)
        image.name = f'{card["name"]}.jpg'
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        await query.edit_message_text(text="❌ Не удалось загрузить изображение карты. Попробуй ещё раз.")
        return

    # Подпись к фото
    caption = (
        f"🎴 *{card['name']}*\n"
        f"🌀 *Ориентация:* {orientation}\n\n"
        f"💬 _{meaning}_"
    )

    # Отправляем фото
    await query.message.reply_photo(photo=image, caption=caption, parse_mode='Markdown')

    # Обновляем кнопку под старым сообщением
    keyboard = [[InlineKeyboardButton("🎴 Вытянуть ещё одну карту", callback_data='draw')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(draw_card, pattern='^draw$'))

    print("✅ Бот запущен! Напиши ему в Telegram: /start")

    application.run_polling()

if __name__ == '__main__':
    main()

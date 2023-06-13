# Response text.
START_MSG = """Привет!
Это бот, который проводит анонимные опросы для оценки преподавателей.

Список доступных команд:
<em>/start</em> - Запустить бот
<em>/help</em> - Посмотреть справку
"""
ADD_TEACHER = "Выберите своего преподавателя, которого вы собираетесь оценивать."
TYPE_TEACHER_NAME = "Введите имя преподователя"
TYPE_TEACHER_NAME_ERROR_NO_USER = "Извините! Вы не принадлежите группе"
TYPE_TEACHER_NAME_ERROR_BOT_KICKED = "Извините! Бот был удален из группы"
TYPE_TEACHER_NAME_ERROR_NO_GROUP = "Бот пока не добавлен в группу"
TYPE_TEACHER_NAME_ERROR_NO_ADMIN = "Простите! Только админы могут добавить преподователя"
TYPE_TEACHER_NAME_ERROR_DUPLICATE = "Преподователь был ранее добавлен"
# Buttoms text.
BUTTON_ADD_TEACHER = "👨‍🏫   Добавить преподвателя"
BUTTON_RATE_TEACHER = "🏅   Оценить преподвателя"
BUTTON_LIST_TEACHER = "📓   Список преподвателей"


# Handler text.
HANDLER_ADD_TEACHER = "Добавить преподвателя"
HANDLER_RATE_TEACHER = "Оценить преподвателя"
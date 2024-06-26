from pathlib import Path

from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont

role_fields = {
    "Администратор": ["Оплачено,\xa0₽", "Инициатор"],
    "Тренер": ["Сумма", "Автодействие", "Комментарий", "Сотрудник"],
}

months = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

data_button_pattern = "%m.%Y"
font_path = Path("files/Source Serif Pro.ttf")
custom_font = TrueTypeFont.true_type_font_from_file(font_path)
DB_MODE_ROLES = [
    "SMM",
]

import datetime
import re

from bot.constants.keyboards import Buttons, keyboard_generator
from bot.constants.states import States
from bot.utils import send_or_edit_message
from core.crud import get_schedule
from core.models import Employee
from dateutil.relativedelta import relativedelta

from constants import data_button_pattern, months


async def show_schedule(update, context):
    query = update.callback_query
    now_date = datetime.datetime.today()
    if query and query.data and re.match(r"^[0-9]{2}\.[0-9]{4}$", query.data):
        data_range = datetime.datetime.strptime(
            query.data, data_button_pattern
        )
    else:
        data_range = now_date
    up = data_range + relativedelta(months=1)
    down = data_range + relativedelta(months=-1)
    buttons = [
        [
            [
                "<- " + months[down.month - 1],
                down.strftime(data_button_pattern),
            ],
            [months[up.month - 1] + " ->", up.strftime(data_button_pattern)],
        ],
        [[Buttons.TODAY.value, now_date.strftime(data_button_pattern)]],
    ]
    employee = await Employee.objects.aget(
        telegram_id=update.effective_chat["id"]
    )
    if employee.is_stuff:
        message = await get_schedule(data_range)
    elif employee.сontract.template.hourly_payment:
        message = await get_schedule(data_range, employee)
    else:
        message = "Для вашей роли не доступно расписание."
    await send_or_edit_message(
        update, message, reply_markup=keyboard_generator(buttons)
    )
    return States.SCHEDULE

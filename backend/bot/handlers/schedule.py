import datetime
import re

from bot.constants.keyboards import Buttons, keyboard_generator
from bot.constants.states import States
from bot.crud import get_permission
from bot.handlers.start import start
from bot.utils import send_or_edit_message
from constants import data_button_pattern, months
from core.crud import get_schedule
from dateutil.relativedelta import relativedelta


async def show_schedule(update, context):
    permission = await get_permission(update)
    is_admitted, employee_filter = permission.get(
        States.SCHEDULE, (False, None)
    )
    if not is_admitted:
        return await start(update, context)
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
    message = await get_schedule(data_range, employee_filter)
    await send_or_edit_message(
        update, message, reply_markup=keyboard_generator(buttons)
    )
    return States.SCHEDULE

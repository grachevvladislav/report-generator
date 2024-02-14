import datetime
import re

import dateutil

from constants.constants import data_button_pattern, months
from constants.keyboards import Buttons, keyboard_generator
from constants.states import States
from google_sheet_backend import get_admin_schedule
from utils import send_or_edit_message


async def show_schedule(update, context):
    query = update.callback_query
    now_date = datetime.datetime.today()
    if query and query.data and re.match(r"^[0-9]{2}\.[0-9]{4}$", query.data):
        data_range = datetime.datetime.strptime(
            query.data, data_button_pattern
        )
    else:
        data_range = now_date
    up = data_range + dateutil.relativedelta.relativedelta(months=1)
    down = data_range + dateutil.relativedelta.relativedelta(months=-1)
    buttons = [
        [
            [
                "<- " + months[down.month - 1],
                down.strftime(data_button_pattern),
            ],
            [months[up.month - 1] + " ->", up.strftime(data_button_pattern)],
        ],
        [[Buttons.RELOAD.value, data_range.strftime(data_button_pattern)]],
    ]
    if str(update.effective_chat["id"]) in context.bot_data["stuff_ids"]:
        employee = None
        buttons.append([Buttons.MENU])
    else:
        employee = context.bot_data["admins_dict"][
            str(update.effective_chat["id"])
        ]
    message = get_admin_schedule(data_range, employee)
    await send_or_edit_message(
        update, message, reply_markup=keyboard_generator(buttons)
    )
    return States.SCHEDULE

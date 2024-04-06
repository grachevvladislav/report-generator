from datetime import datetime

import dateutil

from constants.constants import DB_MODE_ROLES
from constants.exceptions import AdminFail, EmployeeFail, InnerFail, ParseFail
from constants.keyboards import confirm_keyboard
from constants.states import States
from file_parse import create_pdf, report_parsing
from google_sheet_backend import (
    get_employees_info,
    get_settings_sheets,
    update_document_counter,
)
from utils import send_or_edit_message


async def counter_increase(update, context):
    update_document_counter(context.bot_data)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Счетчик документов успешно обновлен. Жду новые файлы."
    )
    return States.WAITING_FOR_FILE


async def wait_for_new_report(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Жду исправлений.")
    return States.WAITING_FOR_FILE


async def make_report(update, context):
    context.bot_data.update(get_settings_sheets())
    context.bot_data[
        "report_interval"
    ] = datetime.now() + dateutil.relativedelta.relativedelta(months=-1)
    if update.message:
        file = await update.message.document.get_file()
        binary_file = await file.download_as_bytearray()
        await send_or_edit_message(update, "Данные обрабатываются ⏳")
    else:
        await send_or_edit_message(
            update,
            f"Режим поддерживает акты только для ролей {' ,'.join(DB_MODE_ROLES)}",
        )
        employees = get_employees_info(
            context.bot_data["employees"], DB_MODE_ROLES
        )
        pdf_file = create_pdf(employees, context.bot_data)
        chat_id = update.effective_chat.id
        await context.bot.send_document(
            chat_id,
            pdf_file,
            filename=f"{datetime.today().strftime('%d.%m.%Y')}.pdf",
        )
        await send_or_edit_message(
            update,
            "\n\n".join(employees.notification) + "Документы верны?",
            reply_markup=confirm_keyboard,
        )
        return States.CHECK_FILE
    try:
        employees = report_parsing(binary_file, context.bot_data)
        pdf_file = create_pdf(employees, context.bot_data)
    except ParseFail as e:
        await send_or_edit_message(update, f"Парсинг файла:\n\n{e}")
    except AdminFail as e:
        await send_or_edit_message(update, f"График работы:\n\n{e}")
    except InnerFail as e:
        await send_or_edit_message(update, f"Внутренняя ошибка:\n\n{e}")
    except EmployeeFail as e:
        await send_or_edit_message(update, f"Информация о сотрудниках:\n\n{e}")
    else:
        await update.message.reply_document(
            pdf_file,
            filename=f"{datetime.today().strftime('%d.%m.%Y')}.pdf",
        )
        await update.message.reply_text(
            "\n\n".join(employees.notification) + "Документы верны?",
            reply_markup=confirm_keyboard,
        )
        return States.CHECK_FILE
    return States.WAITING_FOR_FILE

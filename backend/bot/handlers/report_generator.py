from datetime import datetime

import dateutil
from constants.exceptions import AdminFail, EmployeeFail, InnerFail, ParseFail
from constants.keyboards import confirm_keyboard
from constants.states import States
from google_sheet_backend import get_settings_sheets, update_document_counter

from file_parse import create_pdf, report_parsing


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
    file = await update.message.document.get_file()
    binary_file = await file.download_as_bytearray()
    await update.message.reply_text("Данные обрабатываются ⏳")
    constants = get_settings_sheets()
    constants[
        "report_interval"
    ] = datetime.now() + dateutil.relativedelta.relativedelta(months=-1)

    try:
        employees = report_parsing(binary_file, constants)
        pdf_file = create_pdf(employees, constants)
    except ParseFail as e:
        await update.message.reply_text(f"Парсинг файла:\n\n{e}")
    except AdminFail as e:
        await update.message.reply_text(f"График работы:\n\n{e}")
    except InnerFail as e:
        await update.message.reply_text(f"Внутренняя ошибка:\n\n{e}")
    except EmployeeFail as e:
        await update.message.reply_text(f"Информация о сотрудниках:\n\n{e}")
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

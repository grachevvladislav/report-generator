import datetime

import dateutil.relativedelta

from exceptions import ParseFail
from file_parse import create_pdf, report_parsing
from google_sheet_backend import (
    get_admins_working_time,
    get_constants,
    get_employees,
    get_settings_sheets,
    update_document_counter,
)


async def make_report(update, context):
    settings_sheets = get_settings_sheets()
    constants = get_constants(settings_sheets)
    if not update.message.from_user["id"] in constants["stuff_ids"]:
        await update.message.reply_text("Обработка файлов недоступна!")
        return

    try:
        employees: dict = get_employees(settings_sheets["employees"])
    except ParseFail as e:
        await update.message.reply_text(f"Информация о сотрудниках:\n\n{e}")
        return

    file = await update.message.document.get_file()
    binary_file = await file.download_as_bytearray()
    try:
        report_parsing(employees, binary_file)
    except ParseFail as e:
        await update.message.reply_text(f"Отчет KPI:\n\n{e}")
        return

    last_month = (
        datetime.datetime.now()
        + dateutil.relativedelta.relativedelta(months=-1)
    )
    try:
        get_admins_working_time(employees, last_month, constants)
    except ParseFail as e:
        await update.message.reply_text(
            f"График работы администраторов:\n\n{e}"
        )
        return
    await update.message.reply_text("Данные обрабатываются ⏳")
    try:
        pdf_file = create_pdf(employees, last_month, constants)
    except ParseFail as e:
        await update.message.reply_text(f"Сборка отчета:\n\n{e}")
        return
    await update.message.reply_document(
        pdf_file, filename=f'{last_month.strftime("%B %Y")}.pdf'
    )
    update_document_counter(constants)

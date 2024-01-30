import datetime

from telegram.ext import CommandHandler

from constants.exceptions import AdminFail, EmployeeFail, InnerFail, ParseFail
from constants.keyboards import (
    confirm_keyboard,
    keyboard_from_list,
    start_keyboard,
)
from constants.states import States
from file_parse import create_pdf, report_parsing
from google_sheet_backend import (
    get_admin_schedule,
    get_settings_sheets,
    get_user_permissions,
    update_document_counter,
)


async def show_schedule(update, context):
    query = update.callback_query
    if query:
        data_delta = query.data
    else:
        data_delta = None
    schedule, buttons = get_admin_schedule(
        context.user_data["admins_dict"][str(update.effective_chat["id"])],
        data_delta,
    )
    if update.message:
        await update.message.reply_text(
            "\n".join(schedule),
            reply_markup=keyboard_from_list(buttons),
        )
    else:
        await query.edit_message_text(
            "\n".join(schedule),
            reply_markup=keyboard_from_list(buttons),
        )
    return States.SCHEDULE


async def start(update, context):
    context.user_data.update(get_user_permissions())
    client_id = str(update.effective_chat["id"])
    if client_id in context.user_data["admins_dict"].keys():
        return await show_schedule(update, context)
    elif client_id in context.user_data["stuff_ids"]:
        await update.message.reply_text(
            "Отправьте отчет о продажах или проведенных занятиях"
        )
        return States.WAITING_FOR_FILE
    else:
        for stuff in context.user_data["stuff_ids"]:
            if "request_send" not in context.user_data.keys():
                await context.bot.send_message(
                    chat_id=stuff,
                    text=f"Поступил запрос от {update.effective_chat.first_name} "
                    f"{update.effective_chat.last_name}\n"
                    f"@{update.effective_chat.username}\n"
                    f"id:{update.effective_chat.id}",
                )
                context.user_data["request_send"] = True
        if update.message:
            await update.message.reply_text(
                "Доступ пока закрыт, но запрос уже отправлен администратору!",
                reply_markup=start_keyboard,
            )
        else:
            query = update.callback_query
            await query.edit_message_text(
                "Доступ пока закрыт, но запрос уже отправлен администратору!\n"
                "Обновлено "
                + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                reply_markup=start_keyboard,
            )
        return States.PERMISSION_DENIED


start_handler = CommandHandler("start", start)


async def make_report(update, context):
    context.user_data.update(get_settings_sheets())
    file = await update.message.document.get_file()
    binary_file = await file.download_as_bytearray()
    await update.message.reply_text("Данные обрабатываются ⏳")

    try:
        employees = report_parsing(binary_file, context.user_data)
        pdf_file = create_pdf(employees, context.user_data)
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
            filename=f"{context.user_data['last_month'].strftime('%B %Y')}.pdf",
        )
        await update.message.reply_text(
            "\n\n".join(employees.notification) + "Документы верны?",
            reply_markup=confirm_keyboard,
        )
        return States.CHECK_FILE
    return States.WAITING_FOR_FILE


async def counter_increase(update, context):
    update_document_counter(context.user_data)
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

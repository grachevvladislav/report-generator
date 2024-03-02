# import datetime
#
# from bot.constants.constants import BACK
# from bot.constants.keyboards import (
#     Buttons,
#     start_keyboard,
#     stuff_menu_keyboard,
# )
# from bot.constants.states import States
# from bot.handlers.report_generator import (
#     counter_increase,
#     make_report,
#     wait_for_new_report,
# )
# from bot.handlers.stuff import report_menu
# from bot.utils import PATTERN, send_or_edit_message
# from core.models import Employee
# from telegram.ext import (
#     CallbackQueryHandler,
#     CommandHandler,
#     ConversationHandler,
#     MessageHandler,
#     filters,
# )
#
# from .schedule import show_schedule
#
#
# async def start(update, context):
#     employee, _ = await Employee.objects.aget_or_create(
#         telegram_id=update.effective_chat["id"]
#     )
#     if employee.role == Employee.Role.ADMIN:
#         return await show_schedule(update, context)
#     elif employee.role == Employee.Role.STUFF:
#         await send_or_edit_message(
#             update,
#             "Управление ботом:",
#             reply_markup=stuff_menu_keyboard,
#         )
#         return States.STUFF_MENU
#     else:
#         for stuff in Employee.objects.filter(role=Employee.Role.STUFF).exclude(
#             telegram_id__exact=""
#         ):
#             if "request_send" not in context.bot_data.keys():
#                 await context.bot.send_message(
#                     chat_id=stuff,
#                     text=f"Поступил запрос от {update.effective_chat.first_name} "
#                     f"{update.effective_chat.last_name}\n"
#                     f"@{update.effective_chat.username}\n"
#                     f"id:{update.effective_chat.id}",
#                 )
#         await send_or_edit_message(
#             update,
#             "Доступ пока закрыт, но запрос уже отправлен администратору!\n"
#             "Обновлено "
#             + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
#             reply_markup=start_keyboard,
#         )
#         return States.PERMISSION_DENIED
#
#
# start_handler = CommandHandler("start", start)
#
# main_handler = ConversationHandler(
#     entry_points=[
#         start_handler,
#     ],
#     persistent=True,
#     name="main_handler",
#     states={
#         States.PERMISSION_DENIED: [
#             CallbackQueryHandler(
#                 start, pattern=PATTERN.format(Buttons.RELOAD.name)
#             ),
#         ],
#         States.STUFF_MENU: [
#             CallbackQueryHandler(
#                 show_schedule, pattern=PATTERN.format(Buttons.SCHEDULE.name)
#             ),
#             CallbackQueryHandler(
#                 report_menu,
#                 pattern=PATTERN.format(Buttons.CREATE_REPORT.name),
#             ),
#         ],
#         States.CREATE_REPORT: [
#             CallbackQueryHandler(
#                 make_report,
#                 pattern=PATTERN.format(Buttons.CREATE.name),
#             ),
#         ],
#         States.CHECK_FILE: [
#             CallbackQueryHandler(
#                 counter_increase, pattern=PATTERN.format(Buttons.YES.name)
#             ),
#             CallbackQueryHandler(
#                 wait_for_new_report, pattern=PATTERN.format(Buttons.NO.name)
#             ),
#         ],
#         States.SCHEDULE: [
#             CallbackQueryHandler(
#                 show_schedule, pattern=PATTERN.format(r"[0-9]{2}\.[0-9]{4}")
#             ),
#             CallbackQueryHandler(
#                 start, pattern=PATTERN.format(Buttons.MENU.name)
#             ),
#         ],
#     },
#     fallbacks=[
#         # CallbackQueryHandler(back_button, pattern=BACK),
#         start_handler
#     ],
# )

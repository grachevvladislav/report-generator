# import datetime
#
# from bot.constants.constants import months
# from bot.constants.exceptions import AdminFail
#
# from backend import settings
#
#
# def get_admins_working_time(employees, constants):
#     results = (
#         service.spreadsheets()
#         .values()
#         .get(
#             spreadsheetId=settings.schedule_url.get_secret_value(),
#             range=f"{constants['report_interval'].year}!A2:I900",
#         )
#         .execute()
#     )
#     for day in results["values"]:
#         if not len(day) > 1 or day[1] == "--":
#             continue
#         if key_name_generator(day[1]) not in employees.get_names():
#             employees.add_notifications(
#                 f'Неизвестный сотрудник в расписании\n {" ".join(day)}'
#             )
#         try:
#             day_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
#         except ValueError:
#             raise AdminFail(f'Ошибка в дате\n{" ".join(day)}')
#         if (
#             day_date.month == constants["report_interval"].month
#             and day_date.year == day_date.year
#         ):
#             if len(day) > 2:
#                 try:
#                     time = float(day[2].replace(",", "."))
#                 except ValueError:
#                     raise AdminFail(
#                         f'Ошибка при указании времени\n {" ".join(day)}'
#                     )
#             else:
#                 time = constants["default_working_time"]
#             employees.set_attribute(day[1].strip(), admin_work_time=time)
#
#
# def get_admin_schedule(
#     data_range: datetime.datetime, employee_name: list = None
# ) -> list:
#     now_date = datetime.datetime.today()
#     raw_table = (
#         service.spreadsheets()
#         .values()
#         .get(
#             spreadsheetId=settings.schedule_url.get_secret_value(),
#             range=f"{data_range.year}!A2:B900",
#         )
#         .execute()
#     )
#     working_days = []
#     message = (
#         f"Актуальный график на {months[data_range.month - 1]}.\n"
#         f"Обновлено "
#         f"{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
#     )
#     for day in raw_table["values"]:
#         if not len(day) > 1:
#             continue
#         try:
#             db_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
#         except ValueError:
#             raise AdminFail(f'Ошибка в дате\n{" ".join(day)}')
#
#         if db_date.month == data_range.month and (
#             not employee_name or employee_name == day[1]
#         ):
#             new_day = WorkingDay(date=db_date, fio=day[1])
#             if working_days and (
#                 (
#                     working_days[-1].date + datetime.timedelta(days=1)
#                     < new_day.date
#                 )
#                 or working_days[-1].fio != new_day.fio
#             ):
#                 working_days.append(WorkingDay(delimiter=True))
#             working_days.append(WorkingDay(date=db_date, fio=day[1]))
#     for day in working_days:
#         message += day.full_string(date=now_date, full=not bool(employee_name))
#     return message

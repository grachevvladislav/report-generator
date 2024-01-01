from telegram.ext import ApplicationBuilder, MessageHandler, Updater, filters

from config import settings
from handlers import make_report


def main():
    """Application launch point."""
    app = (
        ApplicationBuilder()
        .token(settings.telegram_token.get_secret_value())
        #.persistence(persistence)
        .build()
    )
    app.add_handler(MessageHandler(filters.Document.ALL, make_report))
    app.run_polling()


if __name__ == "__main__":
    main()









# with open('../files/employees.json') as json_data:
#     employees: dict = json.load(json_data)
#
#
#
#
#
# if __name__ == '__main__':
#     for FIO, chel in employees.items():
#
#         create_doc(chel)
#         print()

from telegram.ext import ApplicationBuilder
from docxtpl import DocxTemplate
from datetime import datetime
from telegram.ext import Updater, MessageHandler, filters
import json

from config import settings
from handlers import downloader


def create_doc(context):
    #context['date'] = datetime.today().strftime('%d.%m.%Y')
    print(context)
    doc = DocxTemplate('sample.docx')
    # doc.render(context)
    # doc.save("new.docx")


def main():
    """Application launch point."""
    app = (
        ApplicationBuilder()
        .token(settings.telegram_token.get_secret_value())
        #.persistence(persistence)
        .build()
    )
    app.add_handler(MessageHandler(filters.Document.ALL, downloader))
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

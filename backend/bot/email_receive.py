import email
import imaplib
import re
from email.header import decode_header

from bot.constants.exceptions import EmailFail
from bs4 import BeautifulSoup

from backend import settings
from backend.settings import logger


def html_parser(message):
    data = {}
    soup = BeautifulSoup(message, features="lxml")
    body = soup.find(attrs={"style": "background: #ffffff; padding: 30px"})
    table_in_div = body.find(
        attrs={"style": "border-top: 1px solid #e2e8ef; padding: 20px 0 0"}
    )
    data["Название"] = (
        table_in_div.find(string=re.compile("Назначение платежа"))
        .findNext("div")
        .text
    )
    data["Дата"] = (
        table_in_div.find(string=re.compile("Дата платежа")).findNext("p").text
    )
    data["ID клиента"] = (
        table_in_div.find(string=re.compile("ID клиента")).findNext("p").text
    )
    data["E-mail"] = (
        table_in_div.find(string=re.compile("E-mail")).findNext("p").text
    )
    summ_raw = body.find(attrs={"style": "padding: 20px 0"}).text
    summ_start = summ_raw.find("сумму ") + 6
    summ_end = summ_raw.find("RUB") + 3
    data["Сумма"] = summ_raw[summ_start:summ_end].replace("\xa0", "")
    return data


def from_subj_decode(msg_from_subj):
    if msg_from_subj:
        msg_from_subj = decode_header(msg_from_subj)[0][0]
        if isinstance(msg_from_subj, bytes):
            msg_from_subj = msg_from_subj.decode("utf-8")
        msg_from_subj = str(msg_from_subj).strip("<>").replace("<", "")
        return msg_from_subj
    else:
        return None


def get_payments():
    result = []
    with imaplib.IMAP4_SSL(settings.IMAP_SSL_HOST) as imap:
        status, _ = imap.login(
            settings.IMAP_USERNAME,
            settings.IMAP_PASSWORD,
        )
        if status != "OK":
            raise EmailFail("Ошибка подключения к почтовому серверу!")
        imap.select("INBOX")
        if settings.TEST_MAIL:
            _, raw_messages = imap.uid(
                "search",
                "SEEN",
            )
            decoded_messages = raw_messages[0].decode("utf-8").split(" ")[-1:]
        else:
            _, raw_messages = imap.uid(
                "search",
                "UNSEEN",
                "ALL",
            )
            decoded_messages = raw_messages[0].decode("utf-8").split(" ")
        if decoded_messages[0]:
            for message in decoded_messages:
                status, raw_letter = imap.uid("fetch", message, "(RFC822)")
                if status == "OK":
                    message = email.message_from_bytes(raw_letter[0][1])
                    msg_from = from_subj_decode(message["From"])
                    if settings.IMAP_FROM_EMAIL in msg_from:
                        data = html_parser(message.get_payload())
                        result.append(data)
                        logger.info("The message was successfully processed")
                    else:
                        logger.info(
                            f"New unknown mail. target: {settings.IMAP_FROM_EMAIL}, current{msg_from}"
                        )
    return result

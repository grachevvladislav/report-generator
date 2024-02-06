import email
import imaplib
import quopri
import re
from email.header import decode_header

from bs4 import BeautifulSoup

from config import settings
from constants.exceptions import EmailFail


def html_parser(message):
    data = {}
    soup = BeautifulSoup(message, features="lxml")
    result = soup.find_all(
        attrs=dict(
            style=re.compile(
                r"border-collapse:collapse;mso-table-lspace:0;"
                r"mso-table-rspace:0;margin: 0px;"
            )
        )
    )
    pay_name = result[1].text.split(": ")
    if len(pay_name) < 2:
        data["Название"] = "Не указано"
    else:
        data["Название"] = (
            result[1].text.split(": ")[1].replace("&#39", "").replace(";", "")
        )
    data["Дата"] = result[7].text
    data["Сумма"] = result[9].text.replace("\xa0", "")
    data["ID клиента"] = result[11].text
    data["E-mail"] = result[13].text
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
    with imaplib.IMAP4_SSL(settings.imap_ssl_host.get_secret_value()) as imap:
        status, _ = imap.login(
            settings.imap_username.get_secret_value(),
            settings.imap_password.get_secret_value(),
        )
        if status != "OK":
            raise EmailFail("Ошибка подключения к почтовому серверу!")
        imap.select("INBOX")
        _, raw_messages = imap.uid(
            "search",
            "UNSEEN",
            "ALL",
        )
        decoded_messages = raw_messages[0].decode("windows-1251").split(" ")
        if decoded_messages[0]:
            for message in decoded_messages:
                status, raw_letter = imap.uid("fetch", message, "(RFC822)")
                if status == "OK":
                    message = email.message_from_bytes(raw_letter[0][1])
                    quopri_decoded_message = quopri.decodestring(
                        message.get_payload()
                    ).decode(message.get_content_charset())
                    msg_from = from_subj_decode(message["From"])
                    if msg_from == settings.imap_from_email.get_secret_value():
                        data = html_parser(quopri_decoded_message)
                        result.append(data)
    return result

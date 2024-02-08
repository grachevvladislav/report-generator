import email
import imaplib
import re
from email.header import decode_header

from bs4 import BeautifulSoup

from config import settings
from constants.exceptions import EmailFail


def html_parser(message):
    data = {}
    soup = BeautifulSoup(message, features="lxml")
    body = soup.find(attrs={"style": "background: #ffffff; padding: 30px"})
    table_in_div = body.find(
        attrs={"style": "border-top: 1px solid #e2e8ef; padding: 20px 0 0"}
    )
    pay_name = (
        table_in_div.find(string=re.compile("Назначение платежа"))
        .findNext("div")
        .text.split(": ")
    )
    if len(pay_name) < 2:
        data["Название"] = "Не указано"
    else:
        data["Название"] = pay_name[1]
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
            # "UNSEEN",
            "ALL",
        )
        decoded_messages = raw_messages[0].decode("utf-8").split(" ")
        if decoded_messages[0]:
            for message in decoded_messages:
                status, raw_letter = imap.uid("fetch", message, "(RFC822)")
                if status == "OK":
                    message = email.message_from_bytes(raw_letter[0][1])
                    msg_from = from_subj_decode(message["From"])
                    if msg_from == settings.imap_from_email.get_secret_value():
                        data = html_parser(message.get_payload())
                        result.append(data)
    return result

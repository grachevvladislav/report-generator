from google.oauth2.service_account import Credentials
from googleapiclient import discovery

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file(
    filename="inspired-alcove.json", scopes=SCOPES
)
service = discovery.build("sheets", "v4", credentials=credentials)

# Import telegram api
from telegram.ext import Updater
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
#Import google api
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate



updater = Updater(token='2134073881:AAFdncMITTr9ngAErldA3dvcTHgyJK5mGSw', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
SCOPES = ['https://www.googleapis.com/auth/drive.metadata']

def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def searchDrive(service, search):
    result = []
    page_token = None
    query = f"'1CWX2HH65tdndM-k8OLQ5bfn-0JZhYPwS' in parents and name contains '{search}'"
    while True:
        response = service.files().list(q=query,
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return result

def inline_search(update: Update, context: CallbackContext,):
    query = update.inline_query.query
    if not query:
        return
    results = []
    searchResults = searchDrive(get_gdrive_service(), query)
    if not searchResults:
        return
    for i in range(len(searchResults)):
        docLink = f"https://docs.google.com/document/d/{searchResults[i][0]}/edit"
        results.append(
            InlineQueryResultArticle(
                id=id(docLink),
                title=searchResults[i][1],
                input_message_content=InputTextMessageContent(docLink)
            )
        )
    context.bot.answer_inline_query(update.inline_query.id, results)




inline_search_handler = InlineQueryHandler(inline_search)
dispatcher.add_handler(inline_search_handler)

updater.start_polling()
updater.idle
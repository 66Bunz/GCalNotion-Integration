
import json
import base64
import os
import threading
import webbrowser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pymongo
from pymongo import MongoClient
import tkinter as tk
from tkinter import Tk, Label, Button, Frame, messagebox


img = b'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'


class AppGUI:
    """
    Main window class.
    """
    def __init__(self, window):
        self.master = window
        window.title('Google Token Generator')
        window.geometry('300x150')
        window.resizable(False, False)
        window.configure(bg='#202020')
        window.attributes('-alpha', 0.9)
        tmp = open('temp.ico', 'wb+')
        tmp.write(base64.b64decode(img))
        tmp.close()
        root.iconbitmap('temp.ico')
        os.remove('temp.ico')
        self.main_frame = Frame(root, bg='#202020', height=150)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)
        self.main_frame.pack_propagate(0)
        self.label_frame = Frame(self.main_frame, bg='#202020', height=70)
        self.label_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.main_frame.pack_propagate(0)
        self.label = Label(self.label_frame, bg='#202020', fg='#B8B8B8', text='Google Token Generator', font=('Arial', 18))
        self.label.pack(pady=15)
        self.button_frame = Frame(self.main_frame, bg='#202020', height=70)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=20)
        self.generate_button = Button(self.button_frame, bg='#4CA5AC', text='Generate Token', command=self.create_token_thread)
        self.generate_button.pack(side=tk.LEFT, padx=30)
        self.close_button = Button(self.button_frame, bg='#9D1813', fg='white', text='Close', command=root.quit)
        self.close_button.pack(side=tk.RIGHT, padx=40)

    def create_token_thread(self):
        """
        Creates a thread to run the create_token() function.
        """
        thread = threading.Thread(target=self.create_token)
        thread.daemon = True
        thread.start()

    def create_token(self):
        """
        Creates a Google Token.
        """
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        if settings_db.find_one({'name': 'gcal_token'}):
            gcal_token = settings_db.find_one({'name': 'gcal_token'})['value']
            creds = Credentials.from_authorized_user_info(gcal_token, SCOPES)
            messagebox.showinfo('Informations', 'You don\'t need to create a Google Token because it\'s already present in the database.\n\nChecking if your Google Token needs to be refreshed.')
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                messagebox.showinfo('Informations', 'Your Google Token was refreshed.\n\nNow you can close the Google Token Generator app.')
            else:
                res = messagebox.askyesno('Warning', 'You need to create a new Google Token.\n\nComplete the procedure on your browser.')
                if res:
                    credentials = settings_db.find_one({'name': 'gcal_credentials'})['value']
                    flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
                    creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    gcal_token_post = {
                        'name': 'gcal_token',
                        'value': json.loads(creds.to_json())
                    }
                    settings_db.insert_one(gcal_token_post)
                    messagebox.showinfo('Informations', 'Your Google Token was generated and saved on the database.\n\nNow you can close the Google Token Generator app.')
                elif not res:
                    return

def create_settings_file():
    """
        Creates the settings file.
    """
    with open('settings.json', 'w+') as settings_file:
        data = {
            'db_cluster_link' : '',
            'db_cluster' : '',
            'settings_db' : ''
        }
        json_string = json.dumps(data, indent=4)
        settings_file.write(json_string)

def db_init():
    """
    Initializes the MongoDB database.
    """
    with open('settings.json', 'r') as settings_file:
        # Reading from json file
        settings = json.load(settings_file)
    cluster = MongoClient(settings['db_cluster_link'])
    db_cluster = cluster[settings['db_cluster']]
    global settings_db
    settings_db = db_cluster[settings['settings_db']]


if __name__ == '__main__':
    if os.path.exists('settings.json'):
        pass
    else:
        create_settings_file()
    with open('settings.json', 'r') as settings_file:
        # Reading from json file
        settings = json.load(settings_file)
        if not settings['db_cluster_link'] or not settings['db_cluster'] or not settings['settings_db']:
            res = messagebox.showwarning('Attention!!', 'Your settings file is empty\n\nYou need to insert settings before you can continue!')
            if res == 'ok':
                webbrowser.open('settings.json')
        else:
            db_init()
            root = Tk()
            my_gui = AppGUI(root)
            root.mainloop()

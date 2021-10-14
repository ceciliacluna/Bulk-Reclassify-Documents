import json
from tkinter import Tk, Label, Frame, Entry, OptionMenu, Button, END, TOP, HORIZONTAL, BOTTOM, W, S, E, NSEW, StringVar
from tkinter.ttk import Progressbar
from tkinter.messagebox import showerror
import tkinter.filedialog as filedialog
import requests
import pandas as pd
import threading
import re


class GSKTool:
    def __init__(self, master):
        self.master = master
        master.title('Reclassify Tool')

        # MAIN SCREEN
        self.input_frame = Frame(master)
        self.top_frame = Frame(master)
        self.bottom_frame = Frame(master)
        self.line = Frame(master, height=1, width=400, bg="grey90", relief='groove')

        self.url_input = Label(self.input_frame, text="  url:      ")
        self.url_entry = Entry(self.input_frame, text="", width=40)

        self.user_name_input = Label(self.input_frame, text="username:       ")
        self.user_name_entry = Entry(self.input_frame, text="", width=40)

        self.password_input = Label(self.input_frame, text="password:      ")
        self.password_entry = Entry(self.input_frame, text="", width=40, show="*")

        self.file_name_input = Label(self.top_frame, text="Output file name:      ")
        self.file_name_entry = Entry(self.top_frame, text="", width=40)

        self.input_path_label = Label(self.top_frame, text="Input Location:         ")
        self.input_entry = Entry(self.top_frame, text="", width=40)
        self.browse1 = Button(self.top_frame, text="Browse", command=self.input_location)

        self.output_path_label = Label(self.top_frame, text="Output Location:      ")
        self.output_entry = Entry(self.top_frame, text="", width=40)
        self.browse2 = Button(self.top_frame, text="Browse", command=self.output_location)

        self.login_button = Button(self.input_frame, text='Login', command=self.authenticate)
        self.log_in_successful = Label(self.input_frame, text="Login Successful", fg="blue", font="Helvetica 9 bold", pady=6)

        self.progress = Progressbar(master, orient=HORIZONTAL, length=150, mode="determinate", maximum=250, value=0)

        self.begin_button = Button(self.bottom_frame, text='Begin!', command=self.being_task)

        self.completed = Label(master, text="Download Complete", fg="green", font="Helvetica 10 bold", pady=6)
        self.completed_with_errors = Label(master, text="Download Inclueded Errors, Download Complete", fg="red", font="Helvetica 10 bold", pady=6)

        # SETTING LAYOUT

        self.input_frame.pack(side=TOP, pady=5)
        self.line.pack(pady=5)
        self.top_frame.pack(pady=5, padx=5)
        self.bottom_frame.pack(pady=5)

        self.url_input.grid(row=0, column=0, pady=5, sticky=E)
        self.url_entry.grid(row=0, column=1, pady=5)

        self.user_name_input.grid(row=1, column=0, pady=5, sticky=E)
        self.user_name_entry.grid(row=1, column=1, pady=5)

        self.password_input.grid(row=2, column=0, pady=5, sticky=E)
        self.password_entry.grid(row=2, column=1, pady=5)

        self.login_button.grid(row=4, column=1, pady=5, padx=(10, 105), sticky=NSEW)

        self.file_name_input.grid(row=0, column=0, pady=5, sticky=E)
        self.file_name_entry.grid(row=0, column=1, pady=5)

        self.input_path_label.grid(row=1, column=0, pady=5, sticky=E)
        self.input_entry.grid(row=1, column=1, pady=5, sticky=E)
        self.browse1.grid(row=1, column=2, padx=(35, 10), sticky=W)

        self.output_path_label.grid(row=2, column=0, pady=5, sticky=E)
        self.output_entry.grid(row=2, column=1, pady=5, sticky=E)
        self.browse2.grid(row=2, column=2, padx=(35, 10), sticky=W)

        self.begin_button.grid(row=3, column=1, ipadx=40, pady=10, padx=(20, 30), sticky=NSEW)

    # Prompts user to select input file
    def input_location(self):
        global input_path
        input_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Excel files", ".xlsx .xls")])
        self.input_entry.delete(1, END)  # Remove current text in entry
        self.input_entry.insert(0, input_path)  # Insert the 'path'

    # Prompts user to select output location
    def output_location(self):
        global output_path
        output_path = filedialog.askdirectory()
        self.output_entry.delete(1, END)  # Remove current text in entry
        self.output_entry.insert(0, output_path)  # Insert the 'path'

    # Authenticate
    def authenticate(self):
        global session_id
        url = self.url_entry.get()
        username = self.user_name_entry.get()
        password = self.password_entry.get()
        full_url = url + '/api/v20.3/auth'
        payload = {'username': username,
                   'password': password}
        files = [

        ]
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.request("POST", full_url, headers=headers, params=payload, files=files)
            auth_content = response.json()
            session_id = auth_content['sessionId']
            self.log_in_successful.grid(row=5, column=1, pady=5, padx=(10, 105), sticky=NSEW)
        except requests.ConnectionError:
            showerror(title="Error", message="The URL entered is incorrect")
        except Exception:
            msg = response.json().get('responseMessage')
            showerror(title="Error", message=msg)
            print(msg)
            raise MyCustomAPIError(msg)

    def being_task(self):
        threading.Thread(target=self.data_automation).start()

    # Makes API request and generates output file
    def data_automation(self):
        self.completed.pack_forget()
        self.completed_with_errors.pack_forget()
        file_name = self.file_name_entry.get()
        url = self.url_entry.get()

        full_url = url + '/api/v19.1/objects/documents/'
        payload = {}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': session_id
        }

        data = pd.read_excel(input_path)
        self.progress.pack(side=BOTTOM, anchor=S, pady=10, padx=(20, 30))
        output_df = pd.DataFrame(columns=['id', 'responseStatus', 'errors'])

        try:
            self.progress.start()
            self.progress.step(5)
            for index, row in data.iterrows():
                doc_id = str(row['id'])
                reclassify = str(row['reclassify'])
                doc_type = str(row['type__v']).replace(" ", "%20")
                doc_subtype = str(row['subtype__v']).replace(" ", "%20")
                doc_classification = str(row['classification__v']).replace(" ", "%20")
                doc_lifecycle = str(row['lifecycle__v']).replace(" ", "%20")
                request_url = full_url + doc_id
                payload = '?type=' + doc_type + '&subtype__v=' + doc_subtype + '&classification__v=' + \
                          doc_classification + '&lifecycle__v=' + doc_lifecycle + '&reclassify=' + reclassify
                response = requests.put(request_url, headers=headers, data=payload)
                print(request_url)
                json_file = response.json()
                print(response)
                print(json_file)
                if json_file['responseStatus'] == 'SUCCESS':
                    document_id = json_file['id']
                    status = json_file['responseStatus']
                    new_row = {'id': document_id, 'responseStatus': status, 'errors': 'No Errors'}
                    output_df = output_df.append(new_row, ignore_index=True)
                else:
                    status = json_file['responseStatus']
                    error = json_file['errors'][0]['message']
                    print(error)
                    print(status)
                    new_row = {'id': doc_id, 'responseStatus': status, 'errors': error}
                    output_df = output_df.append(new_row, ignore_index=True)

        except Exception:
            self.progress.stop()
            self.progress.pack_forget()
            msg = response.json().get('responseMessage')
            showerror(title="Error", message=msg)
            print(msg)
            raise MyCustomAPIError(msg)

        output_df.to_csv(output_path + '/' + file_name + '.csv', index=False)

        self.completed.pack(side=BOTTOM, anchor=S, pady=10, padx=(20, 30))
        self.progress.pack_forget()


class MyCustomAPIError(requests.exceptions.HTTPError):
    pass


master = Tk()
my_gui = GSKTool(master)
master.mainloop()
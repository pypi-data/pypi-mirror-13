from watson_developer_cloud import DialogV1 as Dialog
from dialog_watson_client.DialogResponse import DialogResponse
from dialog_watson_client.Profile import Profile
from dialog_watson_client.exceptions.ExceptionDialogFile import ExceptionDialogFile
import os
import pkgutil
import StringIO

try:
    from lxml import etree
except ImportError, e:
    pass


class Client:
    DIALOG_ID_FILE = './dialog_id_file.txt'

    def __init__(self, username, password, file, dialog_name, url=None, dialog_id_file=DIALOG_ID_FILE):
        self._check_file(file)
        self.dialog_id_file = dialog_id_file
        self.dialog_name = dialog_name
        if url is None:
            url = Dialog.default_url
        self.dialog = Dialog(url, username=username, password=password)
        self.file = file
        self.conversation_id = None
        self._profile = None
        self.last_response = None
        self.last_response_raw = None
        self.dialog_id = None

    def clean_dialogs(self):
        dialogs = self.get_dialogs()
        for dialog in dialogs['dialogs']:
            self.dialog.delete_dialog(dialog['dialog_id'])

    def get_dialogs(self):
        return self.dialog.get_dialogs()

    def _check_file(self, file):
        if not os.path.exists(file):
            raise ExceptionDialogFile("File '" + file + "' doesn't exist")

    def _validate_xml(self, file):
        if not etree:
            return
        data = pkgutil.get_data('dialog_watson_client', 'WatsonDialogDocument_1.0.xsd')
        dataIo = StringIO.StringIO(data)
        xsd_doc = etree.parse(dataIo)
        xsd = etree.XMLSchema(xsd_doc)
        xml = etree.parse(file)
        xsd.assertValid(xml)

    def _is_dialog_id_created(self):
        if not os.path.exists(self.dialog_id_file):
            return False
        if not os.path.getmtime(self.file) == os.path.getmtime(self.dialog_id_file):
            return False
        return True

    def get_dialog_id(self):
        if not os.path.exists(self.dialog_id_file):
            return None
        if self.dialog_id is not None:
            return self.dialog_id
        dialogIdFile = open(self.dialog_id_file, 'r')
        dialogId = dialogIdFile.readline()
        dialogIdFile.close()
        self.dialog_id = dialogId
        return dialogId

    def delete_dialog(self):
        dialogId = self.get_dialog_id()
        resp = None
        if dialogId is not None and not dialogId:
            resp = self.dialog.delete_dialog(dialogId)
        os.remove(self.dialog_id_file)
        return resp

    def update_dialog(self):
        dialogId = self.get_dialog_id()
        resp = None
        if dialogId is not None and not dialogId:
            with open(self.file) as dialogFile:
                resp = self.dialog.update_dialog(dialogId, dialogFile)
        return resp

    def _touch(self, fname):
        if os.path.exists(fname):
            os.utime(fname, None)
        else:
            open(fname, 'a').close()

    def create_or_update_dialog(self):
        if self._is_dialog_id_created():
            return
        dialogId = self.get_dialog_id()
        filename, ext = os.path.splitext(self.file)
        if ext == 'xml':
            self._validate_xml(self.file)
        if dialogId is not None and self.conversation_id is None:
            self.update_dialog()
        else:
            with open(self.file) as dialogFile:
                resp = self.dialog.create_dialog(dialogFile,
                                                 self.dialog_name)
            f = open(self.dialog_id_file, 'w')
            f.write(resp['dialog_id'])
            f.close()
        self._touch(self.file)

    def get_last_response(self):
        return self.last_response

    def get_last_response_json(self):
        return self.last_response_raw

    def _update_response(self, jsonResp):
        self.last_response_raw = jsonResp
        self.last_response = DialogResponse(jsonResp['response'])
        if 'confidence' in jsonResp:
            self.last_response.confidence = jsonResp['confidence']
        if 'input' in jsonResp:
            self.last_response.input = jsonResp['input']

    def start_dialog(self):
        self.create_or_update_dialog()
        dialogId = self.get_dialog_id()
        initial_response = self.dialog.conversation(dialogId)
        self.last_response_raw = initial_response
        self.conversation_id = initial_response['conversation_id']
        self._profile = Profile(initial_response['client_id'])
        self._update_response(initial_response)
        return self.last_response

    def converse(self, user_input):
        dialogId = self.get_dialog_id()
        if self._profile is None:
            self.start_dialog()
        resp = self.dialog.conversation(dialogId, dialog_input=user_input, client_id=self._profile.client_id,
                                        conversation_id=self.conversation_id)
        self._update_response(resp)
        return self.last_response

    def get_profile(self):
        dialogId = self.get_dialog_id()
        if self._profile is None:
            self.start_dialog()
        resp = self.dialog.get_profile(dialogId, self._profile.client_id)
        self._profile.load_data(resp["name_values"])
        return self._profile

    def get_conversation(self, date_from, date_to):
        dialogId = self.get_dialog_id()
        return self.dialog.get_conversation(dialogId, date_from, date_to)

    def update_profile(self):
        dialogId = self.get_dialog_id()
        profile = self.get_profile()
        data = profile.get_data()
        name_values = [];
        for (name, value) in data.items():
            name_values.append({
                'name': name,
                'value': value
            })
        return self.dialog.update_profile(dialogId, profile.client_id, name_values)

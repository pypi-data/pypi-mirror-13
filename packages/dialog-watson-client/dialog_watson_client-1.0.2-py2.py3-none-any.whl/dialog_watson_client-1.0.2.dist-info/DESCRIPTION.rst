# dialog-watson-client

Client for dialogs watson module

## Requirements

- **Python 2.7**
- **Pip**

## Installation

Install with pip: `pip install dialog-watson-client`

## Run the playground

Simply run in command line: `dialog-watson-client --name=dialog-name path/to/dialog/file [--clean](optional: clean your dialogs in watson)` and you will chat with your robot

**At the first launch it will create a config file located to `~/.config-dialog-watson.yml` and ask you your watson credentials**

## Usage for developers

Bootstrap example:

```python
from dialog_watson_client.Client import Client
watsonClient = Client('user_watson', 'password_watson', 'file/path/to/dialog', 'your_dialog_name') # this library abstract the registering of dialog (and the update when you cahnge it) and run it, to do that it will store your dialog id in a file called `dialog_id_file.txt`
watsonClient.start_dialog() # this will create the dialog into watson or update it and run the initialization of the conversation

resp = watsonClient.converse('hi') # talk to the robot, here it will say 'hi' and watson will answered
print resp.response # show the response from watson
watsonClient.get_profile().get_data() # get extracted data from watson in format: [key => value]
```

**Note**: If your file is in xml (and you have `lxml` lib installed) it will also check your format with xsd: https://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/dialog/download/WatsonDialogDocument_1.0.xsd


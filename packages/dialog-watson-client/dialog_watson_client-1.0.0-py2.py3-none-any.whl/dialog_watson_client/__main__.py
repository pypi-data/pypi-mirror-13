from dialog_watson_client.Client import Client
import os.path
import argparse
import anyconfig
import bunch


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    defaultConfig = {
        'url': 'https://gateway.watsonplatform.net/dialog/api',
        'user': 'user',
        'password': 'password',
    }
    home = os.path.expanduser("~")
    defaultConfigFile = home + '/.config-dialog-watson.yml'
    parser = argparse.ArgumentParser(
        description='Text to speech using watson')

    parser.add_argument('-f', action='store', dest='configFile', default=defaultConfigFile,
                        help='config file',
                        required=False)
    parser.add_argument('dialog_file', action='store', nargs=1)
    parser.add_argument('-n', '--name', dest='dialog_name', action='store', help='Dialog name', required=True)
    parser.add_argument('--clean', dest='clean', action='store_true')
    args = parser.parse_args()
    dialog_file = "".join(args.dialog_file)
    conf = anyconfig.container(defaultConfig)
    if not os.path.isfile(args.configFile):
        print "Config file '" + args.configFile + "' doesn't exist."
        print "Creating it ..."
        user = raw_input("Watson user: ")
        password = raw_input("Watson password: ")
        bconf = bunch.bunchify(conf)
        bconf.user = user
        bconf.password = password
        anyconfig.dump(bconf.toDict(), args.configFile)
    else:
        conf = anyconfig.load(args.configFile)
    bconf = bunch.bunchify(conf)
    watsonClient = Client(bconf.user, bconf.password, dialog_file, "".join(args.dialog_name), bconf.url,
                          os.path.dirname(dialog_file) + "/dialog_id_file.txt")
    if args.clean:
        watsonClient.clean_dialogs()

    resp = watsonClient.start_dialog()
    print ''
    print bcolors.WARNING + "Watson: " + bcolors.OKBLUE + "\n".join(resp.response) + bcolors.ENDC
    while True:
        userResponse = raw_input(bcolors.WARNING + "You: " + bcolors.OKGREEN)
        resp = watsonClient.converse(userResponse)
        print bcolors.WARNING + "Watson: " + bcolors.OKBLUE + "\n".join(resp.response) + bcolors.ENDC
        if userResponse == "bye":
            break
    print ""
    print "Your profile:"
    for name, value in watsonClient.get_profile().get_data().iteritems():
        print "\t" + name + ": " + value
    if __name__ == "__main__":
        main()

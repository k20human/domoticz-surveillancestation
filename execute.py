import json
import os
import sys
import getopt
import logging
from logging.handlers import RotatingFileHandler
from surveillancestation.surveillancestation import Surveillancestation

# Configuration file path
configurationFile = './config.json'

# Configure logs
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

file_handler = RotatingFileHandler('surveillance-station.log', 'a', 1000000, 1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.INFO)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)

# Check if configuration file exists
if os.path.isfile(configurationFile):
    # Import configuration file
    with open(configurationFile) as data_file:
        config = json.load(data_file)
else:
    logger.error('Your configuration file doesn\'t exists')
    sys.exit('Your configuration file doesn\'t exists')


def usage():
    print('execute.py -a <on|off> -c <cam1,cam2,cam...>')


# Main script
def main(argv):
    action = ''
    cams = ''

    try:
        opts, args = getopt.getopt(argv, "h:a:c:", ["action=", "cams=", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <action> -o <cams>')
            sys.exit()
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-c", "--cams"):
            cams = arg.split(',')

    # Check options
    if not action or not cams:
        usage()
        sys.exit(2)

    # Check action
    if action != 'on' and action != 'off':
        usage()
        sys.exit(2)

    # Check cams
    cam_keys = config['cams'].keys()
    for cam in cams:
        if cam not in cam_keys:
            print('The cam [', cam, ']', 'is not in config file')
            sys.exit(2)

    # Convert cam name to cam idx
    cam_idxs = []
    for cam in cams:
        cam_idxs.append(config['cams'][cam])

    # Create API
    api = Surveillancestation(host=config['host'], user=config['login'], passwd=config['password'])

    # Execute action in all cam
    try:
        if action == 'on':
            api_return = api.camera.enable(cam_idxs)
        elif action == 'off':
            api_return = api.camera.disable(cam_idxs)

            sys.exit(0 if api_return['success'] else 1)
    except Exception:
        sys.exit(1)
    finally:
        # Don't forget to logout
        api.logout()


if __name__ == "__main__":
    main(sys.argv[1:])
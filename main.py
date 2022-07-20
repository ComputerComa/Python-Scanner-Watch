from __future__ import print_function, unicode_literals
from re import T
import serial # Import Serial Library
from pushover import Pushover # Import Pushover Library
import yaml
from yaml.loader import SafeLoader
import threading
from InquirerPy import prompt
from pprint import pprint
from os import system, name
import logging
logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
has_congfig = False
write_debug = True
read_error_count = 0
def clear():
   # for windows
   if name == 'nt':
      system('cls')
   # for mac and linux
   else:
    system('clear')
   return
class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def debug(message):
    if write_debug:
        logging.debug(str(message))
        return
    return


try:
    with open('config.yaml') as config_file:
        cfgdata = yaml.load(config_file, Loader=SafeLoader)
    debug('Config file found')
    ListeningCOMPort = cfgdata['LCP']
    debug('LCP ok')
    debug(ListeningCOMPort)
    ListeningCOMPORTBaud = cfgdata['LCPB']
    debug('LLCPB ok')
    debug(ListeningCOMPORTBaud)
    RelayEnabled = cfgdata['RelayEnabled']
    debug('RelayEnabled ok')
    debug(RelayEnabled)
    PushoverAPIKey = cfgdata['PushoverAPIKey']
    debug('PushoverAPIKey ok')
    PushoverRegularUserGroupKey = cfgdata['PushoverRegularUserGroupKey']
    debug('PushoverRegularUserGroupKey ok')
    PushoverAdminUserGroupKey = cfgdata['PushoverAdminUserGroupKey']
    debug('PushoverAdminUserGroupKey ok')
    AlertThreshold = cfgdata['AlertThreshold']
    debug('AlertThreshold ok')
    debug(AlertThreshold)
    if RelayEnabled:
        debug('Relay is Enabled')
        RelayCOMPORT = cfgdata['RCP']
        debug('RCP ok')
        RelayCOMPORTBaud = cfgdata['RCPB']
        debug('RCPB ok')
        RelayTest = cfgdata['RelayTest']
        debug('RelayTest ok')
        debug(RelayTest)
        RelayCommands = cfgdata['RelayCommands']
        debug('RelayCommands ok')
        if RelayTest:
            debug('Relay has Testing commands')
            RelayCommandTest = cfgdata['RelayCommands']['Test']
            debug('RelayCommandTest ok')
            debug(RelayCommandTest)
        RelayCommandOpen = cfgdata['RelayCommands']['OpenRelay']
        debug('RelayCommandOpen ok')
        debug(RelayCommandOpen)
        RelayCommandClose = cfgdata['RelayCommands']['CloseRelay']
        debug('RelayCommandClose ok')
        debug(RelayCommandClose)
    #Initializing pushover object
    pushover = Pushover(PushoverAPIKey)
    debug('Pushover object initialized')
    has_congfig = True
    debug("Config ok")
except:
    print('No config file found. Or the config has errors. Running setup wizard.')
    has_congfig = False






#write a function to print config data to the console
def print_config():
    with open('config.yaml') as config_file:
        cfgdata_I = yaml.load(config_file, Loader=SafeLoader) 
    pprint(cfgdata_I)




def readin():
    try:
        ser = serial.Serial(ListeningCOMPort, ListeningCOMPORTBaud, timeout=5)
        ser.write(b'SYN')
        while not threading.current_thread().stopped():
            try:
                readOut = ser.readline().decode('ascii')
                if readOut != '':
                    debug("- SubThread Output - " + readOut)
            except:
                debug('Error reading serial')
                pass
    except:
        logging.error('Error opening serial')
    ser.close()
    exit


def relay(funcrion):
    if funcrion == 'open':
        ser = serial.Serial(RelayCOMPORT, RelayCOMPORTBaud, timeout=5)
        ser.write(bytes(RelayCommandOpen, 'ascii'))
        ser.close()
    elif funcrion == 'close':
        ser = serial.Serial(RelayCOMPORT, RelayCOMPORTBaud, timeout=5)
        ser.write(bytes(RelayCommandClose, 'ascii'))
        ser.close()
    else:
        exit
def test_relay():
    success = False
    try:
        ser = serial.Serial(RelayCOMPORT, RelayCOMPORTBaud, timeout=1)
        ser.write(bytes(RelayCommandTest, 'ascii'))
        errors = 0
        while True:
            try:
                readOut = ser.readline().decode('ascii')
                debug(readOut)
                if errors > 10:
                    logging.error('No response from relay')
                    success = False
                    break
                elif readOut == 'OK':
                    debug('Relay is working')
                    success = True
                    break
            except:
                errors += 1
                debug('Error reading serial')
                pass
    except:
        logging.error('Error opening serial')
    ser.close()
    return success
    exit

def notify(mode,message):
    msg = pushover.msg(message)
    if mode == 'regular':
        pushover.user(PushoverRegularUserGroupKey)
        msg.set("title", "Alert")
        msg.set("priority", "0")
    elif mode == 'admin':
        pushover.user(PushoverAdminUserGroupKey)
        msg.set("title", "ADMIN Alert")
        msg.set("priority", "1")     
    else:
        logging.error('Invalid mode')
    try:
        pushover.send(msg)
        logging.info('Notification sent')
    except:
        logging.error('Error sending notification')
        pass


th_main = StoppableThread(target=readin)

def build_config():
    logging.error("Config file not found")
    print("Please enter the following details")
    questions = [
        {
            'type': 'input',
            'name': 'ListeningCOMPort',
            'message': 'Enter the COM port for listening: '
        },
        {
            'type': 'input',
            'name': 'ListeningCOMPORTBaud',
            'message': 'Enter the baud rate for listening: '
        },
        {
            'type': 'confirm',
            'name': 'RelayEnabled',
            'message': 'Do you want to enable the relay?',
            'default': True
        },
        {
            'type': 'input',
            'name': 'RelayCOMPort',
            'message': 'Enter the COM port for relay:',
            'when': lambda answers: answers['RelayEnabled'] is True
        },
        {
            'type': 'confirm',
            'name': 'RelayTestConfirm',
            'message': 'Does your relay have an option to send test commands? (If you don\'t know, leave this as false)',
            'when': lambda answers: answers['RelayEnabled'] is True,
            'default': False
        },
        {
            'type': 'input',
            'name': 'RelayTestCommand',
            'message': 'Enter the test command: ',
            'when': lambda answers: answers['RelayEnabled'] is True and answers['RelayTestConfirm'] is True
        },
        {
            'type': 'input',
            'name': 'RelayOpenCommand',
            'message': 'Enter the command to open the relay: ',
            'when': lambda answers: answers['RelayEnabled'] is True and answers['RelayTestConfirm'] is True,
            'default': 'OPEN'
        },
        {
            'type': 'input',
            'name': 'RelayCloseCommand',
            'message': 'Enter the command to close the relay: ',
            'when': lambda answers: answers['RelayEnabled'] is True and answers['RelayTestConfirm'] is True,
            'default': 'CLOSE'
        },
        {
            'type': 'input',
            'name': 'RelayCOMPORTBaud',
            'message': 'Enter the baud rate for relay',
            'when': lambda answers: answers['RelayEnabled'] is True
        },
        {
            'type': 'input',
            'name': 'PushoverAPIKey',
            'message': 'Enter the Pushover API Key: '
        },
        {
            'type': 'input',
            'name': 'PushoverRegularUserGroupKey',
            'message': 'Enter the Pushover Regular User Group Key: '
        },
        {
            'type': 'input',
            'name': 'PushoverAdminUserGroupKey',
            'message': 'Enter the Pushover Admin User Group Key: '
        },
        {
            'type': 'input',
            'name': 'AlertThreshold',
            'message': 'Enter the Alert Threshold: '
        }
    ]
    answers = prompt(questions)
    ListeningCOMPort = answers['ListeningCOMPort']
    ListeningCOMPORTBaud = answers['ListeningCOMPORTBaud']
    RelayEnabled = answers['RelayEnabled']
    PushoverAPIKey = answers['PushoverAPIKey']
    PushoverRegularUserGroupKey = answers['PushoverRegularUserGroupKey']
    PushoverAdminUserGroupKey = answers['PushoverAdminUserGroupKey']
    AlertThreshold = answers['AlertThreshold']
    if RelayEnabled:
        RelayTest = answers['RelayTestConfirm']
        RelayCOMPort = answers['RelayCOMPort']
        RelayCOMPORTBaud = answers['RelayCOMPORTBaud']
        if RelayTest:
            RelayCommandTest = answers['RelayTestCommand']
        else:
            RelayCommandTest = None
        RelayCommandOpen = answers['RelayOpenCommand']
        RelayCommandClose = answers['RelayCloseCommand']
    else:
        RelayCOMPort = None
        RelayCOMPORTBaud = None
        RelayCommandTest = None
        RelayCommandOpen = None
        RelayCommandClose = None
        RelayTest = False
    #dump the config variables to a config.yaml file
    cfgdata = {
        'LCP': ListeningCOMPort,
        'LCPB': ListeningCOMPORTBaud,
        'RelayEnabled': RelayEnabled,
        'RCP': RelayCOMPort,
        'RCPB': RelayCOMPORTBaud,
        'PushoverAPIKey': PushoverAPIKey,
        'PushoverRegularUserGroupKey': PushoverRegularUserGroupKey,
        'PushoverAdminUserGroupKey': PushoverAdminUserGroupKey,
        'AlertThreshold': AlertThreshold,
        'RelayTest': RelayTest,
        'RelayCommands': {
            'Test': str(RelayCommandTest),
            'OpenRelay': str(RelayCommandOpen),
            'CloseRelay': str(RelayCommandClose)
        }

    }
    with open('config.yaml', 'w') as outfile:
        yaml.dump(cfgdata, outfile, default_flow_style=False)
    return

print("Welcome to TCST Alert System")
if has_congfig:
    print("Config file found")
else:
    build_config()

def edit_config():
    clear()
    config_options = [
        {
            'type': 'list',
            'name': 'cfg_menu',
            'message': 'What config option would you like to edit?',
            'choices': ["Listening COM Port","Listening COM Port Baud Rate","Relay COM Port","Relay COM Port Baud Rate","Relay Enabled","Pushover API Key","Pushover Regular User Group Key","Pushover Admin User Group Key","Alert Threshold","Cancel"]
        }
    ]
    config_answers = prompt(config_options)
    if config_answers['cfg_menu'] == 'Listening COM Port':
        ListeningCOMPort = input("Enter the new COM port for listening: ")
        cfgdata['LCP'] = ListeningCOMPort
    elif config_answers['cfg_menu'] == 'Listening COM Port Baud Rate':
        ListeningCOMPORTBaud = input("Enter the new baud rate for listening: ")
        cfgdata['LCPB'] = ListeningCOMPORTBaud
    elif config_answers['cfg_menu'] == 'Relay COM Port':
        RelayCOMPort = input("Enter the new COM port for relay: ")
        cfgdata['RCP'] = RelayCOMPort
    elif config_answers['cfg_menu'] == 'Relay COM Port Baud Rate':
        RelayCOMPORTBaud = input("Enter the new baud rate for relay: ")
        cfgdata['RCPB'] = RelayCOMPORTBaud
    elif config_answers['cfg_menu'] == 'Relay Enabled':
        RelayEnabled = input("Do you want to enable the relay? (y/n)")
        if RelayEnabled == 'y':
            RelayEnabled = True
        else:
            RelayEnabled = False
        cfgdata['RelayEnabled'] = RelayEnabled
    elif config_answers['cfg_menu'] == 'Pushover API Key':
        PushoverAPIKey = input("Enter the new Pushover API Key: ")
        cfgdata['PushoverAPIKey'] = PushoverAPIKey
    elif config_answers['cfg_menu'] == 'Pushover Regular User Group Key':
        PushoverRegularUserGroupKey = input("Enter the new Pushover Regular User Group Key: ")
        cfgdata['PushoverRegularUserGroupKey'] = PushoverRegularUserGroupKey
    elif config_answers['cfg_menu'] == 'Pushover Admin User Group Key':
        PushoverAdminUserGroupKey = input("Enter the new Pushover Admin User Group Key: ")
        cfgdata['PushoverAdminUserGroupKey'] = PushoverAdminUserGroupKey
    elif config_answers['cfg_menu'] == 'Alert Threshold':
        AlertThreshold = input("Enter the new Alert Threshold: ")
        cfgdata['AlertThreshold'] = AlertThreshold
    elif config_answers['cfg_menu'] == 'Cancel':
        return
    with open('config.yaml', 'w') as outfile:
        yaml.dump(cfgdata, outfile, default_flow_style=False)
    return

def main_list():
    clear()
    if th_main.is_alive():
        main_list_questions = [
        {
        'type': 'list',
        'name': 'menu',
        'message': 'The watch thread is running \n What would you like to do?',
        'choices': ["Stop"]
        }]
    else:
        main_list_questions = [
        {
        'type': 'list',
        'name': 'menu',
        'message': 'What would you like to do?',
        'choices': ["Start","Rebuild Config","Edit Config","Print Config","Test Notifications","Test Relay","Exit"]
        }
    ]
    answers = prompt(main_list_questions)
    if answers['menu'] == 'Start':
        debug('Starting')
        th_main.start()
    elif answers['menu'] == 'Stop':
        debug('Stopping')
        th_main.stop()
        th_main.join()
        return
    elif answers['menu'] == 'Test Notifications':
        print('Testing Notifications')
        notify('regular', 'Testing Notifications')
        notify('admin', 'Testing Notifications')
        main_list()
    elif answers['menu'] == 'Rebuild Config':
        build_config()
        quit()
    elif answers['menu'] == 'Edit Config':
        edit_config()
    elif answers['menu'] == 'Print Config':
        print_config()
        print('\n')
        input("Press enter to continue")
    elif answers['menu'] == 'Test Relay':
        if RelayEnabled:
            out = test_relay()
            debug(out)
        else:
            print('Relay is not enabled')
    elif answers['menu'] == 'Exit':
        quit()
    else:
        print('Invalid option')

while True:
    main_list()
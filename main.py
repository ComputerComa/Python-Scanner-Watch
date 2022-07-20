from __future__ import print_function, unicode_literals
from pip import main
import serial # Import Serial Library
from pushover import Pushover # Import Pushover Library
import yaml
from yaml.loader import SafeLoader
from threading import Thread
from InquirerPy import prompt
from pprint import pprint
has_congfig = False
try:
    with open('config.yaml') as config_file:
        cfgdata = yaml.load(config_file, Loader=SafeLoader)
    ListeningCOMPort = cfgdata['LCP']
    ListeningCOMPORTBaud = cfgdata['LCPB']
    RelayEnabled = cfgdata['RelayEnabled']
    RelayCOMPORT = cfgdata['RCP']
    RelayCOMPORTBaud = cfgdata['RCPB']
    PushoverAPIKey = cfgdata['PushoverAPIKey']
    PushoverRegularUserGroupKey = cfgdata['PushoverRegularUserGroupKey']
    PushoverAdminUserGroupKey = cfgdata['PushoverAdminUserGroupKey']
    AlertThreshold = cfgdata['AlertThreshold']
    #Initializing pushover object
    pushover = Pushover(PushoverAPIKey)
    has_congfig = True
except:
    has_congfig = False




def readin():
    ser = serial.Serial(ListeningCOMPort, ListeningCOMPORTBaud, timeout=1)
    ser.write(b'SYN')
    while True:
        try:
            readOut = ser.readline().decode('ascii')
            #print(readOut)
        except:
            pass

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
        print('Invalid mode')
    try:
        pushover.send(msg)
        print('Notification sent')
    except:
        print('Error sending notification')
        pass


th_main = Thread(target=readin)

print("Welcome to TCST Alert System")
if has_congfig:
    print("Config file found")
else:
    print("Config file not found")
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
    RelayCOMPort = answers['RelayCOMPort']
    RelayCOMPORTBaud = answers['RelayCOMPORTBaud']
    PushoverAPIKey = answers['PushoverAPIKey']
    PushoverRegularUserGroupKey = answers['PushoverRegularUserGroupKey']
    PushoverAdminUserGroupKey = answers['PushoverAdminUserGroupKey']
    AlertThreshold = answers['AlertThreshold']

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
        'AlertThreshold': AlertThreshold
    }
    with open('config.yaml', 'w') as outfile:
        yaml.dump(cfgdata, outfile, default_flow_style=False)
    exit()
def edit_config():
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
    main_list_questions = [
    {
        'type': 'list',
        'name': 'menu',
        'message': 'What would you like to do?',
        'choices': ["Start","Edit Config","Test Notifications","Exit"]
    }
]
    answers = prompt(main_list_questions)
    if answers['menu'] == 'Start':
        print('Starting')
        th_main.start()
    elif answers['menu'] == 'Test Notifications':
        print('Testing Notifications')
        notify('regular', 'Testing Notifications')
        notify('admin', 'Testing Notifications')
    elif answers['menu'] == 'Edit Config':
        edit_config()
    elif answers['menu'] == 'Exit':
        exit()
    else:
        print('Invalid option')
        main_list()

main_list()

##test_notify()
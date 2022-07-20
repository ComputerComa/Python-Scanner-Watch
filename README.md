# Python Scanner Watch
## Getting Started
### You have two options to get started:
- Clone the config.example.yaml file to config.yaml and edit it to suite you needs.
- Run main.py with no configuration file. and then follow the prompts to create a config.yaml file.
## Unsing the Configuration File
### The configuration file is a YAML file. It has the following structure
        ```
        Alert Threshold:
        not yet implemented
        LCP:
        The COM port name of the incoming data from the scanner
        LCPB:
        The BAUD rate for the COM port of the incoming data from the scanner
        PushoverAPIKey:
            The API key for the Pushover API service.
        PushoverAdminUserGroupKey:
                The admin user group key for the Pushover API service. (Please note this is different from your standalone user key and must be setup withing pushover.)
        PushoverRegularUserGroupKey:
                The regular user group key for the Pushover API service. (Please note this is different from your standalone user key and must be setup withing pushover.)
        RCP:
            The COM port for outgoing commands to an optional relay controller for remote power cycling of the scanner.
        RCPB:
            The BAUD rate for the COM port of outgoing commands to an optional relay controller for remote power cycling of the scanner.
        RelayEnabled:
            Whether or not to use a relay controller for remote power cycling of the scanner.
        ```

### TODO
- Needed / Confirmed
[ ] YAML section for Relay commands
[ ] implement alerts for offline notifications and errors
[ ] implememnt configurable alerts for scanner.
- Wants / Possible
[ ] possibility of tone recognition etc.

## Misc and housekeeping

Pushover library used => https://github.com/Wyattjoh/pushover
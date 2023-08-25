# PiFM

A complete radio station for the Raspberry Pi

## Features
- Web interface for management
- Get music from FTP
- Automated news reports

## Installation
1. Install the latest version of Raspbian on your Raspberry Pi
2. Close the repo:
```sudo apt install git && git clone https://github.com/Sid220/PiFM.git```
3. Run the install script:
```cd PiFM && python3 install.py```

You can then start the radio with ```python3 start.py```

## Disclaimer
In most countries, transmitting radio waves without a state-issued licence specific to the transmission modalities (frequency, power, bandwidth, etc.) is illegal.

Therefore, always connect a shielded transmission line from the Raspberry Pi directly to a radio receiver, so as not to emit radio waves. Never use an antenna.

Even if you are a licensed amateur radio operator, using PiFM to transmit radio waves on ham frequencies without any filtering between the Raspberry Pi and an antenna is probably illegal as bandwidth requirements are likely not met.

I could not be held liable for any misuse of your own Raspberry Pi. Any experiment is made under your own responsibility.

From [fm_transmitter](https://github.com/markondej/fm_transmitter) (the backend of this project):
### Legal note
Please keep in mind that transmitting on certain frequencies without special permissions may be illegal in your country.

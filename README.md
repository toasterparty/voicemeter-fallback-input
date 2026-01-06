# VoiceMeter Fallback Input

Background Windows script for automating the switching of input devices in [VoiceMeter](https://vb-audio.com/Voicemeeter/index.htm). Specifically, it will default to a "fallback" input device for a single channel if the "preferred" one is not detected and restart the audio engine as necessary.

## Requirements

- Windows 10+
- [Python](https://www.python.org/downloads/)

## How to Use

1. Download and extract the [latest release](https://github.com/toasterparty/voicemeter-fallback-input/releases)

2. Open `main.py` in a text editor. Edit the `USER CONFIG` section to meet your specific needs.

3. Test using `start.cmd`

4. Once you've verified the script is working, run `start-hidden.cmd` to have it run in the background indefinitely

5. [Optional] Create a shortcut to `start-hidden.cmd` and place it in `C:\Users\Blake\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`. This will make it run on Windows login.

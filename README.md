# VoiceTT-Live

VoiceTT-Live is a real-time voice transcription program that uses the Deepgram API. It automatically copies transcribed text to the clipboard and plays a sound notification after each completed phrase.

## Features

- Real-time voice transcription
- Automatic copying of text to clipboard
- Sound notification after each transcribed phrase
- Saving transcription history to a file
- Minimalist and user-friendly interface

## Requirements

- Python 3.7 or newer
- Microphone access
- Deepgram API key

## Installation

1. Clone the repository or download the project files.
2. Create a `.env` file in the project directory and add your Deepgram API key:
   ```
   DEEPGRAM_API_KEY=your_api_key_here
   ```
3. Ensure you have Python 3.7 or newer installed.

## Usage

### For Windows:

1. Double-click the `run_voicett_windows.bat` file or run it from the command line.
2. The program will automatically create a virtual environment, install dependencies, and launch the script.

### For MacOS:

1. Open a terminal in the project directory.
2. Make the `run_voicett_macos.command` file executable using the command:
   ```
   chmod +x run_voicett_macos.command
   ```
3. Double-click the `run_voicett_macos.command` file in Finder or run it from the terminal:
   ```
   ./run_voicett_macos.command
   ```
4. The program will automatically create a virtual environment, install dependencies, and launch the script.

## Additional Setup for MacOS

On MacOS, you may need to grant permission to access the microphone. If you encounter issues with microphone access:

1. Open "System Preferences" > "Security & Privacy" > "Privacy".
2. Select "Microphone" from the left menu.
3. Find Python or Terminal in the list and check the box to allow access.

## Using the Program

After launching the program:

1. You will see a window with a text field.
2. The program will automatically start listening to your microphone.
3. Speak, and you will see the transcribed text in the program window.
4. Each completed phrase will be automatically copied to the clipboard.
5. You will hear a sound notification after each copied phrase.
6. To end the session, simply close the program window.

## Troubleshooting

If you experience issues launching the program:

1. Ensure you have correctly specified your Deepgram API key in the `.env` file.
2. Check if all dependencies are installed by running `pip install -r requirements.txt` manually.
3. Make sure your microphone is properly connected and configured in your system.

If problems persist, please create an issue in the project repository with a detailed description of the problem.
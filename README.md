# Ableton Live Projects - Plugin Statistics

This application is designed to help music producers and sound engineers analyze the use of plugins within Ableton Live Set (.als) files. It provides an easy-to-use graphical interface for selecting specific projects or folders, generating a report on plugin usage across selected Ableton Live Sets.

## Features

- **Configurable Threshold**: Set a custom threshold to categorize plugins as 'often used' based on their occurrence.
- **Cleanup Temp Folder Option**: Choose whether to automatically clean up the temporary folder after processing.
- **File and Folder Selection**: Add individual .als files or entire folders for analysis. The application will recursively search through folders, excluding any files within "Backup" directories.
- **Generate Reports**: Create a markdown report listing all plugins used, categorized by usage frequency and sorted by occurrence.
- **Remove Selected or All Items**: Easily manage your selection before processing.

## Background

Ableton Live projects are saved in .als file format. These contain all project settings and information in a gzipped xml, which is easily parseable with python.
The script looks for all occurances of the following xPaths in the projects and sum up the used instances.
- .//PluginDesc/AuPluginInfo/Name
- .//PluginDesc/Vst3PluginInfo/Name

## Setup

1. **Clone the Repository**: Clone this project to your local machine.
2. **Install Dependencies**: Ensure you have Python installed, along with the following packages (see requirements.txt):
   - `lxml`
   - `PyYAML`
   - `tkinter` (usually included with Python)

3. **Run the Application**: Execute the main script to launch the GUI.
   ```bash
   python main.py
## How to Use
1. Configure Settings: Upon starting the application, first configure the desired threshold and whether to clean up the temp folder after processing. Click "Save Config" to apply changes.

2. Add Files or Folders: Use the "Add Files" or "Add Folder" buttons to select the .als files or folders you want to analyze. The application will ignore any files located in folders named "Backup".

3. Manage Selection: Use the "Remove Selected" or "Remove All" buttons if you need to adjust your selection.

4. Generate Report: Click "Generate Report" to process the selected files. The application will create a markdown report with the plugin statistics, saved with a timestamp in the filename.

## Configuration File
The application uses a config.yaml file to store settings. You can edit this file directly or use the GUI to modify settings such as the threshold for plugin usage and whether to clean up the temporary folder.

## Note
This tool is designed to read and analyze .als files without modifying the original projects. Always ensure you have backups of your projects before using any third-party tools. I take no responsibility for any loss of data. <3 
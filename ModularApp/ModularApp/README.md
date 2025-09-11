# ModularApp Documentation

## Overview
ModularApp is a flexible application designed to manage and display overlays for various modules. It allows users to create, customize, and manage overlays that can enhance the user experience in different scenarios, particularly in gaming environments.

## Project Structure
The project consists of the following main components:

- **gui_main.py**: The main GUI application that sets up the user interface and manages the loading of modules and overlays.
- **main.py**: The entry point for the application, responsible for initializing the module loader and managing the execution of module logic.
- **overlay_manager.py**: Manages the overlay windows, including their visibility and interactions with the overlays.
- **modules/**: Contains all the modules and their respective widgets and overlays.
  - **Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/**: The specific module for SCUM, containing widgets and overlays.
    - **widgets/**: Contains the widget definitions.
      - **console.py**: Defines the `ConsoleWidget` class for displaying log data.
      - **overlay.py**: (To be replaced) Handles the creation of overlays.
      - **custom_overlays.py**: Manages loading and saving of overlays from `custom_overlays.json`.
      - **overlays.py**: Manages standalone overlays, their deletion, and copying.
      - **overlay_console.py**: Defines an overlay that refreshes data based on a show mode.
    - **overlays/**: Contains JSON files for storing overlay configurations.
      - **custom_overlays.json**: Stores configurations for custom overlays.

## Features
- **Overlay Management**: Create, delete, and manage overlays with customizable properties.
- **Dynamic Updates**: Overlays can refresh their data based on user interactions and visibility states.
- **User-Friendly Interface**: The GUI is designed to be intuitive, allowing users to easily navigate and manage overlays.

## Usage
1. **Launching the Application**: Run `main.py` to start the application.
2. **Creating Overlays**: Use the interface to select widgets and create custom overlays.
3. **Managing Overlays**: Overlays can be shown, hidden, or deleted as needed.
4. **Saving Configurations**: Custom overlay settings are saved in `custom_overlays.json` for persistence across sessions.

## Future Enhancements
- Additional modules and widgets can be integrated to expand functionality.
- Improved user interface elements for better user experience.
- Enhanced overlay customization options.

## License
This project is open-source and available for modification and distribution under the terms specified in the project's license file.
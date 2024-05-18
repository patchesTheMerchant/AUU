# Among Us Undetectable (AUU)

## Disclaimer
This project is created for educational purposes only. The techniques and code discussed here are meant to provide insights into game development and anti-cheat mechanisms. This is not intended for use in actual gameplay or to disrupt the gaming experience of others.

## Overview
Among Us Undetectable (AUU) is a demonstration of how simple memory reading techniques can be utilized to identify player roles in the game "Among Us" without detection. The purpose of this project is to explore the challenges and techniques involved in creating and detecting cheats in video games.

## Features
- **Role Detection:** Identifies player roles through memory reading, press 1 on the keyboard after you enter a lobby.
- **Stealth Mode:** Designed to avoid detection by common anti-cheat systems.
- **Radar:** Will display a radar of where players are on the map.
- **Panic Mode:** Press 9 to delete the cheat file, pross 0 to close it.
- You can run the cheat by only downloading the relesase file and running it on your PC.

<img width="364" alt="Start" src="https://github.com/patchesTheMerchant/AUU/assets/169628962/42d3cdb6-af55-4dfa-a673-7848e8da23af">
<img width="362" alt="running" src="https://github.com/patchesTheMerchant/AUU/assets/169628962/199fe3c5-cfa7-41bd-82e9-999ae62a0b7c">


## Prerequisites
Before you modify AUU, you will need:
- Python 3.8 or higher
- pyinstaller if you want to create a .exe file
- tkinter for the GUI
- pymem to read memory
- Access to a development environment where you have permissions to read memory

## Installation
- Clone the repository locally using git clone https://github.com/patchesTheMerchant/AUU.git
- Install the needed dependencies and run! 
- Or you can just download the launch.exe file from releases and use it.
- Ensure that you are in a controlled environment meant for testing and educational purposes.
- To generate EXE file: pyinstaller --onefile --windowed --clean -F -w --add-data "Polus.png;." AUU.py 

## Contributing
- Contributions to this project are welcome, especially from those who are looking to improve game security and understand anti-cheat mechanisms. To contribute, please fork the repository and submit a pull request.

## License
- This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

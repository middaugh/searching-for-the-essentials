# Information First for CM Dashboard App
![](https://img.shields.io/badge/platform-windows-lightgrey?style=for-the-badge&logo=windows)
![](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue?style=for-the-badge&logo=python)

A fledgling attempt at something different.

## Quick Start Installation & Usage
1. Clone this repository, eg `git clone https://github.com/middaugh/dashboard_app.git`
2. Create and activate a virtual Environment, `pip install virtualenv`, `virtualenv venv`, `venv\Scripts\activate`
3. Run `pip install -r requirements.txt`
4. Update _config.ini_ to reflect your dataset and Content Manager SQL & Service API Setup
5. Run `python model.py` to pull data in from CM, and or setup Windows Task Manager to run model.py on a regular basis (daily, weekly, etc).
5. Run `python app.py` to view your Dashboard.

For full installation, configuration, and deployment via IIS instructions, please [_see the Wiki_](https://github.com/middaugh/dashboard_app/wiki).


### Requirements and Compatibility Information
- Windows
- Python versions 3.6.1+ 
- MicroFocus Content Manager 9.3 or 9.4
- MS SQL Express or MS SQL Standard
- Windows Server 2012 R2


### Attribution
[Plotly's Dash](https://github.com/plotly/dash)

# kyt-python-sentiment-analysis

### How to start the app
1. Download [Python 🐍](https://www.python.org/downloads/)
2. run `python -m venv .env`[^1]
3. run `.env/Scripts/activate`[^2] or run `source .env/bin/activate`[^3]
4. run `pip install transformers`, `pip install torch`, and `pip install tensorflow`[^4]
5. Finally run `python app.py` to start the App 🥳

### Available API Endpoints
- **GET**("/")
- **POST**("/get-searched-tweets-list")
- **POST**("/get-comments-analised")
- **POST**("/get-comments-analised-bulk")

[^1]: Create virtual environment
[^2]: Activate the virtual environment for **Linux** and **MacOs**
[^3]: Activate the virtual environment for **Windows**
[^4]: Installs package transformers, tensorflow, and pytorch accordingly

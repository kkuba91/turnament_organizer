"""runner.py

    Main application core.

"""
# Global package imports:
# Local package imports:
from browser import File
from application import Application


if __name__ == "__main__":
    # Application life handler 
    app = Application('Chess Organizer')
    app.init()
    app.run()
    app.end()

"""runner.py

    Main application core.

"""
# Global package imports:
# Local package imports:
from Application import Application
from Resources import APPLICATION_NAME


if __name__ == "__main__":
    # Application life handler
    app = Application(APPLICATION_NAME)
    app.init()
    app.run()
    app.end()

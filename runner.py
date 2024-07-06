"""runner.py

    Main application core.

"""
# Global package imports:
# Local package imports:
from Application import Application, ArgInfo
from Resources import APPLICATION_NAME

PORT = 8000
DEBUG = True


if __name__ == "__main__":
    # Application life handler
    args = ArgInfo(default_port=PORT, default_debug=DEBUG, app_name=APPLICATION_NAME)
    app = Application(name=APPLICATION_NAME, port=args.port, debug=args.debug)
    app.init()
    app.run()
    app.end()

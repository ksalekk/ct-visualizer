import signal
import sys

from app.mvc_app import MvcApp

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = MvcApp(sys.argv)
    sys.exit(app.exec())

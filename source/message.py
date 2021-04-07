from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import webbrowser
import traceback

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class ErrorMessage(QtWidgets.QMessageBox):
    def __init__(self, message, parent_w):
        try:
            self.parent_w = parent_w
            super(ErrorMessage, self).__init__()
            title = "Unknown error!"
            self.message = self.parent_w.deep_settings.send_report_ask + "\n" + message
            self.setText(self.message)
            self.setWindowTitle(title)
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
            self.filename = self.parent_w.deep_settings.report_dir + self.parent_w.deep_settings.get_report_filename()
            log = ""
            with open(self.parent_w.deep_settings.log_dir + self.parent_w.deep_settings.log_filename, "r") as log_file:
                for line in log_file:
                    log += line

            with open(self.filename, "w", encoding="utf-8-sig") as report_file:
                report_file.write(self.message + "\n log:\n")
                report_file.write(log)

            open_btn_text = "Open the bug report"
            ok_text = "Ok"
            ok_btn = self.addButton(ok_text, QtWidgets.QMessageBox.AcceptRole)
            open_push_btn = QtWidgets.QPushButton(open_btn_text)
            open_btn = self.addButton(open_push_btn, QtWidgets.QMessageBox.NoRole)
            open_push_btn.clicked.connect(self.open_report)

            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
        except Exception as e:
            print("First Error: ", self.message)
            msg = traceback.format_exc()
            logger.error("Error in ErrorMessage:", exc_info=True)
            print(msg)
            QtCore.QThread.sleep(300)
            raise SystemExit(1)

    def open_report(self):
        webbrowser.open(self.filename)


class Message(QtWidgets.QMessageBox):
    def __init__(self, message, title, parent_w):
        try:
            super(Message, self).__init__()

            self.parent_w = parent_w

            section = self.parent_w.user_settings.language.upper()

            self.setText(message)
            self.setWindowTitle(title)
            self.setWindowIcon(QtGui.QIcon(self.parent_w.deep_settings.window_icon_filename))
            ok_text = self.parent_w.lang_parser.get(section, "Ok", fallback="Ok")
            ok_btn = self.addButton(ok_text, QtWidgets.QMessageBox.AcceptRole)

            logger.debug("Init Message")

        except Exception as e:
            msg = traceback.format_exc()
            logger.error("Unknown error", exc_info=True)
            emsg = ErrorMessage(message=msg, parent_w=self.parent_w)
            emsg.exec_()
            raise SystemExit(1)

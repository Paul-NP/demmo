from configparser import ConfigParser
from os import path
import datetime as dt
import logging

logger = logging.getLogger("main." + __name__)
logger.debug("load module")


class Settings:
    def __init__(self, settings=None, check_period=100, braking_dist=20,
                 threshold=0.0001, limit_step=1000, stop_mode="a", max_step=10000, divided_n=True):
        if settings is None:
            self.check_period = check_period
            self.braking_dist = braking_dist
            self.threshold = threshold
            self.limit_step = limit_step
            self.max_step = max_step
            self.stop_mode = stop_mode
            self.divided_n = divided_n
        else:
            self.check_period = settings.check_period
            self.braking_dist = settings.braking_dist
            self.threshold = settings.threshold
            self.limit_step = settings.limit_step
            self.max_step = settings.max_step
            self.stop_mode = settings.stop_mode
            self.divided_n = settings.divided_n

    def take_default(self):
        self.check_period = 100
        self.braking_dist = 20
        self.threshold = 0.0001
        self.limit_step = 1000
        self.max_step = 10000
        self.stop_mode = "a"

    def check_settings(self):
        info = []
        check = True
        element = ""
        if not isinstance(self.check_period, int):
            try:
                self.check_period = int(self.check_period)
                if self.check_period <= 0:
                    raise ValueError
            except ValueError:
                info.append(["Incorrect_check_period", "", ""])
                check = False
        if not isinstance(self.braking_dist, int):
            try:
                self.braking_dist = int(self.braking_dist)
                if self.braking_dist <= 0:
                    raise ValueError
            except ValueError:
                info.append(["Incorrect_braking_dist", "", ""])
                check = False
        if not isinstance(self.threshold, (float, int)):
            try:
                self.threshold = float(self.threshold)
                if self.threshold <= 0:
                    raise ValueError
            except ValueError:
                info.append(["Incorrect_threshold", "", ""])
                check = False
        if not isinstance(self.max_step, int):
            try:
                self.max_step = int(self.max_step)
                if self.max_step <= 0:
                    raise ValueError
            except ValueError:
                info.append(["Incorrect_max_step", "", ""])
                check = False

        return [check, info]

    def check_limit_step(self):
        info = []
        check = True
        if not isinstance(self.limit_step, int):
            try:
                self.limit_step = int(self.limit_step)
                if self.limit_step <= 0:
                    raise ValueError
            except ValueError:
                info.append(["Incorrect_limit_step", "", ""])
                check = False
        return [check, info]


class DeepSettings:
    def __init__(self, path):
        program_path = path.replace("\\", "/")
        self.program_version = "0.0.1 beta"
        self.program_name = "DEMMo"
        self.full_name = "{name} {vers}".format(name=self.program_name, vers=self.program_version)
        self.max_recent_file = 10
        self.num_char_label = 10
        self.file_extension = ".ecm"
        self.default_model_name = "untitled_model"
        self.default_path = program_path + "models/"
        self.default_filename = program_path + "models/untitled.edm"
        self.language_file = program_path + "locales/{}.ini"
        self.language_dir = program_path + "locales/"
        self.result_dir = program_path + "result/"
        self.result_file = program_path + "result/{0}_result_{1:02d}.csv"
        self.recent_file = program_path + "data/recent_lst.txt"
        self.user_file = program_path + "data/user_settings.ini"
        self.data_dir = program_path + "data/"
        self.group_suffix = "_group_{:02d}.csv"
        self.program_title = "{} - " + self.full_name
        self.log_dir = program_path + "logs/"
        log_temple_filename = self.full_name.replace(".", "_") + "_log_%Y_%m_%d_time_%H_%M_%S.log"
        self.log_temple_filename = log_temple_filename.replace(" ", "_")
        self.log_filename = ""
        self.help_dir = program_path + "help/"
        self.help_filename = "DEMMo_help.pdf"
        self.file_log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        self.console_log_format = "%(message)-20s\t- %(levelname)s\t- %(name)s"
        self.splash_filename = program_path + "image/splash.png"
        self.window_icon_filename = program_path + "image/logo_title.png"

        self.report_dir = program_path + "reports/"
        self.send_report_ask = "Please send the bug report to this mail: demmo.development@gmail.com\nlocation: " + self.report_dir
        report_temple_filename = self.full_name.replace(".", "_") + "_bug_report_%Y_%m_%d_time_%H_%M_%S.txt"
        self.report_temple_filename = report_temple_filename.replace(" ", "_")
        logger.debug("Init DeepSettings")

    def get_log_filename(self):
        date_now = dt.datetime.now()
        self.log_filename = date_now.strftime(self.log_temple_filename)
        return self.log_filename

    def get_report_filename(self):
        date_now = dt.datetime.now()
        return date_now.strftime(self.report_temple_filename)


class UserSettings:
    def __init__(self, deep_settings, user_settings=None, max_num_graphs=4, file_delimiter=",", language="english",
                 dfactor_file_head=False, floating_point=","):
        if user_settings is None:
            self.dfactor_file_head = dfactor_file_head
            self.file_delimiter = file_delimiter
            self.language = language
            self.deep_settings = deep_settings
            self.floating_point = floating_point
            # стоит убрать и сделать не изменяемым параметром
            # либо если предупредить пользователя о плохом восприятии и невозможности сделать понятно
            self.max_num_graphs = max_num_graphs
        else:
            self.dfactor_file_head = user_settings.dfactor_file_head
            self.file_delimiter = user_settings.file_delimiter
            self.language = user_settings.language
            self.deep_settings = user_settings.deep_settings
            self.floating_point = user_settings.floating_point
            self.max_num_graphs = user_settings.max_num_graphs

        logger.debug("Init UserSettings")

    def check_settings(self):
        info = []
        check = True
        if self.file_delimiter == "":
            info.append(["Incorrect_file_delimiter", "", ""])
            check = False
        try:
            self.max_num_graphs = int(self.max_num_graphs)
            if self.max_num_graphs <= 0:
                raise ValueError
        except ValueError:
            info.append(["Incorrect_max_num_graphs", "", ""])
            check = False

        return [check, info]

    def take_default(self):
        self.dfactor_file_head = False
        self.file_delimiter = ","
        self.max_num_graphs = 4
        self.language = "english"

    def get_user_settings(self):
        user_parser = ConfigParser()
        user_settings = UserSettings(self.deep_settings)
        if path.exists(self.deep_settings.user_file):
            user_parser.read(self.deep_settings.user_file)

            if user_parser.has_option("LOCALE", "language") and user_parser.has_option("OTHER", "max_num_graphs")\
                    and user_parser.has_option("OTHER", "file_delimiter")\
                    and user_parser.has_option("OTHER", "dfactor_file_head"):
                user_settings.language = user_parser.get("LOCALE", "language")
                user_settings.max_num_graphs = int(user_parser.get("OTHER", "max_num_graphs"))
                user_settings.file_delimiter = user_parser.get("OTHER", "file_delimiter")
                user_settings.dfactor_file_head = user_parser.get("OTHER", "dfactor_file_head") == "True"
                logger.debug("in get_user_settings: " + str(user_settings.dfactor_file_head))
                return user_settings
            else:
                self.write_user_settings()
                return user_settings
        else:
            self.write_user_settings()
            return user_settings

    def write_user_settings(self):
        user_parser = ConfigParser()
        dictionary = dict(vars(self))
        other_dict = dict(dictionary)
        del other_dict["language"]
        del other_dict["deep_settings"]
        lang_dict = {"language": dictionary["language"]}
        user_parser["OTHER"] = other_dict
        user_parser["LOCALE"] = lang_dict
        with open(self.deep_settings.user_file, "w") as file:
            user_parser.write(file)

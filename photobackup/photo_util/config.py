import configparser, os


class Config:
    # 定数
    SEC_DIR = 'DIRECTORY'
    SEC_SET = 'SETTING'
    MAIN_DIR = 'MainDirectory'
    BK_DIR = 'BackupDirectory'
    ARCH_MONTH = 'ArchiveMonth'
    FILE_PATH = 'setting.ini'

    _instance = None
    __config = configparser.ConfigParser()

    def __init__(self):
        if os.path.exists(self.FILE_PATH):
            self.__config.read(self.FILE_PATH)
        else:
            self.__config.add_section(self.SEC_DIR)
            self.__config.set(self.SEC_DIR, self.MAIN_DIR, '')
            self.__config.set(self.SEC_DIR, self.BK_DIR, '')
            self.__config.add_section(self.SEC_SET)
            self.__config.set(self.SEC_SET, self.ARCH_MONTH, '3')
            with open(self.FILE_PATH, 'w') as file:
                self.__config.write(file)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, section, key):
        return self.__config.get(section, key)

    def load_section(self, section):
        return self.__config.items(section)

    def save(self, section, kwargs):
        for k, v in kwargs.items():
            self.__config.set(section, k, v)
        with open(self.FILE_PATH, 'w') as file:
            self.__config.write(file)

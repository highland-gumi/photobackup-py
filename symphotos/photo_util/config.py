import configparser, os
from threading import Lock


class Config:
    # 定数
    SEC_DIR = 'DIRECTORY'
    SEC_SET = 'SETTING'
    MAIN_DIR = 'MainDirectory'
    BK_DIR = 'BackupDirectory'
    EXT_DIR = 'ExternalDirectory'
    ARCH_MONTH = 'ArchiveMonth'
    FILE_PATH = 'setting.ini'

    __instance = None
    __lock = Lock()
    __config = configparser.ConfigParser()

    def __new__(cls):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
                if os.path.exists(cls.FILE_PATH):
                    cls.__config.read(cls.FILE_PATH)
                else:
                    cls.__config.add_section(cls.SEC_DIR)
                    cls.__config.set(cls.SEC_DIR, cls.MAIN_DIR, '')
                    cls.__config.set(cls.SEC_DIR, cls.BK_DIR, '')
                    cls.__config.set(cls.SEC_DIR, cls.EXT_DIR, '')
                    cls.__config.add_section(cls.SEC_SET)
                    cls.__config.set(cls.SEC_SET, cls.ARCH_MONTH, '3')
                    with open(cls.FILE_PATH, 'w') as file:
                        cls.__config.write(file)
        return cls.__instance

    def load(self, section, key):
        return self.__config.get(section, key)

    def load_section(self, section):
        return self.__config.items(section)

    def save(self, section, kwargs):
        for k, v in kwargs.items():
            self.__config.set(section, k, v)
        with open(self.FILE_PATH, 'w') as file:
            self.__config.write(file)

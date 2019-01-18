import configparser

# 定数
SEC_DIR = 'DIRECTORY'
SEC_SET = 'SETTING'
MAIN_DIR = 'MainDirectory'
BK_DIR = 'BackupDirectory'
ARCH_MONTH = 'ArchiveMonth'
file_path = 'setting.ini'

__config = configparser.ConfigParser()
__config.read(file_path)


def load(section, key):
    return __config.get(section, key)


def load_section(section):
    return __config.items(section)


def save(section, kwargs):
    for k, v in kwargs.items():
        __config.set(section, k, v)

    with open(file_path, 'w') as file:
        __config.write(file)

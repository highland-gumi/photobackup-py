import re, datetime, os, filecmp, shutil
from typing import List
from dateutil.relativedelta import relativedelta
from photo_util.config import Config as Conf


class DateUtil:
    @staticmethod
    def parse(*, year, date=None, month=None, day=None) -> datetime:
        if date is not None:
            if str.isdigit(date):
                month = date[0:2]
                day = date[2:4]
            else:
                split = re.split(r'[^0-9]+', date)
                month = split[0]
                day = split[1]
        return datetime.datetime.strptime('%04s%02s%02s' % (year, month, day), '%Y%m%d')

    @staticmethod
    def default_from_day(arch_month=None):
        if not arch_month:
            conf = Conf()
            arch_month = conf.load(conf.SEC_SET, conf.ARCH_MONTH)
        if arch_month:
            return datetime.datetime.today() - relativedelta(months=int(arch_month))


class FileUtil:
    @staticmethod
    def contains_dir(target_dir, bk_dir) -> List:
        file_list = [f for f in os.listdir(target_dir) if not FileUtil.is_hidden(f)]
        for f in file_list:
            if os.path.isdir(f):
                # ディレクトリの場合は、サブディレクトリを処理する
                FileUtil.contains_dir(os.path.join(target_dir, bk_dir), os.path.join(target_dir, bk_dir))
        # チェック実施
        _, mismatch, error = filecmp.cmpfiles(target_dir, bk_dir, file_list)
        return mismatch + error

    @staticmethod
    def get_year_list(target_dir):
        for dir_name in os.listdir(target_dir):
            if dir_name.isdigit() and os.path.isdir(os.path.join(target_dir, dir_name)):
                yield dir_name

    @staticmethod
    def copy_not_exist(src, dest):
        if os.path.isdir(src) and not os.path.exists(dest):
            shutil.copytree(src, dest)
            return True
        ret = False
        for filename in os.listdir(src):
            src_path = os.path.join(src, filename)
            dest_path = os.path.join(dest, filename)
            if not os.path.exists(dest_path) and not FileUtil.is_hidden(filename):
                shutil.copy2(src_path, dest)
                ret = True
        return ret

    @staticmethod
    def is_hidden(filename):
        return filename.startswith('.')

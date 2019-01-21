import re, datetime, os, filecmp
from typing import List


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


class FileUtil:
    @staticmethod
    def contains_dir(target_dir, bk_dir) -> List:
        file_list = [f for f in os.listdir(target_dir) if not f.startswith('.')]
        for f in file_list:
            if os.path.isdir(f):
                # ディレクトリの場合は、サブディレクトリを処理する
                FileUtil.contains_dir(os.path.join(target_dir, bk_dir), os.path.join(target_dir, bk_dir))
        # チェック実施
        _, mismatch, error = filecmp.cmpfiles(target_dir, bk_dir, file_list)
        return mismatch + error








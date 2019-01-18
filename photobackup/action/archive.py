import os, datetime, re, shutil
from gui import window as window
from photo_util import common_utils as utils

# 定数
DATE_FORMAT = '%Y/%m/%d'


class Archive:
    def __init__(self):
        self.main_dir = window.Top.main_dir.get()
        self.bk_dir = window.Top.bk_dir.get()
        self.archive_day = datetime.datetime.today()

    def archive_previous_date(self, date):
        try:
            window.Top.log_info('【アーカイブ処理開始】')
            self.archive_day = date
            # 主処理
            for year in os.listdir(self.main_dir):
                year_dir = os.path.join(self.main_dir, year)
                if not os.path.exists(year_dir) or not year.isdigit() or os.path.islink(year_dir):
                    continue
                for month in os.listdir(year_dir):
                    month_dir = os.path.join(self.main_dir, year, month)
                    if not os.path.exists(month_dir) or os.path.islink(month_dir):
                        continue
                    elif 2 < len(month) and re.search(r'^[0-9]{1,2}[^0-9]*[0-9]{1,2}$', month):
                        # mmdd形式の処理
                        target_date = utils.DateUtil.parse(year=year, date=month)
                        self.exec_archive(target_date, month_dir)
                    elif month.isdigit():
                        # mm/dd形式の処理
                        for day in os.listdir(month_dir):
                            day_dir = os.path.join(self.main_dir, year, month, day)
                            if not os.path.exists(day_dir) or not day.isdigit() or os.path.islink(day_dir):
                                continue
                            else:
                                target_date = utils.DateUtil.parse(year=year, month=month, day=day)
                                self.exec_archive(target_date, day_dir)

        except Exception as e:
            window.Top.log_warn(e)
            pass
        finally:
            window.Top.log_info('【アーカイブ処理終了】')
        return

    def exec_archive(self, target_date, target_dir):
        if self.archive_day < target_date:
            return
        # 処理対象ディレクトリパス取得
        tmp_dir = target_dir + "_tmp"
        bk_dir = target_dir.replace(self.main_dir, self.bk_dir)
        not_bk_files = utils.FileUtil.contains_dir(target_dir, bk_dir)
        if not_bk_files:
            for file_name in not_bk_files:
                window.Top.log_info('バックアップされていないファイル：' + os.path.join(target_dir, file_name))
            return

        # 削除するファイルを一時的に移動
        shutil.move(target_dir, tmp_dir)
        # シンボリックリンク作成
        try:
            os.symlink(bk_dir, target_dir)
            window.Top.log_info('シンボリックリンク作成 ' + target_dir + ' -> ' + bk_dir)
        except Exception as e:
            window.Top.log_warn(e)
            shutil.move(tmp_dir, target_dir)
            pass
        shutil.rmtree(tmp_dir)
        window.Top.log_info(target_dir + 'を削除しました')

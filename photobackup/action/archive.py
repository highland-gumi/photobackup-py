import os, datetime, re, shutil
from gui import window as win
from photo_util import common_utils as utils
from photo_util.config import Config as Conf

# 定数
DATE_FORMAT = '%Y/%m/%d'


class Archive:
    def __init__(self, *,from_date=None, to_date=None):
        if from_date and isinstance(from_date, str):
            self.from_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
        else:
            self.from_date = from_date
        if to_date and isinstance(to_date, str):
            self.to_date = datetime.datetime.strptime(to_date, DATE_FORMAT)
        else:
            self.to_date = from_date
        conf = Conf()
        self.main_dir = conf.load(conf.SEC_DIR, conf.MAIN_DIR)
        self.bk_dir = conf.load(conf.SEC_DIR, conf.BK_DIR)

    def archive_previous_date(self):
        try:
            if not os.path.exists(self.main_dir):
                raise ValueError('メインディレクトリの設定が正しくありません：' + self.main_dir)
            if not os.path.exists(self.bk_dir):
                raise ValueError('バックアップディレクトリの設定が正しくありません：' + self.bk_dir)
            win.Top.log_info('【メイン→バックアップ アーカイブ処理開始】')

            # 主処理
            for year in os.listdir(self.main_dir):
                year_dir = os.path.join(self.main_dir, year)
                if not os.path.exists(year_dir) or os.path.islink(year_dir) or not year.isdigit() or len(year) != 4:
                    continue
                for month in os.listdir(year_dir):
                    month_dir = os.path.join(self.main_dir, year, month)
                    if not os.path.exists(month_dir) or os.path.islink(month_dir):
                        continue
                    if 2 < len(month) and re.search(r'^[0-9]{1,2}[^0-9]*[0-9]{1,2}.*$', month):
                        # 月と日が同一ディレクトリの処理
                        target_date = utils.DateUtil.parse(year=year, date=month)
                        self.exec_archive_dir(target_date, month_dir)
                    elif month.isdigit():
                        # 月の中に日のサブディレクトリの処理
                        for day in os.listdir(month_dir):
                            day_dir = os.path.join(self.main_dir, year, month, day)
                            if not os.path.exists(day_dir) or not day.isdigit() or os.path.islink(day_dir):
                                continue
                            target_date = utils.DateUtil.parse(year=year, month=month, day=day)
                            self.exec_archive_dir(target_date, day_dir)
            win.Top.log_info('【メイン→バックアップ アーカイブ処理終了】')
        except Exception as e:
            win.Top.log_warn(e)
            raise e

    def exec_archive_dir(self, target_date, target_dir):
        # 処理日付チェック
        if (self.from_date and target_date < self.from_date) \
                or (self.to_date and self.to_date < target_date):
            return
        # 処理対象ディレクトリパス取得
        tmp_dir = target_dir + "_tmp"
        bk_dir = target_dir.replace(self.main_dir, self.bk_dir)
        # バックアップディレクトリ存在確認
        if not os.path.exists(bk_dir):
            win.Top.log_info('バックアップディレクトリがありません：' + bk_dir)
            return
        not_bk_files = utils.FileUtil.contains_dir(target_dir, bk_dir)
        if not_bk_files:
            for file_name in not_bk_files:
                win.Top.log_info('バックアップされていないファイル：' + os.path.join(target_dir, file_name))
            return
        # 削除するファイルを一時的に移動
        shutil.move(target_dir, tmp_dir)
        # シンボリックリンク作成
        try:
            os.symlink(bk_dir, target_dir)
            win.Top.log_info('シンボリックリンク作成：' + target_dir + ' -> ' + bk_dir)
        except Exception as e:
            win.Top.log_warn(e)
            shutil.move(tmp_dir, target_dir)
            raise e
        shutil.rmtree(tmp_dir)
        win.Top.log_info(target_dir + 'を削除しました')


class BackArchive:
    def __init__(self, *,from_date=None, to_date=None):
        if from_date and isinstance(from_date, str):
            self.from_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
        else:
            self.from_date = from_date
        if to_date and isinstance(to_date, str):
            self.to_date = datetime.datetime.strptime(to_date, DATE_FORMAT)
        else:
            self.to_date = from_date
        conf = Conf()
        self.main_dir = conf.load(conf.SEC_DIR, conf.MAIN_DIR)
        self.bk_dir = conf.load(conf.SEC_DIR, conf.BK_DIR)

    def back_archive_by_date(self):
        try:
            if not os.path.exists(self.main_dir):
                raise ValueError('メインディレクトリの設定が正しくありません：' + self.main_dir)
            if not os.path.exists(self.bk_dir):
                raise ValueError('バックアップディレクトリの設定が正しくありません：' + self.bk_dir)
            win.Top.log_info('【バックアップ→メインコピー開始】')

            # 主処理
            for year in os.listdir(self.main_dir):
                year_dir = os.path.join(self.main_dir, year)
                if not os.path.exists(year_dir) or os.path.islink(year_dir) or not year.isdigit() or len(year) != 4:
                    continue
                for month in os.listdir(year_dir):
                    month_dir = os.path.join(self.main_dir, year, month)
                    if 2 < len(month) and re.search(r'^[0-9]{1,2}[^0-9]*[0-9]{1,2}.*$', month):
                        # 月と日が同一ディレクトリの処理
                        if not os.path.islink(month_dir):
                            continue
                        target_date = utils.DateUtil.parse(year=year, date=month)
                        self.exec_copy(target_date, month_dir)
                    elif month.isdigit():
                        # 月の中に日のサブディレクトリの処理
                        for day in os.listdir(month_dir):
                            day_dir = os.path.join(self.main_dir, year, month, day)
                            if not day.isdigit() or not os.path.islink(day_dir):
                                continue
                            target_date = utils.DateUtil.parse(year=year, month=month, day=day)
                            self.exec_copy(target_date, day_dir)

            win.Top.log_info('【バックアップ→メインコピー処理終了】')
        except Exception as e:
            win.Top.log_warn(e)
            raise e

    def exec_copy(self, target_date, target_dir):
        # 処理日付チェック
        if (self.from_date and target_date < self.from_date) \
                or (self.to_date and self.to_date < target_date):
            return
        # 処理対象ディレクトリパス取得
        tmp_dir = target_dir + "_tmp"
        bk_dir = target_dir.replace(self.main_dir, self.bk_dir)
        # バックアップディレクトリ存在確認
        if not os.path.exists(bk_dir):
            win.Top.log_info('バックアップディレクトリがありません：' + bk_dir)
            return
        # 削除するシンボリックリンクを一時的に移動
        shutil.move(target_dir, tmp_dir)
        # シンボリックリンク削除とファイルコピー
        try:
            shutil.copytree(bk_dir, target_dir)
            win.Top.log_info('ファイルコピー：' + bk_dir + ' -> ' + target_dir)
        except Exception as e:
            win.Top.log_warn(e)
            shutil.rmtree(target_dir)
            shutil.move(tmp_dir, target_dir)
            raise e
        os.remove(tmp_dir)
        win.Top.log_info('シンボリックリンク削除：' + target_dir)


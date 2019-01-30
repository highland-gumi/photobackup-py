import os, datetime, re, shutil
from distutils import dir_util
from gui import window as win
from photo_util import common_utils as utils
from photo_util.config import Config as Conf

# 定数
DATE_FORMAT = '%Y/%m/%d'
TYPE_COPY = 0
TYPE_MOVE = 1


class Archive:
    def __init__(self, *,from_date=None, to_date=None):
        if from_date and isinstance(from_date, str):
            self.from_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
        else:
            self.from_date = from_date
        if to_date and isinstance(to_date, str):
            self.to_date = datetime.datetime.strptime(to_date, DATE_FORMAT)
        else:
            self.to_date = to_date
        conf = Conf()
        self.main_dir = conf.load(conf.SEC_DIR, conf.MAIN_DIR)
        self.bk_dir = conf.load(conf.SEC_DIR, conf.BK_DIR)

    def func_exec_by_date(self):
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

    def func_copy_to_backup(self):
        try:
            if not os.path.exists(self.main_dir):
                raise ValueError('メインディレクトリの設定が正しくありません：' + self.main_dir)
            if not os.path.exists(self.bk_dir):
                raise ValueError('バックアップディレクトリの設定が正しくありません：' + self.bk_dir)
            win.Top.log_info('【メイン→バックアップ コピー処理開始】')

            # 主処理
            for year in os.listdir(self.main_dir):
                year_dir = os.path.join(self.main_dir, year)
                if not os.path.exists(year_dir) or os.path.islink(year_dir) or not year.isdigit() or len(year) != 4:
                    continue
                for month in os.listdir(year_dir):
                    month_dir = os.path.join(self.main_dir, year, month)
                    if 2 < len(month) and re.search(r'^[0-9]{1,2}[^0-9]*[0-9]{1,2}.*$', month):
                        # 月と日が同一ディレクトリの処理
                        if os.path.islink(month_dir):
                            continue
                        target_date = utils.DateUtil.parse(year=year, date=month)
                        self.exec_copy(target_date, month_dir)
                    elif month.isdigit():
                        # 月の中に日のサブディレクトリの処理
                        for day in os.listdir(month_dir):
                            day_dir = os.path.join(self.main_dir, year, month, day)
                            if not day.isdigit() or os.path.islink(day_dir):
                                continue
                            target_date = utils.DateUtil.parse(year=year, month=month, day=day)
                            self.exec_copy(target_date, day_dir)

            win.Top.log_info('【メイン→バックアップ コピー処理終了】')
        except Exception as e:
            win.Top.log_warn(e)
            raise e

    def exec_copy(self, target_date, src_dir):
        # 処理日付チェック
        if (self.from_date and target_date < self.from_date) \
                or (self.to_date and self.to_date < target_date):
            return

        bk_dir = src_dir.replace(self.main_dir, self.bk_dir)
        result = utils.FileUtil.copy_not_exist(src_dir, bk_dir)
        if result:
            win.Top.log_info('ファイルコピー：' + src_dir + ' -> ' + bk_dir)


class BackArchive:
    def __init__(self, *,from_date=None, to_date=None):
        if from_date and isinstance(from_date, str):
            self.from_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
        else:
            self.from_date = from_date
        if to_date and isinstance(to_date, str):
            self.to_date = datetime.datetime.strptime(to_date, DATE_FORMAT)
        else:
            self.to_date = to_date
        conf = Conf()
        self.main_dir = conf.load(conf.SEC_DIR, conf.MAIN_DIR)
        self.bk_dir = conf.load(conf.SEC_DIR, conf.BK_DIR)

    def func_exec_by_date(self):
        try:
            if not os.path.exists(self.main_dir):
                raise ValueError('メインディレクトリの設定が正しくありません：' + self.main_dir)
            if not os.path.exists(self.bk_dir):
                raise ValueError('バックアップディレクトリの設定が正しくありません：' + self.bk_dir)
            win.Top.log_info('【バックアップ→メイン 復元コピー開始】')

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

            win.Top.log_info('【バックアップ→メイン 復元コピー処理終了】')
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


class ExtDisk:
    def __init__(self, year, exec_type):
        self.year = year
        self.type = exec_type
        conf = Conf()
        self.main_dir = conf.load(conf.SEC_DIR, conf.MAIN_DIR)
        self.bk_dir = conf.load(conf.SEC_DIR, conf.BK_DIR)
        self.ext_dir = conf.load(conf.SEC_DIR, conf.EXT_DIR)

    def func_exec(self):
        try:
            if not os.path.exists(self.main_dir):
                raise ValueError('メインディレクトリの設定が正しくありません：' + self.main_dir)
            if not os.path.exists(self.bk_dir):
                raise ValueError('バックアップディレクトリの設定が正しくありません：' + self.bk_dir)
            if not os.path.exists(self.ext_dir):
                raise ValueError('外部ディスクの設定が正しくありません：' + self.ext_dir)
            main_year_dir = os.path.join(self.main_dir, self.year)
            tmp_main_dir = main_year_dir + '_tmp'
            bk_year_dir = os.path.join(self.bk_dir, self.year)
            ext_year_dir = os.path.join(self.ext_dir, self.year)
            if os.path.exists(ext_year_dir) or os.path.islink(main_year_dir):
                raise ValueError('指定した年は既に外部ディスクにコピーされています')
            if not os.path.exists(bk_year_dir):
                raise ValueError('指定した年のバックアップは存在しません')

            # 処理開始
            win.Top.log_info('【バックアップ→外部ディスクコピー開始】')

            # コピー実行
            shutil.copytree(bk_year_dir, ext_year_dir)
            if not utils.FileUtil.contains_dir(ext_year_dir, bk_year_dir):
                # コピー失敗時は元の状態に戻す
                shutil.rmtree(ext_year_dir)
                raise ValueError('外部ディスクへのコピーに失敗しました')
            try:
                # シンボリックリンク作成
                shutil.move(main_year_dir, tmp_main_dir)
                os.symlink(ext_year_dir, main_year_dir)
                win.Top.log_info('シンボリックリンク作成：' + main_year_dir + '->' + ext_year_dir)
                shutil.rmtree(tmp_main_dir)
            except Exception as e:
                # シンボリックリンク作成失敗
                shutil.rmtree(ext_year_dir)
                shutil.move(tmp_main_dir, main_year_dir)
                raise e

            if self.type == TYPE_MOVE:
                # 動作モードが移動の場合はバックアップディレクトリ削除
                shutil.rmtree(bk_year_dir)
                win.Top.log_info('外部ディスクに移動しました：' + bk_year_dir + ' -> ' + ext_year_dir)
            else:
                win.Top.log_info('外部ディスクにコピーしました：' + bk_year_dir + ' -> ' + ext_year_dir)

            win.Top.log_info('【バックアップ→外部ディスクコピー終了】')
        except Exception as e:
            win.Top.log_warn(e)
            raise e

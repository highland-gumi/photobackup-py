import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk
import os, threading
from datetime import datetime
from action import archive
from photo_util.config import Config as Conf
from photo_util.common_utils import DateUtil as DateUtil
from photo_util.thread_lock import Lock as Lock

# 定数
MAIN_TO_BK_COPY = 'メイン→バックアップ コピー'
MAIN_TO_BK_ARCH = 'メイン→バックアップ リンク作成'
BK_TO_MAIN_BACK = 'バックアップ→メイン 復元コピー'


class Top:
    def __init__(self):
        conf = Conf()
        self.main_dir.set(conf.load(Conf.SEC_DIR, Conf.MAIN_DIR))
        self.bk_dir.set(conf.load(Conf.SEC_DIR, Conf.BK_DIR))
        self.ext_dir.set(conf.load(Conf.SEC_DIR, Conf.EXT_DIR))
        arch_month = int(conf.load(Conf.SEC_SET, Conf.ARCH_MONTH))
        if arch_month:
            default_day = DateUtil.default_from_day()
            self.archive_to.set(default_day.strftime(archive.DATE_FORMAT))
        self.ext_type = archive.TYPE_COPY

    # 画面用変数
    root = tk.Tk()
    main_dir = tk.StringVar()
    bk_dir = tk.StringVar()
    ext_dir = tk.StringVar()
    archive_from = tk.StringVar()
    archive_to = tk.StringVar()
    ext_year = tk.StringVar()
    ext_type = tk.IntVar()
    logs = tk.Text()
    arch_combo = ttk.Combobox()

    @classmethod
    def main_dir_ref(cls):
        refs = tk.filedialog.askdirectory(initialdir=cls.main_dir.get())
        if refs:
            cls.main_dir.set(refs.replace('/', os.sep))

    @classmethod
    def bk_dir_ref(cls):
        refs = tk.filedialog.askdirectory(initialdir=cls.bk_dir.get())
        if refs:
            cls.bk_dir.set(refs.replace('/', os.sep))

    @classmethod
    def ext_dir_ref(cls):
        refs = tk.filedialog.askdirectory(initialdir=cls.ext_dir.get())
        if refs:
            cls.ext_dir.set(refs.replace('/', os.sep))

    @classmethod
    def exec_save(cls):
        conf = Conf()
        dic = {Conf.MAIN_DIR: cls.main_dir.get(),
               Conf.BK_DIR: cls.bk_dir.get(),
               Conf.EXT_DIR: cls.ext_dir.get()}
        conf.save(conf.SEC_DIR, dic)
        cls.log_info('設定値を保存しました')

    @classmethod
    def exec_arch(cls):
        if not Lock().is_locked():
            cls.log_warn('別の処理を実行中です')
            return

        # 実行
        from_date = cls.archive_from.get()
        to_date = cls.archive_to.get()
        cmd = cls.arch_combo.get()
        if not from_date and not to_date:
            cls.log_info('対象日が指定されていません')
            return
        cls.exec_save()

        if cmd == MAIN_TO_BK_ARCH:
            action = archive.Archive(from_date=from_date, to_date=to_date)
            threading.Thread(target=action.func_exec_by_date).start()
        elif cmd == MAIN_TO_BK_COPY:
            action = archive.Archive(from_date=from_date, to_date=to_date)
            threading.Thread(target=action.func_copy_to_backup).start()
        elif cmd == BK_TO_MAIN_BACK:
            action = archive.BackArchive(from_date=from_date, to_date=to_date)
            threading.Thread(target=action.func_exec_by_date).start()

    @classmethod
    def exec_ext_move(cls):
        exec_type = cls.ext_type.get()
        year = cls.ext_year.get()
        if not year.isdigit():
            cls.log_info('年の形式が正しくありません')
            return
        if exec_type in (archive.TYPE_COPY, archive.TYPE_MOVE):
            cls.exec_save()
            archive.ExtDisk(year, exec_type).func_exec()

    @classmethod
    def log_warn(cls, msg):
        cls.add_log('WARN', msg)

    @classmethod
    def log_info(cls, msg):
        cls.add_log('INFO', msg)

    @classmethod
    def add_log(cls, level, msg):
        now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        cls.logs.insert(tk.END, '[%s][%s] %s\n' % (now, level, msg))
        cls.logs.see(tk.END)

    @classmethod
    def create_window(cls):
        cls.root.title('写真バックアップツール')

        # フレーム
        out_frame = ttk.Frame(cls.root, padding=10)
        out_frame.grid()
        frame1 = ttk.Frame(out_frame, padding=(0, 5))
        frame1.grid(row=1, column=0)
        frame2 = ttk.Frame(out_frame, padding=(0, 10))
        frame2.grid(row=2, column=0)
        frame3 = ttk.Frame(out_frame, padding=(0, 5))
        frame3.grid(row=3, column=0)

        # ディレクトリ設定
        label1_1 = ttk.Label(frame1, text='メインディレクトリ', padding=(5, 2))
        label1_1.grid(row=0, column=0, sticky=tk.E)
        main_dir_entry = ttk.Entry(
            frame1,
            textvariable=cls.main_dir,
            width=30)
        main_dir_entry.grid(row=0, column=1)
        main_dir_ref_btn = ttk.Button(frame1, text='参照', command=cls.main_dir_ref)
        main_dir_ref_btn.grid(row=0, column=2)

        label1_2 = ttk.Label(frame1, text='バックアップディレクトリ', padding=(5, 2))
        label1_2.grid(row=1, column=0, sticky=tk.E)
        bk_dir_entry = ttk.Entry(
            frame1,
            textvariable=cls.bk_dir,
            width=30)
        bk_dir_entry.grid(row=1, column=1)
        bk_dir_ref_btn = ttk.Button(frame1, text='参照', command=cls.bk_dir_ref)
        bk_dir_ref_btn.grid(row=1, column=2)

        label1_3 = ttk.Label(frame1, text='外部ディスク', padding=(5, 2))
        label1_3.grid(row=2, column=0, sticky=tk.E)
        ext_dir_entry = ttk.Entry(
            frame1,
            textvariable=cls.ext_dir,
            width=30)
        ext_dir_entry.grid(row=2, column=1)
        ext_dir_ref_btn = ttk.Button(frame1, text='参照', command=cls.ext_dir_ref)
        ext_dir_ref_btn.grid(row=2, column=2)

        # 設定保存
        save_btn = ttk.Button(frame1, text='設定保存', command=cls.exec_save)
        save_btn.grid(row=3, column=2)

        # 期間指定
        frame2_1 = ttk.Frame(frame2)
        frame2_1.grid(row=0, column=0, sticky=tk.W)
        archive_from = ttk.Entry(
            frame2_1,
            textvariable=cls.archive_from,
            width=10)
        archive_from.grid(row=0, column=0)
        label2_2 = ttk.Label(frame2_1, text='から', padding=(5, 2))
        label2_2.grid(row=0, column=1, sticky=tk.E)
        archive_to = ttk.Entry(
            frame2_1,
            textvariable=cls.archive_to,
            width=10)
        archive_to.grid(row=0, column=2)
        # プルダウン作成
        cls.arch_combo = ttk.Combobox(frame2_1, state='readonly', width=25)
        cls.arch_combo['values'] = (MAIN_TO_BK_COPY, MAIN_TO_BK_ARCH, BK_TO_MAIN_BACK)
        cls.arch_combo.current(1)
        cls.arch_combo.grid(row=0, column=3, padx=5, sticky=tk.E)
        # 実行ボタン
        arch_btn1 = ttk.Button(frame2, text='実行', command=cls.exec_arch)
        arch_btn1.grid(row=0, column=1)

        # バックアップ→外部ディスクコピー
        frame2_2 = ttk.Frame(frame2)
        frame2_2.grid(row=1, column=0, sticky=tk.W)

        label2_4 = ttk.Label(frame2_2, text='バックアップ→外部ディスク', padding=(5, 2))
        label2_4.grid(row=0, column=0, sticky=tk.E)

        ext_copy_year = ttk.Entry(
            frame2_2,
            textvariable=cls.ext_year,
            width=6)
        ext_copy_year.grid(row=0, column=1)
        label2_4 = ttk.Label(frame2_2, text='年', padding=(5, 2))
        label2_4.grid(row=0, column=2, sticky=tk.E)
        ext_radio1 = tk.Radiobutton(frame2_2, value=archive.TYPE_COPY, variable=cls.ext_type, text='コピー')
        ext_radio1.grid(row=0, column=3, sticky=tk.E)
        ext_radio2 = tk.Radiobutton(frame2_2, value=archive.TYPE_MOVE, variable=cls.ext_type, text='移動')
        ext_radio2.grid(row=0, column=4, sticky=tk.E)
        arch_btn3 = ttk.Button(frame2, text='実行', command=cls.exec_ext_move)
        arch_btn3.grid(row=1, column=1)

        # ログエリア
        log_msg = ttk.Label(frame3, text='ログ', padding=(5, 2))
        log_msg.grid(row=0, column=0)
        cls.logs = tk.Text(frame3)
        cls.logs.grid(row=1, column=0)
        scrollbar = ttk.Scrollbar(
            frame3,
            orient=tk.VERTICAL,
            command=cls.logs.yview)
        cls.logs[tk.Y + tk.SCROLL + tk.COMMAND] = scrollbar.set
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # ループ
        cls.root.mainloop()

import tkinter as tk
from tkinter import ttk as ttk
from datetime import datetime
import threading, os
from dateutil.relativedelta import relativedelta
import tkinter.filedialog as filedialog
from photo_util.config import Config as Conf
from photo_util.common_utils import FileUtil as FUtil
from action import archive

class Top:
    def __init__(self):
        conf = Conf()
        self.main_dir.set(conf.load(conf.SEC_DIR, conf.MAIN_DIR))
        self.bk_dir.set(conf.load(conf.SEC_DIR, conf.BK_DIR))
        self.ext_dir.set(conf.load(conf.SEC_DIR, conf.EXT_DIR))
        arch_month = int(conf.load(conf.SEC_SET, conf.ARCH_MONTH))
        default_day = datetime.today() - relativedelta(months=arch_month)
        self.archive_to.set(default_day.strftime(archive.DATE_FORMAT))
        self.ext_type = archive.TYPE_COPY

    _instance = None
    _lock = threading.Lock()
    root = tk.Tk()
    main_dir = tk.StringVar()
    bk_dir = tk.StringVar()
    ext_dir = tk.StringVar()
    archive_from = tk.StringVar()
    archive_to = tk.StringVar()
    archive_back_from = tk.StringVar()
    archive_back_to = tk.StringVar()
    ext_year = tk.StringVar()
    ext_type = tk.IntVar()
    logs = tk.Text()

    @classmethod
    def main_dir_ref(cls):
        refs = filedialog.askdirectory(initialdir=cls.main_dir.get())
        if refs:
            cls.main_dir.set(refs.replace('/', os.sep))

    @classmethod
    def bk_dir_ref(cls):
        refs = filedialog.askdirectory(initialdir=cls.bk_dir.get())
        if refs:
            cls.bk_dir.set(refs.replace('/', os.sep))

    @classmethod
    def ext_dir_ref(cls):
        refs = filedialog.askdirectory(initialdir=cls.ext_dir.get())
        if refs:
            cls.ext_dir.set(refs.replace('/', os.sep))

    @classmethod
    def exec_save(cls):
        conf = Conf()
        dic = {conf.MAIN_DIR: cls.main_dir.get(),
               conf.BK_DIR: cls.bk_dir.get(),
               conf.EXT_DIR: cls.ext_dir.get()}
        conf.save(conf.SEC_DIR, dic)
        cls.log_info('設定値を保存しました')

    @classmethod
    def exec_arch(cls):
        # 実行
        from_date = cls.archive_from.get()
        to_date = cls.archive_to.get()
        if not from_date and not to_date:
            cls.log_info('対象日が指定されていません')
            return
        cls.exec_save()
        archive.Archive(from_date=from_date, to_date=to_date).func_exec_by_date()

    @classmethod
    def exec_back_arch(cls):
        # 実行
        from_date = cls.archive_back_from.get()
        to_date = cls.archive_back_to.get()
        if not from_date and not to_date:
            cls.log_info('対象日が指定されていません')
            return
        cls.exec_save()
        archive.BackArchive(from_date=from_date, to_date=to_date).func_exec_by_date()

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
    def add_log(cls, level, msg):
        now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        cls.logs.insert(tk.END, '[%s][%s] %s\n' % (now, level, msg))
        cls.logs.see(tk.END)

    @classmethod
    def log_warn(cls, msg):
        cls.add_log('WARN', msg)

    @classmethod
    def log_info(cls, msg):
        cls.add_log('INFO', msg)

    @classmethod
    def create_window(cls):
        cls.root.title('写真バックアップツール')

        # フレーム
        out_frame = ttk.Frame(cls.root, padding=10)
        out_frame.grid()
        frame1 = ttk.Frame(out_frame, padding=(0, 5))
        frame1.grid(row=1, column=0)
        frame2 = ttk.Frame(out_frame, padding=(0, 10))
        frame2.grid(row=2, column=0, sticky=tk.W)
        frame3 = ttk.Frame(out_frame, padding=(0, 5))
        frame3.grid(row=3, column=0, sticky=tk.W)

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

        # アーカイブ実行
        label2_1 = ttk.Label(frame2, text='メイン→バックアップ アーカイブ', padding=(5, 2))
        label2_1.grid(row=0, column=0, sticky=tk.E)
        archive_from = ttk.Entry(
            frame2,
            textvariable=cls.archive_from,
            width=10)
        archive_from.grid(row=0, column=1)
        label2_2 = ttk.Label(frame2, text='から', padding=(5, 2))
        label2_2.grid(row=0, column=2, sticky=tk.E)
        archive_to = ttk.Entry(
            frame2,
            textvariable=cls.archive_to,
            width=10)
        archive_to.grid(row=0, column=3)
        arch_btn1 = ttk.Button(frame2, text='実行', command=cls.exec_arch)
        arch_btn1.grid(row=0, column=4)

        # アーカイブ復帰実行
        label2_3 = ttk.Label(frame2, text='バックアップ→メイン コピー', padding=(5, 2))
        label2_3.grid(row=1, column=0, sticky=tk.E)
        arch_back_from = ttk.Entry(
            frame2,
            textvariable=cls.archive_back_from,
            width=10)
        arch_back_from.grid(row=1, column=1)
        label2_4 = ttk.Label(frame2, text='から', padding=(5, 2))
        label2_4.grid(row=1, column=2, sticky=tk.E)
        arch_back_to = ttk.Entry(
            frame2,
            textvariable=cls.archive_back_to,
            width=10)
        arch_back_to.grid(row=1, column=3)
        arch_btn2 = ttk.Button(frame2, text='実行', command=cls.exec_back_arch)
        arch_btn2.grid(row=1, column=4)

        # バックアップ→外部ディスクコピー
        label2_4 = ttk.Label(frame2, text='バックアップ→外部ディスク', padding=(5, 2))
        label2_4.grid(row=2, column=0, sticky=tk.E)
        frame2_1 = ttk.Frame(frame2)
        frame2_1.grid(row=2, column=1, sticky=tk.W)
        ext_copy_year = ttk.Entry(
            frame2_1,
            textvariable=cls.ext_year,
            width=6)
        ext_copy_year.grid(row=0, column=1)
        label2_4 = ttk.Label(frame2_1, text='年', padding=(5, 2))
        label2_4.grid(row=0, column=2, sticky=tk.E)
        frame2_2 = ttk.Frame(frame2)
        frame2_2.grid(row=2, column=2, columnspan=2, sticky=tk.E)
        ext_radio1 = tk.Radiobutton(frame2_2, value=archive.TYPE_COPY, variable=cls.ext_type, text='コピー')
        ext_radio1.grid(row=0, column=0, sticky=tk.E)
        ext_radio2 = tk.Radiobutton(frame2_2, value=archive.TYPE_MOVE, variable=cls.ext_type, text='移動')
        ext_radio2.grid(row=0, column=1, sticky=tk.E)
        arch_btn3 = ttk.Button(frame2, text='実行', command=cls.exec_ext_move)
        arch_btn3.grid(row=2, column=4)

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

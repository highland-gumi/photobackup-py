import tkinter as tk
from tkinter import ttk as ttk
from datetime import datetime
import threading
from dateutil.relativedelta import relativedelta
import tkinter.filedialog as filedialog
from action.archive import Archive
import photo_util.config as conf
import action.archive as archive


class Top:
    def __init__(self):
        self.main_dir.set(conf.load(conf.SEC_DIR, conf.MAIN_DIR))
        self.bk_dir.set(conf.load(conf.SEC_DIR, conf.BK_DIR))
        arch_month = int(conf.load(conf.SEC_SET, conf.ARCH_MONTH))
        default_day = datetime.today() - relativedelta(months=arch_month)
        self.archive_day.set(default_day.strftime(archive.DATE_FORMAT))

    _instance = None
    _lock = threading.Lock()
    root = tk.Tk()
    main_dir = tk.StringVar()
    bk_dir = tk.StringVar()
    archive_day = tk.StringVar()
    logs = tk.Text()

    @classmethod
    def main_dir_ref(cls):
        refs = filedialog.askdirectory(initialdir=cls.main_dir.get())
        cls.main_dir.set(refs)

    @classmethod
    def bk_dir_ref(cls):
        refs = filedialog.askdirectory(initialdir=cls.bk_dir.get())
        cls.bk_dir.set(refs)

    @classmethod
    def exec_save(cls):
        dic = {conf.MAIN_DIR:cls.main_dir.get(),
               conf.BK_DIR:cls.bk_dir.get()}
        conf.save(conf.SEC_DIR, dic)
        cls.log_info('設定値を保存しました')

    @classmethod
    def exec_arch(cls):
        cls.exec_save()
        # 実行
        archive_day = datetime.strptime(cls.archive_day.get(), archive.DATE_FORMAT)
        Archive().archive_previous_date(archive_day)

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
        cls.root.resizable(False, False)
        # フレーム
        out_frame = ttk.Frame(cls.root, padding=10)
        out_frame.grid()
        frame1 = ttk.Frame(out_frame, padding=(0, 5))
        frame1.grid()
        frame2 = ttk.Frame(out_frame, padding=(0, 10))
        frame2.grid(row=2, column=0, sticky=tk.W)
        frame3 = ttk.Frame(out_frame, padding=(0, 5))
        frame3.grid(row=3, column=0, sticky=tk.W)

        # ディレクトリ設定
        label1 = ttk.Label(frame1, text='メインディレクトリ', padding=(5, 2))
        label1.grid(row=0, column=0, sticky=tk.E)
        main_dir_entry = ttk.Entry(
            frame1,
            textvariable=cls.main_dir,
            width=30)
        main_dir_entry.grid(row=0, column=1)
        main_dir_ref_btn = ttk.Button(frame1, text='参照', command=cls.main_dir_ref)
        main_dir_ref_btn.grid(row=0, column=2)

        label2 = ttk.Label(frame1, text='バックアップディレクトリ', padding=(5, 2))
        label2.grid(row=1, column=0, sticky=tk.E)
        bk_dir_entry = ttk.Entry(
            frame1,
            textvariable=cls.bk_dir,
            width=30)
        bk_dir_entry.grid(row=1, column=1)
        bk_dir_ref_btn = ttk.Button(frame1, text='参照', command=cls.bk_dir_ref)

        # 設定保存
        bk_dir_ref_btn.grid(row=1, column=2)
        save_btn = ttk.Button(frame1, text='設定保存', command=cls.exec_save)
        save_btn.grid(row=2, column=2)

        # アーカイブ実行
        label3 = ttk.Label(frame2, text='指定日以前一括アーカイブ', padding=(60, 2))
        label3.grid(row=0, column=0, sticky=tk.E)
        archive_entry = ttk.Entry(
            frame2,
            textvariable=cls.archive_day,
            width=10)
        archive_entry.grid(row=0, column=1)
        arch_btn = ttk.Button(frame2, text='実行', command=cls.exec_arch)
        arch_btn.grid(row=0, column=2)

        # ログエリア
        label4 = ttk.Label(frame3, text='ログ', padding=(5, 2))
        label4.grid(row=0, column=0)
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

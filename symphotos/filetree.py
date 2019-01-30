import tkinter as tk
from tkinter import ttk as ttk
import os


ROOT_PATH = '/Users/sohei/photo/main'


class Main:
    root = tk.Tk()
    row = 0
    cul = 0

    def dir_tree(self, path):
        self.row = 0
        self.cul = 0
        self.__dir_tree(path)

    def __dir_tree(self, path):
        self.create_label('/' + os.path.basename(path), self.row, self.cul)
        self.label_rule(self.row, self.cul)
        self.row += 1
        for dir_name in sorted(os.listdir(path)):
            print(dir_name)
            dir_path = os.path.join(path, dir_name)
            if os.path.isdir(dir_path):
                self.cul += 1
                self.__dir_tree(dir_path)
                self.cul -= 1



    def exec(self):
        self.dir_tree(ROOT_PATH)
        self.root.mainloop()


    def create_label(self, text, row, column):
        label = ttk.Label(self.root, text=text)
        label.grid(row=row, column=column)
        print(text + '→' + str(row) + ':' + str(column))


    def label_rule(self, row, cul, last=False):
        for i in range(cul):
            if i == cul - 1:
                if last:
                    self.create_label('└', row, i)
                else:
                   self.create_label('├', row, i)
            else:
                self.create_label('│', row, i)


Main().exec()
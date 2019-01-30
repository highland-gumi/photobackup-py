#!/usr/bin/python
# coding:utf-8

#==============================
# ファイルツリーを標準出力に出力
#
# filetree.py <directory>
#==============================

import os
import sys

target = '/Users/sohei/photo/main'
# ファイルリスト作成

flist = []
for root,dirs,files in os.walk(target):
	root = os.path.relpath(root, target)
	if root == '.': root = ''

	flist.append([root, sorted(dirs), sorted(files)])

# ファイル名表示

def print_file(fname,lvlist,last):
	t = ''

	if len(lvlist): t += ' '

	if len(lvlist) >= 2:
		for b in lvlist[1:]:
			if b:
				t += '　  '
			else:
				t += '│  '

	if len(lvlist):
		if last:
			t += '└ '
		else:
			t += '├ '
	print(t + fname)

# メイン処理

def func_main(arg,lvlist):
	root,dirs,files = arg

	dirlen = len(dirs)
	flen = len(files)

	# サブディレクトリ処理

	for i,dname in enumerate(dirs):
		nounder = (i == dirlen - 1 and flen == 0)

		print_file(dname, lvlist, nounder)

		# このサブディレクトリを親とするディレクトリ

		under_root = os.path.join(root, dname)
		under_list = []

		for t in flist:
			if t[0] == under_root:
				under_list.append(t)

		for j,t in enumerate(under_list):
			if nounder and j == len(under_list) - 1:
				add = [True]
			else:
				add = [False]

			func_main(t, lvlist + add)


# 開始

func_main(flist.pop(0), [])

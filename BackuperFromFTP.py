# -*- coding: utf-8 -*-
import ftplib, os
#import Tkinter as tkinter

path_local = "hosting" # Data will copy to this directory
if not os.path.exists(path_local): os.mkdir(path_local)

server = "0.0.0.0"
login = "blabla"
password = "qwerty"

class adminFTP():
  ftp = None
  def __init__(self, server, login, password):
    self.ftp = ftplib.FTP(server, login, password)

  def _download_file(self, local_path, name):
    """ Загружает файл с сервера на локальный компьютер """
    """ Load data from ftp to your computer"""
    f = open(local_path+"/"+name, "wb")
    self.ftp.retrbinary("RETR "+name, f.write)
    f.close()

  def _download_lines(self):
    """ Возвращает список директорий и файлов на сервере """
    """ Return list of directories and files from ftp"""
    list_dirs = []
    self.ftp.retrlines("LIST", list_dirs.append)

    index = 0
    while index < len(list_dirs):
      list_dirs[index] = list_dirs[index].split()
      list_dirs[index] = list_dirs[index][-1], list_dirs[index][0][0]
      if list_dirs[index][0] in [".", ".."]:
        del list_dirs[index]
        index -= 1
      index += 1

    return list_dirs

  def download_from(self, start_dir=None, local_path=path_local, depth = 0):
    """ Загружает все файлы и директории с сервера на локальный компьютер """
    if start_dir != None: self.ftp.cwd(start_dir)
    list_dirs = self._download_lines()
    #for i in list_dirs: print i
    #print ""
    for name_dir in list_dirs:
      print "  "*depth + name_dir[0], name_dir[1]
      if name_dir[1] == "d":
        if not os.path.exists(local_path + "/" + name_dir[0]):
          os.mkdir(local_path + "/" + name_dir[0])
        depth = self.download_from(name_dir[0], local_path+"/"+name_dir[0]+"/", depth+1)
      elif name_dir[1] == "-":
        self._download_file(local_path, name_dir[0])
    if start_dir != None: self.ftp.cwd("..")
    return depth - 1

aftp = adminFTP(server, login, password)
aftp.download_from()


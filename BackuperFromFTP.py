# -*- coding: utf-8 -*-
# 2015.01.08    2015.01.16
import ftplib, os

""" Чтобы удалить файл или директорию, необходимо сначала удалить файл или
    директорию на серверне, а затем на компьютере. Иначе - файл будет копироваться
    на сервер и удаления не произойдёт.
"""

path_local = "hosting" # Data will copy to this directory
if not os.path.exists(path_local): os.mkdir(path_local)
path_temp = "temp" # Data will copy to this directory
if not os.path.exists(path_temp): os.mkdir(path_temp)

server = "0.0.0.0"
login = "login"
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
      list_dirs[index] = list_dirs[index].split(None, 8)
      list_dirs[index] = list_dirs[index][-1], list_dirs[index][0][0]
      if list_dirs[index][0] in [".", ".."]:
        del list_dirs[index]
        index -= 1
      index += 1

    return list_dirs

  def make_backup(self, start_dir=None, local_path=path_local, depth = 0):
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
        depth = self.make_backup(name_dir[0], local_path+"/"+name_dir[0]+"/", depth+1)
      elif name_dir[1] == "-":
        self._download_file(local_path, name_dir[0])
    if start_dir != None: self.ftp.cwd("..")
    return depth - 1

  def _eq_hash(self, local_path, name):
    """ Сравнивает хэш-суммы файла на локальном компьютере и сервере """
    f = open(local_path+"/"+name, "rb")
    local_hash = hash(f.read())
    f.close()

    f = open(path_temp+"/"+name, "wb")
    self.ftp.retrbinary("RETR "+name, f.write)
    f.close()
    f = open(path_temp+"/"+name, "rb")
    ftp_hash = hash(f.read())
    f.close()
    os.remove(path_temp+"/"+name)

    #print local_hash == ftp_hash, local_path+"/"+name
    if local_hash == ftp_hash: return True
    else: return False

  def _copy2ftp(self, local_path, name, mode='rewrite'):
    with open(local_path+"/"+name, "rb") as f:
      if mode == 'rewrite': self.ftp.delete(name)
      self.ftp.storbinary("STOR "+name, f)
      f.close()

  def _is_exists(self, local_name):
    """ Если файл существует на сервере, то вернёт его тип: d, l ,-.
        Иначе - None.
    """
    lines = self._download_lines()
    for server_name, server_typ in lines:
      if server_name == local_name: return server_typ
    return None

  def upload_modified(self, start_dir=None, local_path=path_local):
    """ Выгружает на сервер файлы, которые были модифицированы """
    if start_dir != None: self.ftp.cwd(start_dir)
    list_dirs = os.listdir(local_path)
    for local_name in list_dirs:
      if os.path.isdir(local_path+"/"+local_name):
        # если директории не существует на сервере, то создать её
        if self._is_exists(local_name) != "d":
          self.ftp.mkd(local_name)
          print "maked dir:", local_path+"/"+local_name
        self.upload_modified(local_name, local_path+"/"+local_name)
      elif os.path.isfile(local_path+"/"+local_name):
        # если файла не существует на сервере, то создать его
        if self._is_exists(local_name) != "-":
          self._copy2ftp(local_path, local_name, 'create')
          print "created file:", local_path+"/"+local_name
          continue
        # если содержимое файла отличное от сервера, то скопировать его
        eq = self._eq_hash(local_path, local_name)
        if eq == False:
          print "copied file:", local_path+"/"+local_name
          self._copy2ftp(local_path, local_name)
    if start_dir != None: self.ftp.cwd("..")


if __name__ == '__main__':
  import Tkinter as tkinter, time

  args = ("www/just-idea.ru", path_local+"/www/just-idea.ru")
  
  aftp = adminFTP(server, login, password)
  aftp.make_backup(*args)
  aftp.ftp.cwd("..")
  print ""
  while 1:
    aftp.upload_modified(*args)
    aftp.ftp.cwd("..")
    time.sleep(0.1)
  print "End :))"

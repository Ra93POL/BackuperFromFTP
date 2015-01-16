# BackuperFromFTP
The code copy all data from ftp to local directory.

 main class:
#aftp = adminFTP(server, login, password)
 make the backup of FTP. The tree of files and dirs will  save to local computer.
#aftp.make_backup()
 This cycle check all files and dirs on local computer and try to compare them with FTP's files and dirs.
 If a local file is not equal, it copies to the FTP.
 If a local file or dir doesn't exists on FTP, it creates.
#while 1:
#    aftp.upload_modified()
#    aftp.ftp.cwd("..")
#    time.sleep(0.1)

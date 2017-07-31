# -*- coding: utf-8 -*-
import ftplib
import logging
import os
from ftplib import FTP, socket

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
_logger.addHandler(ch)


BUFFER_SIZE = 4096
class HclFtpLib(object):

    def __init__(self, ip_addr='192.168.2.6', port='21', debug_lv=0, login_name='pdm', pwd='robotime', op_path='/home/pdm/', direct_connect=True):
        self.ftp = FTP()
        self.ip_addr = ip_addr
        self.port = port
        self.debug_lv = debug_lv
        self.login_name = login_name
        self.pwd = pwd
        self.op_path = op_path

        if direct_connect:
            self.connect()

    def connect(self):
        # 打开调试级别2，显示详细信息;0为关闭调试信息
        self.ftp.set_debuglevel(self.debug_lv)

        # 连接
        try:
            self.ftp.connect(self.ip_addr, self.port)
        except socket.error, e:
            _logger.error((u"%s addr:%s, port:%s"% (e, self.ip_addr, self.ip_addr)))
            return
        # 登录
        try:
            self.ftp.login(self.login_name, self.pwd)
            # 显示ftp服务器欢迎信息
            _logger.info(self.ftp.getwelcome())
            # 切换目录
            self.ftp.cwd(self.op_path)

        except ftplib.error_perm, e:
            _logger.error((u"%s login:%s, pwd:%s, path:%s" % (e, self.login_name, self.pwd, self.op_path)))
            return

    def upload_file(self, local_file, remote_file, callback=None):
        if not os.path.isfile(local_file):
            return False
        file_handle = open(local_file, "rb")
        if os.path.isfile(local_file):
            new_path = os.path.dirname(remote_file)
            file_name = os.path.basename(remote_file)
            self.create_dir(new_path)
            if file_name in self.ftp.nlst():
                self.ftp.delete(file_name)
            # self.ftp.cwd(new_path)
        else:
            raise "path error"
        self.ftp.storbinary("STOR " + file_name, file_handle, BUFFER_SIZE, callback=callback)
        file_handle.close()
        return True

    def download_file(self, local_file, remote_file):
        file_handler = open(local_file, 'wb')
        self.ftp.retrbinary("RETR " + remote_file, file_handler.write)
        file_handler.close()
        return True

    def delete_file(self, remote_file):
        self.ftp.delete(remote_file)

    def _split_path(self, path):
        path_list = []
        a = path
        while a != '' and a != '/':
            s = os.path.split(a)
            path_list.append(s[1])
            a = s[0]

        path_list.reverse()
        return path_list

    def create_dir(self, my_path):
        paths = self._split_path(my_path)
        for path in paths:
            try:
                next_path = self.ftp.mkd(path)
                self.ftp.cwd(next_path)
            except ftplib.error_perm:
                self.ftp.cwd(self.ftp.pwd() + '/' + path)
                continue


# ftp = HclFtpLib('192.168.2.6', '21', op_path='/home/pdm/', login_name='pdm', pwd='robotime')
# ftp.download_file(remote_file='pdm/sys/a001.txt', local_file='/Users/charynbryant/Desktop/b.txt')
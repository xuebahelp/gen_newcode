import os
import sys
import uuid

import qrcode
import requests
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow
from pyzbar.pyzbar import decode


# from PyInstaller.utils.hooks import collect_data_files

# datas = collect_data_files('PyQt5.Qt')
# datas += [('main.ui','main.ui')]

def get_qrcode_data(fdir, fn, address):
    upload_url = 'http://xuebahelp.club:8002/upload_img/'
    files = {
        'img': open(os.path.join(fdir, fn), 'rb'),

    }
    upload_data = {
        'app': 'gen_newcode',
        'mac_address': address
    }
    upload_res = requests.post(upload_url, files=files, data=upload_data)
    img_url = upload_res.json()['img_url']
    # print('upload_res',upload_res.text)

    url = 'https://qrdetector-api.cli.im/v1/detect_binary'
    data = {
        'remove_background': 1,
        'image_path': img_url
    }
    res = requests.post(url, data=data)
    return res.json()['data']['qrcode_content']


class WorkerThread(QThread):
    update_message = pyqtSignal(str)

    def __init__(self, dir, des_dir, address):
        super().__init__()
        self.dir = dir
        self.des_dir = des_dir
        self.address = address

    def run(self):
        for tfile in os.listdir(self.dir):
            file = os.path.join(self.dir, tfile)
            if os.path.splitext(file)[-1].lower() not in ['.jpg', '.jpeg', '.png']:
                continue
            try:
                data = get_qrcode_data(self.dir, tfile, self.address)
            except Exception as e:
                self.update_message.emit(f'文件:{file}读取异常.\n')
                continue

            self.update_message.emit(f'文件:{file}正在生成二维码.\n')
            qr = qrcode.QRCode(version=1, box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image()
            img.save(os.path.join(self.des_dir, tfile))

        self.update_message.emit('所有图片文件生成完成.')


class MainWindow(QMainWindow):
    def get_macaddres(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return '-'.join(mac[i:i + 2] for i in range(0, 11, 2))

    def choosefile_clicked(self):
        self.dir = QFileDialog.getExistingDirectory(None, "请选择二维码文件夹", "")
        self.dir = self.dir.strip()
        self.message.insertPlainText('原始选择的文件夹为:' + self.dir + '\n')
        print('ExistingDirectory：', dir)
        if self.dir == '':  #
            return

    def desdir_clicked(self):
        self.des_dir = QFileDialog.getExistingDirectory(None, "请选择新生成的二维码的路径", "")
        self.des_dir = self.des_dir.strip()
        self.message.insertPlainText('新生成的二维码的路径为:' + self.des_dir + '\n')
        print('ExistingDirectory：', self.des_dir)
        if self.des_dir == '':  #
            return

    # def gen_binary_file(self,fdir, fn):
    #     qrcode = Image.open(os.path.join(fdir, fn))
    #     # qrcode.show()
    #     # 将图像转为灰度度
    #     gray_qrcode = qrcode.convert('L')
    #     # gray_qrcode.show()
    #
    #     # 将灰度图转为二值图
    #     binary_qrcode = gray_qrcode.point(lambda x: 255 if x < 200 else 0, '1')
    #     binary_qrcode.save(os.path.join(fdir,f'binary_{fn}'))
    #     return f'binary_{fn}'
    def gencode_clicked(self):
        '''判断是否macaddress授权率start'''
        address = self.get_macaddres()
        url = f'http://xuebahelp.club:8002/get_auth_address?address={address}'
        try:
            res = requests.get(url=url)
        except Exception as e:
            QMessageBox.critical(self, '提示', '请联网使用不要开vpn!', QMessageBox.No)
            self.message.insertPlainText('请联网使用不要开vpn!\n')
            return
        if res.json()['has_auth'] == False:
            QMessageBox.critical(self, '提示', '请联系开发者easinlee 对您的机器进行授权后使用!', QMessageBox.No)
            self.message.insertPlainText('请联系开发者easinlee 对您的机器进行授权后使用!\n')
            return

        '''判断是否macaddress授权率end'''
        if self.dir == '' or self.des_dir == '':
            QMessageBox.critical(self, '提示', '你没有原始二维码路径或者新二维码路径!!', QMessageBox.No)
            return

        self.thread = WorkerThread(self.dir, self.des_dir, address)
        self.thread.update_message.connect(self.message.insertPlainText)
        self.thread.start()
        #
        # for tfile in os.listdir(self.dir):
        #
        #     file = os.path.join(self.dir, tfile)
        #     if os.path.splitext(file)[-1].lower() not in ['.jpg', '.jpeg', '.png']:
        #         continue
        #     try:
        #         # binary_file = self.gen_binary_file(self.dir,tfile)
        #         data = self.get_qrcode_data(self.dir,tfile,address)
        #     except:
        #         self.message.insertPlainText(f'文件:{file}读取异常.\n')
        #         # data = decode(Image.open(file)).decode('utf-8')
        #         continue
        #     self.message.insertPlainText(f'文件:{file}正在生成二维码.\n')
        #     # data = decode(Image.open(file))[0][0].decode("utf-8")
        #     qr = qrcode.QRCode(version=1, box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_L)
        #     qr.add_data(data)
        #     qr.make(fit=True)
        #     img = qr.make_image()
        #     # img.show()
        #     # if not os.path.exists(os.path.join(self.dir,'GEN')):
        #     #     os.mkdir(os.path.join(self.dir,'GEN'))
        #     img.save(os.path.join(self.des_dir,tfile))
        # self.message.insertPlainText(f'所有图片文件生成完成.')

    def __init__(self):
        super().__init__()
        self.lui = uic.loadUi("main.ui", self)
        self.macaddress.setText(self.macaddress.text() + self.get_macaddres())
        self.choosefile.clicked.connect(self.choosefile_clicked)
        self.gencode.clicked.connect(self.gencode_clicked)
        self.desdir.clicked.connect(self.desdir_clicked)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(App.exec_())

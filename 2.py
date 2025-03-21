import cv2
from pyzbar.pyzbar import decode


def detect_qrcode(image_path):
    # 读取图片
    image = cv2.imread(image_path)
    # 转换为灰度图
    # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 解码图像中的二维码
    decoded_objects = decode(image)
    print('decoded objects:', decoded_objects)

    for obj in decoded_objects:
        # 提取二维码的位置
        x, y, w, h = obj.rect
        # 画出二维码的矩形框
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # 二维码的数据
        print("二维码内容：", obj.data.decode('utf-8'))

    # 显示图像
    cv2.imshow('Image with QR Code', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 使用函数检测图片中的二维码
detect_qrcode('0c6d2b7409409d0e4a058979827cb49.jpg')
import requests

def get_qrcode_data(fdir,fn):

    upload_url = 'http://xuebahelp.club:8002/upload_img/'
    files = {
        'img':open('SOURCE/f63d4a2dbcddbf3052abf4e219ef264.jpg','rb')
    }
    upload_data = {
        'app':'gen_newcode'
    }
    upload_res = requests.post(upload_url,files=files,data=upload_data)
    img_url = upload_res.json()['img_url']
    # print('upload_res',upload_res.text)


    url = 'https://qrdetector-api.cli.im/v1/detect_binary'
    data = {
        'remove_background':1,
        'image_path':img_url
    }
    res = requests.post(url, data=data)
    return res.json()['data']['qrcode_content']
if __name__ == '__main__':
    R = get_qrcode_data(None,None)
    print(R)


from flask import Flask, render_template,request,jsonify

# coding=utf-8
app = Flask(__name__)
# 文字识别程序开始
# coding=utf-8

import sys
import json
import base64


# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'p2xF1Phgalo5TA2lbNDLftOs'

SECRET_KEY = 'i3Pvw9QdgRcLoy8o2zYN8zY56193psTM'


OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"


"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
def myrequest(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)
#文字识别结束

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')




@app.route('/proxy',methods=["POST","GET"])
def proxy():  # put application's code here
    if request.method == "GET":
        comment = request.args.get("content")
        # comment = request.values.get("content")
    if request.method == "POST":
        if request.content_type.startswith('application/json'):
            # comment = request.get_json()["content"]
            comment = request.json.get('content')
        elif request.content_type.startswith('multipart/form-data'):
            comment = request.form.get('content')
        else:
            comment = request.values.get("content")

    # 获取access token
    token = fetch_token()
    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token

    text = ""

    # 读取测试图片
    # file_content = read_file('./test.png')
    # 直接获取所要的base64编码然后进行识别文字
    # 调用文字识别服务
    result = myrequest(image_url, urlencode({'image':comment}))

    # 解析返回结果
    result_json = json.loads(result)
    for words_result in result_json["words_result"]:
        text = text + words_result["words"]

    return jsonify({"code": 0, "msg": "state:200","data":text})


if __name__ == '__main__':
    app.run()


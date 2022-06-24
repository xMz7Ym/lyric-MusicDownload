import requests
import re
import time
import json
import base64
import binascii
import random
import string
from urllib import parse
from Crypto.Cipher import AES
import os
# 根据给的歌单ID给出歌单的歌曲ID 因网易云更新，web端只能获取前10首，ε=(´ο｀*)))唉 想当年能全看.....
def _MusicList(id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.89 "
                      "Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
    }

    url = "https://music.163.com/playlist?id=" + str(id)
    rs = requests.get(url=url ,headers=headers)
    _Id = re.findall("/song\?id=(\d*)\"",rs.text)
    _Name = []
    _Name =re.findall("(?:a href=\")/song\?id=(?:\d+)\">([^<].*?)[<]",rs.text)
    return _Id,_Name


# 根据ID与Name 下载歌曲
def _MusicDownload(id, name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.89 "
                      "Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
    }

    url = f"http://music.163.com/song/media/outer/url?id={id}.mp3"
    r1 = requests.get(url=url, headers=headers).content
    with open(f'./Download/{name}.mp3', 'wb') as f:
        f.write(r1)
        print(f"音乐{name}下载成功！")
        time.sleep(3)


# 根据ID转换名字(与客户端下载出来的命名相同)
def _IDto_Name(id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.89 "
                      "Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
    }

    url = "https://y.music.163.com/m/song?id=" + str(id)
    r2 = requests.get(url=url, headers=headers)
    _Name_1 = re.findall("\"description\": \"歌曲名《(.*)由", r2.text)[0]
    _Name_2 =re.findall("由(.+)演唱", r2.text)[0]
    try:
        _Name =  _Name_2 + '-' + _Name_1[:-2]
        time.sleep(1)
        return _Name
    except:
        return "error"



# 歌词下载模块
def _LyricDownload(id,name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.89 "
                      "Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
    }

    url = "https://music.163.com/api/song/media?id=" + str(id)
    r3 = requests.get(url=url, headers=headers).text
    r = json.loads(r3)
    Yric = str(r["lyric"])
    with open(f'./Download/{name}.lrc', 'w') as f:
        f.write(Yric)
        time.sleep(0.1)
# 一个专属的模块
def _LyricDownload2(id,name,LU):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.89 "
                      "Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
    }

    url = "https://music.163.com/api/song/media?id=" + str(id)
    r3 = requests.get(url=url, headers=headers).text
    r = json.loads(r3)
    Yric = str(r["lyric"])

    with open(f'{LU}/{name}.lrc', 'w') as f:
        f.write(Yric)
        time.sleep(0.1)

# 从a-z,A-Z,0-9中随机获取16位字符
def get_random():
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return random_str


# AES加密要求加密的文本长度必须是16的倍数，密钥的长度固定只能为16,24或32位，因此我们采取统一转换为16位的方法
def len_change(text):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    text = text.encode("utf-8")
    return text


# AES加密方法
def aes(text, key):
    # 首先对加密的内容进行位数补全，然后使用 CBC 模式进行加密
    iv = b'0102030405060708'
    text = len_change(text)
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(text)
    encrypt = base64.b64encode(encrypted).decode()
    return encrypt


# js中的 b 函数，调用两次 AES 加密
# text 为需要加密的文本， str 为生成的16位随机数
def b(text, str):
    first_data = aes(text, '0CoJUm6Qyw8W8jud')
    second_data = aes(first_data, str)
    return second_data


def c(text):
    e = '010001'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    text = text[::-1]
    result = pow(int(binascii.hexlify(text.encode()), 16), int(e, 16), int(f, 16))
    return format(result, 'x').zfill(131)


# 获取最终的参数 params 和 encSecKey 的方法
def get_final_param(text, str):
    params = b(text, str)
    encSecKey = c(str)
    return {'params': params, 'encSecKey': encSecKey}


# 通过参数获取搜索歌曲的列表
def get_music_list(params, encSecKey):
    url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="

    payload = 'params=' + parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
    headers = {
        'authority': 'music.163.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://music.163.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://music.163.com/search/',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text



def _NameTo_ID(song_name):
    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])
    music_info = json.loads(song_list)['result']['songs']
    for i in range(len(music_info)):
        if music_info[i]["ar"][0]["name"] in song_name:
            return music_info[i]["id"]
    else :
        return music_info[1]["id"]

def _nametomusic_down(song_name):
    d = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": song_name, "type": "1", "offset": "0",
         "total": "true", "limit": "30", "csrf_token": ""}
    d = json.dumps(d)
    random_param = get_random()
    param = get_final_param(d, random_param)
    song_list = get_music_list(param['params'], param['encSecKey'])
    music_info = json.loads(song_list)['result']['songs']
    for i in range(min(len(music_info),10)):
        b = music_info[i]["ar"][0]["name"]
        c = music_info[i]["name"]
        print(f"{i+1}.{c}-{b}")
    print("请输入您想下载的版本(输入序号)：")
    try:
        a = int(input())
    except:
        print("发生不可预料的错误，请检查您是否输入的为数字")
        print("请输入您想下载的版本(输入序号)：")
        a = int(input())
    d = music_info[a-1]["ar"][0]["name"]
    f = music_info[a-1]["name"]
    _LyricDownload(music_info[a-1]["id"],f"{d}-{f}")
    _MusicDownload(music_info[a-1]["id"],f"{d}-{f}")


# 以下为功能的实现： 1.根据歌单下载所有歌单的所有歌曲AND歌曲
def _DownList():
    List_ID = input("大于10首的之后web有限制的下载不了建议多创建几个歌单或者使用别的下载方法~\n请输入您需要下载的歌单ID（一定要是ID)：")
    print(f"正在获取ID为{List_ID}的歌曲")
    ID, Name = _MusicList(List_ID)
    for i in range(len(ID)):
        print(F"正在下载{Name[i]}并写入歌曲（{i+1}/{len(ID)}）", end='\r')
        try:
            _LyricDownload(ID[i], Name[i])
        except:
            print(f"歌曲{Name[i]}歌词下载失败,稍后请重试一下叭~")
        try:
            _MusicDownload(ID[i], Name[i])
        except:
            print(f"因不可控原因{Name[i]}歌曲下载失败，可以尝试单个ID下载哟~")

# _DownList() 测试成功
# 2.根据文件夹中的歌曲下载对应的歌词
def _M_LRC():
    os.makedirs('./music', exist_ok=True)
    print("请确保您想下载的歌词的歌曲在本文件夹的music中~\n当然您如果想导入自己的文件夹目录也可以")
    LU = input("若用本文件的music文件请输入Y，若不想，请输入您需要下载歌词的文件夹（你自己想下载的音乐文件必须在这个文件夹里面）")
    if LU == "Y":
        LU = "./music"
    try:
        for i in os.listdir(rf'{LU}'):
            try:
                print(f"正在下载<{i[:-4]}>歌词")
                _LyricDownload2(_NameTo_ID(i[:-4]),i[:-4],LU)
                print(f"歌曲{i[:-4]}下载成功")
            except:
                print(f"因不可控原因{i[:-4]}歌曲下载失败，可以尝试单个ID下载哟~")
    except:
        print("文件夹目录提供错误")

# _M_LRC()  测试成功

# 3.根据单个ID下载歌曲和歌词
def _Downmusic():
    try:
        a = int(input("请输入您要下载个歌曲ID"))
    except:
        print("请输入纯数字,请再次输入")
        a = int(input("请输入您要下载个歌曲ID"))
    try:
        _MusicDownload(a,_IDto_Name(a))
        _LyricDownload(a,_IDto_Name(a))
    except:
        print("请仔细检查您输入的歌曲ID是否存在，已退出本系统")
# _Downmusic() 测试成功

#4.根据歌曲名称下载歌曲
def _NameTomusic():
    a = input("请输入您要下载的名字，搜索 歌名和作家名 成功搜到您想要的歌曲成功率更高哦~")
    _nametomusic_down(a)

#_NameTomusic() 测试成功
print("本软件提供网易云音乐下载，歌词自动补全，下载歌单，下载歌曲等服务。")
a = input("本软件仅供学习交流，如作他用所承受的法律责任一概与作者无关,下载者务必24小时内删除本软件\n您是否同意以上观点（Y/N）")

if a not in ["y","Y","YES","yes","Yes","YEs","Yes"]:
    print("已退出本系统,保持本页面10s自动删除本文件")
    time.sleep(10)
    os.remove(__file__)
    time.sleep(2)

s = '''
.----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  ____  ____  | || | ____    ____ | || |   ________   | || |   _______    | || |  ____  ____  | || | ____    ____ | |
| | |_  _||_  _| | || ||_   \  /   _|| || |  |  __   _|  | || |  |  ___  |   | || | |_  _||_  _| | || ||_   \  /   _|| |
| |   \ \  / /   | || |  |   \/   |  | || |  |_/  / /    | || |  |_/  / /    | || |   \ \  / /   | || |  |   \/   |  | |
| |    > `' <    | || |  | |\  /| |  | || |     .'.' _   | || |      / /     | || |    \ \/ /    | || |  | |\  /| |  | |
| |  _/ /'`\ \_  | || | _| |_\/_| |_ | || |   _/ /__/ |  | || |     / /      | || |    _|  |_    | || | _| |_\/_| |_ | |
| | |____||____| | || ||_____||_____|| || |  |________|  | || |    /_/       | || |   |______|   | || ||_____||_____|| |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
'----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'
'''
print(s)
print("如果喜欢本系统可以去 https://github.com/xMz7Ym/lyric-MusicDownload 点个start吗？？感谢不尽~")
print("请确保电脑是否联网，是否已经生成Download文件夹。如果发生报错，闪退请上上述地址下载源码版本进行下载~~~（编译BUG多）")
os.makedirs('./Download', exist_ok=True)
while a in ["y","Y","YES","yes","Yes","YEs","Yes"]:
    print("本系统提供三种下载方式,请输入1,2,3来选择自己想要的模式，"
          "\n1.按照歌单ID下载歌曲和歌词,在网易云web端的网址栏查看，就是在歌单页面中最后那一串数字"
          "\n2.按照文件夹的已经存在的歌曲进行下载歌词"
          "\n3.按照歌曲ID下载歌曲和歌词,在网易云web端的网址栏查看，就是在歌曲页面中最后那一串数字"
          "\n4.输入歌曲名字（或者一句歌词），根据检索提供您可能想下载的歌曲名字"
          "\n5.退出本系统\n")
    YouSelect = input("您想进行哪种服务~？\n")
    if YouSelect == "1":
        _DownList()
        cas =input("下载进程完成,是否要继续使用？(Y/N)")
        if cas in ["y","Y","YES","yes","Yes","YEs","Yes"]:
            continue
        else:
            break
    elif YouSelect == "2":
        _M_LRC()
        cas = input("下载进程完成,是否要继续使用？(Y/N)")
        if cas in ["y", "Y", "YES", "yes", "Yes", "YEs", "Yes"]:
            continue
        else:
            break
    elif YouSelect == "3":
        _Downmusic()
        cas = input("下载进程完成,是否要继续使用？(Y/N)")
        if cas in ["y", "Y", "YES", "yes", "Yes", "YEs", "Yes"]:
            continue
        else:
            break
    elif YouSelect == "4":
        try:
            _NameTomusic()
        except:
            print("请不要乱输入名字，不然我就报错了哦 ╭(╯^╰)╮")
            _NameTomusic()

    elif YouSelect == "5":
        print("已退出，感谢使用")
        time.sleep(3)
        break
    else:
        print("输入错误请在两秒后重新输入")
        time.sleep(2)

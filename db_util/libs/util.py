#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'Silva'

import re, sys, time, datetime, locale, traceback, subprocess, os, signal, smtplib, urllib, math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

try:
    import json
except ImportError:
    import simplejson as json
from urllib.parse import urlparse, urlunparse, urljoin, urlsplit
import hashlib
import base64
import six

'''
工具函数，封装常用操作
'''


def date(timestamp=None, format='%Y-%m-%d %H:%M'):
    '''
    时间戳格式化转换日期

    @params
            timestamp ：时间戳，如果为空则显示当前时间
            format : 时间格式

        @return
            返回格式化的时间，默认为 2014-07-30 09:50 这样的形式
        '''
    if timestamp is None:
        timestamp = int(time.time())
    if not isinstance(timestamp, int):
        timestamp = int(timestamp)
    d = datetime.datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def strtotime(string, format="%Y-%m-%d %H:%M", debug=False):
    '''
    字符串转时间戳

    @params
        string : 需要转换成时间戳的字符串，需要与后面的format对应
        format : 时间格式

    @return
        返回对应的10位int数值的时间戳
    '''
    try:
        return int(time.mktime(time.strptime(string, format)))
    except Exception as e:
        if debug:
            print(e)
        return 0


def cleartext(text, *args, **kwargs):
    '''
    过滤特殊字符，获取纯文本字符串，默认过滤换行符 \n、\r、\t 以及多余的空格

    @params
        args : 为添加需要为过滤的字符

    @return
        返回过滤后的字符串，如果为非字符串类型则会被转换成字符串再过滤
    '''
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r", '')
    text = text.replace("\n", '')
    text = text.replace("\t", '')
    text = text.rstrip()
    text = text.lstrip()
    for arg in args:
        text = text.replace(arg, '')
    return text


def addslashes(text):
    '''
    使用反斜线转义字符串中的字符

    @params
        text : 需要转义的字符串

    @return
        返回转义的字符串
    '''
    if not isinstance(text, str):
        text = str(text)
    l = ["\\", '"', "'", "\0"]
    for i in l:
        if i in text:
            text = text.replace(i, '\\' + i)
    return text


_number_regex = None


def number_format(num, places=5, index=0, calc=1, smart=False):
    '''
    格式化数值

    @params
        num     可为任意数值，如果为 'kk12.3dsd' 则实际num将为 12.3; asas126.36.356sa => 126.36
        places  小数点后位数，默认为5，如果为0或者负数则返回整数值
        index   索引值，即匹配的第几个数值 - 1,除非你清楚匹配的索引值，否则建议默认
        smart   智能匹配，如果为True'时即当index无法匹配时，智能匹配至与index最近的一个，
                选择False当不匹配时会抛出异常；选择None则会匹配最小的情况
    @return
        格式化的float值或者int值
    '''
    global _number_regex
    if not isinstance(num, (int, float)):
        if _number_regex is None:
            _number_regex = re.compile('(\-{0,1}\d*\.{0,1}\d+)')
        if isinstance(num, str):
            num = num.encode('utf-8')
        num = str(num).replace(',', '')
        match = _number_regex.findall(num)
        try:
            num = float(match[index]) if match else 0.0
        except Exception as e:
            if smart is None:
                num = match[0]
            elif smart:
                num = float(match[len(match) - 1])
            else:
                raise Exception(str(e))
    if places > 0:
        if calc == 2:
            return locale.format("%.*f", (places, float(num)), True)
        else:
            return float(locale.format("%.*f", (places, float(num)), True))
    else:
        return int(num)


def traceback_info(e=None, return_all=False):
    '''
    获取traceback信息
    '''
    try:
        _info = sys.exc_info()
        if return_all:
            etb_list = traceback.extract_tb(_info[2])
            _trace_info = "Traceback (most recent call last):\n"
            for etb in etb_list:
                _trace_info += "  File: \"%s\" ,line %s, in %s\n      %s\n" % (etb[0], etb[1], etb[2], etb[3])
            _trace_info += '%s : %s' % (_info[1].__class__.__name__, _info[1])
            return _trace_info
        else:
            etb = traceback.extract_tb(_info[2])[0]
            return '<traceback: %s ,line %s, %s ; message: %s>' % (etb[0], etb[1], etb[3], _info[1])
    except Exception:
        return str(e) if e else None


def open_subprocess(cmd, obstruct=True):
    '''
    启动一个新的子进程

    @param cmd      命令
    @param obstruct 阻塞式，默认为true，阻塞式将重定向子进程的输出信息至缓冲区（如希望子进程后台运行不显示信息）

    '''
    if not obstruct:
        if os.name == 'nt':
            process = subprocess.Popen(cmd, shell=True)
        else:
            process = subprocess.Popen(cmd, shell=True)
    else:
        if os.name == 'nt':
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, preexec_fn=os.setsid,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def kill_subprocess(process):
    '''
    结束一子进程
    '''
    if process is None:
        return
    try:
        if os.name == 'nt':
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait()
    except Exception:
        pass


def filemtime(path, root_path=None):
    '''
    取得文件修改的时间
    '''
    FILE_PATH = os.path.join(root_path, path) if root_path else path
    return os.stat(FILE_PATH).st_mtime


def filectime(path, root_path=None):
    '''
    取得文件创建的时间
    '''
    FILE_PATH = os.path.join(root_path, path) if root_path else path
    return os.stat(FILE_PATH).st_ctime


def sendmail(to_email, subject=None, body=None, attachment=None, **kwargs):
    '''
    发送邮件

    @param to_email     发送对方邮件，可为列表、字符串、元祖
    @param subject      邮件主题，默认为 system@hqchip.com
    @param body         邮件内容
    @param attachment   附件
        支持直接字符串路径 '/var/usr/file' 或者多个附件 ['/var/usr/file1','/var/usr/file2']
        及重命名式的 ('附件','/var/usr/file') 或者 [('附件1','/var/usr/file1'),('附件2','/var/usr/file2')]
        抑或 ('附件1',open('/var/usr/file1','rb'))
    @param kwargs       邮件配置
        SMTP_HOST       smtp服务器地址，域名(不带http)或者ip地址
        SMTP_PORT       smtp服务器端口，默认为25
        SMTP_USER       smtp登陆账号
        SMTP_PASSWORD   smtp登陆密码
        SMTP_FROM       smtp发信来源，部分邮箱检测较为严格，如果与SMTP_USER不一致可能被判为垃圾邮件或者拒绝接收
        SMTP_DEBUG      smtp DEBUG默认为True,True将打印debug信息

    @return 成功返回 True 失败返回 异常信息
    '''
    if not to_email:
        return
    try:
        kwargs.update(setting.EMAIL)
    except Exception:
        pass
    if attachment is None:
        attachment = []
    if body is None:
        body = ''

    if not isinstance(to_email, (list, tuple)):
        to_email = [to_email]

    # 创建一个带附件的实例
    msg = MIMEMultipart()
    # 添加邮件头部信息
    msg['From'] = kwargs.get('SMTP_FROM', 'system@hqchip.com')
    msg['To'] = ';'.join(to_email)
    msg['Subject'] = 'FROM : %s' % kwargs.get('SMTP_FROM', 'system@hqchip.com') if subject is None else subject
    msg['Date'] = time.ctime(time.time())
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    # 处理附件
    if not isinstance(attachment, list):
        attachment = [attachment]

    for attach in attachment:
        fp = None
        if isinstance(attach, (tuple, list)):
            if attach[1].__class__.__name__ == 'file':
                fp = attach[1]
            elif os.path.exists(attach[1]):
                fp = open(attach[1], 'rb')
            fn = attach[0]
        elif os.path.exists(attach):
            fn = os.path.basename(attach)
            fp = open(attach, 'rb')
        if not fp:
            continue
        att = MIMEText(fp.read(), 'base64', 'utf-8')
        fp.close()
        att["Content-Type"] = 'application/octet-stream'
        if not isinstance(fn, str):
            fn = str(fn).decode('utf-8')
        att.add_header('content-disposition', 'attachment', filename=fn.encode('gbk'))
        msg.attach(att)

    try:
        smtp = smtplib.SMTP()
        if not kwargs.get('SMTP_EXCEPT_RETURN', False):
            smtp.set_debuglevel(kwargs.get('SMTP_DEBUG', False))
        smtp.connect(kwargs.get('SMTP_HOST', None), kwargs.get('SMTP_PORT', 25))
        smtp.login(kwargs.get('SMTP_USER', None), kwargs.get('SMTP_PASSWORD', None))
        smtp.sendmail(kwargs.get('SMTP_FROM', 'system@hqchip.com'), to_email, msg.as_string())
        smtp.close()

        return True
    except Exception as e:
        if kwargs.get('SMTP_DEBUG', False):
            logging.exception('STATUS:215 ; INFO:%s' % traceback_info(e))
        if kwargs.get('SMTP_EXCEPT_RETURN', False):
            return str(e)
        return False


def file(name='', value='', path='', root_path=None, _cache={}):
    '''
    快速存取文件内容
    '''
    if not name:
        return None
    if not root_path:
        root_path = setting.APP_ROOT
    filepath = os.path.join(root_path, 'data', path, name)
    if value != '':
        if value is None:
            try:
                os.unlink(filepath)
                del _cache[name]
                return True
            except Exception:
                return False
        else:
            dirpath = os.path.dirname(filepath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, mode=0o777)
            _cache[name] = value
            fp = open(filepath, 'w+')
            fp.write(json.dumps(value))
            fp.close()
            return True

    if name in _cache:
        return _cache[name]

    if os.path.isfile(filepath):
        fp = open(filepath, 'r+')
        try:
            value = json.loads(fp.read())
        except ValueError:
            value = None
        fp.close()
        if value:
            _cache[name] = value
    else:
        value = None
    return value


def urlencode(s):
    return urllib.parse.quote_plus(s)


def urldecode(s):
    return urllib.parse.unquote_plus(s)


def parse_str(qs):
    '''
    解析字符串
    >例如 qs => http://xxx.com?m[]=1&m[]=2&action=search&id=11 解析结果为 {'m':['1','2'],'action':'search','id':'11'}
    '''
    qs = qs.split('?')[-1]
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        if not name_value:
            continue
        nv = name_value.split('=', 1)
        if len(nv[1]):
            name = urldecode(nv[0])
            value = urldecode(nv[1])
            r.append((name, value))
    str_dict = {}
    for name, value in r:
        if name in str_dict:
            str_dict[name].append(value)
        elif name[-2:] == '[]':
            name = name[:-2]
            if not name:
                continue
            str_dict[name] = [value]
        else:
            str_dict[name] = value
    return str_dict


_strip_regex = None
_smart_strip_regex = None


def strip_tags(html_str, allowable_tags=None, smart=True):
    '''
    去除html标签

    @param html_str         html字符串
    @param allowable_tags   允许的标签,可为字符串、列表、元祖
    @param smart            智能去除模式，部分html数据可能存在元素残缺的现象，可以使用智能去除模式，耗时相对长一些

    @return 返回去除html标签的数据
    '''
    global _strip_regex, _smart_strip_regex

    if not html_str:
        return
    if not isinstance(html_str, str):
        html_str = str(html_str)

    if allowable_tags:
        if isinstance(allowable_tags, (list, tuple)):
            allowable_tags = '|'.join(allowable_tags)
        if not isinstance(allowable_tags, str):
            raise Exception('Argument error')
        _regex = re.compile(r'<[/|\s]*(?!' + allowable_tags + ')([^<]*)>')
        return _regex.sub('', html_str)
    elif _strip_regex is None:
        _strip_regex = re.compile(r'<[^<]+>')

    if smart:
        html_str = _strip_regex.sub('', html_str)
        if _smart_strip_regex is None:
            _smart_strip_regex = re.compile(r'<[^<]+')
        if '>' not in html_str:
            return _smart_strip_regex.sub('', html_str)
    return _strip_regex.sub('', html_str)


def get_host(url):
    """
    对于给定的url，返回其协议 scheme，主机名 host和 端口 port，如果没有这些则会返回None

    示例：

        >>> get_host('http://google.com/mail/')
        ('http', 'google.com', None)
        >>> get_host('google.com:80')
        ('http', 'google.com', 80)
    """
    port = None
    scheme = 'http'
    if '://' in url:
        scheme, url = url.split('://', 1)
    if '/' in url:
        url, _path = url.split('/', 1)
    if '@' in url:
        _auth, url = url.split('@', 1)
    if ':' in url:
        url, port = url.split(':', 1)
        if not port.isdigit():
            raise Exception("Failed to parse: %s")
        port = int(port)
    return scheme, url, port


def get_local_ip(ifname='eth0'):
    '''
    获取本地ip地址
    :param ifname:      网卡名称，仅对unix or linux系统有效
    :return:
    '''
    import socket
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = '127.0.0.1'
        if os.name != 'nt':
            import fcntl, struct
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
    return ip


def md5(text):
    return hashlib.md5(text).hexdigest()


def base64_encode(text):
    return base64.b64encode(text)


def base64_decode(text):
    return base64.b64decode(text)


def price_format(price, money_type=0, size=4, calc=1):
    '''
    价格保留小数格式化
    2017年9月14日 价格计算由原来的四舍五入改为进一的方式
    如：0.0019 * 1.02 = 0.001938
    四舍五入方式：0.0019
    向前进一方式：0.0020
    :param price:
    :param money_type:
    :param size:
    :return:
    '''
    if isinstance(price, str):
        price = float(price)
    if calc == 2:
        price = price + 0.0000000001
    else:
        price = price + 4 / math.pow(10, size + 1) + 0.0000000001
    price = round(price, size)
    money_type = number_format(money_type, 0, calc=calc)
    if money_type > 0:
        pre = ''
        if money_type == 1:
            pre = '￥'
        elif money_type == 2:
            pre = '$'
        return '%s %s' % (pre, price)
    return price


def text_type(text):
    if isinstance(text, six.binary_type):
        return text.decode('utf-8')
    return six.text_type(text)


def binary_type(text):
    if isinstance(text, six.text_type):
        return text.encode('utf-8')
    return six.binary_type(text)


def u2b(text):
    return binary_type(text)


def intval(text):
    return number_format(text, 0)


def floatval(text):
    return number_format(text, 4)


def api_sign(secret, parameters, _type=1):
    """自定义签名方法
    @param secret: 签名需要的密钥
    @param parameters: 支持字典和string两种
    """
    secret = binary_type(secret)
    if hasattr(parameters, "items"):
        keys = parameters.keys()
        keys.sort()

        parameters = "%s%s%s" % (secret if _type != 2 else '',
                                 '&'.join('%s=%s' % (key, binary_type(parameters[key])) for key in keys
                                          if key not in ('sign',)), secret if _type != 2 else '')
        if _type == 2:
            parameters = '%s&sign=%s' % (parameters, secret)
    sign = hashlib.md5(parameters).hexdigest().upper()
    if _type == 2:
        sign = sign.lower()
    return sign
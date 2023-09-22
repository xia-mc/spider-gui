from http.client import *
from urllib import request
from concurrent.futures import ThreadPoolExecutor, Future

download_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)


def check_url(url: str) -> bool:
    """
    检查URL是否正确，使用urllib.request.urlopen()方法。
    :param url: 网页链接
    :return: 布尔类型
    """
    req = request.Request(url)
    try:
        request.urlopen(req)
        return True
    except IOError:
        ...
    except ValueError:
        ...
    return False


def get_html(url: str, encoding: str = "UTF-8") -> str:
    """
    获取网页源代码 (工作在静态页面上)
    :param url: 网页链接
    :param encoding: 输出的编码
    :return: 网页源代码
    """
    req: request.Request = request.Request(url)
    response: HTTPResponse = request.urlopen(req)
    html = response.read().decode(encoding)
    return html


def web_downloader(url: str, encoding: str = "UTF-8") -> Future:
    """
    在额外的线程下载网页。
    使用线程池方案获得结果，对于每个下载，最大线程数为1。
    :param url: 网页链接
    :param encoding: 编码
    :return: 这个运行中的任务future对象
    """
    global download_pool
    thr: Future = download_pool.submit(get_html, url, encoding)
    return thr

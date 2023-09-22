from web import *
import easygui as gui
import os
from concurrent.futures import ThreadPoolExecutor, Future


DEFAULT_TITLE = "爬虫工具"
DEFAULT_CHOICE_MSG = "选择一个选项"
DEFAULT_ENTER_MSG = "我们需要一些信息"
DEFAULT_WAIT_MSG = "正在执行操作\n这可能需要一些时间\n\n关闭窗口以取消操作"

waiting_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)  # 一个包含且仅包含 等待窗口 任务future的线程池，用于显式shutdown


def waiting_window(message: str = DEFAULT_WAIT_MSG, title: str = DEFAULT_TITLE) -> Future:
    """
    当程序在执行一个阻塞操作时，多线程显示一个等待页面。
    基于一个独立的线程池，以实现优雅的关闭等待窗口。
    :param message: 等待提示信息
    :param title: 等待窗口标题
    :return: 一个任务future，即等待窗口
    """
    global waiting_pool

    def window(msg: str, tle: str):
        gui.msgbox(msg, tle)

    thr: Future = waiting_pool.submit(window, message, title)
    return thr


def main_window():
    """
    程序主页面，展示功能列表。
    基于gui.choicebox()
    """
    MODULES = ["下载网页", "设定", "关于", "退出"]

    message = DEFAULT_CHOICE_MSG
    while True:  # 应用程序主循环
        user_input = gui.choicebox(
            msg=message,
            title=DEFAULT_TITLE,
            choices=MODULES
        )

        # 有效判定
        if user_input is None:
            return
        elif user_input not in MODULES:
            message = f"选项选择可能出现了问题。\n{DEFAULT_CHOICE_MSG}"
            continue

        # 选择功能判定
        if user_input == MODULES[0]:
            download_window()
        elif user_input == MODULES[1]:
            setting_window()
        elif user_input == MODULES[2]:
            about_window()
        elif user_input == MODULES[3]:
            return
        else:
            message = f"选项选择可能出现了问题。\n{DEFAULT_CHOICE_MSG}"
            continue


def download_window():
    """
    程序功能页面。下载网页。
    基于gui.multenterbox()
    """
    # url: str = ""
    # web_encoding: str = ""
    # file_encoding: str = ""
    # filedir: str = ""

    # 获取用户输入
    message = DEFAULT_ENTER_MSG
    while True:
        user_input = gui.multenterbox(
            msg=message,
            title=DEFAULT_TITLE,
            fields=["网址(完整URL)", "解析网页的编码", "写入文件的编码"],
            values=["http://", "UTF-8", "UTF-8"]
        )
        if user_input is None:  # 取消或关闭
            return
        elif check_url(user_input[0]) is False:  # 网址不可用
            message = "无效的网址"
        else:  # 可用的输入
            url = user_input[0]
            web_encoding = user_input[1]
            file_encoding = user_input[2]
            break

    # 保存目录
    filedir = gui.filesavebox(
        title="选择一个保存目录",
        default=f"{os.getcwd()}//网页存档.html",
        filetypes="*.html"
    )
    if filedir is None:
        return

    # 执行（最先进的一次）
    downloader: Future = web_downloader(url, web_encoding)  # 发布下载请求
    waiting_thr = waiting_window()  # 发布等待窗口，返回任务future
    while downloader.running():
        if waiting_thr.running() is False:  # 用户关闭了等待窗口，代表取消操作
            # 回收线程
            downloader.cancel()  # 为什么不是shutdown: 代码缺陷，先妥协一下（
            # waiting_pool.shutdown(False)  # 强制停止: 这里直接面向用户，妥协不了
            return
        pass
    html: str = downloader.result()

    with open(filedir, "w", encoding=file_encoding) as file:  # 写入文件
        file.write(html)

    # waiting_pool.shutdown(False)  # 要是一开始就知道，我可能会去用tkinter。我花了好久时间解决这个问题。

    # 汇报结果
    gui.msgbox(
        msg=f"下载完成！\n\n文件已保存至：\n{filedir}",
        title=DEFAULT_TITLE
    )
    return


def setting_window():
    message = "目前没有可供设置的选项，因为认为代码仍不需要庞大的设置。EasyGUI也不适合写灵活的设置GUI。\n" \
               "但是我们在源代码层面上提供了一些方便修改的常量，如果需要，请访问我们的Github仓库。\n"
    gui.msgbox(msg=message, title=DEFAULT_TITLE, ok_button="好")
    return


def about_window():
    message = "\n" \
                    "爬虫工具 ver1.0  by xia__mc (20220922)\n" \
                    "目前仅在静态、仅HTML、无外置资源的网页上工作良好，仅能爬取HTML文件。\n" \
                    "\n\n\n" \
                    "已知问题：\n" \
                    "1.下载中的窗口不能被自动关闭。目前移除了自动关闭代码以允许手动关闭。\n" \
                    "2.不能爬取网页所包含的外置资源（无法解析HTML）。\n" \
                    "3.不能绕过部分网站的检测。" \
                    "\n\n" \
                    "事实上真正用来爬取的代码只有三行，难度大头都在GUI页面上\n" \
                    "但是GUI页面不是很酷吗（笑）\n" \
                    "\n" \
                    "本软件基于GPL-3.0协议发布，请遵守该协议\n" \
                    "开源地址: https://github.com/xia-mc/spider-gui"
    gui.msgbox(msg=message, title=DEFAULT_TITLE, ok_button="好")
    return


if __name__ == "__main__":
    gui.egdemo()

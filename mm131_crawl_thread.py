# *-* encoding: utf-8 *-*

'''
python 爬虫，爬取https://www.mm131.net/网站的美女图片
'''

import requests
from bs4 import BeautifulSoup
import re
import os
import concurrent.futures

# 忽略ssl认证告警信息打印
import urllib3
urllib3.disable_warnings()

__author__ = "Jemmy"

# 网站及地址
base_url = 'https://www.mm131.net/'
# 图片地址域名
img_base_url = "https://img1.mmmw.net/"
# 图片分类及id映射
category_dict = {'xinggan': 6, 'qingchun': 1, 'xiaohua': 2, 'chemo': 3, 'qipao': 4, 'mingxing': 5}

# 网站访问请求header，注意必须要添加Referer字段
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "Referer": base_url
}


# 操作类
class Spider(object):
    def __init__(self):
        # 每一个图片分类分页数目
        self.totalpages = {}
        # 获取每个分类的总分页数目
        self.get_total_page()
        # 保存每个图片的入口url
        self.url_list = []

    # 获取图片每个分类的总页数
    def get_total_page(self):
        for category in category_dict:
            self.goto_category_page(category)
        print(self.totalpages)

    # 获取图片分类分页数目的函数，
    def goto_category_page(self, category):
        # 构造进入分类的url
        url = base_url + category
        try:
            # 发起网络请求
            res = requests.get(url, headers=headers)
            # 获取返回结果，并用BeautifulSoup解析
            soup = BeautifulSoup(res.text, "html.parser")
            # 找到page标签并找到最后一个"末页"的href值，<a href="list_6_210.html" class="page-en"></a>
            page_a = soup.find_all('a', {"class": "page-en"})
            # 获取href的值
            total_page_str = page_a[-1].get("href")
            # 从list_6_210.html字段中解析出总页数：210
            total_page = int((total_page_str.split('.')[0].split('_'))[-1])
            self.totalpages[category] = total_page
        except Exception as e:
            print(e)

    # 获取每一张图片的url
    def get_img_url(self, url):

        referer_ = url[:-5]
        image_id = url.split('/')[-1].split('.')[0]
        print(image_id)
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        img_num_soup = soup.find("div", class_="content-page").find("span").text
        img_num = int("".join(re.findall(r"\d", img_num_soup)))
        for index in range(1, img_num + 1):
            img_url = "{}pic/{}/{}.jpg".format(img_base_url, str(image_id), str(index))
            if index == 1:
                referer = url
            else:
                referer = '{}_{}.html'.format(referer_, index)
            self.download_img(img_url, referer, image_id, str(index))

    def download_img(self, img_url, Referer, id, img_name):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": Referer
        }
        category = Referer.split('/')[-2]
        img_directory = '../' + category + '/' + str(id)

        img_path_name = img_directory + '/' + img_name + '.jpg'
        if not os.path.exists(img_directory):
            os.makedirs(img_directory)
        if os.path.isfile(img_path_name):
            print("{}已存在".format(img_path_name))
        else:
            with open(img_path_name, 'wb') as f:
                f.write(requests.get(img_url, headers=headers, verify=False).content)
                print('已保存{}'.format(img_path_name))

    # 获取每个分类下的所有图片
    def get_url(self, category):
        for i in range(1, self.totalpages[category] + 1):
            # 构造当前page url
            page_suffix = '' if i == 1 else '/list_' + str(category_dict[category]) + '_' + str(i) + '.html'
            page_url = '{}{}{}'.format(base_url, category, page_suffix)
            # print(page_url)
            res = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            # 找到封面图片的图片url， 并保存至
            page_div = soup.find('dl', {'class': 'list-left public-box'}).findAll('dd')
            del page_div[-1]
            urls = []
            for dd in page_div:
                url = dd.find('a').get('href')
                urls.append(url)
            self.get_page_img(urls)

    # 使用多线程启动图片下载
    def get_page_img(self, urls):
        with concurrent.futures.ThreadPoolExecutor() as excutor:
            excutor.map(self.get_img_url, urls)


def main():
    spider = Spider()
    with concurrent.futures.ThreadPoolExecutor() as excutor:
        excutor.map(spider.get_url, list(category_dict.keys()))


if __name__ == "__main__":
    main()

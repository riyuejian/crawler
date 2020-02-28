# *-* encoding: utf-8 *-*

import requests
from bs4 import BeautifulSoup
import re
import os

__author__ = "Jemmy"

base_url = 'https://www.mm131.net/'
img_base_url = "https://img1.mmmw.net/"
category_dict = {'xinggan': 6, 'qingchun' : 1, 'xiaohua' : 2, 'chemo' : 3, 'qipao' : 4, 'mingxing' : 5}
category_typeid_list = [6, 1, 2, ]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "Referer": base_url
}


class Spider(object):
    def __init__(self):
        self.totalpages = {}
        self.get_total_page()
        self.url_list = []

    def get_total_page(self):
        for category in category_dict:
            self.goto_category_page(category)
        print(self.totalpages)

    def goto_category_page(self, category):
        url = base_url + category
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            page_a = soup.find_all('a', {"class": "page-en"})
            total_page_str = page_a[-1].get("href")
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

    # 获取图片首页url
    def get_url(self, category):
        for i in range(1, self.totalpages[category] + 1):
            page_suffix = '' if i == 1 else '/list_' + str(category_dict[category]) + '_' + str(i) + '.html'
            page_url = '{}{}{}'.format(base_url, category, page_suffix)
            # print(page_url)
            res = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            page_div = soup.find('dl', {'class': 'list-left public-box'}).findAll('dd')
            del page_div[-1]
            for dd in page_div:
                url = dd.find('a').get('href')
                self.get_img_url(url)
                # self.url_list.append(url)
        # print(len(self.url_list))




def main():
    spider = Spider()
    for category in category_dict:
        spider.get_url(category)


if __name__ == "__main__":
    main()

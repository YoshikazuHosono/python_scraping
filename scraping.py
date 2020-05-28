from urllib import request
from bs4 import BeautifulSoup
from multiprocessing import Pool
import re

PARSER = "html.parser"

def analysis_article(article_url):
    article_response = request.urlopen("https://girlschannel.net" + article_url)
    article_soup = BeautifulSoup(article_response, PARSER)

    # 記事のタイトル
    article_title = article_soup.h1.text.strip()

    # 記事のコメント
    comment_dict_list = list( map(lambda x : {"item" : x} , article_soup.find_all("li", class_="comment-item") ) )
    for comment_item in comment_dict_list:
        # ID
        original_id = re.search(r'\d+', comment_item["item"].find("p","info").text).group()
        comment_item["original_id"] = int(original_id)

        # 返信ID
        res_anchor = comment_item["item"].find("span","res-anchor")
        if res_anchor is not None:
            comment_item["original_parent_id"] = int(res_anchor.text.replace(">>", ""))
            res_anchor.decompose() # コメント本文に返信IDがあって邪魔なので、消しておく
        else:
            comment_item["original_parent_id"] = None

        # 本文
        comment_item["text"] = comment_item["item"].find("div","body").text.strip()

        # 画像
        img_item = comment_item["item"].find("div","comment-img")
        if img_item is not None:
            comment_item["attachment_url"] = img_item.img.get("data-src")
        else:
            comment_item["attachment_url"] = "no_image"

    print('-' * 50)
    print(article_title)
    print('-' * 50)
    for comment in comment_dict_list:
        del comment["item"]
        print(comment)

top_page_response = request.urlopen("https://girlschannel.net/topics/category/gossip/")
top_page_soup = BeautifulSoup(top_page_response, PARSER)

article_url_list = list(map(lambda x : x.a.get("href") , top_page_soup.find_all("li", class_="flc")))

if __name__ == "__main__":
    p = Pool(len(article_url_list))
    p.map(analysis_article,article_url_list)
    p.close()

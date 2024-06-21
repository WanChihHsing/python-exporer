import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

# 定义豆瓣电影Top 250的URL
base_url = "https://movie.douban.com/top250"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/86.0.4240.111 Safari/537.36'}

# 用于存放图片
os.makedirs("images", exist_ok=True)

# 用于存储电影数据的列表
movies = []

# 爬取每一页的内容
for start in range(0, 250, 25):
    url = f"{base_url}?start={start}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # 查找所有电影条目
    items = soup.find_all('div', class_='item')

    for item in items:
        # 获取电影排名
        rank = item.find('em').text

        # 获取电影标题
        title = item.find('span', class_='title').text

        # 图片链接
        img = item.find('img')['src']

        # 下载图片
        pic = requests.get(img)
        if pic.status_code == 200:
            with open("images/" + title + ".jpg", "wb") as f:
                f.write(pic.content)

        # 获取电影的详细信息
        info = item.find('div', class_='bd').p.text.strip()

        # 获取电影评分
        rating = item.find('span', class_='rating_num').text

        # 获取评价人数
        quote = item.find('span', class_='inq')
        quote_text = quote.text if quote else ""

        # 将电影信息添加到列表中
        movies.append([rank, title, img, info, rating, quote_text])

# 创建DataFrame
df = pd.DataFrame(movies, columns=["Rank", "Title", "Img", "Info", "Rating", "Quote"])

# 导出到Excel
df.to_excel("Douban_Top_250_Movies.xlsx", index=False)

print("数据爬取完成并导出到 Douban_Top_250_Movies.xlsx")

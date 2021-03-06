import logging
import sqlite3
import threading
import time
import requests

class Eastmoney(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        logging.basicConfig(level=logging.DEBUG,
                            filename="news.log",
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format='%(asctime)s - %(levelname)s - %(module)s@%(lineno)d : %(message)s')
        self.logger = logging.getLogger()
        self.headers = {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def run(self):
        while True:
            response = requests.get("https://kuaixun.eastmoney.com/yw.html", headers=self.headers).text
            text = response[response.find('<div class="livenews-list font-12" id="livenews-list">'):response.find('</span></h2></div><div class="media-comment"></div></div></div>')]
            items = text.split('<div class="media-content">')[1:]
            connection = sqlite3.connect('news.db')
            cursor = connection.cursor()
            print("Get %d items" % len(items))
            self.logger.info("Get %d items" % len(items))
            for item in items:
                # get_time = item[19:24]
                item = item[105:]
                link = item[:item.find('class="media-title"') - 2]
                content = item[item.find('class="media-title">')+20:item.find('</a><span class="media-title">')]
                result = None
                try:
                    cursor.execute("SELECT id FROM news WHERE link = ?", (link,))
                    result = cursor.fetchone()
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error("Cannot query news %s" % link)
                if not result:
                    print("Insert %s" % link)
                    self.logger.info("Insert %s" % link)
                    try:
                        cursor.execute("INSERT INTO news (time, link, content, pushed, code) VALUES (?,?,?,?, ?)",
                                       (int(time.time()), link, content,-1, "General"))
                        connection.commit()
                    except Exception as e:
                        self.logger.error(e)
                        self.logger.error("Cannot insert torrent %s" % link)
                        connection.rollback()
            cursor.close()
            connection.close()

            time.sleep(30)

east_money = Eastmoney()

if __name__ == '__main__':
    east_money.run()
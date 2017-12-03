from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from s3pipeline import Page


class TabelogSpider(CrawlSpider):
    name = "tabelog"
    allowed_domains = ["tabelog.com"]
    start_urls = (
        # 東京の昼のランキングのURL。
        # 普通にWebサイトを見ていると、もっとパラメーターが多くなるが、
        # ページャーのリンクを見ると、値が0のパラメーターは省略できることがわかる。
        'https://tabelog.com/tokyo/rstLst/lunch/?LstCosT=2&RdoCosTp=1',
    )

    rules = [
        # ページャーをたどる（最大9ページまで）。
        # 正規表現の \d を \d+ に変えると10ページ目以降もたどれる。
        Rule(LinkExtractor(allow=r'/\w+/rstLst/lunch/\d/')),
        # レストランの詳細ページをパースする。
        Rule(LinkExtractor(allow=r'/\w+/A\d+/A\d+/\d+/$'),
             callback='parse_restaurant'),
    ]

    def parse_restaurant(self, response):
        """
        レストランの詳細ページをパースする。
        """

        yield Page.from_response(response)

# このファイルは食べログのHTML構造に合わせてtabelog.pyからCSSセレクターを変更したものです。
# Spider名もtabelog_modに変更しています。

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.items import Restaurant


class TabelogSpider(CrawlSpider):
    name = "tabelog_mod"
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
        # Google Static Mapsの画像のURLから緯度と経度を取得。
        latitude, longitude = response.css(
            'img.js-map-lazyload::attr("data-original")').re(
                r'markers=.*?%7C([\d.]+),([\d.]+)')

        # キーの値を指定してRestaurantオブジェクトを作成。
        item = Restaurant(
            name=response.css('.display-name').xpath('string()').extract_first().strip(),
            address=response.css('.rstinfo-table__address').xpath('string()').extract_first().strip(),
            latitude=latitude,
            longitude=longitude,
            station=response.css('dt:contains("最寄り駅")+dd span::text').extract_first(),
            score=response.css('[rel="v:rating"] span::text').extract_first(),
        )

        yield item

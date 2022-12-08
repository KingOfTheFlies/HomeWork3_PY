import scrapy
from urllib.parse import urlencode
from ..items import SpidersteamItem


queries = ['indie', 'kids', 'novel']
API = '3418ca8efdc7a84af03bb7fbc44ca490'


def get_url(url):
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class SteamgamespiderSpider(scrapy.Spider):
    name = 'SteamGameSpider'
    page = 1

    def start_requests(self):
        for query in queries:
            for page in range(1, 3):
                url = 'https://store.steampowered.com/search/?' + urlencode({'term': query,
                                                                             'supportedlang': 'russian',
                                                                             'category1': str(998),
                                                                             "ndl": str(1),
                                                                             'page': str(page)})
                yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        games = set()
        for res in response.xpath('//a[contains(@class, "search_result_row ds_collapse_flag ")]/@href').extract():
            if 'app' in res:
                games.add(res)

        for game in games:
            game_url = game
            yield scrapy.Request(url=get_url(game_url), callback=self.parse_game_page)



    def parse_game_page(self, response):
        release_date = response.xpath('//div[@class="date"]/text()').extract()
        rd = int(''.join(release_date).strip()[-4:])
        if rd is not None and rd < 2000:
            return
        item = SpidersteamItem()
        name = response.xpath('//title/text()').extract()
        category = response.xpath('//div[@class="glance_tags popular_tags"]/a//text()').extract()
        rating = response.xpath('//div[@class="summary_section"]/span/text()').extract()
        developer = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        tags = response.xpath('//div[@class="glance_tags popular_tags"]/a//text()').extract()
        price = response.xpath('//div[@class="discount_final_price"]/text() | //div[@class="game_purchase_price price"]/text()').extract()
        opsys = response.xpath('//div[@class="sysreq_tabs"]/div//text()').extract()
        translator = str.maketrans({'\n': '', '\t': '', '\r': ''})
        item["game_name"] = ''.join(name).strip()[:-9]
        item["game_category"] = '/'.join(category).strip().translate(translator)
        item["game_rating"] = ''.join(rating).strip()
        item["game_release_date"] = ''.join(release_date).strip()
        item["game_developer"] = ''.join(developer).strip()
        item["game_tags"] = '/'.join(tags).strip().translate(translator)
        item["game_price"] = ''.join(price).strip()
        item["game_opsys"] = '/'.join(opsys).strip().translate(translator)
        yield item

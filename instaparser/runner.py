from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser.spiders.instafollowing import InstafollowingSpider

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(InstagramSpider)
    runner.crawl(InstafollowingSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
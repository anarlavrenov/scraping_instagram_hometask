# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    user_followed = scrapy.Field()
    user_following = scrapy.Field()
    username = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    _id = scrapy.Field()

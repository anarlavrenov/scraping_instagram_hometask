# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import collections

from itemadapter import ItemAdapter

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from hashlib import md5

class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        if spider.name == 'instagram':
            item['_id'] = self.hash_id(item)

        if spider.name == 'instafollowing':
            item['_id'] = self.hash_id(item)


        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            pass
        return item



    def hash_id(self, item):
        bytes_input = str(item).encode('utf-8')

        return md5(bytes_input).hexdigest()



#{'user_followed': 'sergeo_belov'}
#{'user_following': 'am_amir_mohseni'}


import scrapy
import re
from scrapy.http import HtmlResponse
import json
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']

    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'anar_lavrenov'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1650862358:AbBQAH6KEQzvux6EpsdlT9hjSU470uHUGZ90JgVrvrsJNsNY6YZdMcIy4s51JEz+tFySj2NGN9PkWUrXqvLZykCGnBxb+9pdBYZG5thMTJ2qgxf0DsDJcptWdIK1jqrA1HztyNA9zwcEILyCClo='

    parse_users = ['sergeo_belov', 'am_amir_mohseni']

    search_surface = 'follow_list_page'


    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login, 'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        inst_api_link = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?'
        count = 12
        url_followers = f'{inst_api_link}count={count}&search_surface={self.search_surface}'

        yield response.follow(url_followers, callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'count': count,
                                         'inst_api_link': inst_api_link},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})


    def user_followers_parse(self, response: HtmlResponse, username, user_id, count, inst_api_link):
        j_data = response.json()
        if j_data.get('next_max_id'):
            url_followers = f"{inst_api_link}count={count}&max_id={j_data.get('next_max_id')}&search_surface={self.search_surface}"
            yield response.follow(url_followers, callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'count': count,
                                             'inst_api_link': inst_api_link},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        followers = j_data.get('users')
        for follower in followers:
            item = InstaparserItem(
                user_followed=username,
                username=follower.get('username'),
                user_id=follower.get('pk'),
                photo=follower.get('profile_pic_url')
            )
            yield item





    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace('"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
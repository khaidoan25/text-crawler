# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class WavPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        file_url = item['file_urls'][0]
        meta = {'filename': item['file_name'][0]}
        yield Request(url=file_url, meta=meta)

    def file_path(self, request, response=None, info=None):
        return request.meta.get('filename','')

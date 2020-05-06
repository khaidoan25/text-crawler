# How to run
# scrapy crawl <name>

from __future__ import absolute_import
from scrapy import Spider
import scrapy
from scrapy.loader import ItemLoader
from crawler.items import WavItem
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import platform
import pandas as pd
# from scrapy.items import CrawlerItem

class CrawlerTextSpider(Spider):
    name = "text_crawler"
    # allower_domains = ["thegioididong.com"]
    start_urls = [
        # "https://www.thegioididong.com/dtdd-samsung",
        "https://id.foody.vn/account/login?returnUrl=https://www.foody.vn/ho-chi-minh/quan-an?CategoryGroup=food"
    ]

    def __init__(self):
        if platform.system() == "Linux":
            self.driver = webdriver.Chrome("/home/ddkhai/Documents/text-crawler/crawler/linux/chromedriver")
        elif platform.system() == "Windows":
            self.driver = webdriver.Chrome("D:\\github\\text-crawler\\crawler\\windows\\chromedriver.exe")

        self.outfile = open("raw_negative.txt", "w")

    def parse(self, response):
        self.driver.get(response.url)

        username = self.driver.find_element_by_id("Email")
        username.clear()
        # Hide
        # username.send_keys()

        password = self.driver.find_element_by_name("Password")
        password.clear()
        # Hide
        # password.send_keys()

        self.driver.find_element_by_id("bt_submit").click()
        time.sleep(3)
        
        # Scroll down to bottom of the page
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait the page load
        time.sleep(5)
        for _ in range(10):
            ele = self.driver.find_element_by_xpath('//div[@id="scrollLoadingPage"]')
            self.driver.execute_script("arguments[0].click()", ele)
            time.sleep(2)
        elements = self.driver.find_elements_by_xpath('//div[@class="row-view-right"]/div/div/h2/a')
        scores = [ele.text for ele in self.driver.find_elements_by_xpath('//*[@class="point highlight-text"]')]
        # print(len(scores))
        for score, ele in zip(scores, elements):
            if float(score) <= 7.5:
                yield scrapy.Request(ele.get_attribute('href'), callback=self.parse_intemediate_page)
            else:
                continue

    def parse_intemediate_page(self, response):
        self.driver.get(response.url)
        # time.sleep(10)
        # Scroll down to bottom of the page
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait the page load
        time.sleep(2)
        try:
            self.driver.find_elements_by_xpath('//*[@class="fd-btn-more"]')
            elements = self.driver.find_elements_by_xpath('//*[@class="ldc-item-h-name"]/h2/a')
            scores = [ele.text for ele in self.driver.find_elements_by_xpath('//*[@class="ldc-item-h-ranking avg-bg-highlight"]/span')]
            for score, ele in zip(scores, elements):
                if float(score) <= 7.5:
                    yield scrapy.Request(ele.get_attribute('href'), callback=self.parse_single_page)
                else:
                    continue
        except:
            yield scrapy.Request(self.driver.current_url, callback=self.parse_single_page)

    def parse_single_page(self, response):
        self.driver.get(response.url)
        comment_elements = self.driver.find_elements_by_xpath('//li[@class="review-item fd-clearbox ng-scope"]/div[2]/div[1]/span')
        old_len = len(comment_elements)
        while True:
            # Scroll down to bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(2)
            # Wait the page load
            # time.sleep(4)
            # Scroll up
            self.driver.execute_script('arguments[0].scrollIntoView(true);', comment_elements[-1])
            time.sleep(2)
            try:
                # Scroll down to bottom of the page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait the page load
                # self.driver.execute_script('arguments[0].scrollIntoView(true);', comment_elements[-1])
                time.sleep(2)
                # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                show_more = self.driver.find_element_by_xpath('//a[@ng-class="{\'loading\':IsLoading}"]')
                self.driver.execute_script('arguments[0].scrollIntoView(true);', show_more)
                time.sleep(1)
                action = ActionChains(self.driver)
                action.move_to_element(show_more).click().perform()
                time.sleep(2)
            except:
                break
            # Find comments
            comment_elements = self.driver.find_elements_by_xpath('//li[@class="review-item fd-clearbox ng-scope"]/div[2]/div[1]/span')
            if old_len == len(comment_elements):
                break
            else:
                old_len = len(comment_elements)

        comment_elements = self.driver.find_elements_by_xpath('//li[@class="review-item fd-clearbox ng-scope"]/div[2]/div[1]/span')
        scores = [ele.text for ele in self.driver.find_elements_by_xpath('//li[@class="review-item fd-clearbox ng-scope"]/div[1]/div[2]/div[1]/span')]
        
        for score, comment in zip(scores, comment_elements):
            if float(score) <= 6.0:
                self.outfile.write(comment.text + '\n===***===\n')

        print(len(comment_elements))
        print("***************************")
        print(len(scores))

class CrawlerWavSpider(Spider):
    name = "wav_crawler"

    start_urls = [
        "https://ailab.hcmus.edu.vn/vosdemo"
        ]
    
    def __init__(self):
        if platform.system() == "Linux":
            self.driver = webdriver.Chrome("/home/ddkhai/Documents/text-crawler/crawler/linux/chromedriver")
        elif platform.system() == "Windows":
            self.driver = webdriver.Chrome("D:\\github\\text-crawler\\crawler\\windows\\chromedriver.exe")

        self.data = pd.read_csv("metadata.csv", header=None, sep="|")

    def parse(self, response):
        self.driver.get(response.url)
        iframe = self.driver.find_element_by_css_selector('iframe')
        self.driver.switch_to_frame(iframe)
        element = self.driver.find_element_by_xpath("/html/body/form/textarea")
        for i in range(len(self.data)):
            file_name = self.data.iloc[i, 0] + ".mp3"
            text = self.data.iloc[i, 1]
            element.clear()
            element.send_keys(text)
            self.driver.find_element_by_xpath("/html/body/form/input[5]").click()
            time.sleep(2)
            download_element = self.driver.find_element_by_xpath("/html/body/audio/source")
            loader = ItemLoader(item=WavItem(), selector=download_element)
            relative_url = download_element.get_attribute("src")
            absolute_url = response.urljoin(relative_url)
            loader.add_value("file_urls", absolute_url)
            loader.add_value("file_name", file_name)
            yield loader.load_item()
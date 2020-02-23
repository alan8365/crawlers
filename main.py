from EasyCodingCrawler import EasyCodingCrawler
from NutcCurriculumCrawler import CleanTool

from bs4 import BeautifulSoup
from requests import get

import re


def output_to_file(content, filename):
    with open(filename, 'w', encoding='utf8') as f:
        f.write(content)


if __name__ == '__main__':
    crawler = EasyCodingCrawler()
    crawler.course_parser()

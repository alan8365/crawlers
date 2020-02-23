from EasyCodingCrawler import EasyCodingCrawler
from NutcCurriculumCrawler import CleanTool

from bs4 import BeautifulSoup
from requests import get
from MySQLdb import connect

import re


def output_to_file(content, filename):
    with open(filename, 'w', encoding='utf8') as f:
        f.write(content)


if __name__ == '__main__':
    crawler = EasyCodingCrawler()
    test = crawler.course_parser()


def output_to_db(data):
    db = connect(host="172.17.135.89", user="easyuser",
                 passwd="easy1234", db="easy", charset='utf8')
    c = db.cursor()

    course_info = data['course_info']
    course_block = data['course_block']

    c.execute(
        f'''SELECT id FROM course_course 
            WHERE lesson_id={course_info["lesson_number"]}
            and chapter={course_info["chapter"]}
        ''')

    course_id, = c.fetchone()

    content_data = []
    for i in range(len(course_block)):
        block = course_block[i]
        block_type = block['type']

        temp = (
            block['content'],
            i,
            1 if block_type == 'title' else 0,
            1 if block_type == 'subtitle' else 0,
            1 if block_type == 'text' else 0,
            1 if block_type == 'code' else 0,
            1 if block_type == 'image' else 0,
            1 if block_type == 'link' else 0,
            1 if block_type == 'table' else 0,
            course_id
        )

        content_data.append(temp)

    c.executemany(
        """
        REPLACE INTO course_content 
        SET content=%s, 
        number=%s, 
        isTitle=%s, 
        isSubTitle=%s, 
        isText=%s, 
        isCode=%s, 
        isImage=%s, 
        isLink=%s, 
        isTable=%s, 
        course_id=%s
        """,
        content_data
    )

    db.commit()

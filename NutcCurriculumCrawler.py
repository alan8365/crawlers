from bs4 import BeautifulSoup
from datetime import date
from requests import get

import os
import re
import json
import NutcCurriculumCleanTool as CleanTool

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class NutcCurriculumCrawler:

    def __init__(self, sem=''):
        if sem:
            self.sem = sem
        else:
            today = date.today()
            self.sem = str(today.year - 1912)

            if today.month < 7:
                self.sem += '2'
            else:
                self.sem += '1'

        self.dir_root = os.path.join(BASE_DIR, 'json', 'NutcCurriculumData', self.sem)

        if not os.path.isdir(self.dir_root):
            os.mkdir(self.dir_root)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
        }

    def teacher_setup(self):
        file_path = os.path.join(self.dir_root, 'teacher_number.json')
        url = 'http://aisap.nutc.edu.tw/public/teacher_list.js'

        js_text = get(url, verify=False, headers=self.headers).text

        js_sentences = js_text.strip().split('\n')
        js_sentences = list(filter(lambda s: re.search(rf'D\d_{self.sem}', s), js_sentences))

        contents = []
        for js_sentence in js_sentences:
            js_sentence = js_sentence.split('=')[1].strip().replace(';', '')

            contents += eval(js_sentence)

        contents = sorted(list(set(map(tuple, contents))), key=lambda li: li[0])
        contents = [{'id': content[0], 'name': content[1]} for content in contents]
        contents = [{'id': 0, 'name': '很多個'}, {'id': 1, 'name': '待聘'}] + contents

        with open(file_path, 'w') as f:
            json.dump(contents, f)

    def class_setup(self):

        file_path = os.path.join(self.dir_root, 'class_number.json')
        url = 'http://aisap.nutc.edu.tw/public/clsno_list.js'

        js_text = get(url, verify=False, headers=self.headers).text

        js_sentences = js_text.strip().split('\n')
        js_sentence, = list(filter(lambda s: re.search(rf'D1_{self.sem}', s), js_sentences))
        js_sentence = js_sentence.split('=')[1].strip().replace(';', '')

        contents = eval(js_sentence)
        contents = [{'number': content[0], **CleanTool.change_to_three_part(content[1])} for content in contents]

        with open(file_path, 'w') as f:
            json.dump(contents, f)

    def course_crawl(self):

        file_path = os.path.join(self.dir_root, 'course_info.json')
        base_url = f'http://aisap.nutc.edu.tw/public/day/course_list.aspx?sem={self.sem}&clsno='

        with open(os.path.join(self.dir_root, 'class_number.json'), 'r') as f:
            class_numbers = [i['number'] for i in json.load(f)]

        with open(os.path.join(self.dir_root, 'teacher_number.json'), 'r') as f:
            teacher_infos = json.load(f)
            teacher_infos = {teacher_info['name']: teacher_info['id'] for teacher_info in teacher_infos}

        contents = []
        for class_number in class_numbers:

            url = base_url + class_number

            html_text = get(url, verify=False, headers=self.headers).text

            soup = BeautifulSoup(html_text, 'html.parser')

            trs = soup.find_all('tr')[2:]

            for tr in trs:
                tds = tr.find_all('td')
                tds = list(map(lambda tag: tag.text, tds))[1:-2]

                time = CleanTool.delete_location(tds[4])

                temp = {'id': int(tds[0][1:]),
                        'classes_id': class_number,
                        'name': tds[2],
                        'time': time,
                        'classroom': CleanTool.delete_time(tds[4]),
                        'compulsory': tds[5] == '選',
                        'credit': tds[6],
                        'popular_limit': tds[7],
                        'teacher_id': teacher_infos[tds[8]] if tds[8] in teacher_infos.keys() else 0,
                        'course_time': CleanTool.cut_time_to_list(time)}

                contents.append(temp)

        with open(file_path, 'w') as f:
            json.dump(contents, f)

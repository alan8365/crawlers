from bs4 import BeautifulSoup
from requests import get

import re
import json


class EasyCodingCrawler:
    def __init__(self):
        root_url = 'https://hackmd.io/5Elwp94uQf2SvWhn7Oy_gg'

        html_text = get(root_url).text

        soup = BeautifulSoup(html_text, 'html.parser')
        doc = soup.find('div', id='doc')

        markdown_string = doc.contents[0]

        patten = r'\[.*\]'
        temp_headers = re.findall(patten, markdown_string)
        temp_headers = list(map(lambda s: s[1:-1], temp_headers))

        patten = r'\(.*\)'
        temp_urls = re.findall(patten, markdown_string)
        temp_urls = list(map(lambda s: s[1:-1] if 'https' in s else f'https://hackmd.io{s[1:-1]}', temp_urls))

        temp_mix = tuple(zip(temp_headers, temp_urls))

        self.pairs = {
            'documents': temp_mix[:8],
            'course': temp_mix[8:39],
            'assessment': temp_mix[44:-1]
        }

    def course_parser(self):
        pairs = self.pairs['course']

        for name, url in pairs:
            html_text = get(url).text

            soup = BeautifulSoup(html_text, 'html.parser')
            doc = soup.find('div', id='doc')

            raw_text = doc.text

            pattern = r':::.*([\w\W]*):::'
            answer_match = re.search(pattern, raw_text, re.MULTILINE)

            pattern = r'===|# U*\d+-\d+.*\n'
            header_match = re.search(pattern, raw_text, re.MULTILINE)

            filter_text = raw_text[header_match.end():answer_match.start()]
            split_texts = filter_text.split('\n')
            split_texts = list(filter(lambda s: bool(s), split_texts))

            course_block = self.course_type_parser(split_texts)

            answer_text = answer_match.group(1)
            answer_split_texts = answer_text.split('\n')
            answer_split_texts = list(filter(lambda s: bool(s), answer_split_texts))

            answer_block = self.course_type_parser(answer_split_texts)

            name = name[1:] if name[0] == 'U' else name
            course_info = {
                'lesson_number': name[0],
                'chapter': name[2],
                'name': name[3:]
            }

            data = {
                'course_info': course_info,
                'course_block': course_block,
                'answer_block': answer_block
            }

            with open(f'json/{name}.json', 'w', encoding='utf8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def course_type_parser(split_texts: list) -> list:
        seek = 0
        all_block = []
        while seek < len(split_texts):
            temp_str = split_texts[seek]

            if r'```' in temp_str:
                right_seek = seek + 1

                while r'```' not in split_texts[right_seek]:
                    right_seek += 1

                temp_block = {
                    'type': 'code',
                    'content': '\n'.join(split_texts[seek: right_seek + 1])
                }

                seek = right_seek
            elif r'<table>' in temp_str:
                right_seek = seek + 1

                while r'</table>' not in split_texts[right_seek]:
                    right_seek += 1

                temp_block = {
                    'type': 'table',
                    'content': '\n'.join(split_texts[seek: right_seek + 1])
                }

                seek = right_seek
            elif r'<h4>' in temp_str:
                temp_block = {
                    'type': 'title',
                    'content': temp_str
                }
            elif r'<h5>' in temp_str:
                temp_block = {
                    'type': 'subtitle',
                    'content': temp_str
                }
            else:
                temp_block = {
                    'type': 'text',
                    'content': temp_str
                }

            all_block.append(temp_block)
            seek += 1

        return all_block

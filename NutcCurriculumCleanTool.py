import re

reference_string = "零一二三四五六日"


def my_int(s: str):
    if s in reference_string:
        return reference_string.find(s)
    else:
        return int(s)


def delete_combine(li: list) -> str:
    if len(li) == 2:
        if '\n' in li[1]:
            result = li[0]
        else:
            result = li[0] + li[1]
    else:
        result = li[0]

    return result.strip()


# '資管三Ａ' -> ['資管', 3, 'Ａ']
def change_to_three_part(s: str) -> dict:
    pattern = f'([{reference_string}])'
    temp = re.split(pattern, s)

    if temp[2] == '':
        temp[2] = '1'

    result = {
        'department': temp[0],
        'grade': my_int(temp[1]),
        'classes': temp[2]
    }
    return result


# 星期三第５～７節 (---) -> 星期三第５～７節
def delete_location(s: str) -> str:
    s = re.sub(r'\(.{3,5}\)', '', s)
    s = s.replace(' ', '')
    return s


# 星期三第５～７節 (1403) -> (1403)
def delete_time(s: str) -> str:
    s = re.search(r'\(.{3,5}\)', s)[0]
    return s[1:-1]


def cut_time_to_list(str_of_time: str) -> list:
    if str_of_time == '':
        return []

    period = []
    week = my_int(str_of_time[2])

    if str_of_time.find('/') != -1:
        result = []
        for i in str_of_time.split('/'):
            result += cut_time_to_list(i)

        return result

    str_of_time = str_of_time[4:-1]

    if str_of_time.find('、') != -1:
        first_cuts = str_of_time.split('、')

        for first_cut in first_cuts:

            if first_cut.find('～') != -1:
                second_cuts = first_cut.split('～')

                for i in range(my_int(second_cuts[0]), my_int(second_cuts[1]) + 1):
                    period.append(i)

            elif first_cut.find('、') != -1:
                second_cuts = first_cut.split('、')

                for second_cut in second_cuts:
                    period.append(my_int(second_cut))
            else:
                period.append(my_int(first_cut))

    elif str_of_time.find('～') != -1:
        first_cuts = str_of_time.split('～')

        for i in range(my_int(first_cuts[0]), my_int(first_cuts[1]) + 1):
            period.append(i)

    else:
        period.append(my_int(str_of_time))

    result = [(week, p) for p in period]

    return result

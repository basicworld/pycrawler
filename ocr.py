# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import string
from PIL import Image
import pytesseract


def ocr(img, bw_degree=1):
    """
    接受一个image对象，返回识别的字符
    """
    gray = img.convert('L')  # 灰度化
    bw = gray.point(lambda x: 0 if x < bw_degree else 255, '1')  # 阈值化
    word = pytesseract.image_to_string(bw)
    ascii_word = ''.join(c for c in word if c in string.letters).lower()  # 小写字母
    return ascii_word


def test_sample():
    """
    识别率90%
    """
    import csv
    correct = total = 0
    for filename, text in csv.reader(open('samples/samples.csv')):
        img = Image.open('samples/%s' % filename)
        if ocr(img) == text:
            correct += 1
            print text
        total += 1

    print correct, total


if __name__ == '__main__':
    test_sample()

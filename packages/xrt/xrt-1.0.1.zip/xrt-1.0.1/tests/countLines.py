# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 09:46:31 2015

@author: konkle
"""
import os

exts = ['.py', '.cl']
count_empty_line = True
here = os.path.abspath(r"c:\Ray-tracing\xrt")
#here = os.path.abspath(r"c:\Ray-tracing\examples")


def read_line_count(fname):
    count = 0
    with open(fname) as f:
        for line in f:
            if count_empty_line or len(line.strip()) > 0:
                count += 1
    return count


def main():
    line_count = 0
    file_count = 0
    for base, dirs, files in os.walk(here):
        for f in files:
            if f.find('.') < 0:
                continue
            ext = (f[f.rindex('.'):]).lower()
            if ext in exts:
                file_count += 1
                path = base + '/' + f
                c = read_line_count(path)
                print('.{0} : {1}'.format(path[len(here):], c))
                line_count += c

    print('File count : {0}'.format(file_count))
    print('Line count : {0}'.format(line_count))

if __name__ == '__main__':
    main()

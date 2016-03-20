import urllib.parse
import os
import html.parser

src_dir = '/Users/james/Programming/projects/periculo/data/Seedrs'
files = os.listdir(src_dir)

class Row:
    name = None
    source = None
    company = None
    founded = None
    location = None
    target = None
    equity = None
    funded = None
    pre_valuation = None
    sector_1 = None
    sector_2 = None
    sector_3 = None
    days_left = None
    start = None
    end = None
    pitch_period = None
    scheme = None

    def __repr__(self):
        return '{0}: {1}'.format(self.company, self.funded)


class CompanyParser(html.parser.HTMLParser):

    print_tag = False

    def __init__(self, row : Row):
        super().__init__()
        self.row = row

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.print_tag = False
        if self.print_tag:
            print("Encountered a start tag: {0} with attributes {1}", tag, attrs)

    def handle_endtag(self, tag):
        if self.print_tag:
            print("Encountered an end tag :", tag)
        if tag == 'script':
            self.print_tag = True

    def handle_data(self, data):
        if self.print_tag:
            print("Encountered some data  :", data)



rows = []
for file in files:
    print('Parsing file {0}'.format(file))
    html = open('{0}/{1}'.format(src_dir, file), 'rt').read()
    row = Row()
    parser = CompanyParser(row)
    parser.feed(html)

    row.company = 'Test'
    row.funded = 100

    rows.append(row)
    break

print(rows)
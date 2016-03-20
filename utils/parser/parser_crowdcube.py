import pandas as pd
import os
import html.parser
import re
from utils.parser.pitch import Pitch

pd.set_option('display.max_columns', 200)
pd.set_option('display.width', 500)
pd.set_option('display.precision', 4)
pd.set_option('display.float_format', '{:,.2f}'.format)


class SummaryParser(html.parser.HTMLParser):
    pitches = []
    current_pitch = None

    def __init__(self):
        super().__init__()
        self.mode = None

    def handle_starttag(self, tag, attrs):
        for (key, value) in attrs:
            if tag == 'section' and key == 'class' and value == 'pitch__detail':
                self.current_pitch = Pitch()
            elif self.current_pitch:
                if key == 'class' and value == 'pitch__title':
                    self.mode = 'company'
                elif key == 'class' and value == 'tax__item':
                    self.mode = 'tax'
                elif key == 'class' and value == 'pitchProgress__figure':
                    self.mode = 'progress'
                elif key == 'class' and value == 'pitch__statLabel':
                    self.mode = 'stat'
                elif key == 'class' and value == 'timeRemaining__figure':
                    self.mode = 'stat.days'


    def handle_endtag(self, tag):
        if tag == 'section':
            if self.current_pitch:
                self.pitches.append(self.current_pitch)
                self.current_pitch = None
        return

    def handle_data(self, data):
        if not self.current_pitch:
            return

        data = data.strip(' ').replace('\n', '')
        if len(data) == 0:
            return

        if self.mode == 'company':
            self.current_pitch.company = data
            self.mode = None
        elif self.mode == 'tax':
            self.current_pitch.scheme = data
            self.mode = None
        elif self.mode == 'progress':
            self.current_pitch.investment_received = data
            self.mode = None
        elif self.mode == 'stat':
            if data == 'Target':
                self.mode = 'stat.target'
            elif data == 'Equity':
                self.mode = 'stat.equity'
            elif data == 'Investors':
                self.mode = 'stat.investors'
            elif data == 'Days left':
                self.mode = 'stat.days'

        elif self.mode == 'stat.target':
            self.current_pitch.investment_required = data
            self.mode = None
        elif self.mode == 'stat.equity':
            self.current_pitch.equity_perc_offered = data
            self.mode = None
        elif self.mode == 'stat.investors':
            self.current_pitch.num_investors = data
            self.mode = None
        elif self.mode == 'stat.days':
            self.current_pitch.days_left = data
            self.mode = None


class DetailParser(html.parser.HTMLParser):
    def __init__(self, pitches: dict):
        super().__init__()
        self.pitches = pitches
        self.current_pitch = None
        self.active = False
        self.mode = None

    def handle_starttag(self, tag, attrs):
        for (key, value) in attrs:
            if key == 'data-pitch-name':
                self.current_pitch = self.pitches[value]

        if tag == 'li':
            self.active = True
        return

    def handle_endtag(self, tag):
        if tag == 'li':
            self.active = False
        return

    def handle_data(self, data):
        if not self.current_pitch:
            return

        data = data.strip(' ').replace('\n', '')
        if len(data) == 0:
            return

        if self.active and not self.mode:
            if data == 'Location:':
                self.mode = 'location'
            elif data == 'Sectors:':
                self.mode = 'sectors'
            elif data == 'Share Type:':
                self.mode = 'type'

        elif self.active and self.mode == 'location':
            self.current_pitch.location = data
            self.mode = None

        elif self.active and self.mode == 'type':
            data = re.sub(' +', ' ', data)
            self.current_pitch.type = data
            self.mode = None

        elif self.active and self.mode == 'sectors':
            sectors = [d.strip(' ') for d in data.split(',')]
            self.current_pitch.sector_1 = sectors.pop() if len(sectors) > 0 else None
            self.current_pitch.sector_2 = sectors.pop() if len(sectors) > 0 else None
            self.current_pitch.sector_3 = ','.join(sectors)
            self.mode = None

def parse() -> pd.DataFrame:
    src_dir = '../../data/Crowdcube'
    files = os.listdir(src_dir)
    rows = {}
    for file in files:
        if not file.endswith('.html'):
            continue

        abs_file = '{0}/{1}'.format(src_dir, file)
        if os.path.isfile(abs_file):
            html = open(abs_file, 'rt').read()
            parser = SummaryParser()
            parser.feed(html)
            for pitch in parser.pitches:
                rows[pitch.company] = pitch

    src_dir = '../../data/Crowdcube/detail'
    files = os.listdir(src_dir)
    for file in files:
        if not file.endswith('.html'):
            continue

        abs_file = '{0}/{1}'.format(src_dir, file)
        if os.path.isfile(abs_file):
            html = open(abs_file, 'rt').read()
            parser = DetailParser(rows)
            parser.feed(html)

    df = pd.DataFrame([row.__dict__ for row in rows.values()])
    df = df.dropna(axis=0, how='all')
    df['Source'] = 'Crowdcube'
    return df

import pandas as pd
import html.parser
import re
from utils.parser.pitch import Pitch
from utils.parser.crowdcube import page_loader

pd.set_option('display.max_columns', 200)
pd.set_option('display.width', 500)
pd.set_option('display.precision', 4)
pd.set_option('display.float_format', '{:,.2f}'.format)


class SummaryParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.pitches = []
        self.current_pitch = None

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.current_pitch = Pitch()

        for (key, value) in attrs:
            if self.current_pitch:
                if tag == 'article' and key == 'id':
                    self.current_pitch.pitch_id = value
                elif key == 'class' and value == 'pitch__title':
                    self.mode = 'company'
                elif key == 'class' and value == 'tax__item':
                    self.mode = 'tax'
                elif key == 'class' and value == 'pitchProgress__figure':
                    self.mode = 'progress'
                elif key == 'class' and value == 'pitch__statLabel':
                    self.mode = 'stat'
                elif key == 'class' and value == 'timeRemaining__figure':
                    self.mode = 'stat.days'
                elif tag == 'a' and self.mode == 'company' and key == 'href':
                    self.current_pitch.pitch_url = value

    def handle_endtag(self, tag):
        if tag == 'section':
            if self.current_pitch:
                self.pitches.append(self.current_pitch)
                self.current_pitch = None
        return

    def handle_data(self, data):
        if not self.current_pitch:
            return

        data = data.replace('\n', '').replace('\r', '').strip(' ')
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
    def __init__(self, pitch: Pitch):
        super().__init__()
        self.pitch = pitch
        self.active = False
        self.mode = None

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'li':
            self.active = False
        return

    def handle_data(self, data):

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
            self.pitch.location = data
            self.mode = None

        elif self.active and self.mode == 'type':
            data = re.sub(' +', ' ', data)
            self.pitch.type = data
            self.mode = None

        elif self.active and self.mode == 'sectors':
            sectors = [d.strip(' ') for d in data.split(',')]
            self.pitch.sector_1 = sectors.pop() if len(sectors) > 0 else None
            self.pitch.sector_2 = sectors.pop() if len(sectors) > 0 else None
            self.pitch.sector_3 = ','.join(sectors)
            self.mode = None


class CompanyParser(html.parser.HTMLParser):
    def __init__(self, pitch: Pitch):
        super().__init__()
        self.pitch = pitch
        self.active = False
        self.mode = None

    def handle_starttag(self, tag, attrs):
        if self.active:
            if tag == 'label':
                self.mode = 'parse_label'

        else:
            for (key, value) in attrs:
                if tag == 'ul' and key == 'class' and value == 'company-details-list':
                    self.active = True

    def handle_endtag(self, tag):
        if self.active and tag == 'ul':
            self.active = False
        return

    def handle_data(self, data):
        data = data.replace('\n', '').strip(' ')
        if len(data) == 0:
            return

        if self.mode == 'parse_label':
            if data == 'Company number:':
                self.mode = 'company_number'
            elif data == 'Incorporation date:':
                self.mode = 'company_founded'
            else:
                self.mode = None

        elif self.mode == 'company_number':
            self.pitch.company_number = data
            self.mode = None
        elif self.mode == 'company_founded':
            self.pitch.founded = data
            self.mode = None


def parse(include_funded = False) -> pd.DataFrame:
    pitches = []

    if include_funded:
        # Load all funded pitches
        funded_pitches_url='https://www.crowdcube.com/investments?sort_by=0&q=&joined=3&hof=1&i1=0&i2=0&i3=0&i4=0&sort_by=7'
        funded_pitches_html = page_loader.get_page(funded_pitches_url)
        funded_pitches_parser = SummaryParser()
        funded_pitches_parser.feed(funded_pitches_html)
        print('CROWDCUBE - Found {0} funded pitches'.format(len(funded_pitches_parser.pitches)))
        for pitch in funded_pitches_parser.pitches:
            pitches.append(pitch)

    # Load all open pitches
    open_pitches_url='https://www.crowdcube.com/investments?sort_by=0&q=&joined=3&hof=0&i1=0&i2=0&i3=0&i4=0&sort_by=7'
    open_pitches_html = page_loader.get_page(open_pitches_url)
    open_pitches_parser = SummaryParser()
    open_pitches_parser.feed(open_pitches_html)
    print('CROWDCUBE - Found {0} open pitches'.format(len(open_pitches_parser.pitches)))
    for pitch in open_pitches_parser.pitches:
        pitches.append(pitch)

    num = 0
    for pitch in pitches:
        num += 1
        if pitch.pitch_url:
            try:
                print('CROWDCUBE - Fetching ({0} / {1}) pitch data from {2}'.format(num, len(pitches), pitch.pitch_url))
                pitch_html = page_loader.get_page(pitch.pitch_url)
                detail_parser = DetailParser(pitch)
                detail_parser.feed(pitch_html)

                company_detail_url = pitch.pitch_url.replace('/investment/','/company-details/')
                print('CROWDCUBE - Fetching ({0} / {1}) data from {2}'.format(num, len(pitches), company_detail_url))
                company_detail_html = page_loader.get_page(company_detail_url)
                detail_parser = CompanyParser(pitch)
                detail_parser.feed(company_detail_html)

            except:
                print('Failed to fetch pitch data for: {0}'.format(pitch.pitch_url))

    df = pd.DataFrame([pitch.__dict__ for pitch in pitches])
    df = df.dropna(axis=0, how='all')
    df['Source'] = 'Crowdcube'
    return df


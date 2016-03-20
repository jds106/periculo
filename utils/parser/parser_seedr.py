import pandas as pd
import os
import html.parser
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
        if tag == 'article':
            self.current_pitch = Pitch()

            for (key, value) in attrs:
                if key == 'data-campaign-categories':
                    sectors = [s.strip(' ') for s in value.split(',')]
                    self.current_pitch.sector_1 = sectors.pop() if len(sectors) > 0 else None
                    self.current_pitch.sector_2 = sectors.pop() if len(sectors) > 0 else None
                    self.current_pitch.sector_3 = ','.join(sectors)
                elif key == 'data-campaign-id':
                    self.current_pitch.campaign_id = value
                elif key == 'data-campaign-name':
                    self.current_pitch.company = value
                elif key == 'data-campaign-type':
                    self.current_pitch.type = value

        elif self.current_pitch is not None:
            for (key, value) in attrs:
                if key == 'class':
                    values = value.split(' ')
                    if 'CampaignCard-country' in values:
                        self.mode = 'country'
                    elif 'CampaignCard-taxIncentives' in values:
                        self.mode = 'taxIncentives'
                    elif 'CampaignCard-statTitle' in values:
                        self.mode = 'stats'
                    elif 'CampaignCard-progressMessage' in values:
                        self.mode = 'CampaignCard-progressMessage'

    def handle_endtag(self, tag):
        if tag == 'article':
            if self.current_pitch:
                self.pitches.append(self.current_pitch)
            self.current_pitch = None

    def handle_data(self, data):
        data = data.strip(' \n')
        if len(data) == 0:
            return

        if self.mode == 'country':
            self.current_pitch.country = data
            self.mode = None

        elif self.mode == 'taxIncentives':
            self.current_pitch.scheme = data
            self.mode = None

        elif self.mode == 'stats':
            if data == 'Equity':
                self.mode = 'stats.equity'
            elif data == 'Investment':
                self.mode = 'stats.investment'
            elif data == 'Investors':
                self.mode = 'stats.investors'

        elif self.mode == 'stats.equity':
            self.current_pitch.equity_perc_offered = data
            self.mode = None

        elif self.mode == 'stats.investment':
            self.current_pitch.investment_required = data
            self.mode = None

        elif self.mode == 'stats.investors':
            self.current_pitch.num_investors = data
            self.mode = None

        elif self.mode == 'CampaignCard-progressMessage':
            self.current_pitch.days_left = data
            self.mode = None


class DetailParser(html.parser.HTMLParser):
    def __init__(self, pitches: dict):
        super().__init__()
        self.pitches = pitches
        self.mode = None
        self.mode_active = False
        self.current_pitch = None

    def handle_starttag(self, tag, attrs):
        if tag == 'dd' and self.mode:
            self.mode_active = True

        else:
            for (key, value) in attrs:
                if key == 'data-campaign-name':
                    self.current_pitch = self.pitches[value]

                elif key == 'class':
                    values = value.split(' ')
                    if 'investment_already_funded' in values:
                        self.mode = 'investment_already_funded'
                        self.mode_active = False
                    elif 'valuation' in values:
                        self.mode = 'valuation'
                        self.mode_active = False
                    elif 'location' in values:
                        self.mode = 'location'
                        self.mode_active = False

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        if not self.current_pitch:
            return

        if isinstance(data, str):
            data = data.strip(' ').replace('\n','')
            if len(data) > 0:
                if self.mode_active:
                    if self.mode == 'investment_already_funded':
                        self.current_pitch.investment_received = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'Incorporation date':
                        self.current_pitch.founded = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'Registered number':
                        self.current_pitch.company_number = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'location':
                        self.current_pitch.location = data
                        self.mode = None
                        self.mode_active = False

                if data == 'Incorporation date':
                    self.mode = 'Incorporation date'
                elif data == 'Registered number':
                    self.mode = 'Registered number'

def parse() -> pd.DataFrame:
    src_dir = '../../data/Seedrs'
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

    src_dir = '../../data/Seedrs/detail'
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
    df['Source'] = 'Seedrs'
    return df

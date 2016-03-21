import pandas as pd
import os
import html.parser
from utils.parser.pitch import Pitch
from utils.parser.seedr import page_loader

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
                    p = self.current_pitch
                    (p.sector_1, p.sector_2, p.sector_3) = self._parse_sectors(sectors)
                elif key == 'data-campaign-id':
                    self.current_pitch.pitch_id = value
                elif key == 'data-campaign-name':
                    self.current_pitch.company = value
                elif key == 'data-campaign-type':
                    self.current_pitch.type = value

        elif self.current_pitch is not None:
            is_pitch_link = False
            for (key, value) in attrs:
                if key == 'class':
                    values = value.split(' ')
                    if 'CampaignCard-taxIncentives' in values:
                        self.mode = 'taxIncentives'
                    elif 'CampaignCard-statTitle' in values:
                        self.mode = 'stats'
                    elif 'CampaignCard-progressMessage' in values:
                        self.mode = 'CampaignCard-progressMessage'
                    elif 'Card-link' in values:
                        is_pitch_link = True
                elif key == 'href' and is_pitch_link:
                    self.current_pitch.pitch_url = 'https://www.seedrs.com{0}'.format(value)
                    is_pitch_link = False

    def handle_endtag(self, tag):
        if tag == 'article':
            if self.current_pitch:
                self.pitches.append(self.current_pitch)
            self.current_pitch = None

    def handle_data(self, data):
        data = data.strip(' \n')
        if len(data) == 0:
            return

        if self.mode == 'taxIncentives':
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
            self.current_pitch.days_left = self._parse_days(data)
            self.mode = None

    def _parse_days(self, data: str):
        # Examples:
        #       23 days to go - 24% Funded          -> 23
        #       Open for investment - 100% Funded   -> None
        if data and len(data) > 0:
            possible_days = data.split(' ')
            try:
                return int(possible_days[0])
            except:
                return None
        else:
            return None

    def _parse_sectors(self, sectors: list) -> (str, str, str):
        s1 = None
        s2 = None
        s3 = []

        for sector in sectors:
            assert(isinstance(sector, str))
            s1_match = [sector.find(s) != -1 for s in ['B2B', 'B2C', 'B2G']]
            s1_filter = [match for match in filter(lambda s: s, s1_match)]
            if len(s1_filter) > 0:
                s1 = sector
            elif sector.startswith('Mixed') or sector in ['Digital', 'Non-Digital']:
                s2 = sector
            else:
                s3.append(sector)

        return s1, s2, ','.join(s3)



class DetailParser(html.parser.HTMLParser):
    def __init__(self, pitch: Pitch):
        super().__init__()
        self.pitch = pitch
        self.mode = None
        self.mode_active = False

    def handle_starttag(self, tag, attrs):
        if tag == 'dd' and self.mode:
            self.mode_active = True

        else:
            for (key, value) in attrs:
                if key == 'class':
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
        if isinstance(data, str):
            data = data.strip(' ').replace('\n','')
            if len(data) > 0:
                if self.mode_active:
                    if self.mode == 'investment_already_funded':
                        self.pitch.investment_received = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'Incorporation date':
                        self.pitch.founded = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'Registered number':
                        self.pitch.company_number = data
                        self.mode = None
                        self.mode_active = False

                    elif self.mode == 'location':
                        self.pitch.location = data
                        self.mode = None
                        self.mode_active = False

                if data == 'Incorporation date':
                    self.mode = 'Incorporation date'
                elif data == 'Registered number':
                    self.mode = 'Registered number'


def parse() -> pd.DataFrame:
    pitches_url = 'https://www.seedrs.com/invest'
    pitches_html = page_loader.get_page(pitches_url)
    pitches_parser = SummaryParser()
    pitches_parser.feed(pitches_html)
    print('SEEDR - Found {0} open pitches'.format(len(pitches_parser.pitches)))

    for pitch in pitches_parser.pitches:
        if pitch.pitch_url:
            print('SEEDR - Fetching pitch data from {0}'.format(pitch.pitch_url))
            pitch_html = page_loader.get_page(pitch.pitch_url)
            pitch_parser = DetailParser(pitch)
            pitch_parser.feed(pitch_html)

    df = pd.DataFrame([pitch.__dict__ for pitch in pitches_parser.pitches])
    df = df.dropna(axis=0, how='all')
    df['Source'] = 'Seedrs'
    return df


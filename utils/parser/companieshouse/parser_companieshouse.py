import urllib
import urllib.request
import http.client
import html.parser


class SummaryParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.company_status = None
        self.company_incorporated = None

    def handle_starttag(self, tag, attrs):
        if tag == 'dt':
            self.mode = 'label'

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        data = data.replace('\n', '').replace('\r', '').strip(' ')
        if len(data) == 0:
            return

        if self.mode == 'label':
            if data == 'Company status':
                self.mode = 'status'
            elif data == 'Incorporated on':
                self.mode = 'incorporated'
            else:
                self.mode = None
        elif self.mode == 'status':
            self.company_status = data
            self.mode = None
        elif self.mode == 'incorporated':
            self.company_incorporated = data
            self.mode = None


def _fetch_company_data(company_number: str):
    url = 'https://beta.companieshouse.gov.uk/company/{0}'.format(company_number)
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode()
    except:
        print('No company information found for {0}'.format(company_number))
        return None


def parse(company_number: str) -> (str, str):
    html = _fetch_company_data(company_number)
    if not html:
        return None

    parser = SummaryParser()
    parser.feed(html)
    return parser.company_status, parser.company_incorporated


import urllib
import urllib.request
import html.parser
from base64 import b64encode


class SummaryParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.company_status = None
        self.company_incorporated = None
        self.company_type = None

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
            elif data == 'Company type':
                self.mode = 'company_type'
            else:
                self.mode = None
        elif self.mode == 'status':
            self.company_status = data
            self.mode = None
        elif self.mode == 'incorporated':
            self.company_incorporated = data
            self.mode = None
        elif self.mode == 'company_type':
            self.company_type = data
            self.mode = None


def _fetch_company_data(company_number: str):

    api_token = 'nFBsAgLcP6j3-8t6-3kTUB76RG7uq82rMQk3JV3o'
    api_auth = b64encode('{0}:{1}'.format(api_token,'').encode()).decode()

    req = urllib.request.Request(
            url='https://api.companieshouse.gov.uk/company/04877859/officers',
            headers={
                'Authorization':'Basic {0}'.format(api_auth)
            })

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode()
    except Exception as e:
        print('No company information found for {0}: {1}'.format(company_number, e))
        return None


def parse(company_number: str) -> (str, str, str):
    html = _fetch_company_data(company_number)
    if not html:
        return None

    parser = SummaryParser()
    parser.feed(html)
    return parser.company_status, parser.company_incorporated, parser.company_type

print(_fetch_company_data(''))
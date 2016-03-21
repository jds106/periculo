
class Pitch:
    pitch_id = None
    pitch_url = None
    company = None
    founded = None
    company_number = None
    location = None
    equity_perc_offered = None
    investment_required = None
    investment_received = None
    num_investors = None
    pre_valuation = None
    sector_1 = None
    sector_2 = None
    sector_3 = None
    days_left = None
    start = None
    end = None
    pitch_period = None
    scheme = None

    def __init__(self):
        return

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))
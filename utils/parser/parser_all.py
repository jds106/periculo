import utils.parser.crowdcube.parser_crowdcube as parser_crowdcube
import utils.parser.seedr.parser_seedr as parser_seedr
import utils.parser.companieshouse.parser_companieshouse as parser_companieshouse
import pandas as pd


def pitch_fetcher() -> pd.DataFrame:
    df_seedr = parser_seedr.parse()
    df_crowdcube = parser_crowdcube.parse(include_funded=True)

    assert(isinstance(df_crowdcube, pd.DataFrame))
    assert(isinstance(df_seedr, pd.DataFrame))

    all_df = df_crowdcube.append(df_seedr)
    assert(isinstance(all_df, pd.DataFrame))
    all_df.to_csv('../../data/all.csv', sep='\t', index=False)
    return all_df


def pitch_loader() -> pd.DataFrame:
    df = pd.read_csv('../../data/all.csv', sep='\t', dtype={'company_number': str})
    assert(isinstance(df, pd.DataFrame))
    df[['companies_house_status','companies_house_incorporated']] = df.company_number.apply(lambda num: parser_companieshouse.parse(num)).apply(pd.Series)
    df.to_csv('../../data/all_with_ch.csv', sep='\t', index=False)
    return df

pitch_loader()

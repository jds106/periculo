import utils.parser.parser_crowdcube as parser_crowdcube
import utils.parser.parser_seedr as parser_seedr
import pandas as pd

df_crowdcube = parser_crowdcube.parse()
df_seedr = parser_seedr.parse()

assert(isinstance(df_crowdcube, pd.DataFrame))
assert(isinstance(df_seedr, pd.DataFrame))

print(df_crowdcube.append(df_seedr))
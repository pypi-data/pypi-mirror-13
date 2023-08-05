import six
from six.moves import configparser as CP
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import create_engine

# TODO want to probabilistically infer what a mixed dtype column type is

def df_drop_cols(df, cols):
    return df.drop(cols, axis=1)

def df_encode_factor_cols(df, cols):
    obj_df = df[cols].astype(object)
    encode_df = pd.get_dummies(obj_df[cols])
    ret_df = df_drop_cols(df, cols)
    return pd.concat([ret_df, encode_df], axis=1)

def df_convert_dates(df, cols):
    # TODO
    # Convert dates
    X[date_cols] = X[date_cols].apply(pd.to_datetime)

    new_cols = [c + '_month' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.month)
    numeric_cols += new_cols

    new_cols = [c + '_day' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.day)
    numeric_cols += new_cols

    new_cols = [c + '_dayofyear' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.dayofyear)
    numeric_cols += new_cols

    new_cols = [c + '_week' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.week)
    numeric_cols += new_cols

    new_cols = [c + '_weekday' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.weekday)
    numeric_cols += new_cols

    new_cols = [c + '_quarter' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.quarter)
    numeric_cols += new_cols

    new_cols = [c + '_year' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.year)
    numeric_cols += new_cols

    new_cols = [c + '_is_month_start' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_month_start)

    new_cols = [c + '_is_month_end' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_month_end)

    new_cols = [c + '_is_quarter_start' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_quarter_start)

    new_cols = [c + '_is_quarter_end' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_quarter_end)

    new_cols = [c + '_is_year_start' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_year_start)

    new_cols = [c + '_is_year_end' for c in date_cols]
    X[new_cols] = X[date_cols].apply(lambda x: x.dt.is_year_end)

    X = X.drop(date_cols, axis=1)
    year_df = X[year_cols]
    year_df = year_df.where((pd.notnull(year_df)), None) # convert NaN to None
    year_df = year_df.apply(lambda x: pd.to_datetime(x, format='%Y', coerce=True))
    X[year_cols] = year_df
    X[year_cols] = X[year_cols].apply(lambda x: x.dt.year)
    numeric_cols += year_cols

    return "!!!! TODO"

def df_standardize_numeric(df, numeric_cols):
    # Standardize numeric columns
    num_df = X[numeric_cols].astype(np.float64)
    num_df = (num_df - num_df.mean())/num_df.std()
    ret_df = X.drop(numeric_cols, axis=1)
    X = pd.concat([ret_df, num_df], axis=1)

    return "!!!!! TODO"

def preprocess(data,
               drop_cols=None,
               factor_cols=None,
               date_cols=None,
               numeric_cols=None):
    """
    TODO
    """

    df = pd.DataFrame(data)

    df = df_drop_cols(df, drop_cols)
    df = df_encode_factor_cols(df, factor_cols)
    df = df_encode_dates(df, date_cols)
    df = df_standardize_numeric(df, numeric_cols)

    # Fill NaN values
    X = X.fillna(X.mean())

    return X

def sql_preprocess_table(table, **kwargs):
    """
    Initailize a dataframe using probabilistic data cleaning heuristics from a sql table.
    """
    # TODO df from sql table

    return magic_preprocess(df, **kwargs)

def proportion_na(df):
    pass

def duplicate_rows(df):
    pass

def constant_columns(df):
    pass

def infer_column_type(df, col):
    # hist of characters...
    # match to thingy
    pass

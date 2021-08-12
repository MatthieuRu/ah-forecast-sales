import pandas as pd
from datetime import datetime
from pandarallel import pandarallel


def get_data(path: str) -> pd.DataFrame:
    """Read the data from a path

    Args:
        path (str): path to get the date

    Returns:
        pd.DataFrame: dataframe of the data
    """
    return pd.read_parquet(path)


def get_procceed_data() -> pd.DataFrame:
    """Clean and add variables used for the modelisation.

    Returns:
        pd.DataFrame:  dataframe of the proceed data
    """

    path = "./assets/dataset.parquet"
    # Path to the data parquet file
    df = get_data(path)
    print('Number of observation:', len(df))
    print('Number of features:', len(list(df)))

    # Useless Column (No different Value)
    uselessColumns = [x for x in list(df) if len(df[x].unique()) == 1]
    print(
        'Variable with an unique Value',
        uselessColumns
    )
    df = df.drop(columns=uselessColumns)

    # Create Column dummies values only for Hollydays
    isNationalHolidayColumns = [x for x in list(df) if 'national_holiday' in x]
    df['isNationalHoliday'] = df[isNationalHolidayColumns].max(axis=1)
    isSchoolHolidayColumns = [x for x in list(df) if 'SchoolHoliday' in x]
    df[isSchoolHolidayColumns] = df[isSchoolHolidayColumns].fillna(0)
    df['isSchoolHoliday'] = df[isSchoolHolidayColumns].sum(axis=1)

    # Create a column for Years and month
    df['years'] = df['DateKey'].apply(lambda x: str(x)[0:4])
    df['month'] = df['DateKey'].apply(lambda x: str(x)[4:6])

    # Column with NaN values
    NaNColumns = [x for x in list(df) if len(df[df[x].isna()]) > 1]
    for column in NaNColumns:
        print(
            'Variable with NaN Value for',
            column,
            len(df[df[column].isna()]) / len(df)
        )

    # Transforn the DateKey to a proper variable

    def func(x):
        return datetime.strptime(str(x), '%Y%m%d')

    pandarallel.initialize()
    df['DateKey'] = df.DateKey.parallel_apply(lambda x: func(x))

    # Drop some observation with None Values ShelfCapacity / UnitSales - See explanation Markdown Below
    df = df[
        (~df.ShelfCapacity.isna()) &
        (~df.UnitSales.isna())
    ]

    categorical_variable = [
        x for x in list(df) if 'holiday' in x.lower()
    ] + [
        'ItemNumber', 'GroupCode', 'CategoryCode', 'CommunicationChannel'
    ]

    df[categorical_variable] = df[categorical_variable].astype("category")

    print('Number of observation:', len(df))
    print('Number of features:', len(list(df)))

    # Create code for communication Channel
    df['CommunicationChannelCode'] = df.CommunicationChannel.cat.codes
    return df


def get_sample(df: pd.DataFrame, n=10, sample_extract=True) -> pd.DataFrame:
    """Return a dataFrame to use for the evaluation.
        or to get only the data we want to forecats
        at least 25 observation IsPromo = True in 2017
        at least 25 observation IsPromo = False in 2017

    Args:
        df (pd.DataFrame): full dataset to look for good times series
        n (int, optional): number of ItemNumber we want. Defaults to 10.
        sample_extract (bool, optional): if we want the full list we can by sample_extract = False.
         Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with the good ItemNumber and the number of observation.
    """
    # We select only the dara with more than 25 point for IsPromo True and False
    # There is a parameter for every changepoint (n_changepoints of them, default 25)
    # To use as minimum of point above the number of n_changepoints

    sample = df.groupby(['ItemNumber', 'IsPromo', 'years']).size().reset_index().rename(
        columns={0: 'nb_observations'}
    )

    IsPromoItemNumber = sample[
        (sample.IsPromo) &
        (sample.nb_observations > 25) &
        (sample.years == '2017')
    ].ItemNumber.tolist()

    IsNotPromoItemNumber = sample[
        (~sample.IsPromo) &
        (sample.nb_observations > 25) &
        (sample.years == '2017')
    ].ItemNumber.tolist()

    sample = df.groupby(['ItemNumber']).size().reset_index().rename(
        columns={0: 'nb_observations'}
    )

    if sample_extract:
        sample = sample[
            (sample.ItemNumber.isin(IsPromoItemNumber)) &
            (sample.ItemNumber.isin(IsNotPromoItemNumber))
        ].sample(n=n, random_state=1)
    else:
        sample = sample[
            (sample.ItemNumber.isin(IsPromoItemNumber)) &
            (sample.ItemNumber.isin(IsNotPromoItemNumber))
        ]

    return sample

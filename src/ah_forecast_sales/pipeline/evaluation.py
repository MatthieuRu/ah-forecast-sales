from src.ah_forecast_sales.pipeline.fbProphetMultivariate import fbProphetMultivariate
from src.ah_forecast_sales.pipeline.fbProphetUnivariate import fbProphetUnivariate
import pandas as pd
from typing import List


def get_evaluation_fbProphetUnivariate(
    sample: pd.DataFrame,
    df: pd.DataFrame,
    ItemNumber: str,
    model_name: str
) -> pd.DataFrame:
    """Add the RMSE and NRMSE for a ItemNumber.
    Run the univariate model and then compile the evaluation of this one.

    Args:
        sample (pd.DataFrame): DataFrame to fill by the RMSE and NRMSE
        df (pd.DataFrame): The full dataset using to create the model
        ItemNumber (str): the ItemNumber wanted to create the model.
        model_name (str): The name to track the model used (uniqueIdentifier)

    Returns:
        pd.DataFrame: the same dataframe with value for the RMSE and NRMSE
    """
    # Step 1 - fb Prophet Univariate 2016 / 2017
    tmp = df[
        (df.ItemNumber == ItemNumber)
    ].copy()
    fb_prophet_forecast = fbProphetUnivariate(tmp, start_date='2018-01-01')

    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_RMSE_12ear'
    ] = fb_prophet_forecast.rmse
    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_NRMSE_2year'
    ] = fb_prophet_forecast.nrmse

    # Step 2 - fb Prophet Univariate  2016
    tmp = df[
        (df.ItemNumber == ItemNumber) &
        (df.years == '2017')
    ].copy()
    fb_prophet_forecast = fbProphetUnivariate(tmp, start_date='2018-01-01')

    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_RMSE_1year'
    ] = fb_prophet_forecast.rmse
    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_NRMSE_1year'
    ] = fb_prophet_forecast.nrmse

    return sample


def get_evaluation_fbProphetMultivariate(
    sample: pd.DataFrame,
    df: pd.DataFrame,
    ItemNumber: str,
    model_name: str,
    regressors: List(str),
    log: bool
) -> pd.DataFrame:
    """Add the RMSE and NRMSE for a ItemNumber.
    Run the multivariate model and then compile the evaluation of this one.

    Args:
        sample (pd.DataFrame): DataFrame to fill by the RMSE and NRMSE
        df (pd.DataFrame): The full dataset using to create the model
        ItemNumber (str): the ItemNumber wanted to create the model.
        model_name (str): The name to track the model used (uniqueIdentifier)
        regressors (List(str)): List of regressors we want to use for the model
        log (bool): True or False if we want to use a logarithm transformation

    Returns:
        pd.DataFrame: the same dataframe with value for the RMSE and NRMSE
    """
    # Step 1 - fb Prophet Univariate 2016 / 2017
    tmp = df[
        (df.ItemNumber == ItemNumber)
    ].copy()
    fb_prophet_forecast = fbProphetMultivariate(
        tmp,
        start_date='2018-01-01',
        regressors=regressors,
        log=log
    )

    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_RMSE_12ear'
    ] = fb_prophet_forecast.rmse
    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_NRMSE_2year'
    ] = fb_prophet_forecast.nrmse

    # Step 2 - fb Prophet Univariate  2016
    tmp = df[
        (df.ItemNumber == ItemNumber) &
        (df.years == '2017')
    ].copy()
    fb_prophet_forecast = fbProphetMultivariate(
        tmp,
        start_date='2018-01-01',
        regressors=regressors
    )
    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_RMSE_1year'
    ] = fb_prophet_forecast.rmse
    # NRMSE
    sample.loc[
        sample.ItemNumber == ItemNumber,
        model_name + '_NRMSE_1year'
    ] = fb_prophet_forecast.nrmse

    return sample

from numpy import integer
from pandas.core.arrays import boolean
from fbprophet import Prophet
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from typing import List
from sklearn.metrics import mean_squared_error
from math import sqrt
import numpy as np


class fbProphetMultivariate():
    """
        Model Class to:
        - train a model 
        - get the differents KPI associate to the model 
        - forecasts Unit Sales for the comming week.
        The model use IsPromo as a regressors, but more regressors
        can be add to the fb Prophet model
    """

    def __init__(
        self,
        data: pd.DataFrame,
        start_date: str,
        regressors=[],
        log=False
    ) -> None:
        """Init the  fbProphetMultivariate Model Class.

        Args:
            data (pd.DataFrame): data including the times series to train the model.
            start_date (str): start date to start the forecast of the week.
            regressors (list, optional): list of variable we want to use as regressors
                . Defaults to [].
            log (bool): True or False if we want to use a logarithm transformation
            Defaults to False.
        """
        # rename the column to follow the rules of the library
        self.data = data.rename(
            columns={
                'DateKey': 'ds',
                'UnitSales': 'y'
            }
        )

        self.data
        self.regressors = regressors
        self.model = self._get_model(log)
        self.forecast = self.get_forecast(
            start_date,
            log
        )
        self.metrics = self._get_metrics()
        self.rmse = self._get_rmse()
        self.nrmse = self._get_nrmse()

    def _get_model(self, log: bool) -> Prophet:
        """Get the model used for the class.

        Args:
            log (bool): True or False if we want to use a logarithm transformation
            Defaults to False.
        Returns:
            Prophet: Prophet class of the fb prophet library.
        """
        model = Prophet(
            interval_width=0.95,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.add_regressor('IsPromo')

        for regressor in self.regressors:
            model.add_regressor(regressor)
        if log:
            tmp = self.data.copy()
            tmp.y = np.log(tmp.y)
            model.fit(tmp)
        else:
            model.fit(self.data)

        return model

    def get_forecast(
        self,
        start_date: str,
        log: bool
    ) -> pd.DataFrame:
        """Get the DataFrame with the forecast done by the model, on old 
        and future week after the start date.

        Args:
            start_date (str): start date to start the forecast of the week.
            log (bool): True or False if we want to use a logarithm transformation
            Defaults to False.
        Returns:
            pd.DataFrame: Data including all the forecast on the old data and future
            week after the start date
        """
        start_datetime = dt.datetime.strptime(start_date, '%Y-%m-%d')
        future_datesIsPromo = pd.DataFrame({
            'ds': [start_datetime + dt.timedelta(days=i) for i in range(1, 8)]
        })
        future_datesIsPromo['IsPromo'] = True

        future_datesIsNotPromo = pd.DataFrame({
            'ds': [start_datetime + dt.timedelta(days=i) for i in range(1, 8)]
        })
        future_datesIsNotPromo['IsPromo'] = False

        for regressor in self.regressors:
            future_datesIsPromo[regressor] = 1
            future_datesIsNotPromo[regressor] = 0

        future_dates = pd.concat([
            self.data[['ds', 'IsPromo'] + self.regressors],
            future_datesIsPromo,
            future_datesIsNotPromo,
        ])
        forecast = self.model.predict(future_dates)
        if log:
            forecast.yhat = np.exp(forecast.yhat)

        return forecast

    def _get_plot_component(self) -> None:
        """Display the plot of the component of the model
        """
        print('Component For Forecast Product')
        print('First two Graphs Not in Promotion')
        print('Last two Graphs in Promotion')
        fig = self.model.plot_components(
            self.forecastIsNotPromo,
        )
        fig.show()

    def _get_rmse(self) -> float:
        """Get the rmse of the model.

        Returns:
            float: rmse of the model
        """
        rmse = sqrt(mean_squared_error(
            self.metrics.y,
            self.metrics.yhat
        ))
        return rmse

    def _get_nrmse(self) -> float:
        """Get the nrmse of the model.

        Returns:
            float: nrmse of the model
        """
        nrmse = self.rmse / self.metrics.y.mean()
        return nrmse

    def _get_metrics(self) -> pd.DataFrame:
        """Final metrics dataframe including the actual and forecast values

        Returns:
            pd.DataFrame: metrics dataframe
        """
        metrics = self.forecast.merge(
            self.data[['ds', 'y', 'IsPromo'] + self.regressors],
            how='inner',
            on='ds'
        ).sort_values('ds', ascending=False)

        return metrics

    def get_vizualisation_metrics(self):
        """Return the vizualisation on the actual vs forecast data
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Actual",
            x=self.metrics.ds,
            y=self.metrics.y,
        ))
        fig.add_trace(go.Bar(
            name="Forecast",
            x=self.metrics.ds,
            y=self.metrics.yhat,
        ))
        fig.update_layout(title_text='Final Times Series of Daily UniteSales')

        return fig

    def get_vizualisation(self):
        """Return the vizualisation on the actual vs forecast data
            split by Pomotion or not and the forecast for the next week
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="No Promotion",
            x=self.data[~self.data.IsPromo].ds,
            y=self.data[~self.data.IsPromo].y,
        ))

        fig.add_trace(go.Bar(
            name="Promotion",
            x=self.data[self.data.IsPromo].ds,
            y=self.data[self.data.IsPromo].y,
        ))

        fig.add_trace(go.Bar(
            name="Forecast No Promotion",
            x=self.forecast[self.forecast.IsPromo < 0.1].ds,
            y=self.forecast[self.forecast.IsPromo < 0.1].yhat,
        ))

        fig.add_trace(go.Bar(
            name="Forecast Promotion",
            x=self.forecast[self.forecast.IsPromo > 0.1].ds,
            y=self.forecast[self.forecast.IsPromo > 0.1].yhat,
        ))

        fig.update_layout(title_text='Times Series of Daily UniteSales')
        return fig

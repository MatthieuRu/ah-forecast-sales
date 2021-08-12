from fbprophet import Prophet
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error
from math import sqrt


class fbProphetUnivariate():
    """
        Model Class to:
        - train a model 
        - get the differents KPI associate to the model 
        - forecasts Unit Sales for the comming week.
        The model concatenates two  models, using:
         - data with IsPromo = True
         - data with IsPromo = False

    """

    def __init__(self, data: pd.DataFrame, start_date: str) -> None:
        """Init the  fbProphetUnivariate Model Class.

        Args:
            data (pd.DataFrame): data including the times series to train the model.
            start_date (str): start date to start the forecast of the week.
        """
        # rename the column to follow the rules of the library
        self.data = data.rename(
            columns={
                'DateKey': 'ds',
                'UnitSales': 'y'
            }
        )
        data['floor'] = 0
        self.data
        self.modelIsPromo = self._get_modelIsPromo()
        self.modelIsNotPromo = self._get_modelIsNotPromo()
        self.forecastIsPromo = self.get_forecast(
            start_date,
            self.modelIsPromo
        )
        self.forecastIsNotPromo = self.get_forecast(
            start_date,
            self.modelIsNotPromo
        )
        self.metrics = self._get_metrics()
        self.rmse = self._get_rmse()
        self.nrmse = self._get_nrmse()

    def _get_modelIsPromo(self) -> Prophet:
        """Get the model for promotion used for the class.

        Returns:
            Prophet: Prophet class of the fb prophet library.
            model where the data isPromo = True
        """
        model = Prophet(
            interval_width=0.95,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.fit(self.data[self.data.IsPromo])
        return model

    def _get_modelIsNotPromo(self) -> Prophet:
        """Get the model for not-promotion used for the class.

        Returns:
            Prophet: Prophet class of the fb prophet library.
            model where the data isPromo = False
        """
        model = Prophet(
            interval_width=0.95,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.fit(self.data[~self.data.IsPromo])
        return model

    def get_forecast(self, start_date: str, model: Prophet) -> pd.DataFrame:
        """Get the DataFrame with the forecast done by the model, on old 
        and future week after the start date.

        Args:
            start_date (str): start date to start the forecast of the week.
            model (Prophet): the model used to get the forecast (Promotion or not)
        Returns:
            pd.DataFrame: Data including all the forecast on the old data and future
            week after the start date
        """
        start_datetime = dt.datetime.strptime(start_date, '%Y-%m-%d')
        future_dates = pd.DataFrame({
            'ds': [start_datetime + dt.timedelta(days=i) for i in range(1, 8)]
        })
        future_dates = pd.concat([
            self.data[['ds']],
            future_dates
        ])

        forecast = model.predict(future_dates)
        return forecast

    def _get_metrics(self) -> pd.DataFrame:
        """Final metrics dataframe including the actual and forecast values

        Returns:
            pd.DataFrame: metrics dataframe
        """
        metrics = pd.concat([
            self.forecastIsPromo.merge(
                self.data[
                    self.data.IsPromo
                ][['ds', 'y', 'IsPromo']],
                how='inner',
                on='ds'
            ),
            self.forecastIsNotPromo.merge(
                self.data[
                    ~self.data.IsPromo
                ][['ds', 'y', 'IsPromo']],
                how='inner',
                on='ds'
            ),
        ]).sort_values('ds', ascending=False)

        return metrics

    def _get_plot_component(self):
        """Display the plot of the component of the model
        """
        print('Component For Forecast Product')
        print('First two Graphs Not in Promotion')
        print('Last two Graphs in Promotion')
        fig = self.modelIsNotPromo.plot_components(
            self.forecastIsNotPromo,
        )

        self.modelIsPromo.plot_components(
            self.forecastIsPromo,
        ).show()

    def _get_rmse(self):
        """Get the rmse of the model.

        Returns:
            float: rmse of the model
        """
        rmse = sqrt(mean_squared_error(
            self.metrics.y,
            self.metrics.yhat
        ))
        return rmse

    def _get_nrmse(self):
        """Get the nrmse of the model.

        Returns:
            float: nrmse of the model
        """
        nrmse = self.rmse / self.metrics.y.mean()
        return nrmse

    def get_vizualisation_metrics(self) -> pd.DataFrame:
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
        fig.update_layout(title_text='FInale Times Series of Daily UniteSales')

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
            name="Forecast No pomotion",
            x=self.forecastIsNotPromo.ds,
            y=self.forecastIsNotPromo.yhat,
        ))

        fig.add_trace(go.Bar(
            name="Forecast Promotion",
            x=self.forecastIsPromo.ds,
            y=self.forecastIsPromo.yhat,
        ))

        fig.update_layout(
            title_text='Times Series based Promotion for daily UnitSales')
        return fig

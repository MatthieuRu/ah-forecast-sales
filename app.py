import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from src.ah_forecast_sales.pipeline.fbProphetMultivariate import fbProphetMultivariate
from src.ah_forecast_sales.utils.exploratory_analysis import get_procceed_data
from src.ah_forecast_sales.utils.exploratory_analysis import get_sample


# ---------- Parameter of the app
app = dash.Dash(
    __name__,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.title = "Forecast Sales"
app_color = {"graph_bg": "#F2F6FC", "graph_line": "#007ACE"}
server = app.server


# ---------- Read the file
data = get_procceed_data()
data = data[
    data.ItemNumber.isin(get_sample(data, n=1000).ItemNumber)
]

ItemNumber_ = '10469'
itemNumberSample = data[
    data.ItemNumber == ItemNumber_
].copy()


# ---------- Layer of the App

app.layout = html.Div([
    html.Div(
        [
            html.H4("Forecast Unit Sales",
                    className="app__header__title"),
            html.P(
                "This app allows you to forecast for a product the number of UnitSales and the effect if of the promotion.",
                className="app__header__title--grey",
            ),
            html.P(
                "Select a ItemNumber:",
                className="app__header__title--grey",
            ),
        ],
        className="app__header__desc",
    ),
    dcc.Dropdown(
        id="ItemNumber",
        options=[{"label": x, "value": x}
                 for x in list(data.ItemNumber.unique())],
        value='10469',
        clearable=False,
    ),
    dcc.Graph(id="ForecastGraph")
])


# ---------- update Data when we choose a new product
@app.callback(
    Output('ForecastGraph', 'figure'),
    # Input("btn-nclicks-1", "n_clicks"),
    Input("ItemNumber", "value")
)
def get_figure(ItemNumber_: str):
    print(ItemNumber_)
    itemNumberSample = data[
        data.ItemNumber == ItemNumber_
    ].copy()

    if len(itemNumberSample) < 1:
        return go.Figure()
    else:
        itemNumberSample = itemNumberSample[
            (itemNumberSample.DateKey > '2017-01-01')
        ]

        # Get the model
        fb_prophet_forecast = fbProphetMultivariate(
            itemNumberSample,
            start_date='2018-01-01',
            regressors=['CommunicationChannelCode'],
            log=True
        )

        # Create the figue
        fig = fb_prophet_forecast.get_vizualisation()

    # The Design x Colors of the Graph
    layout = dict(
        title_text='Forecast Times Series of Daily UniteSales',
        height=350,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        xaxis={
            "title": "Date",
            "showgrid": False,
            "showline": True,
            "color": 'black'
        },
        yaxis={
            "title": "UnitSales",
            "showgrid": True,
            "showline": False,
            "color": 'black'
        },

        hovermode="closest",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "xanchor": "center",
            "y": 1,
            "x": 0.5,

        },
    )
    fig.update_layout(layout)

    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)

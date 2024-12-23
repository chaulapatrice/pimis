from django.core.management.base import BaseCommand, CommandError
from neuralprophet import NeuralProphet
import pandas as pd
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Trains the model'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Training the model')
            df = pd.read_excel("/media/exports.xlsx")
            df['Date Created'] = pd.to_datetime(df['Date Created'])

            df = df.sort_values('Date Created')

            df = df[['Date Created', 'Total Revenue']]
            df = df.groupby(df['Date Created'].dt.date).size().reset_index(name='count')
            df['Date Created'] = pd.to_datetime(df['Date Created'])
            df.columns = ['ds', 'y']

            df = df.sort_values('ds')

            model = NeuralProphet(trend_reg=0.5, seasonality_reg=0.5)
            model.fit(df, freq='D', early_stopping=True)

            future = model.make_future_dataframe(df, periods=365)
            forecast = model.predict(future)

            actual_prediction = model.predict(df)
            actual_prediction.set_index('ds', inplace=True)
            actual_prediction_monthly = actual_prediction.resample('ME').sum()
            actual_prediction_monthly.to_excel("/media/actual_prediction.xlsx", sheet_name='Actual Prediction')

            df.set_index('ds', inplace=True)
            actual_monthly = df.resample('ME').sum()
            actual_monthly.to_excel("/media/actual.xlsx", sheet_name='Actual')

            forecast.set_index('ds', inplace=True)
            forecast_monthly = forecast.resample('ME').sum()
            forecast_monthly.to_excel("/media/forecast.xlsx", sheet_name="Forecast")

            plt.figure(figsize=(20, 5))
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.plot(actual_prediction_monthly.index, actual_prediction_monthly['yhat1'], label='Actual Prediction',
                     c='r',
                     marker='o')
            plt.plot(forecast_monthly.index, forecast_monthly['yhat1'], label='Future Prediction', c='b', marker='o')
            plt.plot(actual_monthly.index, actual_monthly['y'], label='Actual', c='g', marker='o')
            plt.legend()

            plt.savefig("/media/graph.pdf")
            self.stdout.write(self.style.SUCCESS('🚀 Successfully trained the model'))

        except Exception as e:
            raise CommandError(str(e))

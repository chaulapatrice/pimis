from core.models import PredictionJob, generate_excel_report
from celery import shared_task
from django.core.files import File
from django.db import transaction
import sentry_sdk
import logging
from neuralprophet import NeuralProphet
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


@shared_task
def run_prediction_job(job_id: int):
    try:
        logger.info(f"Prediction job {job_id} started.")
        prediction_job = PredictionJob.objects.get(id=job_id)
        prediction_job.status = PredictionJob.Status.RUNNING
        prediction_job.save()

        logger.info(f"Generating excel file for prediction job {prediction_job.id}")
        generate_excel_report(prediction_job)

        df = pd.read_excel("/media/exports.xlsx")
        df['Date Created'] = pd.to_datetime(df['Date Created'])

        df = df.sort_values('Date Created')

        df = df[['Date Created', 'Total Revenue']]
        df = df.groupby(df['Date Created'].dt.date).size().reset_index(name='count')
        df['Date Created'] = pd.to_datetime(df['Date Created'])
        df.columns = ['ds', 'y']

        df = df.sort_values('ds')

        model = NeuralProphet(trend_reg=0.5, seasonality_reg=0.5)
        model.fit(df, freq='D')

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
        plt.plot(actual_prediction_monthly.index, actual_prediction_monthly['yhat1'], label='Actual Prediction', c='r',
                 marker='o')
        plt.plot(forecast_monthly.index, forecast_monthly['yhat1'], label='Future Prediction', c='b', marker='o')
        plt.plot(actual_monthly.index, actual_monthly['y'], label='Actual', c='g', marker='o')
        plt.legend()

        plt.savefig("/media/graph.pdf")

        with transaction.atomic():
            with open('/media/actual.xlsx', 'rb') as f:
                actual = File(f)
                prediction_job.actual.save("actual.xlsx", actual, save=True)

            with open('/media/forecast.xlsx', 'rb') as f:
                forecast = File(f)
                prediction_job.forecast.save("forecast.xlsx", forecast, save=True)

            with open('/media/actual_prediction.xlsx', 'rb') as f:
                actual_prediction = File(f)
                prediction_job.actual_prediction.save("actual_prediction.xlsx", actual_prediction, save=True)

            with open('/media/graph.pdf', 'rb') as f:
                graph = File(f)
                prediction_job.graph.save("graph.pdf", graph, save=True)

            prediction_job.status = PredictionJob.Status.COMPLETED
            prediction_job.save()

    except Exception as e:
        logger.error(e)
        sentry_sdk.capture_exception(e)
        prediction_job.status = PredictionJob.Status.FAILED
        prediction_job.save()

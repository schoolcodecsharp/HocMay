"""Tiền xử lý luôn nằm trong Pipeline, chỉ fit trên train."""

from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def linear_pipeline():
    return Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())])

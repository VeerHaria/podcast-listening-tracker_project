"""Matplotlib charts. Each function returns a figure."""
from matplotlib.figure import Figure
import analysis

COLOR = "#2F4B66"


def _new(title, xlabel, ylabel):
    fig = Figure(figsize=(7, 4.5), layout="constrained")
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig, ax


def _tilt(ax):
    for label in ax.get_xticklabels():
        label.set_rotation(25)
        label.set_ha("right")


def minutes_per_podcast(df):
    table = analysis.by_podcast(df)
    fig, ax = _new("Minutes listened per podcast", "Podcast", "Minutes")
    ax.bar(table.index, table["minutes"], color=COLOR)
    _tilt(ax)
    return fig


def minutes_per_month(df):
    table = analysis.by_month(df)
    fig, ax = _new("Minutes listened per month", "Month", "Minutes")
    ax.plot(table.index, table["minutes"], marker="o", color=COLOR)
    ax.set_ylim(bottom=0)
    return fig


def rating_per_podcast(df):
    table = analysis.by_podcast(df)
    fig, ax = _new("Average rating per podcast", "Podcast", "Rating (1 to 5)")
    ax.bar(table.index, table["avg_rating"], color="#3E7C79")
    ax.set_ylim(0, 5)
    _tilt(ax)
    return fig


CHARTS = {"minutes_per_podcast": minutes_per_podcast,
          "minutes_per_month": minutes_per_month,
          "rating_per_podcast": rating_per_podcast}

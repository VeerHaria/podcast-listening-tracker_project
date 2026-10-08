"""Analysis with pandas (tables) and NumPy (numbers)."""
import numpy as np
import pandas as pd


def prepare(episodes, podcasts):
    """Join episodes with podcast category and fix column types."""
    df = episodes.merge(podcasts, on="podcast", how="left")
    df["date"] = pd.to_datetime(df["date"])
    df["minutes"] = pd.to_numeric(df["minutes"])
    df["rating"] = pd.to_numeric(df["rating"])
    return df


def totals(df):
    return {"episodes": len(df),
            "total_minutes": int(df["minutes"].sum()),
            "avg_minutes": round(df["minutes"].mean(), 1),
            "avg_rating": round(df["rating"].mean(), 2)}


def by_podcast(df):
    table = df.groupby("podcast").agg(episodes=("title", "count"),
                                      minutes=("minutes", "sum"),
                                      avg_rating=("rating", "mean"))
    return table.round(2).sort_values("minutes", ascending=False)


def by_month(df):
    month = df["date"].dt.strftime("%Y-%m")
    table = df.groupby(month).agg(episodes=("title", "count"),
                                  minutes=("minutes", "sum"),
                                  avg_rating=("rating", "mean"))
    table = table.rename_axis("month").round(2)
    table["change"] = table["minutes"].diff()     # this month minus last month
    return table


def consistency(df):
    days = df["date"].dt.normalize().drop_duplicates().sort_values()
    days = days.to_numpy().astype("datetime64[D]")
    gaps = np.diff(days).astype(int)              # days between listening days
    span = int((days[-1] - days[0]).astype(int)) + 1
    return {"days_listened": len(days),
            "days_in_period": span,
            "percent_days": round(len(days) / span * 100, 1),
            "longest_break": int(gaps.max()) - 1 if len(gaps) else 0}


def preferences(df):
    table = by_podcast(df)
    rated = table[table["episodes"] >= 2]         # need 2+ episodes to judge
    return {"most_listened": table["minutes"].idxmax(),
            "best_rated": rated["avg_rating"].idxmax() if len(rated) else "not enough data",
            "favourite_category": df.groupby("category")["minutes"].sum().idxmax(),
            "liked_percent": round(float(np.mean(df["rating"] >= 4)) * 100, 1)}


def report(df):
    t, c, p = totals(df), consistency(df), preferences(df)
    return "\n".join([
        "TOTALS",
        f"  Episodes listened : {t['episodes']}",
        f"  Total minutes     : {t['total_minutes']}",
        f"  Average minutes   : {t['avg_minutes']}",
        f"  Average rating    : {t['avg_rating']}",
        "", "CONSISTENCY",
        f"  Days listened     : {c['days_listened']} of {c['days_in_period']} ({c['percent_days']}%)",
        f"  Longest break     : {c['longest_break']} days",
        "", "PREFERENCES",
        f"  Most listened     : {p['most_listened']}",
        f"  Best rated        : {p['best_rated']}",
        f"  Favourite category: {p['favourite_category']}",
        f"  Rated 4 or 5      : {p['liked_percent']}%",
        "", "COMPARE PODCASTS", by_podcast(df).to_string(),
        "", "COMPARE MONTHS", by_month(df).to_string()])

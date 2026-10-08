# Podcast Listening Tracker

CE0525 Programming for Scientific Computing (Python), Project P70.
Student: Veer Paresh Haria, IU2441230463.

Desktop app to record podcasts and episodes listened to (date, minutes,
rating), search them, and see totals, comparisons, consistency, preferences
and charts.

## Run

    pip install -r requirements.txt
    python main.py

Tests:

    python -m unittest discover -s tests -v

## Files

| File | Job |
| --- | --- |
| main.py | start the app |
| gui.py | Tkinter screens |
| validation.py | check user input |
| storage.py | read and write CSV files |
| analysis.py | pandas and NumPy calculations |
| charts.py | Matplotlib charts |
| data/ | podcasts.csv, episodes.csv (sample records, replace with your own) |
| reports/ | saved chart images |
| tests/ | unit tests |

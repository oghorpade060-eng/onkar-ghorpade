# BikeWise model card

**Maintainer:** Onkar Ghorpade  
**Task:** Estimate hourly rental counts; supervised regression.  
**Intended use:** Learning, portfolio demonstrations and historical scenario exploration.

## Data and provenance

UCI Bike Sharing, hourly Capital Bikeshare records from 2011–2012. The downloaded `hour.csv` has 17,379 observations. It is public aggregate data; the application does not ingest personal rider records.

The original CSV is unmodified. Its SHA-256 is pinned in the downloader and training script. Outputs are derived aggregates, trained parameters and predictions. The source includes some missing clock hours; the project treats rows as observed hours and does not silently impute unrecorded hours.

## Inputs and target

Target: `cnt`, total hourly rentals. Inputs: season, year code, month, hour, holiday, weekday, working-day status, weather category, normalized temperature, humidity and wind speed.

`casual` and `registered` are excluded because they sum to `cnt`. `instant` and the raw date are excluded as identifiers; calendar features from the dataset remain. `atemp` is omitted to keep the weather-input contract simpler.

The scenario API uses the actual dataset calendar, not a guessed seasonal mapping. Temperature normalization follows the hourly dataset documentation: `(Celsius + 8) / 47`; humidity is divided by 100 and wind speed by 67.

## Training and evaluation

Training ends 2012-06-30; validation ends 2012-09-30; the test period is October–December 2012. All rows from a given date stay in the same split. Preprocessing is fitted within each candidate pipeline. The best validation MAE chooses the final model; the test set is not used for selection or hyperparameter tuning.

The winner is histogram gradient boosting with Poisson loss, 250 iterations, learning rate 0.07, 31 maximum leaves and L2 regularization 1.0. Random seed: 42. Early stopping is disabled. Candidates are refitted on train + validation before the final test evaluation. Negative predictions are clipped at zero consistently in evaluation and serving.

Test MAE: **46.994 bikes/hour**. RMSE: **71.129 bikes/hour**. R²: **0.8755**. These are measured benchmark results, not a guarantee or an accuracy percentage. Full parameters are in `model.py`; split counts and package versions are in `reports/metrics.json`.

Permutation importance is measured on validation data using the training-only winner, before refitting. It is an association-based diagnostic. Correlated inputs can share or obscure importance. It is not a causal explanation.

## Important limits

- One system and two old years: demand patterns may shift substantially across time and cities.
- Evaluation includes recorded weather, not weather forecasts available in advance.
- The chosen holdout tests one season; rolling-origin evaluation would provide a broader estimate.
- Rare extreme-weather events are underrepresented. The UI allows only weather categories 1–3.
- The 24-hour scenario keeps the user's weather values constant for every hour.
- No calibrated prediction intervals, live feeds, retraining scheduler or drift detector are implemented.
- Scenario dates before October 2012 overlap fitting data and are labelled accordingly.
- Permutation importance and aggregate scores can hide poor performance for individual circumstances.

Do not use this unvalidated historical model to make present-day operational commitments. Establish contemporary data quality, forecast availability and operational evaluation first.

## Privacy and security

No user accounts, credentials, cookies or access tokens are used by BikeWise. No user-uploaded models or datasets are accepted. Request bodies are limited to 4 KiB; extra fields, invalid categories, impossible dates and nonfinite numbers are rejected. The model artifact is local and intentionally excluded from Git. A SHA-256 provenance field is an integrity check for accidental mismatch, not protection against a malicious pickle file.

## Sources

- [UCI dataset and license](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)
- [Histogram gradient boosting](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
- [Flask production deployment guidance](https://flask.palletsprojects.com/en/stable/deploying/)


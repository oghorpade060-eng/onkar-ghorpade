# Understand and present BikeWise

**For Onkar Ghorpade · AI & Data Science**

## Start with this explanation

BikeWise predicts how many bikes may be rented during one hour. It learns from historical calendar and weather observations, compares three regression approaches, and displays measured results in a dashboard.

**मराठीत:** वेळ, सुट्टीचा दिवस आणि हवामान यांचा वापर करून एका तासात किती सायकली भाड्याने घेतल्या जातील याचा अंदाज करतो. जुन्या डेटावर मॉडेल शिकते. नंतरच्या वेगळ्या डेटावर त्याची चूक मोजतो.

## How AI, ML and Data Science connect

| Term | Simple meaning | In this project |
| --- | --- | --- |
| Artificial intelligence | A broad area of building systems that perform tasks associated with intelligence | The overall intelligent prediction application |
| Machine learning | Learn patterns from examples instead of writing every prediction rule | Ridge regression and gradient boosting |
| Data science | Use data, statistics and code to understand a question | Data validation, charts, experiments, evaluation and communication |
| Supervised learning | Train using examples with known answers | Features paired with historical rental counts |
| Regression | Predict a numerical quantity | Predict bikes rented per hour |
| Feature | An input used for prediction | Hour, weather, humidity, working-day status |
| Target | The answer the model learns to predict | `cnt`, the total rental count |
| Inference | Use the trained model on a new input | Submit the scenario form |

## Follow the code in this order

1. **`download_data.py`:** retrieves the public UCI archive and checks its SHA-256. A checksum helps ensure everyone runs on the same source bytes.
2. **`model.py`:** lists the exact features, transforms them, defines candidate models and validates scenario inputs.
3. **`train.py`:** sorts observations by date and hour, compares models, writes measured results and exports the selected fitted model.
4. **`reports/metrics.json`:** records the actual split sizes, scores and package versions.
5. **`app.py`:** loads the local artifact, validates JSON inputs and returns predictions.
6. **`static/app.js`:** turns responses into charts and updates the scenario result.
7. **`tests/test_project.py`:** checks data separation, real inference, invalid inputs and missing-model behavior.

## The experiment

| Stage | Data | Why it exists |
| --- | --- | --- |
| Training | Jan 2011–Jun 2012 | Learn model parameters |
| Validation | Jul–Sep 2012 | Choose between the candidate models |
| Testing | Oct–Dec 2012 | Measure the chosen method on later observations |

All candidate preprocessing is fitted within the training pipeline. After selection, models are refitted using training + validation data, and evaluated on the test period. No observation from the test period is used in that final fitting.

**Why not randomly shuffle?** Future information could enter training while earlier observations appear in the test set. A chronological split better represents learning from the past and evaluating later data. One held-out period still has limitations; rolling-origin evaluation is a useful next step.

## Three models in plain language

**Mean baseline:** always predicts the training average. It tells us how well a very simple method performs.

**Ridge regression:** learns a weighted combination of encoded inputs. Its regularization discourages very large coefficients. It is useful as an interpretable linear comparison.

**Gradient boosting:** combines many small decision trees. Later trees help reduce mistakes made by the earlier model. This project uses histogram gradient boosting with a Poisson loss suitable for nonnegative count targets.

Gradient boosting had the lowest validation MAE in this experiment, so it was selected. That is an observed outcome, not a rule that it always wins.

## Explain the scores correctly

- **MAE = 46.994 bikes/hour:** on the held-out test data, absolute prediction errors averaged about 47 bikes per hour. It does not mean every prediction is within 47.
- **RMSE = 71.129 bikes/hour:** emphasizes larger errors more than MAE does.
- **R² = 0.8755:** a measure relative to the test target's mean-reference squared error. **Do not say “87.55% accuracy.”**

For two observations, if actual demand is `[100, 200]` and predictions are `[90, 230]`, absolute errors are `[10, 30]`; MAE is `(10 + 30) / 2 = 20` bikes/hour. This is a teaching example, not this project's measured result.

## The most important mistake to avoid

The dataset has `casual`, `registered` and `cnt` columns:

```python
cnt = casual + registered
```

Putting `casual` or `registered` into the model would expose parts of the answer. This is **target leakage**. BikeWise excludes both columns. It also excludes `cnt` from its feature list.

**मराठीत:** उत्तर आधीच input मध्ये दिलं तर मॉडेलची परीक्षा योग्य होत नाही. म्हणून उत्तरातून तयार झालेले columns inputs मध्ये घेत नाही.

## What happens after you click Estimate demand?

1. JavaScript collects date, hour, weather, temperature, humidity and wind speed.
2. It sends JSON to Flask's `POST /api/predict` route.
3. Flask checks required fields, finite numbers and allowed ranges.
4. The date supplies the original calendar values from the archive.
5. The pipeline encodes/scales inputs, then the regressor predicts demand.
6. Flask returns the hourly estimate and a 24-hour scenario curve.
7. The browser displays the result without a full-page refresh.

This app does not need login or tokens because it runs locally on public data. That design is separate from YatriFlow's Supabase authentication.

## Viva questions with short answers

**1. What problem does your project solve?**  
It explores how hourly bike rental demand relates to time and weather, and estimates demand for historical scenarios.

**2. Is it classification or regression?**  
Regression, because the output is a numerical rental count.

**3. Which dataset did you use?**  
The UCI Bike Sharing dataset: 17,379 hourly records from Capital Bikeshare during 2011–2012.

**4. Which inputs are used?**  
Calendar features, hour, weather category, temperature, humidity and wind speed.

**5. Why use one-hot encoding?**  
It represents categories as separate indicators, avoiding an artificial numeric order for linear models.

**6. What is overfitting?**  
Learning patterns or noise that work on training examples but do not generalize to unseen observations.

**7. Why do you need validation data?**  
To choose the model without using the final test results for selection.

**8. Which model was selected?**  
Histogram gradient boosting, because it had the lowest validation MAE among the three candidates.

**9. How did you prevent data leakage?**  
I excluded target-derived columns, separated data chronologically and fitted preprocessing within each training pipeline.

**10. What is permutation importance?**  
Shuffle one feature and measure how much prediction error increases. It indicates model reliance, not causation.

**11. Does the dashboard forecast live demand?**  
No. It demonstrates a historical model. A real future forecast would require current data and weather forecasts available in advance.

**12. What is the biggest limitation?**  
The model was tested on one old bike-sharing dataset and one held-out season; it has not been validated for today's cities.

**13. What is Flask doing?**  
Serving the interface and validating prediction requests before calling the trained model.

**14. Does a high R² prove the model is production-ready?**  
No. Production use also requires appropriate current data, operational validation, monitoring and reliable serving.

**15. What would you improve next?**  
Add rolling-origin tests, leakage-safe lag features, a seasonal baseline, forecast-weather inputs and calibrated prediction intervals.

## A 30-second presentation

“My name is Onkar Ghorpade. My project is BikeWise, an AI & Data Science application that predicts hourly bike rental demand. I used a public UCI dataset and compared a mean baseline, Ridge regression and gradient boosting. The model is selected on validation data and evaluated on later test data. The dashboard shows predictions, model comparisons and important inputs. This is a historical learning project, and I explain its limitations alongside its results.”

## Practice before presenting

Open the dashboard, show the three models, and explain the chronological split. Run the morning commute preset, then the rainy evening preset. Read the displayed predictions; do not memorize or invent them. Finish with the data-leakage example and one limitation.


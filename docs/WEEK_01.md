# Week 1: start here

**Goal:** write small Python programs and explain what each line does. Spend about 90 minutes on each weekday; use Saturday for a small task.

| Day | Topic | Task | Check |
| --- | --- | --- | --- |
| 1 | Variables and lists | Store five daily rental counts; print total and mean | `[12, 18, 10, 20, 15]` has total 75 and mean 15 |
| 2 | Conditions and loops | Count values above the mean | The same list has two values above 15 |
| 3 | Functions | Write `average(values)` | Decide what an empty list should do and document it |
| 4 | Dictionaries | Count ham/spam labels in a small example | `['ham', 'spam', 'ham']` gives ham 2, spam 1 |
| 5 | Files and exceptions | Save a small CSV; read it back | Handle a missing filename with a clear error |
| 6 | Mini-project | Summarize a seven-day rental CSV and print its busiest day | Try a tie and an invalid number |
| 7 | Rest/review | Explain one program aloud | Explain it without reading a generated answer |

## First lesson: a value, a collection and a calculation

```python
rentals = [12, 18, 10, 20, 15]
total = sum(rentals)
average = total / len(rentals)
print("Total:", total)
print("Average:", average)
```

Output:

```text
Total: 75
Average: 15.0
```

`rentals` is a list. `sum` adds its values. `len` counts them. Dividing total by count gives the mean. This is a descriptive statistic, not yet machine learning.

**मराठीत:** List मध्ये पाच दिवसांचे आकडे आहेत. `sum` बेरीज करते आणि `len` किती आकडे आहेत ते सांगते. बेरीजला संख्येने भाग दिला की सरासरी मिळते.

Now change the last value from 15 to 25. Before running it, calculate the new total and mean on paper. Expected: total **85**, mean **17.0**.

## Connect this to the portfolio

- BikeWise's simplest baseline predicts an average; a learned model must improve on a meaningful baseline.
- MessageLab counts categories and evaluates predictions rather than averaging labels.
- LibraryLens uses SQL's `COUNT` and `GROUP BY` to summarize rows in related tables.

Do not start neural networks until loops, functions, arrays and data tables feel manageable. Use [Kaggle Python](https://www.kaggle.com/learn/python) for exercises and the [Python tutorial](https://docs.python.org/3/tutorial/) as a reference.

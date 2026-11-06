# MessageLab: understand it before presenting it

## 1. What problem is being solved?

The input is an English SMS. The output is one of two learned categories: **ham** (ordinary message) or **spam**. This is classification. BikeWise is regression because its output is a number of bike rentals.

**मराठीत:** MessageLab message कोणत्या प्रकारचा आहे ते सांगते. BikeWise किती सायकली लागतील याचा अंदाज देते. प्रकार निवडणे म्हणजे classification; संख्या सांगणे म्हणजे regression.

## 2. How does text become numbers?

`TfidfVectorizer` builds a vocabulary from the fitting data and gives words numerical weights. Words occurring in many messages tend to be less distinctive than words concentrated in fewer messages. The project uses single words and two-word phrases.

Look at `candidates()` in `projects/messagelab/model.py`:

```python
Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2,
                             sublinear_tf=True, strip_accents="unicode")),
    ("classifier", LogisticRegression(...)),
])
```

This is a simplified extract: the full estimator arguments are in the file. The pipeline keeps the same transformation attached to the classifier. During model selection, vocabulary and weights are learned from the training partition only.

**मराठीत:** Computer ला शब्द थेट समजत नाहीत. TF–IDF शब्दांचे numbers बनवते. मग classifier त्या numbers मधील patterns शिकतो.

## 3. Why remove duplicate messages?

If the same message appears in training and testing, the test becomes easier than it should be. This project normalizes case and whitespace, removes duplicate messages before splitting, and checks for conflicting labels. Near duplicates and common templates can still remain; that is a limitation worth saying aloud.

## 4. What are train, validation and test sets?

| Part | What you do with it | Project size |
| --- | --- | ---: |
| Train | Fit candidate models | 3,095 |
| Validation | Choose the candidate | 1,032 |
| Test | Measure the final result | 1,032 |

After choosing logistic regression on validation spam F1, the final version is fitted on train + validation. Test examples are still excluded. The split is stratified: it keeps approximately similar label proportions. It is a fixed historical benchmark, not a future-time evaluation.

## 5. Read the confusion matrix

The model found 121 spam messages, missed 7, incorrectly flagged 6 ordinary messages, and correctly left 898 ordinary messages unflagged.

- **Precision:** `121 / (121 + 6) = 0.9528`. Of the messages called spam, how many were spam?
- **Recall:** `121 / (121 + 7) = 0.9453`. Of all actual spam messages, how many did we catch?
- **F1:** `2 × precision × recall / (precision + recall) = 0.9490`.
- **False positive:** an ordinary message incorrectly marked spam.
- **False negative:** spam missed by the classifier.

**मराठीत:** Precision म्हणजे spam म्हटलेले messages किती बरोबर होते. Recall म्हणजे खरे spam messages किती पकडले. F1 या दोन्हींचा समतोल दाखवतो.

The majority baseline gets 87.60% accuracy by predicting ham every time, but its spam recall is zero. That is why accuracy alone is a poor summary here.

## 6. Follow one request

1. Type a message in the local page.
2. The browser sends JSON to `/api/predict`.
3. Flask validates the text and request size.
4. The saved pipeline transforms text and predicts a label.
5. The page shows the score, word signals and limitations.

No model API key, account or GPU is involved. Unknown vocabulary produces an explicit unknown result. A ham label does not certify that a link is safe. A displayed score is not calibrated certainty.

## 7. Viva: ten short answers

| Question | Answer |
| --- | --- |
| Why is this NLP? | It processes human-language text. |
| What does ham mean? | An ordinary, non-spam label in this dataset. |
| Why TF–IDF? | It gives a simple, efficient numerical representation of text. |
| Why use a baseline? | To check whether a learned model improves on a simple rule. |
| Why choose logistic regression? | It had the highest validation spam F1 among the fixed candidates. |
| What is leakage? | Learning from information that should be unavailable during fitting or selection. |
| What does class imbalance mean? | There are many more ham than spam examples. |
| Why not report only accuracy? | A majority prediction can score well while missing every spam message. |
| What do word contributions show? | How individual features affect this fitted model's decision, not a sender's intent. |
| What would you improve? | Try template-separated evaluation, current consented data and validation-based calibration. |

## 8. A practice assignment

Run both sample messages. Write down their labels, scores and two influential terms. Then answer: does the explanation make sense, and where might it mislead you?

Next, fit the Naive Bayes candidate and explain why its higher precision and lower recall are a different tradeoff. Do not choose an improvement only because it improves the published test score. Record design decisions before a new final evaluation.

## 9. A 30-second explanation

“MessageLab is a small English SMS classifier. It compares a majority baseline, Naive Bayes and logistic regression using TF–IDF features. Duplicate messages are removed before splitting, and the final model is chosen on validation F1. On the held-out test set, logistic regression achieved spam F1 of about 0.949. The interface lets me inspect predictions and word signals. It is a learning project on historical data, not a production spam filter.”

References: [text features](https://scikit-learn.org/stable/modules/feature_extraction.html), [pipelines](https://scikit-learn.org/stable/modules/compose.html), [data leakage](https://scikit-learn.org/stable/common_pitfalls.html).

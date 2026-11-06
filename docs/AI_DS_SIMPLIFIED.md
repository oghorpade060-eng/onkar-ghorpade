# AI & Data Science, in plain language

| Concept | Simple meaning | Example from this portfolio |
| --- | --- | --- |
| Data science | Use data to answer a question, explain the method and check the answer | Study borrowing patterns with SQL |
| Machine learning | Fit a pattern from examples, then evaluate it on unseen examples | Learn relationships between weather, time and rentals |
| Feature | An input available when making a prediction | Hour, temperature or text-derived word weights |
| Target | The answer the model is trained to estimate | Rental count or ham/spam label |
| Regression | Predict a number | BikeWise estimates rentals per hour |
| Classification | Predict a category | MessageLab chooses ham or spam |
| Training | Fit model parameters using examples | Learn logistic-regression coefficients |
| Validation | Compare design choices before final evaluation | Select a candidate using validation F1 |
| Testing | Measure the chosen procedure on held-out examples | Report a confusion matrix |
| Overfitting | Fit details that fail to generalize | Memorize repeated text instead of useful patterns |
| Leakage | Use information that should not be available during fitting or selection | Include rental-count components in BikeWise inputs |
| Baseline | A simple reference method | Always predict the mean or majority class |
| SQL join | Match related rows from different tables | Connect a loan to its book and member |
| Window function | Calculate across related rows without collapsing them into one group | Rank books within each category |
| API | An agreed way for software to request data or an action | A form sends JSON to Flask for a prediction |
| RAG | Retrieve relevant evidence, then use it to help generate an answer | A planned course-notes assistant; not implemented here yet |

## Three distinctions to remember

**Accuracy and confidence are different.** Accuracy measures correct predictions over a labeled dataset. A score for one message does not automatically have the same meaning as a calibrated probability.

**Prediction and explanation are different.** A coefficient or feature-importance value tells you something about a fitted model. It does not prove that changing a feature causes a real-world outcome.

**Authentication and authorization are different.** Authentication establishes identity. Authorization controls what that identity can access. A client-side login screen alone does not protect database rows; see the [YatriFlow walkthrough](YATRIFLOW_AUTHENTICATION.md).

**मराठीत:** AI हा मोठा विषय आहे. Machine learning मध्ये examples वरून pattern शिकतात. Data science मध्ये data स्वच्छ करणे, analysis करणे, result तपासणे आणि तो समजावणे यांचाही समावेश होतो. Model ने उत्तर दिलं म्हणजे ते नक्की बरोबर आहे असं नसतं.

Learn by doing: [first week](WEEK_01.md) · [BikeWise lesson](LEARNING_GUIDE.md) · [MessageLab lesson](MESSAGELAB_LESSON.md) · [full study plan and references](STUDY_PLAN.md).

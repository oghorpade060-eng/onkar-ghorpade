# AI & Data Science study plan

**Start with what you can explain and run. Move to the next phase when you pass its checks.**

This plan adapts the supplied *AI Career Roadmap — Updated Edition*. It keeps the progression from Python, maths and SQL to ML, deep learning, RAG and deployment. It does not assume that the PDF's August 2026 starting phase has already been completed.

The suggested start is **9 November 2026**. At roughly **10.5 hours a week**, the first pass runs for 26 weeks, through **9 May 2027**. Dates are planning targets, not predictions of mastery or employment. If a check is difficult, repeat the relevant week. Keep the longer July 2028 goal as a planning horizon, not a guaranteed job date.

## First, check your starting point

Try these without copying a complete solution:

1. Write a function that returns the mean of a list and handles an empty list.
2. Read a CSV, count missing values, group rows and produce a small chart.
3. Join two SQL tables and explain why an INNER JOIN might lose rows.
4. Explain the difference between training, validation and testing.
5. Clone a repository, run it, change one small behavior and inspect the diff.

If the first three are unfamiliar, begin at week 1. If you can do all five and explain the choices, compress the early revision only after reproducing the project results yourself.

## A routine that fits around college

| Day | Time | Work |
| --- | --- | --- |
| Monday–Friday | 90 minutes/day | 25 minutes learning, 45 minutes coding, 20 minutes review |
| Saturday | 3 hours | One project task, checks, and a short explanation of what changed |
| Sunday | Rest | Optional light revision; do not count it as required study time |

That is **10.5 scheduled hours/week**. The PDF suggests 5.5 study hours per day; use that only if it fits your actual commitments. Do not sacrifice the hands-on part to finish more videos.

## Phase 1 · Python, data and SQL

**Weeks 1–6 · 9 November–20 December 2026**

| Week | Learn | Build or practise | Exit check |
| --- | --- | --- | --- |
| 1 | Variables, lists, conditions, loops, functions | [Seven-day starter](WEEK_01.md) | Explain every line of a small program |
| 2 | Files, CSV, exceptions, Git | Read a CSV and save summary statistics | Handle an empty file or invalid input |
| 3 | NumPy arrays, pandas filtering/grouping | Inspect BikeWise's dataset; plot rentals by hour | Distinguish a row, feature and target |
| 4 | Mean, median, spread, probability, vectors | Compute MAE by hand; calculate one dot product | Explain why an average can hide variation |
| 5 | SELECT, WHERE, JOIN, GROUP BY, NULL | Run LibraryLens and explain three queries | Keep an unused book visible with LEFT JOIN |
| 6 | CTEs, LAG, DENSE_RANK, review | Add a department report to LibraryLens | Explain a window function and one edge case |

Use **Kaggle Python** for exercises, the **Python tutorial** as a reference, **pandas tutorials** for tables and **SQLZoo** for query practice. See the verified links below. The Python tutorial assumes some prior programming knowledge; do not use it as your only exercise source if starting from zero.

## Phase 2 · Classical machine learning and evaluation

**Weeks 7–10 · 21 December 2026–17 January 2027**

| Week | Focus | Evidence to produce |
| --- | --- | --- |
| 7 | Regression, baselines, chronological splits | Reproduce BikeWise; explain MAE, RMSE and R² |
| 8 | Classification, precision, recall, F1 | Reproduce MessageLab; calculate its confusion-matrix metrics |
| 9 | Preprocessing, leakage, class imbalance | Explain why `fit` belongs on training data and why duplicates matter |
| 10 | One controlled experiment and error analysis | Compare a change on validation data; write the decision before final testing |

**Exit check:** run both ML projects from a clean environment, explain a failure case, identify a possible source of leakage, and say what the model has not been validated for. The published code is a study starting point; a repository existing on your profile does not establish that you have mastered it.

## Phase 3 · Deep learning, then a small fine-tuning experiment

**Weeks 11–16 · 18 January–28 February 2027**

1. Follow PyTorch's tensors, datasets, autograd and training-loop lessons.
2. Train a small image classifier; track training and validation loss.
3. Compare a simple baseline with a small neural network.
4. Read the Hugging Face course on tokenization and transformers.
5. Try a small text-model fine-tune only after understanding the data split and training loop.
6. If hardware permits, study LoRA/QLoRA and run a bounded adapter experiment.

The PDF names Mistral-7B as a milestone. Treat that as an optional later experiment, not the first model you must train. Quantization and adapters can reduce memory use, but GPU availability and whether a particular run fits depend on the model, sequence length, batch size and training configuration. Do not assume a free T4 is always available or sufficient. Begin with a smaller model and record hardware, runtime, dataset license and evaluation.

**Exit check:** show a loss curve, explain gradient descent, reproduce a checkpoint, and explain why validation loss might worsen while training loss improves.

## Phase 4 · Retrieval, RAG and bounded tool use

**Weeks 17–22 · 1 March–11 April 2027**

| Week | Focus | Deliverable |
| --- | --- | --- |
| 17 | Chunking and lexical retrieval | Search a small set of notes that you have permission to use |
| 18 | Embeddings and nearest-neighbor search | Compare retrieved passages for 20 written questions |
| 19 | Add answer generation with citations | Show exactly which passages support each answer |
| 20 | Evaluation and missing information | Test answerable and unanswerable questions; record failures |
| 21 | One read-only tool, with explicit scope | Add a bounded calculator or document lookup |
| 22 | Reproducibility and a clear demo | Publish code, dataset permissions, evaluation and limitations |

**Next larger project idea: StudySource**, a question-answering app over your own course notes. Start with retrieval; add an LLM only after you can measure retrieval quality. A search-only implementation is not a completed RAG app. A tool demo is not an autonomous production agent. This project is **planned**, not currently implemented in the portfolio.

Keep API secrets in server-side environment variables. Establish a small explicit spending limit before using a paid service. Retrieved documents are evidence, not instructions to execute actions.

**Exit check:** on a fixed question set, report retrieval hit rate and answer-support checks; demonstrate a sensible “not enough information” result.

## Phase 5 · Deployment and reliable delivery

**Weeks 23–26 · 12 April–9 May 2027**

- Package one app with Docker and document its start command.
- Learn a small FastAPI endpoint, request validation and error responses.
- Add automated checks before deployment; verify failure cases as well as the happy path.
- Publish one working demo after checking the hosting service's current limits and costs.
- Write a short model/data card and record operational limits.

**Exit check:** a new person can reproduce the app, the live demo matches the README, secrets are absent from git, and you can diagnose a failed request. A green test run is useful evidence; it is not proof of production readiness.

## After this first pass

Choose one project to deepen. Add a better dataset, a more demanding evaluation or a documented user need. Apply for suitable internships or junior roles when you can demonstrate the relevant skills. Include local or hybrid opportunities as well as remote ones; availability and eligibility vary by role. Avoid treating any course, ranking or number of projects as a guaranteed offer.

Use the [progress log](PROGRESS_LOG.md) to record completed work. Post only work you actually ran and can discuss. Keep source credits for forks and public datasets.

## References, with a specific task for each

Links checked on **6 November 2026**. Course pages and interfaces can change. Use the repository's pinned package versions when reproducing its experiments; current documentation may describe newer versions.

| Resource | Use it for |
| --- | --- |
| [Kaggle Python](https://www.kaggle.com/learn/python) | Practise functions, lists, loops and dictionaries |
| [Python tutorial](https://docs.python.org/3/tutorial/) | Look up control flow, functions, data structures and file handling |
| [pandas getting-started tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html) | Read CSVs, select rows, group and combine tables |
| [SQLZoo](https://sqlzoo.net/wiki/SQL_Tutorial) | Work through SELECT, joins, aggregates and NULL exercises |
| [SQLite window functions](https://www.sqlite.org/windowfunctions.html) | Read LAG and ranking examples while studying LibraryLens |
| [SQLite date functions](https://www.sqlite.org/lang_datefunc.html) | Understand the overdue-day calculation |
| [scikit-learn text classification](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html) | Understand sparse text representations and model comparison |
| [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | Identify preprocessing and leakage mistakes |
| [PyTorch Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) | Build a training loop and understand autograd |
| [Hugging Face LLM course](https://huggingface.co/learn/llm-course/chapter1/1) | Learn tokenizers, transformers and fine-tuning |
| [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization) | Study the constraints of adapter training with quantized models |
| [Microsoft Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners) | Work through structured GenAI lessons and examples |
| [Docker Get Started](https://docs.docker.com/get-started/) | Package and run a container |
| [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) | Implement typed inputs and an API endpoint |

## How to ask for help while studying

Send the week number, the code or traceback, what you expected, and what you already tried. Ask for a hint first, make the change yourself, then explain the result in two sentences. That makes the project useful preparation for a viva or interview.

**मराठीत:** रोज थोडं वाचा, पण code स्वतः चालवा. Error आला तर त्याचा अर्थ समजून घ्या. पुढच्या topic ला जाण्याआधी आजचं काम स्वतःच्या शब्दांत समजावून सांगा. Profile पेक्षा तुम्हाला project समजतो का, हे जास्त महत्त्वाचं आहे.

# Explain It To Me: Marketing Attribution & Budget ROI

## Section 1: Plain-English Walkthrough

Marketing attribution is the question of who gets credit when a customer converts.

Imagine someone sees several display ads from different publisher placements before buying. If the business uses last-touch attribution, the final observed placement gets all the credit. That is easy to explain, but it can be misleading if earlier placements helped move the customer along.

For this project, I used a real public sample from CriteoPrivateAd, an anonymized advertising dataset hosted by Criteo on Hugging Face. The source has user IDs, impression order, campaign IDs, publisher IDs, click labels, and sales labels. It does not reveal friendly channel names or real advertiser revenue, so I map anonymized publishers into placement groups like `Publisher 01` and keep the dollar assumptions separate.

Here is what I built:

1. Pull and prepare a CriteoPrivateAd sample.
2. Explore placement frequency, conversion rates, and journey length.
3. Compare first-touch, last-touch, linear, and Markov attribution.
4. Translate attribution results into budget reallocation scenarios.
5. Recommend a balanced budget move while clearly saying the model is correlational, not causal.

## Section 2: Explanation Versions

### 30-Second Version

This project shows why last-touch attribution can be shaky as a budget tool. I use a real CriteoPrivateAd sample, turn anonymized display impressions into user journeys, compare first-touch, last-touch, linear, and Markov attribution, then connect the output to budget scenarios. The dollar values are assumptions because the source includes sales labels, not advertiser revenue or budget.

### 2-Minute Version

Attribution is the problem of deciding which touchpoints deserve credit for conversions. Many teams use last-touch because it is simple: whichever touchpoint came right before conversion gets all the credit. The issue is that journeys often have multiple touches. Earlier touches may matter even if they were not last.

I use CriteoPrivateAd, a public anonymized advertising dataset. The repo takes one real Parquet shard, filters to users with at least two impressions, and turns those impressions into touchpoint-level journeys. The source does not provide named marketing channels, so publisher IDs are grouped into anonymized placement groups.

Then I compare simple attribution methods against a Markov removal-effect model. The Markov model asks: if this placement group disappeared from the journey graph, how much would modeled conversion probability fall? That gives a more journey-aware way to allocate credit than simply picking the first or last touch.

Finally, I connect the attribution result to a budget decision. Because the source does not include spend or revenue, the budget and contribution values are stated assumptions. So the result is a decision framework, not proof that a specific budget move will work.

### 5-Minute Version

The project is built around a real marketing decision: how to allocate budget when customers interact with more than one ad placement before converting.

The dataset is sourced, not invented. It comes from CriteoPrivateAd on Hugging Face. The source data is anonymized, so it gives IDs rather than brand/channel names. That means the project is honest about what can and cannot be interpreted: we can compare publisher-placement groups, but we cannot say "paid search" or "email" because those labels are not in the data.

The first part checks whether the prepared sample makes sense. It counts touchpoints by placement group, measures conversion rates for journeys that included each group, calculates average journey length, and summarizes common paths.

The second part compares attribution methods:

- First-touch gives all credit to the first placement group in a converting journey.
- Last-touch gives all credit to the final placement group.
- Linear attribution splits credit evenly across touches.
- Markov removal attribution builds a transition graph and estimates how much conversion probability drops when each placement group is removed.

The third part turns the model into strategy. The source data has sales labels, but not a real budget or revenue. So the repo uses an assumed pilot budget and assumed contribution per sale. That lets the deck show the business logic without pretending the dollar values came from Criteo.

## Section 3: How The Code Actually Works

### What Each File And Folder Does

Start here:

1. `README.md`: the executive summary, key findings, and reproduction steps.
2. `data-sources.md`: explains the CriteoPrivateAd source, transformation, and assumptions.
3. `src/attribution_roi/source_data.py`: downloads and prepares the sourced Criteo sample.
4. `src/attribution_roi/data.py`: loads, cleans, validates, and summarizes journeys.
5. `src/attribution_roi/attribution.py`: calculates first-touch, last-touch, linear, and Markov attribution.
6. `src/attribution_roi/budget.py`: turns attribution results into budget gaps and scenarios.
7. `src/attribution_roi/pipeline.py`: runs the full analysis.
8. `reports/strategy_deck.md`: the strategy deck.
9. `outputs/`: generated tables.
10. `tests/`: checks that the key logic works.

### Key Functions In Plain Terms

`download_criteo_source()` downloads the raw CriteoPrivateAd Parquet shard into `data/raw/`.

`prepare_criteo_touchpoints()` reads the real source shard, keeps multi-touch users, maps publisher IDs into placement groups, and writes `data/processed/criteo_touchpoints_sample.csv`.

`journey_table()` collapses touchpoint rows into one row per journey. Attribution needs the ordered path, so this function creates fields like `path`, `path_string`, `journey_length`, and journey-level value.

`first_touch_attribution()` gives all converted value to the first placement group in each converting path.

`last_touch_attribution()` gives all converted value to the last placement group in each converting path.

`linear_attribution()` splits converted value equally across every touch in the converting path.

`markov_removal_attribution()` builds a transition graph from journey paths. It calculates baseline conversion probability, removes one placement group at a time, and measures how much conversion probability drops.

`budget_recommendation()` compares the assumed current budget to the Markov-informed budget. This is where the analysis becomes a business recommendation instead of just a model output.

`scenario_summary()` estimates conservative, balanced, and aggressive reallocation scenarios with a simple diminishing-returns assumption.

### How Markov Attribution Works Conceptually

A Markov chain is a map of movement from one state to another. In this project, the states are placement groups plus start, conversion, and non-conversion.

For example:

`Start -> Publisher 01 -> Long-tail placements -> Publisher 03 -> Conversion`

The model counts how often customers move from each state to the next. Then it asks, "What happens if Publisher 03 is removed?" If removing that placement group causes modeled conversion probability to drop a lot, it gets a lot of credit.

### How To Run The Project End To End

From the repo root, using the committed processed sample:

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

To re-download the source shard:

```bash
python scripts/download_source_data.py
python scripts/run_all.py
pytest
```

`python scripts/run_all.py` regenerates:

- `outputs/*.csv`
- `reports/figures/*.png`
- `reports/summary.md`
- `reports/strategy_deck.md`
- `notebooks/marketing_attribution_analysis.ipynb`

### What To Point To First In A Technical Conversation

I would start with `src/attribution_roi/source_data.py`, because it shows exactly where the sourced data enters the project and how the sample is prepared.

Then I would show `src/attribution_roi/attribution.py`, especially `markov_removal_attribution()`, because that is the core analytical step beyond simple baselines.

Finally, I would show `src/attribution_roi/budget.py`, because it connects the attribution result to an actual budget choice.

## Section 4: Anticipated Questions

### Why does attribution matter?

Because marketing budget is limited. If the measurement system gives too much credit to the final observed placement, the business may underfund touches that helped earlier in the journey.

### Why not just use last-touch?

Last-touch is simple and easy to explain. I would still keep it around for reporting. I just would not use it by itself to decide budget, because it ignores everything before the final touch.

### Why use Markov over last-touch?

Markov uses the whole observed journey sequence. It estimates how much conversion probability drops when a placement group is removed from the path graph, which is closer to the budget question I care about.

### What does "the model is not proving causation" mean?

It means the model is looking at observed patterns, not running an experiment. If journeys with a placement group convert more often, the model can give that placement credit, but it cannot prove the placement caused the conversion.

### What would you do differently with real spend data?

I would replace the assumed pilot budget and assumed contribution per sale with actual spend, media fees, gross margin, returns, discounts, and customer lifetime value. I would also split new and returning customers if the business cared about acquisition efficiency.

### How confident are you in the numbers?

I am confident the code produces the stated outputs from the processed Criteo sample and documented assumptions. I would not claim the budget lift is guaranteed. The dollar values are assumptions, and attribution is still correlational.

### What is the biggest limitation?

The source data is real, but anonymized. The biggest limitation is that placement names, calendar dates, actual revenue, and actual media budget are not disclosed.

### Walk me through this function.

For `prepare_criteo_touchpoints()`, I would say: it reads the real Criteo Parquet shard, filters to users with multiple impressions, maps the top publishers into readable placement groups, defines conversion from the sales label, applies the explicit contribution-per-sale assumption, and saves a clean touchpoint CSV.

For `markov_removal_attribution()`, I would say: it builds a transition graph from all journeys, calculates baseline conversion probability, removes each placement group one at a time, and assigns more credit to groups whose removal causes a bigger conversion-probability drop.

## Glossary

**Attribution:** Assigning credit for a conversion across marketing touchpoints.

**Conversion:** The desired customer action, such as a purchase or sale.

**Touchpoint:** One marketing interaction, such as a display ad impression.

**Customer journey:** The ordered set of touchpoints before a conversion or non-conversion outcome.

**First-touch attribution:** Gives all credit to the first touchpoint in a converting journey.

**Last-touch attribution:** Gives all credit to the final touchpoint before conversion.

**Linear attribution:** Splits credit evenly across all touches in a converting journey.

**Markov chain:** A model that represents movement from one state to another, such as from one publisher placement to another to conversion.

**Removal effect:** The drop in modeled conversion probability when a placement group is removed from the journey graph.

**ROAS:** Return on ad spend. In this repo, ROAS is based on assumed contribution value divided by assumed spend.

**Incremental ROAS:** Additional assumed contribution divided by shifted spend.

**Correlation:** A relationship between two things that move together.

**Causation:** Evidence that one thing caused another thing to happen.

**Incrementality test:** An experiment that estimates what would have happened with and without a marketing activity.

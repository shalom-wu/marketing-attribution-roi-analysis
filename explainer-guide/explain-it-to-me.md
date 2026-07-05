# Explain It To Me: Marketing Attribution & Budget ROI

## Section 1: Plain-English Walkthrough

Marketing attribution means deciding which marketing channels get credit when a customer converts.

Imagine someone sees a display ad, later clicks a paid social post, searches on Google, joins an email list, and finally buys after clicking an email. If the business uses last-touch attribution, Email gets 100% of the credit because it was the final touch before purchase.

That is easy to understand, but it can be misleading. Email may have helped close the sale, but the customer might not have existed in the buying pool without the earlier display or paid social touches. So the real business question is not "what was the last thing the customer clicked?" It is "where should the next marketing dollar go?"

This project builds a full attribution workflow:

1. Generate a synthetic customer journey dataset.
2. Explore channel frequency, conversion rates, and journey length.
3. Compare first-touch, last-touch, linear, and Markov attribution.
4. Translate attribution results into budget reallocation scenarios.
5. Recommend a balanced budget move while clearly saying the model is correlational, not causal.

The current generated run has 15,000 journeys, 47,308 touchpoints, and a 12.7% conversion rate. Last-touch gives Paid Search 26.0% of credit, while Markov removal gives it 18.0%. That difference matters because the budget recommendation changes.

## Section 2: Explanation Versions

### 30-Second Version

This project shows why last-touch attribution can misallocate marketing budget. I generated synthetic customer journeys, compared first-touch, last-touch, linear, and Markov attribution, then translated the differences into budget scenarios. The recommended move is a balanced reallocation toward the Markov-informed mix, with an estimated $21.9K synthetic revenue lift. The model is useful for decision framing, but it does not prove causality.

### 2-Minute Version

Attribution is the problem of deciding which channels deserve credit for conversions. Many teams use last-touch because it is simple: whichever channel came right before purchase gets all the credit. The issue is that customer journeys usually have multiple touches. Earlier channels may create demand, while later channels capture it.

In this project, I generated a synthetic multi-touch dataset with user journeys, dates, channels, conversions, and revenue. Then I ran descriptive analysis to understand channel volume, conversion rates by channel exposure, average journey length, and common paths.

After that, I compared simple attribution methods against a Markov removal-effect model. The Markov model asks: if this channel disappeared from the journey graph, how much would modeled conversion probability fall? That gives a more journey-aware way to allocate credit than simply picking the first or last touch.

Finally, I connected the model to a budget decision. A last-touch allocation would misdirect an estimated $37.8K, or 21.7% of the synthetic quarter's budget, compared with the Markov-informed mix. I recommend a balanced reallocation rather than a full swing to the model, because attribution is still correlational.

### 5-Minute Version

The project is built around a real marketing decision: how to allocate budget when customers interact with several channels before converting.

The dataset is synthetic and clearly labeled that way. I used synthetic data because I did not select a clean, accessible, well-documented public dataset that met the project requirements. The generator creates realistic channel patterns: awareness channels such as Display and Paid Social appear more often early in journeys, while Paid Search, Email, and Direct appear more often near conversion.

The first part of the analysis checks whether the data behaves reasonably. It counts touchpoints by channel, measures conversion rates for journeys that included each channel, calculates average journey length, and summarizes common path patterns. This matters because attribution is only meaningful if the journey data itself makes sense.

The second part compares attribution methods:

- First-touch gives all credit to the first channel in a converting journey.
- Last-touch gives all credit to the final channel.
- Linear attribution splits credit evenly across touches.
- Markov removal attribution builds a transition graph and estimates how much conversion probability drops when each channel is removed.

The result is that last-touch heavily favors closing channels. For example, Paid Search gets 26.0% credit under last-touch but 18.0% under Markov. Display gets 4.2% under last-touch but 11.6% under Markov. That is the kind of difference that can change budget planning.

The third part turns the model into strategy. Under the assumptions in this repo, a last-touch budget guide would misallocate $37.8K. The balanced scenario shifts $19.6K toward the Markov-informed mix and estimates a $21.9K synthetic revenue lift. I would not present that as guaranteed revenue. I would present it as a decision hypothesis to validate with experiments.

## Section 3: How The Code Actually Works

### What Each File And Folder Does

Start here:

1. `README.md`: the executive summary, key findings, and reproduction steps.
2. `data-sources.md`: explains why the dataset is synthetic and how it was generated.
3. `src/attribution_roi/synthetic.py`: creates the synthetic customer journeys.
4. `src/attribution_roi/data.py`: loads, cleans, validates, and summarizes journeys.
5. `src/attribution_roi/attribution.py`: calculates first-touch, last-touch, linear, and Markov attribution.
6. `src/attribution_roi/budget.py`: turns attribution results into budget gaps and scenarios.
7. `src/attribution_roi/pipeline.py`: runs the full project workflow.
8. `reports/strategy_deck.md`: the strategy deck.
9. `outputs/`: generated tables.
10. `tests/`: checks that the key logic works.

### Key Functions In Plain Terms

`generate_synthetic_touchpoints()` in `synthetic.py` creates one row per marketing touch. It picks a journey length, chooses channels in a realistic order, calculates a synthetic conversion probability, decides whether the journey converted, and assigns synthetic revenue if it did.

`journey_table()` in `data.py` collapses touchpoint rows into one row per journey. Attribution needs the ordered channel path, so this function creates fields like `path`, `path_string`, `journey_length`, and journey-level revenue.

`first_touch_attribution()` gives all converted revenue to the first channel in each converting path.

`last_touch_attribution()` gives all converted revenue to the last channel in each converting path.

`linear_attribution()` splits converted revenue equally across every touch in the converting path.

`markov_removal_attribution()` builds a transition graph from journey paths. It calculates the baseline conversion probability, removes one channel at a time, and measures how much conversion probability drops. Channels with larger drops receive more credit.

`budget_recommendation()` compares current budget to the Markov-informed budget. This is where the analysis becomes a business recommendation rather than just a model output.

`scenario_summary()` estimates conservative, balanced, and aggressive reallocation scenarios using a simple diminishing-returns assumption.

### How Markov Attribution Works Conceptually

A Markov chain is a map of movement from one state to another. In this project, the states are channels plus start, conversion, and non-conversion.

For example:

`Start -> Display -> Paid Search -> Email -> Conversion`

The model counts how often customers move from each state to the next. Then it asks, "What happens if Email is removed?" If removing Email causes the modeled conversion probability to drop a lot, Email gets a lot of credit. If removing Display also causes a drop, Display gets credit too, even if it was not the last touch.

That is why Markov attribution is more useful than last-touch for multi-step journeys. It uses the sequence, not just one position.

### How To Run The Project End To End

From the repo root:

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

`python scripts/run_all.py` regenerates:

- `data/synthetic/customer_journeys.csv`
- `outputs/*.csv`
- `reports/figures/*.png`
- `reports/summary.md`
- `reports/strategy_deck.md`
- `notebooks/marketing_attribution_analysis.ipynb`

### What To Point To First In A Technical Conversation

I would start with `src/attribution_roi/attribution.py`, especially `markov_removal_attribution()`, because that is the core analytical step beyond simple baselines.

Then I would show `src/attribution_roi/budget.py`, because it proves the project is not just modeling for modeling's sake. It connects the attribution result to an actual budget choice.

Finally, I would show `tests/test_attribution.py` to demonstrate that the basic attribution math is checked.

## Section 4: Anticipated Questions

### Why does attribution matter?

Because marketing budget is limited. If the measurement system gives too much credit to closing channels, the business may underfund channels that create demand. Attribution helps decide where the next dollar should go.

### Why not just use last-touch?

Last-touch is simple, but it ignores everything that happened before the final click. In this project, Display gets only 4.2% credit under last-touch but 11.6% under Markov. That difference can change the budget plan.

### Why use Markov over last-touch?

Markov uses the whole observed journey sequence. It estimates how much conversion probability drops when a channel is removed from the path graph. That makes it more journey-aware than simply giving all credit to the last touch.

### What does "the model is not proving causation" mean?

It means the model is looking at observed patterns, not running an experiment. If customers who see Email convert more often, the model can give Email credit, but it cannot prove Email caused those customers to convert. To prove causation, I would want incrementality tests, holdouts, or randomized experiments.

### What would you do differently with real spend data?

I would replace the synthetic budget assumptions with actual spend, media fees, gross margin, returns, discounts, and customer lifetime value. I would also separate new customers from returning customers and test whether channels saturate at higher spend levels.

### How confident are you in the numbers?

I am confident that the code produces the stated numbers for the synthetic assumptions. I would not claim the numbers predict a real business. The value is in the framework: compare attribution methods, quantify budget implications, and state the limits clearly.

### What is the biggest limitation?

The biggest limitation is that the data is synthetic and attribution is correlational. The project is a strong portfolio demonstration of method and business framing, not evidence about a real marketing program.

### Walk me through this function.

For `markov_removal_attribution()`, I would say: first it builds a transition graph from all journeys. Then it calculates the baseline probability of reaching conversion. Next it removes each channel one at a time and sends traffic that would have entered that channel to non-conversion. The bigger the conversion-probability drop, the more credit that channel gets.

## Glossary

**Attribution:** Assigning credit for a conversion across marketing channels.

**Conversion:** The desired customer action, such as a purchase or signup.

**Touchpoint:** One marketing interaction, such as an email click, paid search click, or display ad impression.

**Customer journey:** The ordered set of touchpoints before a conversion or non-conversion outcome.

**First-touch attribution:** Gives all credit to the first channel in a converting journey.

**Last-touch attribution:** Gives all credit to the final channel before conversion.

**Linear attribution:** Splits credit evenly across all touches in a converting journey.

**Markov chain:** A model that represents movement from one state to another, such as from Paid Social to Paid Search to Conversion.

**Removal effect:** The drop in modeled conversion probability when a channel is removed from the journey graph.

**ROAS:** Return on ad spend. Revenue divided by spend.

**Incremental ROAS:** Additional revenue divided by additional or shifted spend.

**Correlation:** A relationship between two things that move together.

**Causation:** Evidence that one thing caused another thing to happen.

**Incrementality test:** An experiment that estimates what would have happened with and without a marketing activity.

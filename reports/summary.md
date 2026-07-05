# Marketing Attribution & Budget ROI Analysis

## Bottom Line

Last-touch is not wildly wrong in this sample, but it still changes the budget conversation. The biggest bucket, `Long-tail placements`, gets 50.7% of credit under last-touch and 51.3% under Markov. The more useful signal is in the smaller placements: `Publisher 03` rises from 3.8% to 5.6% under Markov, while `Publisher 04` falls from 7.3% to 4.1%.

Using last-touch as the budget guide would move an estimated **$8.1K** of the assumed pilot budget away from the Markov-informed mix. A balanced reallocation shifts **$33.3K** toward the Markov recommendation and estimates **$6.5K** in assumed contribution lift.

I would treat this as a budget hypothesis, not a final answer. The model is using observed paths, so it is useful for prioritizing where to test, but it does not prove incrementality on its own.

## Dataset Profile

The sample comes from CriteoPrivateAd, a public anonymized advertising dataset hosted on Hugging Face. I use one processed day-one shard and filter to multi-touch users. That leaves **24,075 display touchpoints** across **11,343 journeys**. Conversion rate is **1.8%**, and the average journey has **2.12 touches**.

Criteo gives relative day partitions rather than real calendar dates, so `2025-01-01` is just a plotting date for `day_int=1`.

![Touchpoint frequency](figures/touchpoint_frequency_by_channel.png)

## Placement Performance Context

These conversion rates are descriptive. They answer, "when this placement group showed up in a journey, how often did that journey convert?" They do not answer, "how many conversions did this placement cause?"

| Channel | Touchpoints | Journeys Seen | Conversion Rate When Seen |
|---|---:|---:|---:|
| Publisher 08 | 236 | 138 | 3.6% |
| Publisher 04 | 550 | 300 | 3.3% |
| Publisher 02 | 2,190 | 1,227 | 2.0% |
| Publisher 06 | 319 | 199 | 2.0% |
| Publisher 01 | 4,631 | 2,615 | 1.8% |
| Publisher 07 | 274 | 165 | 1.8% |
| Long-tail placements | 13,994 | 7,147 | 1.7% |
| Publisher 03 | 1,341 | 879 | 1.5% |
| Publisher 05 | 540 | 310 | 1.3% |

## Attribution Model Comparison

First-touch and last-touch are useful because they are simple. The tradeoff is that each one throws away most of the path. Markov removal uses the sequence: it removes one placement group at a time and checks how much modeled conversion probability falls.

![Attribution comparison](figures/attribution_model_comparison.png)

| Channel | First Touch | Last Touch | Linear | Markov Removal |
|---|---:|---:|---:|---:|
| Long-tail placements | 54.5% | 50.7% | 51.9% | 51.3% |
| Publisher 01 | 19.9% | 21.0% | 21.2% | 20.4% |
| Publisher 02 | 8.0% | 9.8% | 9.1% | 10.9% |
| Publisher 03 | 4.9% | 3.8% | 4.3% | 5.6% |
| Publisher 04 | 7.0% | 7.3% | 7.2% | 4.1% |
| Publisher 05 | 1.7% | 1.7% | 1.6% | 2.1% |
| Publisher 06 | 0.3% | 1.4% | 0.9% | 1.7% |
| Publisher 07 | 2.1% | 2.4% | 2.3% | 1.5% |
| Publisher 08 | 1.4% | 1.7% | 1.6% | 2.3% |

## Budget Implication

Under the current pilot-budget assumption, Markov points more money toward `Long-tail placements` and less toward several named publisher groups. The largest positive gap is **Long-tail placements (+$51.2K)**. The largest reduction is **Publisher 03 (-$9.3K)**.

![Budget gap](figures/budget_gap_to_markov.png)

## Scenario Recommendation

| Scenario | Estimated Contribution Lift | Lift % | Incremental ROAS | Tradeoff |
|---|---:|---:|---:|---|
| Conservative rebalance | $3.8K | 11.0% | 0.21x | Move partway toward Markov credit; lowest disruption. |
| Balanced reallocation | $6.5K | 19.0% | 0.20x | Meaningful shift while keeping channel mix diversified. |
| Aggressive Markov target | $9.2K | 26.9% | 0.18x | Fully align budget with Markov credit; highest execution risk. |

My recommendation is the balanced scenario. It moves enough budget to matter without pretending the model is precise enough to justify a full immediate reallocation.

## Caveats And Assumptions

- The dataset is real Criteo data, but this repo uses one shard and filters to multi-touch users.
- Publisher IDs are anonymized, so the placement labels are readable names I assigned for analysis.
- The dollar layer is assumption-based. Criteo provides sales labels, not advertiser revenue or media budget.
- Markov attribution is correlational. I would validate any real budget move with incrementality testing, geo holdouts, randomized experiments, or media-mix modeling.

# Marketing Attribution & Budget ROI Analysis

## Executive Summary

- **Last-touch attribution materially changes channel credit.** The Markov removal model gives the most credit to Long-tail placements at 51.3% of assumed contribution value, while last-touch would credit that channel at 50.7%.
- **The budget issue is not just measurement; it is spend allocation.** A last-touch allocation would misdirect an estimated $8.1K, or 4.7% of the assumed pilot budget, versus the Markov-informed mix.
- **A balanced reallocation is the practical recommendation.** It estimates $6.5K assumed contribution lift (19.0%) while avoiding the execution risk of a full model-driven swing.
- **This is correlational, not causal.** Attribution models allocate credit across observed journeys; they do not prove incremental lift without experiments or stronger causal design.

## Dataset Profile

The repository uses a processed sample from CriteoPrivateAd, a public anonymized Criteo advertising dataset hosted on Hugging Face. The sample contains 24,075 display touchpoints across 11,343 multi-touch user journeys. Journey conversion rate is 1.8%; average journey length is 2.12 touches. Criteo provides relative day partitions rather than calendar dates, so the repo maps `day_int=1` to a relative plotting date.

![Touchpoint frequency](figures/touchpoint_frequency_by_channel.png)

## Channel Performance Context

Channel exposure conversion rates are descriptive. They should be read as "journeys that included this channel converted at this rate," not as a causal lift claim.

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

First-touch and last-touch answer simple operational questions, but they throw away most journey context. The Markov removal model asks how much the overall conversion probability falls when a publisher placement group is removed from paths, then allocates assumed contribution value based on that removal effect.

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

The largest positive Markov budget gap is Long-tail placements at $51.2K; the largest reduction is Publisher 03 at $-9.3K. Positive gaps indicate channels that would receive more budget under the Markov-informed allocation; negative gaps indicate reductions.

![Budget gap](figures/budget_gap_to_markov.png)

## Scenario Recommendation

| Scenario | Estimated Contribution Lift | Lift % | Incremental ROAS | Tradeoff |
|---|---:|---:|---:|---|
| Conservative rebalance | $3.8K | 11.0% | 0.21x | Move partway toward Markov credit; lowest disruption. |
| Balanced reallocation | $6.5K | 19.0% | 0.20x | Meaningful shift while keeping channel mix diversified. |
| Aggressive Markov target | $9.2K | 26.9% | 0.18x | Fully align budget with Markov credit; highest execution risk. |

## Caveats And Assumptions

- The dataset sample is real anonymized Criteo advertising data, but the repo filters to one day-one Parquet shard and multi-touch users.
- Markov attribution is correlational. It is better than last-touch for using journey sequence information, but it still cannot prove what would have happened without a channel.
- Dollarized spend and revenue are assumptions because this Criteo sample provides sales labels but not advertiser revenue or a channel budget.
- Spend response uses a simple diminishing-returns curve. Real budget decisions should be validated with incrementality tests, geo holdouts, media-mix modeling, or randomized lift studies.

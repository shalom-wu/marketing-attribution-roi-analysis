# Source Data Assumptions

This dataset sample is sourced from CriteoPrivateAd, a public anonymized Criteo advertising dataset hosted on Hugging Face. The repo keeps a processed sample rather than the raw Parquet shard.

| Field | Assumption |
|---|---|
| Dataset type | real public dataset sample |
| Source | [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd) |
| Source file | https://huggingface.co/datasets/criteo/CriteoPrivateAd/resolve/main/data/day_int=1/part-00238-7fb458b7-00d9-490c-b19b-addd568a5fe9-c000.gz.parquet |
| Grain | one display-ad impression row transformed into one attribution touchpoint |
| Source period | Criteo 30-day live traffic sample; repo sample uses day_int=1 shard part-00238 |
| Sample filter | users with at least two impressions in the downloaded shard |

## Transformation Notes

- channel is an anonymized publisher placement group. Top eight publishers by touch volume are mapped to Publisher 01-08; the rest are grouped as Long-tail placements.
- CriteoPrivateAd partitions by relative day_int, not real calendar dates. The repo maps day_int=1 to 2025-01-01 as a relative plotting date.
- Revenue is modeled as sales_count * $120 assumed contribution per sale because source data provides sales counts but not advertiser revenue.
- Channels included: Publisher 01, Publisher 02, Publisher 03, Publisher 04, Publisher 05, Publisher 06, Publisher 07, Publisher 08, Long-tail placements.

The source contains real anonymized display-ad impressions, campaign/publisher IDs, clicks, and sales labels. It does not contain named marketing channels, actual calendar dates, advertiser revenue, or a finance-approved media budget.

# Source Data Notes

This sample comes from CriteoPrivateAd, a public anonymized advertising dataset hosted on Hugging Face. I keep the processed sample in the repo and leave the raw Parquet shard out because it is large.

| Field | Assumption |
|---|---|
| Dataset type | real public dataset sample |
| Source | [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd) |
| Source file | https://huggingface.co/datasets/criteo/CriteoPrivateAd/resolve/main/data/day_int=1/part-00238-7fb458b7-00d9-490c-b19b-addd568a5fe9-c000.gz.parquet |
| Grain | one display-ad impression row transformed into one attribution touchpoint |
| Source period | Criteo 30-day live traffic sample; repo sample uses day_int=1 shard part-00238 |
| Sample filter | users with at least two impressions in the downloaded shard |

## Transformation Notes

- `channel` is an anonymized publisher placement group. The eight highest-volume publishers are labeled `Publisher 01` through `Publisher 08`; everything else is grouped as `Long-tail placements`.
- CriteoPrivateAd uses relative `day_int` partitions, not real calendar dates. I map `day_int=1` to `2025-01-01` only to keep plots and tables readable.
- Contribution value is modeled as `sales_count * $120` because the source provides sales labels, not advertiser revenue.
- Channels included: Publisher 01, Publisher 02, Publisher 03, Publisher 04, Publisher 05, Publisher 06, Publisher 07, Publisher 08, Long-tail placements.

The source contains real anonymized display-ad impressions, campaign and publisher IDs, click labels, and sales labels. It does not contain named marketing channels, actual calendar dates, advertiser revenue, or a finance-approved media budget.

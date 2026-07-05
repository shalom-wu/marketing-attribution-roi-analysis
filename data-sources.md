# Data Sources

## Selected Data Source

This project uses a processed sample from [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd), a public anonymized advertising dataset hosted by Criteo on Hugging Face.

The raw source file used by this repo is:

`https://huggingface.co/datasets/criteo/CriteoPrivateAd/resolve/main/data/day_int=1/part-00238-7fb458b7-00d9-490c-b19b-addd568a5fe9-c000.gz.parquet`

The raw file is not committed because it is roughly 100 MB. The committed project dataset is the processed sample at `data/processed/criteo_touchpoints_sample.csv`.

## Source Dataset Description

CriteoPrivateAd represents anonymized Criteo display advertising traffic. The dataset card describes it as a 100M-row sample of 30 days of Criteo live data, partitioned by `day_int`.

Fields used in this repo:

| Source field | Project use |
|---|---|
| `id` | Touchpoint ID |
| `user_id` | User/journey identifier |
| `display_order` | Touchpoint ordering within the observed user path |
| `campaign_id` | Source campaign identifier retained for audit |
| `publisher_id` | Source publisher identifier used to create placement groups |
| `is_clicked` | Descriptive engagement flag |
| `is_click_landed` | Descriptive engagement flag |
| `nb_sales` | Sales label used to define conversion and assumed contribution value |

## Transformation Methodology

The project runs `src/attribution_roi/source_data.py` to prepare the sample:

1. Download the CriteoPrivateAd day-one Parquet shard.
2. Keep users with at least two impressions so the analysis focuses on multi-touch journeys.
3. Sort impressions by `user_id`, `display_order`, and `id`.
4. Treat each impression as one attribution touchpoint.
5. Map the eight highest-volume publishers to `Publisher 01` through `Publisher 08`.
6. Group all remaining publishers as `Long-tail placements`.
7. Define journey conversion as `sales_count > 0`.
8. Use an assumed `$120` contribution per sale because source data provides sales counts but not advertiser revenue.
9. Map `day_int=1` to `2025-01-01` as a relative plotting date. This is not an actual Criteo calendar date.

## Budget Assumptions

The Criteo source data does not include a channel budget or advertiser revenue. To translate attribution into a business recommendation, the repo uses an explicit assumed pilot budget:

| Placement Group | Assumed Pilot Budget |
|---|---:|
| Publisher 01 | $42,000 |
| Publisher 02 | $28,000 |
| Publisher 03 | $19,000 |
| Publisher 04 | $12,000 |
| Publisher 05 | $11,000 |
| Publisher 06 | $9,000 |
| Publisher 07 | $8,000 |
| Publisher 08 | $7,000 |
| Long-tail placements | $38,000 |

These values are business assumptions for scenario modeling, not fields from the Criteo dataset.

## Citation

Dataset: [criteo/CriteoPrivateAd on Hugging Face](https://huggingface.co/datasets/criteo/CriteoPrivateAd)

CriteoPrivateAd references Criteo advertising research and is provided under the license stated on the dataset card. See the Hugging Face dataset card for current license and citation details.

## Important Caveat

Attribution outputs are correlational. They allocate credit across observed paths but do not prove that a placement caused the conversion. Any real budget move should be validated with incrementality testing, geo holdouts, randomized experiments, or media-mix modeling.

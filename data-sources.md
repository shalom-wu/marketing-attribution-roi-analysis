# Data Sources

I used [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd), a public anonymized advertising dataset hosted by Criteo on Hugging Face.

For this repo I worked from one shard:

`https://huggingface.co/datasets/criteo/CriteoPrivateAd/resolve/main/data/day_int=1/part-00238-7fb458b7-00d9-490c-b19b-addd568a5fe9-c000.gz.parquet`

That raw file is included at `data/raw/criteo_day1_part-00238.parquet` because
the portfolio requirement is that reviewers should not need to fetch data
before inspecting the project. The checked-in working file is the processed
project sample: `data/processed/criteo_touchpoints_sample.csv`.

## What The Source Gives Us

CriteoPrivateAd is anonymized display advertising traffic. The dataset card describes it as a 100M-row sample across 30 days, partitioned by `day_int`.

The fields I use are:

| Source field | How I use it |
|---|---|
| `id` | Touchpoint ID |
| `user_id` | User journey ID |
| `display_order` | Order of impressions in the observed path |
| `campaign_id` | Kept for auditability |
| `publisher_id` | Used to create anonymized placement groups |
| `is_clicked` | Descriptive engagement flag |
| `is_click_landed` | Descriptive engagement flag |
| `nb_sales` | Sales label used for conversion and assumed contribution value |

## How I Prepared It

The prep code lives in `src/attribution_roi/source_data.py`.

The short version:

1. Download the day-one Parquet shard.
2. Keep users with at least two impressions.
3. Sort each path by `user_id`, `display_order`, and `id`.
4. Treat each impression as one attribution touchpoint.
5. Label the eight highest-volume publishers as `Publisher 01` through `Publisher 08`.
6. Group the rest as `Long-tail placements`.
7. Mark a journey as converted when its total sales count is greater than zero.
8. Apply an assumed `$120` contribution per sale, since the source has sales labels but no advertiser revenue.
9. Map `day_int=1` to `2025-01-01` only so charts and tables have a date field. It is a relative date, not the real calendar date.

## Budget Inputs

CriteoPrivateAd does not include a channel budget. To turn attribution into a budget discussion, I used this assumed pilot budget:

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

These are modeling inputs, not source data fields.

## Citation And Caveat

Dataset: [criteo/CriteoPrivateAd on Hugging Face](https://huggingface.co/datasets/criteo/CriteoPrivateAd)

The Hugging Face dataset card was checked on 2026-07-06. It lists license
`cc-by-sa-4.0` and identifies the dataset owner as Criteo.

The attribution model is still correlational. It helps allocate credit across observed paths; it does not prove that a placement caused a sale. For a real budget move, I would pair this with an incrementality test, geo holdout, randomized experiment, or media-mix model.

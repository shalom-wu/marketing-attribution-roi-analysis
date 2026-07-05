from attribution_roi.source_data import download_criteo_source, prepare_criteo_touchpoints


if __name__ == "__main__":
    raw_path = download_criteo_source()
    prepare_criteo_touchpoints(raw_path)
    print(f"Downloaded and prepared Criteo source data from {raw_path}.")

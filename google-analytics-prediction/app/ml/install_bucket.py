def install_bucket(value: int) -> str:
    if value < 1_000:
        return "<1K"
    if value < 10_000:
        return "1K-<10K"
    if value < 100_000:
        return "10K-<100K"
    if value < 1_000_000:
        return "100K-<1M"
    if value < 10_000_000:
        return "1M-<10M"
    if value < 100_000_000:
        return "10M-<100M"
    return "100M+"

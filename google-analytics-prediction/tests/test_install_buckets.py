from app.ml import install_bucket, validate_rating

def test_install_bucket_boundaries():
    assert install_bucket(0) == "<1K"
    assert install_bucket(1000) == "1K-<10K"
    assert install_bucket(10_000) == "10K-<100K"
    assert install_bucket(100_000) == "100K-<1M"
    assert install_bucket(1_000_000) == "1M-<10M"
    assert install_bucket(10_000_000) == "10M-<100M"
    assert install_bucket(100_000_000) == "100M+"

def test_rating_is_bounded():
    assert validate_rating(5.5) == 5.0
    assert validate_rating(-0.2) == 0.0

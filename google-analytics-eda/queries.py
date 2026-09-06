"""
PostgreSQL queries used by the Google Play Analytics application.

This module contains SQL queries only.

Responsibilities:
    - Retrieve application data
    - Perform database-level aggregations
    - Prepare data required by the EDA modules

Business logic, statistical interpretation and visualization
remain outside this module.
"""


# ============================================================
# DATASET
# ============================================================

GET_ALL_APPS = """
SELECT
    id,
    app,
    category,
    rating,
    reviews,
    size_mb,
    installs,
    type,
    price,
    content_rating,
    genres,
    last_updated,
    current_version,
    android_version
FROM google_play_apps
ORDER BY id;
"""


# ============================================================
# DATASET OVERVIEW
# ============================================================

GET_DATASET_STATISTICS = """
SELECT
    COUNT(*) AS total_applications,

    COUNT(rating) AS applications_with_rating,

    COUNT(*) - COUNT(rating)
        AS applications_without_rating,

    COUNT(DISTINCT category)
        AS total_categories,

    COUNT(DISTINCT genres)
        AS total_genres,

    COUNT(DISTINCT content_rating)
        AS total_content_ratings,

    COUNT(DISTINCT type)
        AS total_types

FROM google_play_apps;
"""


# ============================================================
# EDA 01
# RATINGS BY CATEGORY
# ============================================================

GET_RATINGS_BY_CATEGORY = """
SELECT
    category,

    COUNT(*) AS app_count,

    COUNT(rating) AS rated_app_count,

    AVG(rating) AS average_rating,

    MIN(rating) AS minimum_rating,

    MAX(rating) AS maximum_rating,

    STDDEV(rating) AS rating_stddev,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY rating
        ) AS median_rating

FROM google_play_apps

WHERE rating IS NOT NULL

GROUP BY category

ORDER BY average_rating DESC;
"""


# ============================================================
# EDA 01
# TOP RATED CATEGORIES
# ============================================================

GET_TOP_RATED_CATEGORIES = """
SELECT
    category,

    COUNT(*) AS app_count,

    AVG(rating) AS average_rating

FROM google_play_apps

WHERE rating IS NOT NULL

GROUP BY category

HAVING COUNT(*) >= :minimum_apps

ORDER BY average_rating DESC

LIMIT :limit;
"""


# ============================================================
# EDA 01
# LOWEST RATED CATEGORIES
# ============================================================

GET_LOWEST_RATED_CATEGORIES = """
SELECT
    category,

    COUNT(*) AS app_count,

    AVG(rating) AS average_rating

FROM google_play_apps

WHERE rating IS NOT NULL

GROUP BY category

HAVING COUNT(*) >= :minimum_apps

ORDER BY average_rating ASC

LIMIT :limit;
"""


# ============================================================
# EDA 01
# RATING DISTRIBUTION
# ============================================================

GET_RATING_DISTRIBUTION = """
SELECT
    rating,
    COUNT(*) AS app_count

FROM google_play_apps

WHERE rating IS NOT NULL

GROUP BY rating

ORDER BY rating;
"""


# ============================================================
# EDA 02
# FREE VS PAID
# ============================================================

GET_FREE_PAID_DISTRIBUTION = """
SELECT
    type,

    COUNT(*) AS app_count,

    COUNT(rating) AS rated_app_count,

    AVG(rating) AS average_rating,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY rating
        ) AS median_rating,

    AVG(reviews) AS average_reviews,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY reviews
        ) AS median_reviews,

    SUM(reviews) AS total_reviews,

    AVG(price) AS average_price,

    MIN(price) AS minimum_price,

    MAX(price) AS maximum_price

FROM google_play_apps

GROUP BY type

ORDER BY type;
"""


# ============================================================
# EDA 02
# FREE VS PAID — RATING COMPARISON
# ============================================================

GET_FREE_PAID_RATING_COMPARISON = """
SELECT
    type,

    COUNT(*) AS app_count,

    AVG(rating) AS average_rating,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY rating
        ) AS median_rating,

    MIN(rating) AS minimum_rating,

    MAX(rating) AS maximum_rating

FROM google_play_apps

WHERE rating IS NOT NULL

GROUP BY type

ORDER BY average_rating DESC;
"""


# ============================================================
# EDA 02
# FREE VS PAID — REVIEW COMPARISON
# ============================================================

GET_FREE_PAID_REVIEW_COMPARISON = """
SELECT
    type,

    COUNT(*) AS app_count,

    AVG(reviews) AS average_reviews,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY reviews
        ) AS median_reviews,

    MIN(reviews) AS minimum_reviews,

    MAX(reviews) AS maximum_reviews,

    SUM(reviews) AS total_reviews

FROM google_play_apps

GROUP BY type

ORDER BY average_reviews DESC;
"""


# ============================================================
# EDA 02
# PAID APPLICATION PRICES
# ============================================================

GET_PAID_PRICE_STATISTICS = """
SELECT
    COUNT(*) AS paid_app_count,

    AVG(price) AS average_price,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY price
        ) AS median_price,

    MIN(price) AS minimum_price,

    MAX(price) AS maximum_price,

    STDDEV(price) AS price_stddev

FROM google_play_apps

WHERE type = 'PAID';
"""


# ============================================================
# EDA 03
# INSTALL DISTRIBUTION
# ============================================================

GET_INSTALL_DISTRIBUTION = """
SELECT
    installs,

    COUNT(*) AS app_count,

    CAST(
        REPLACE(
            REPLACE(installs, ',', ''),
            '+',
            ''
        ) AS BIGINT
    ) AS installs_numeric

FROM google_play_apps

GROUP BY installs

ORDER BY installs_numeric;
"""


# ============================================================
# EDA 03
# INSTALL DISTRIBUTION BY CATEGORY
# ============================================================

GET_INSTALLS_BY_CATEGORY = """
SELECT
    category,

    COUNT(*) AS app_count,

    AVG(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS average_installs,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY
                CAST(
                    REPLACE(
                        REPLACE(installs, ',', ''),
                        '+',
                        ''
                    ) AS BIGINT
                )
        ) AS median_installs,

    MIN(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS minimum_installs,

    MAX(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS maximum_installs,

    SUM(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS total_installs

FROM google_play_apps

GROUP BY category

ORDER BY median_installs DESC;
"""


# ============================================================
# EDA 03
# INSTALLS BY APPLICATION TYPE
# ============================================================

GET_INSTALLS_BY_TYPE = """
SELECT
    type,

    COUNT(*) AS app_count,

    AVG(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS average_installs,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY
                CAST(
                    REPLACE(
                        REPLACE(installs, ',', ''),
                        '+',
                        ''
                    ) AS BIGINT
                )
        ) AS median_installs,

    SUM(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS total_installs

FROM google_play_apps

GROUP BY type

ORDER BY average_installs DESC;
"""


# ============================================================
# EDA 03
# TOP INSTALLED APPLICATIONS
# ============================================================

GET_TOP_INSTALLED_APPS = """
SELECT
    app,

    category,

    rating,

    reviews,

    installs,

    type,

    price

FROM google_play_apps

ORDER BY
    CAST(
        REPLACE(
            REPLACE(installs, ',', ''),
            '+',
            ''
        ) AS BIGINT
    ) DESC

LIMIT :limit;
"""


# ============================================================
# EDA 03
# INSTALLS BY CATEGORY AND TYPE
# ============================================================

GET_INSTALLS_BY_CATEGORY_AND_TYPE = """
SELECT
    category,

    type,

    COUNT(*) AS app_count,

    AVG(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS average_installs,

    SUM(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS total_installs

FROM google_play_apps

GROUP BY
    category,
    type

ORDER BY
    category,
    type;
"""


# ============================================================
# EDA 04
# REVIEW STATISTICS
# ============================================================

GET_REVIEW_STATISTICS = """
SELECT
    COUNT(*) AS app_count,

    AVG(reviews) AS average_reviews,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY reviews
        ) AS median_reviews,

    MIN(reviews) AS minimum_reviews,

    MAX(reviews) AS maximum_reviews,

    STDDEV(reviews) AS review_stddev,

    SUM(reviews) AS total_reviews

FROM google_play_apps;
"""


# ============================================================
# EDA 04
# REVIEWS BY CATEGORY
# ============================================================

GET_REVIEWS_BY_CATEGORY = """
SELECT
    category,

    COUNT(*) AS app_count,

    AVG(reviews) AS average_reviews,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY reviews
        ) AS median_reviews,

    SUM(reviews) AS total_reviews,

    MAX(reviews) AS maximum_reviews

FROM google_play_apps

GROUP BY category

ORDER BY average_reviews DESC;
"""


# ============================================================
# EDA 04
# TOP REVIEWED APPLICATIONS
# ============================================================

GET_TOP_REVIEWED_APPS = """
SELECT
    app,

    category,

    rating,

    reviews,

    installs,

    type,

    price

FROM google_play_apps

ORDER BY reviews DESC

LIMIT :limit;
"""


# ============================================================
# EDA 04
# REVIEWS BY APPLICATION TYPE
# ============================================================

GET_REVIEWS_BY_TYPE = """
SELECT
    type,

    COUNT(*) AS app_count,

    AVG(reviews) AS average_reviews,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (
            ORDER BY reviews
        ) AS median_reviews,

    SUM(reviews) AS total_reviews,

    MAX(reviews) AS maximum_reviews

FROM google_play_apps

GROUP BY type

ORDER BY average_reviews DESC;
"""


# ============================================================
# EDA 04
# REVIEWS VS INSTALLS
# ============================================================

GET_REVIEWS_VS_INSTALLS = """
SELECT
    app,

    category,

    rating,

    reviews,

    installs,

    type,

    CAST(
        REPLACE(
            REPLACE(installs, ',', ''),
            '+',
            ''
        ) AS BIGINT
    ) AS installs_numeric

FROM google_play_apps

WHERE reviews IS NOT NULL

ORDER BY reviews DESC;
"""


# ============================================================
# EDA 04
# REVIEWS VS RATING
# ============================================================

GET_REVIEWS_VS_RATING = """
SELECT
    app,

    category,

    rating,

    reviews,

    installs,

    type

FROM google_play_apps

WHERE
    rating IS NOT NULL
    AND reviews IS NOT NULL

ORDER BY reviews DESC;
"""


# ============================================================
# CROSS-EDA
# CATEGORY OVERVIEW
# ============================================================

GET_CATEGORY_OVERVIEW = """
SELECT
    category,

    COUNT(*) AS app_count,

    AVG(rating) AS average_rating,

    AVG(reviews) AS average_reviews,

    SUM(reviews) AS total_reviews,

    AVG(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS average_installs,

    SUM(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS total_installs

FROM google_play_apps

GROUP BY category

ORDER BY app_count DESC;
"""


# ============================================================
# CROSS-EDA
# CATEGORY + TYPE OVERVIEW
# ============================================================

GET_CATEGORY_TYPE_OVERVIEW = """
SELECT
    category,

    type,

    COUNT(*) AS app_count,

    AVG(rating) AS average_rating,

    AVG(reviews) AS average_reviews,

    SUM(reviews) AS total_reviews,

    AVG(price) AS average_price,

    AVG(
        CAST(
            REPLACE(
                REPLACE(installs, ',', ''),
                '+',
                ''
            ) AS BIGINT
        )
    ) AS average_installs

FROM google_play_apps

GROUP BY
    category,
    type

ORDER BY
    category,
    type;
"""
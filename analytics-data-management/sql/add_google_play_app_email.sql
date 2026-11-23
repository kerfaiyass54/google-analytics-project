-- Owner email for newly created Google Play app records.
-- Existing rows are intentionally left NULL (ownership unknown).
ALTER TABLE google_play_apps
    ADD COLUMN IF NOT EXISTS email VARCHAR(320);

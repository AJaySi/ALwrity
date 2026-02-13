-- Add missing content asset source modules to the AssetSource PostgreSQL enum.
-- Safe to run multiple times.

DO $$
DECLARE
    enum_type_name text;
BEGIN
    SELECT t.typname
    INTO enum_type_name
    FROM pg_type t
    WHERE t.typname IN ('assetsource', 'asset_source')
    LIMIT 1;

    IF enum_type_name IS NULL THEN
        RAISE NOTICE 'AssetSource enum type not found. Skipping enum migration.';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = enum_type_name
          AND e.enumlabel = 'campaign_creator'
    ) THEN
        EXECUTE format('ALTER TYPE %I ADD VALUE ''campaign_creator''', enum_type_name);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = enum_type_name
          AND e.enumlabel = 'video_studio'
    ) THEN
        EXECUTE format('ALTER TYPE %I ADD VALUE ''video_studio''', enum_type_name);
    END IF;
END
$$;

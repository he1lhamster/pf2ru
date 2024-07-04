CREATE OR REPLACE FUNCTION extract_link_name(text) RETURNS text IMMUTABLE AS $$
DECLARE
    matches TEXT[];
    result TEXT := '';
BEGIN
    FOR matches IN SELECT regexp_matches($1, '\[\[.*?\|(.*?)\]\]', 'g') LOOP
        result := result || ' ' || matches[1];
    END LOOP;

    RETURN trim(result);
END;
$$ LANGUAGE plpgsql;
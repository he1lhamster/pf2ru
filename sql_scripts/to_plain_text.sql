CREATE OR REPLACE FUNCTION to_plain_text(text) RETURNS text IMMUTABLE  AS $$
DECLARE
    matches TEXT[];
    result TEXT;
BEGIN
    result := $1;
    FOR matches IN SELECT regexp_matches($1, '\[\[.*?\|(.*?)\]\]', 'g') LOOP
        result := regexp_replace(result, '\[\[.*?\|' || matches[1] || '\]\]', matches[1], 'g');
    END LOOP;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

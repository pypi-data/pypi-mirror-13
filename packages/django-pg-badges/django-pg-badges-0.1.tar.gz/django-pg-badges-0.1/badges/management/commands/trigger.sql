CREATE OR REPLACE FUNCTION badge_{name}() RETURNS trigger AS $badge_{name}$
BEGIN

    IF (
        NOT EXISTS (
        SELECT 1
             FROM badges_badge
             WHERE user_id=NEW.{user_field} AND code=code)
        AND (SELECT {condition})
                ) is TRUE THEN
    INSERT INTO badges_badge (user_id, name, code)
           VALUES (NEW.{user_field}, '{name}', '{code}');
    END IF;
    RETURN NEW;
END;
$badge_{name}$ LANGUAGE plpgsql;
CREATE TRIGGER badge_{name}
    AFTER {trigger_condition} ON {trigger_table}
    FOR EACH ROW
    EXECUTE PROCEDURE badge_{name}();

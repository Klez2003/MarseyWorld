#apply env vars
. /e

#generate seed-emojis-$SITE_NAME.sql
EXPORT_EMOJIS=$(psql --csv --tuples-only -P "null=NULL" -c \
        "SELECT ''''||name||'''', ' '''||kind||'''', ' '||2, ' '''||tags||'''', ' '||nsfw||'', ' '||created_utc||'' FROM emojis WHERE submitter_id IS NULL and author_id != 2 and author_id != 1076771 and name not ilike '%$SITE_NAME%' ORDER BY name" \
        "$DATABASE_URL")
EXPORT_EMOJIS=$(sed 's/.*/\(&\),/' <<< "$EXPORT_EMOJIS")
echo "INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES" > "/d/seed-emojis-$SITE_NAME.sql"
echo "${EXPORT_EMOJIS%?}" >> "/d/seed-emojis-$SITE_NAME.sql"
echo "ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags, kind = EXCLUDED.kind, nsfw = EXCLUDED.nsfw;" >> "/d/seed-emojis-$SITE_NAME.sql"

#pull and push
/d/scripts/g

#execute seed-emojis.sql of other site
if [ $SITE_NAME == "rDrama" ]; then
        psql "$DATABASE_URL" -f /d/seed-emojis-WPD.sql
else
        psql "$DATABASE_URL" -f /d/seed-emojis-rDrama.sql
fi

#clear cache for ppl who have NSFW warnings enabled
redis-cli del "${SITE}_flask_cache_emojis_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Tay_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Platy_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Wolf_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Donkey Kong_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Capy_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Carp_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey Flags_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey Alphabet_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Classic_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Rage_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Wojak_False"
redis-cli del "${SITE}_flask_cache_emoji_list_Misc_False"

#clear cache for ppl who have NSFW warnings disabled
redis-cli del "${SITE}_flask_cache_emojis_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Tay_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Platy_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Wolf_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Donkey Kong_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Capy_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Carp_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey Flags_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Marsey Alphabet_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Classic_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Rage_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Wojak_True"
redis-cli del "${SITE}_flask_cache_emoji_list_Misc_True"

redis-cli del "${SITE}_flask_cache_flag_emojis"

#sync original files
rclone copy /asset_submissions/emojis/original yes:emojis-original
rclone copy yes:emojis-original /asset_submissions/emojis/original

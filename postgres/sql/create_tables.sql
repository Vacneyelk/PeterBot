CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    watch_mode BOOLEAN
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    guild_id BIGINT REFERENCES guilds(guild_id)
);

CREATE TABLE IF NOT EXISTS channels (
    channel_id BIGINT PRIMARY KEY,
    guild_id BIGINT REFERENCES guilds(guild_id)
);

CREATE TABLE IF NOT EXISTS user_logs (
    user_id BIGINT REFERENCES users(user_id),
    guild_id BIGINT REFERENCES guilds(guild_id),
    message_id BIGINT,
    msg TEXT,
    msg_type TEXT,
    msg_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS voice_channels (
    voice_id BIGINT PRIMARY KEY,
    guild_id BIGINT REFERENCES guilds(guild_id),
    text_id BIGINT,
    role_id BIGINT
);

CREATE TABLE IF NOT EXISTS catalogue_alias (
    department TEXT PRIMARY KEY,
    guild_id BIGINT REFERENCES guilds(guild_id),
    alias TEXT
);

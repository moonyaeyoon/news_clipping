CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login_id VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    start_date DATE,
    end_date DATE,
    article_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_users_to_history
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE history_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    history_id UUID NOT NULL,
    title TEXT NOT NULL,
    source VARCHAR(100),
    published_date DATE,
    link TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_history_to_history_details
        FOREIGN KEY (history_id)
        REFERENCES history(id)
        ON DELETE CASCADE
);

CREATE TABLE scraps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    history_id UUID,
    title VARCHAR(200),
    article_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_users_to_scraps
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_history_to_scraps
        FOREIGN KEY (history_id)
        REFERENCES history(id)
        ON DELETE SET NULL
);

CREATE TABLE scrap_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scrap_id UUID NOT NULL,
    title TEXT NOT NULL,
    source VARCHAR(100),
    published_date DATE,
    link TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_scraps_to_scrap_articles
        FOREIGN KEY (scrap_id)
        REFERENCES scraps(id)
        ON DELETE CASCADE
);


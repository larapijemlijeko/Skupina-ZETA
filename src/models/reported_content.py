def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reported_content (
            id SERIAL PRIMARY KEY,
            content_type VARCHAR(20) NOT NULL, -- 'forum' ali 'comment'
            content_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            reported_by INTEGER NOT NULL,
            date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

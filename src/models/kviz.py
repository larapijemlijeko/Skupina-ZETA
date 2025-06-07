
def create_table(cur):
    cur.execute("""
        CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    options TEXT[] NOT NULL,
    answer TEXT NOT NULL
);

INSERT INTO quiz_questions (question, options, answer) VALUES
(
    'What is the capital of France?',
    ARRAY['London', 'Berlin', 'Paris', 'Rome'],
    'Paris'
),
(
    'Which planet is known as the Red Planet?',
    ARRAY['Earth', 'Mars', 'Jupiter', 'Saturn'],
    'Mars'
),
(
    'What is the largest ocean on Earth?',
    ARRAY['Atlantic', 'Indian', 'Arctic', 'Pacific'],
    'Pacific'
); 
    """)
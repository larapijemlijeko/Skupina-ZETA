
def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    options TEXT[] NOT NULL,
    answer TEXT NOT NULL
);

INSERT INTO quiz_questions (question, options, answer) VALUES
(
    'Which country is famous for inventing pizza?',
    ARRAY['France', 'Italy', 'USA', 'Germany'],
    'Italy'
),
(
    'What is the main ingredient in guacamole?',
    ARRAY['Tomato', 'Avocado', 'Cucumber', 'Pepper'],
    'Avocado'
),
(
    'Which vitamin is most prevalent in oranges?',
    ARRAY['Vitamin A', 'Vitamin B', 'Vitamin C', 'Vitamin D'],
    'Vitamin C'
),
(
    'What type of food is Brie?',
    ARRAY['Bread', 'Cheese', 'Fruit', 'Pasta'],
    'Cheese'
),
(
    'Sushi originates from which country?',
    ARRAY['China', 'Japan', 'Thailand', 'South Korea'],
    'Japan'
),
(
    'Which grain is used to make risotto?',
    ARRAY['Basmati rice', 'Brown rice', 'Arborio rice', 'Jasmine rice'],
    'Arborio rice'
),
(
    'What is tofu made from?',
    ARRAY['Cheese', 'Rice', 'Soybeans', 'Wheat'],
    'Soybeans'
),
(
    'Which sauce is traditionally used on eggs benedict?',
    ARRAY['Béchamel', 'Marinara', 'Hollandaise', 'Pesto'],
    'Hollandaise'
),
(
    'Which country is the largest producer of coffee in the world?',
    ARRAY['Colombia', 'Vietnam', 'Brazil', 'Ethiopia'],
    'Brazil'
),
(
    'What kind of nuts are used to make marzipan?',
    ARRAY['Walnuts', 'Almonds', 'Cashews', 'Hazelnuts'],
    'Almonds'
);
    """)

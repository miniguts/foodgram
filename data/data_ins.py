import json
import sqlite3


with open('../data/ingredients.json', 'r', encoding='utf-8') as f:
    ingredients = json.load(f)

with open('../data/tags.json', 'r', encoding='utf-8') as f:
    tags = json.load(f)

conn = sqlite3.connect('../backend/db.sqlite3')
cursor = conn.cursor()

for item in ingredients:
    cursor.execute("""
        INSERT INTO recipes_ingredient (name, measurement_unit)
        VALUES (?, ?)
    """, (item['name'], item['measurement_unit']))

for tag in tags:
    cursor.execute("""
        INSERT INTO recipes_tag (name, slug)
        VALUES (?, ?)
    """, (tag['name'], tag['slug']))

conn.commit()
conn.close()

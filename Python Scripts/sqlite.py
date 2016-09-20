
import sqlite3
import pandas as pd

# Fetch records from the database
db = sqlite3.connect("IrvineMaps.db")
c = db.cursor()
QUERY = "SELECT tags.value, COUNT(*) as count FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) tags WHERE tags.key='postcode' GROUP BY tags.value ORDER BY count DESC;"
c.execute(QUERY)
rows = c.fetchall()
    
df = pd.DataFrame(rows)
print df

db.close()

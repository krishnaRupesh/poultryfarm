import sqlite3

conn = sqlite3.connect('backend/poultry.db')
c = conn.cursor()

# Insert Shed A & Shed B
c.execute("""
INSERT OR IGNORE INTO sheds (shed_id, shed_name, capacity, shed_type, status, location, description, created_by)
VALUES (1, 'Shed A', 10000, 'Layer', 'Active', 'North Wing', 'Automated nipple drinking and belt feeding', 'system')
""")
c.execute("""
INSERT OR IGNORE INTO sheds (shed_id, shed_name, capacity, shed_type, status, location, description, created_by)
VALUES (2, 'Shed B', 8000, 'Layer', 'Active', 'South Wing', 'Semi-automated layer shed', 'system')
""")

# Insert Batches 2026-march-a and 2026-june-b
c.execute("""
INSERT OR IGNORE INTO flock_batches (batch_id, batch_name, shed_id, breed, bird_type, placement_date, initial_birds, current_birds, initial_age_weeks, status, remarks, created_by)
VALUES (1, '2026-march-a', 1, 'BV300 Layer', 'Layer', '2026-03-01', 10000, 9840, 18, 'Active', 'Batch placed in Shed A; peak laying phase', 'system')
""")
c.execute("""
INSERT OR IGNORE INTO flock_batches (batch_id, batch_name, shed_id, breed, bird_type, placement_date, initial_birds, current_birds, initial_age_weeks, status, remarks, created_by)
VALUES (2, '2026-june-b', 2, 'Hy-Line Brown', 'Layer', '2026-06-15', 6000, 5970, 18, 'Active', 'Batch placed in Shed B; young laying flock', 'system')
""")

# Update existing flock status & consumption records with batch_id 1
c.execute("UPDATE daily_flock_status SET batch_id = 1, shed_id = 1 WHERE batch_id IS NULL")
c.execute("UPDATE daily_feed_consumption SET batch_id = 1, shed_id = 1 WHERE batch_id IS NULL")
c.execute("UPDATE daily_egg_operations SET batch_id = 1, shed_id = 1 WHERE batch_id IS NULL")

conn.commit()
conn.close()
print("Sample sheds and batches seeded successfully!")

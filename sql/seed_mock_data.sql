-- ===========================================================================
-- DML Script: Poultry Farm Feed Inventory & Operations Mock Data
-- ===========================================================================

-- 1. Insert Initial Feed Items
INSERT INTO feed_items (name, category, default_unit, current_stock_kg, average_cost_per_kg, reorder_level_kg, created_by)
VALUES
('Yellow Corn', 'Grains', 'kg', 8500.00, 0.2800, 2000.00, 'seed_data'),
('Soybean Meal (48%)', 'Protein Meal', 'kg', 3200.00, 0.5500, 1000.00, 'seed_data'),
('De-oiled Rice Bran (DORB)', 'Energy & Fiber', 'kg', 2400.00, 0.2200, 800.00, 'seed_data'),
('Calcite Grit / Limestone', 'Minerals', 'kg', 1800.00, 0.0900, 500.00, 'seed_data'),
('Layer Vitamin & Mineral Premix', 'Supplements', 'kg', 450.00, 1.8000, 100.00, 'seed_data'),
('Dicalcium Phosphate (DCP)', 'Minerals', 'kg', 600.00, 0.7500, 150.00, 'seed_data')
ON CONFLICT(name) DO UPDATE SET
current_stock_kg=excluded.current_stock_kg,
average_cost_per_kg=excluded.average_cost_per_kg;

-- 2. Insert Feed Purchases
INSERT INTO feed_purchases (item_id, purchase_date, quantity_kg, cost_per_kg, total_cost, vendor_name, invoice_no, remarks, created_by)
VALUES
(1, '2026-09-20', 10000.00, 0.2700, 2700.00, 'Agro Grains Corp', 'INV-CORN-901', 'Bulk procurement 10 MT Corn', 'seed_data'),
(2, '2026-09-22', 4000.00, 0.5400, 2160.00, 'Soya Pro Mills Ltd', 'INV-SOYA-412', '4 MT High Protein Soya', 'seed_data'),
(3, '2026-09-24', 3000.00, 0.2100, 630.00, 'Golden Harvest Mills', 'INV-DORB-108', '3 MT DORB delivered', 'seed_data'),
(4, '2026-09-25', 2000.00, 0.0900, 180.00, 'Minchem Minerals Ltd', 'INV-MIN-554', 'Oyster/Calcite Grit', 'seed_data'),
(5, '2026-09-26', 500.00, 1.8000, 900.00, 'NutriVet Solutions', 'INV-VET-883', 'Layer Booster Premix pack', 'seed_data'),
(1, '2026-10-01', 5000.00, 0.2900, 1450.00, 'Agro Grains Corp', 'INV-CORN-995', '5 MT Corn replenishment', 'seed_data');

-- 3. Daily Flock Status (10,000 birds)
INSERT INTO daily_flock_status (date, active_birds, mortality, remarks, created_by)
VALUES
('2026-10-01', 10000, 4, 'Flock in Shed A & B healthy and laying normally', 'seed_data'),
('2026-10-02', 9996, 3, 'Weather stable, good feed intake', 'seed_data'),
('2026-10-03', 9993, 5, 'Routine vet inspection done', 'seed_data'),
('2026-10-04', 9988, 2, 'Normal conditions', 'seed_data'),
('2026-10-05', 9986, 3, 'Active laying flock count confirmed', 'seed_data')
ON CONFLICT(date) DO UPDATE SET
active_birds=excluded.active_birds,
mortality=excluded.mortality;

-- 4. Daily Feed Consumption (1 MT Corn + other ingredients per day)
INSERT INTO daily_feed_consumption (date, item_id, quantity_kg, cost_per_kg, total_cost, remarks, created_by)
VALUES
-- 2026-10-01
('2026-10-01', 1, 1000.00, 0.2800, 280.00, '1 Metric Ton corn morning & evening feed', 'seed_data'),
('2026-10-01', 2, 250.00, 0.5500, 137.50, 'Soybean meal protein portion', 'seed_data'),
('2026-10-01', 3, 150.00, 0.2200, 33.00, 'Rice bran', 'seed_data'),
('2026-10-01', 4, 80.00, 0.0900, 7.20, 'Calcite grit for shell thickness', 'seed_data'),
('2026-10-01', 5, 15.00, 1.8000, 27.00, 'Premix dosage', 'seed_data'),
-- 2026-10-02
('2026-10-02', 1, 1000.00, 0.2800, 280.00, '1 Metric Ton corn', 'seed_data'),
('2026-10-02', 2, 240.00, 0.5500, 132.00, 'Soybean meal', 'seed_data'),
('2026-10-02', 3, 150.00, 0.2200, 33.00, 'Rice bran', 'seed_data'),
('2026-10-02', 4, 85.00, 0.0900, 7.65, 'Calcite grit', 'seed_data'),
('2026-10-02', 5, 15.00, 1.8000, 27.00, 'Premix', 'seed_data'),
-- 2026-10-03
('2026-10-03', 1, 1000.00, 0.2800, 280.00, '1 Metric Ton corn', 'seed_data'),
('2026-10-03', 2, 260.00, 0.5500, 143.00, 'Soybean meal', 'seed_data'),
('2026-10-03', 3, 140.00, 0.2200, 30.80, 'Rice bran', 'seed_data'),
('2026-10-03', 4, 80.00, 0.0900, 7.20, 'Calcite grit', 'seed_data'),
('2026-10-03', 5, 15.00, 1.8000, 27.00, 'Premix', 'seed_data'),
-- 2026-10-04
('2026-10-04', 1, 1000.00, 0.2800, 280.00, '1 Metric Ton corn', 'seed_data'),
('2026-10-04', 2, 250.00, 0.5500, 137.50, 'Soybean meal', 'seed_data'),
('2026-10-04', 3, 150.00, 0.2200, 33.00, 'Rice bran', 'seed_data'),
('2026-10-04', 4, 80.00, 0.0900, 7.20, 'Calcite grit', 'seed_data'),
('2026-10-04', 5, 15.00, 1.8000, 27.00, 'Premix', 'seed_data'),
-- 2026-10-05
('2026-10-05', 1, 1000.00, 0.2800, 280.00, '1 Metric Ton corn', 'seed_data'),
('2026-10-05', 2, 250.00, 0.5500, 137.50, 'Soybean meal', 'seed_data'),
('2026-10-05', 3, 160.00, 0.2200, 35.20, 'Rice bran', 'seed_data'),
('2026-10-05', 4, 85.00, 0.0900, 7.65, 'Calcite grit', 'seed_data'),
('2026-10-05', 5, 15.00, 1.8000, 27.00, 'Premix', 'seed_data');

-- 5. Daily Egg Operations (Opening stock, Produced, Damaged, Eggs Sold, Closing stock, Price, Revenue)
INSERT INTO daily_egg_operations (date, opening_stock, eggs_produced, damaged_eggs, eggs_available, eggs_sold, closing_stock, egg_price_per_unit, actual_revenue, remarks, created_by)
VALUES
('2026-10-01', 500, 8750, 42, 9208, 7200, 2008, 0.0750, 540.00, 'Good production; 7,200 sold to wholesale distributor', 'seed_data'),
('2026-10-02', 2008, 8820, 38, 10790, 8500, 2290, 0.0760, 646.00, 'High delivery demand', 'seed_data'),
('2026-10-03', 2290, 8780, 45, 11025, 7000, 4025, 0.0740, 518.00, 'Steady collections', 'seed_data'),
('2026-10-04', 4025, 8710, 50, 12685, 9500, 3185, 0.0750, 712.50, 'Weekend market clearance delivery', 'seed_data'),
('2026-10-05', 3185, 8840, 35, 11990, 8000, 3990, 0.0780, 624.00, 'Today collection; egg rates increased to $0.078', 'seed_data')
ON CONFLICT(date) DO UPDATE SET
opening_stock=excluded.opening_stock,
eggs_produced=excluded.eggs_produced,
damaged_eggs=excluded.damaged_eggs,
eggs_available=excluded.eggs_available,
eggs_sold=excluded.eggs_sold,
closing_stock=excluded.closing_stock,
egg_price_per_unit=excluded.egg_price_per_unit,
actual_revenue=excluded.actual_revenue;

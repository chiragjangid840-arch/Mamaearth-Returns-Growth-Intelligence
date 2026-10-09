-- Mamaearth Returns & Growth Intelligence
-- SQLite database se CSV import Python script handle karti hai.
-- Run analysis/load_sqlite.py before executing these checks.

PRAGMA foreign_keys = ON;

-- Verify imported row counts
SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers

UNION ALL

SELECT 'products', COUNT(*)
FROM products

UNION ALL

SELECT 'orders', COUNT(*)
FROM orders;

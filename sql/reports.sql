-- Mamaearth Returns & Growth Intelligence
-- SQLite-compatible SQL reports

-- 1. Total orders, revenue and average order value
SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS average_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- 2. Rated and unrated orders
SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

-- 3. Customers with no orders
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- 4. Cities with return rate above 20%
SELECT
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(o.order_id), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING 100.0 * SUM(o.returned) / COUNT(o.order_id) > 20
ORDER BY return_rate_pct DESC;

-- 5. Top 5 customers by revenue
SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id
LIMIT 5;

-- 6. Revenue by product category
SELECT
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- 7. Customers whose name starts with A
SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;

-- 8. Customer acquisition sources
SELECT acquisition_source, COUNT(*) AS customer_count
FROM customers
GROUP BY acquisition_source
ORDER BY acquisition_source;

-- 9. Loyalty tier based on city tier
SELECT
    CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END AS loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END
ORDER BY loyalty_tier;

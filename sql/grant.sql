-- Create or target a reporting role/group (document if custom group creation is restricted on trial)
GRANT USE CATALOG ON CATALOG workspace TO `account users`;

GRANT USE SCHEMA ON SCHEMA workspace.ecom_poc TO `account users`;

-- Least-privilege SELECT on Gold tables only (no Bronze/Silver grants)
GRANT
SELECT ON
TABLE workspace.ecom_poc.gold_daily_sales TO `account users`;

GRANT
SELECT ON
TABLE workspace.ecom_poc.gold_revenue_breakdown TO `account users`;

GRANT
SELECT ON
TABLE workspace.ecom_poc.gold_payment_success TO `account users`;

GRANT
SELECT ON
TABLE workspace.ecom_poc.gold_top_customers TO `account users`;

-- Verify effective grants on Gold vs. Silver
SHOW GRANTS ON TABLE workspace.ecom_poc.gold_daily_sales;

SHOW GRANTS ON TABLE workspace.ecom_poc.silver_orders;
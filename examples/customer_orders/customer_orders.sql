/*
  AutoPipeline Generated SQL Transformation
  Generated at: 2026-07-16T14:46:50.524323+00:00
  Target: urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.customers,PROD)
  Sources: order_entry_db.order_entry.customers
*/

-- Contains customer demographic and contact information

-- Source: CUSTOMERS (snowflake)

WITH

CUSTOMERS AS (
    SELECT
        customer_id,        cust_first_name,        cust_last_name,        nls_language,        nls_territory,        credit_limit,        cust_email,        account_mgr_id,        customer_since,        customer_class,        suggestions,        dob,        mailshot,        partner_mailshot,        phone_number,        address_line1,        address_line2,        address_line3,        town_city,        country_id,        zipcode,        region_id    FROM order_entry_db.order_entry.CUSTOMERS
),


transformed AS (
    SELECT
        customer_id AS customer_id,        cust_first_name AS cust_first_name,        cust_last_name AS cust_last_name,        nls_language AS nls_language,        nls_territory AS nls_territory,        credit_limit AS credit_limit,        cust_email AS cust_email,        account_mgr_id AS account_mgr_id,        customer_since AS customer_since,        customer_class AS customer_class,        suggestions AS suggestions,        dob AS dob,        mailshot AS mailshot,        partner_mailshot AS partner_mailshot,        phone_number AS phone_number,        address_line1 AS address_line1,        address_line2 AS address_line2,        address_line3 AS address_line3,        town_city AS town_city,        country_id AS country_id,        zipcode AS zipcode,        region_id AS region_id    FROM CUSTOMERS
)

SELECT * FROM transformed;
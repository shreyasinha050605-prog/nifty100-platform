-- 1. Total companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- 2. Total stock price records
SELECT COUNT(*) AS stock_price_records
FROM stock_prices;

-- 3. Companies with highest sales (latest year)
SELECT company_id, sales
FROM profitandloss
WHERE year='Mar 2024'
ORDER BY sales DESC
LIMIT 10;

-- 4. Highest net profit companies
SELECT company_id, net_profit
FROM profitandloss
WHERE year='Mar 2024'
ORDER BY net_profit DESC
LIMIT 10;

-- 5. Debt free companies
SELECT company_id, borrowings
FROM balancesheet
WHERE year='Mar 2024'
AND borrowings=0;

-- 6. Highest ROE companies
SELECT company_id, return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- 7. Companies by sector
SELECT broad_sector, COUNT(*)
FROM sectors
GROUP BY broad_sector
ORDER BY COUNT(*) DESC;

-- 8. Top market cap companies
SELECT company_id, market_cap_crore
FROM market_cap
WHERE year=2024
ORDER BY market_cap_crore DESC
LIMIT 10;

-- 9. Companies with positive free cash flow
SELECT company_id, free_cash_flow_cr
FROM financial_ratios
WHERE free_cash_flow_cr > 0
ORDER BY free_cash_flow_cr DESC;

-- 10. Company document count
SELECT company_id, COUNT(*) AS reports
FROM documents
GROUP BY company_id
ORDER BY reports DESC;
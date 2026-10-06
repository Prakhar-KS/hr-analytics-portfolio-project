-- Business Question: How does attrition rate compare across departments, and which departments contribute most to total leavers?
-- Uses: CTEs, Aggregate Functions, Window Functions (RANK, AVG, SUM)
WITH DeptStats AS (
    SELECT 
        d.department_name,
        COUNT(e.employee_id) AS headcount,
        SUM(e.attrition_flag) AS leavers,
        CAST(SUM(e.attrition_flag) AS FLOAT) / COUNT(e.employee_id) AS attrition_rate
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    GROUP BY d.department_name
)
SELECT 
    department_name,
    headcount,
    leavers,
    attrition_rate,
    RANK() OVER (ORDER BY attrition_rate DESC) AS attrition_rank,
    AVG(attrition_rate) OVER () AS company_avg_attrition,
    attrition_rate - AVG(attrition_rate) OVER () AS gap_vs_company_avg,
    CAST(leavers AS FLOAT) / SUM(leavers) OVER () AS share_of_total_leavers
FROM DeptStats;

-- Business Question: How does pay relate to attrition within departments? Do lower-paid employees leave more frequently?
-- Uses: CTEs, Aggregate Functions, Window Functions (NTILE, LAG)
WITH EmployeeQuartiles AS (
    SELECT 
        e.employee_id,
        d.department_name,
        e.attrition_flag,
        c.monthly_income,
        NTILE(4) OVER (PARTITION BY d.department_name ORDER BY c.monthly_income) AS income_quartile
    FROM employees e
    JOIN compensation c ON e.employee_id = c.employee_id
    JOIN departments d ON e.department_id = d.department_id
),
QuartileStats AS (
    SELECT 
        department_name,
        income_quartile,
        AVG(CAST(monthly_income AS FLOAT)) AS avg_income,
        CAST(SUM(attrition_flag) AS FLOAT) / COUNT(employee_id) AS attrition_rate
    FROM EmployeeQuartiles
    GROUP BY department_name, income_quartile
)
SELECT 
    department_name,
    income_quartile,
    avg_income,
    attrition_rate,
    LAG(attrition_rate, 1) OVER (PARTITION BY department_name ORDER BY income_quartile) AS prev_quartile_attrition_rate,
    attrition_rate - LAG(attrition_rate, 1) OVER (PARTITION BY department_name ORDER BY income_quartile) AS attrition_rate_diff
FROM QuartileStats
ORDER BY department_name, income_quartile;

-- Business Question: What is the combined risk of overtime and tenure? 
-- Uses: CTEs, Aggregate Functions, Window Functions (SUM, DENSE_RANK, Conditional Aggregation)
WITH BaseStats AS (
    SELECT 
        tenure_band,
        over_time,
        COUNT(employee_id) AS headcount,
        SUM(attrition_flag) AS leavers,
        CAST(SUM(attrition_flag) AS FLOAT) / NULLIF(COUNT(employee_id), 0) AS attrition_rate
    FROM employees
    GROUP BY tenure_band, over_time
),
AggStats AS (
    SELECT 
        tenure_band,
        MAX(CASE WHEN over_time = 'Yes' THEN attrition_rate END) AS overtime_attrition_rate,
        MAX(CASE WHEN over_time = 'No' THEN attrition_rate END) AS no_overtime_attrition_rate,
        SUM(leavers) AS total_leavers_in_band
    FROM BaseStats
    GROUP BY tenure_band
)
SELECT 
    tenure_band,
    overtime_attrition_rate,
    no_overtime_attrition_rate,
    total_leavers_in_band,
    SUM(total_leavers_in_band) OVER (ORDER BY tenure_band ROWS UNBOUNDED PRECEDING) AS cumulative_leavers,
    overtime_attrition_rate / NULLIF(no_overtime_attrition_rate, 0) AS overtime_risk_ratio,
    DENSE_RANK() OVER (ORDER BY (overtime_attrition_rate - COALESCE(no_overtime_attrition_rate, 0)) DESC) AS highest_risk_rank
FROM AggStats
ORDER BY tenure_band;

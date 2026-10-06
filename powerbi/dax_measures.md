# DAX Measures for HR Analytics Dashboard

| Name | Expression | Purpose |
|------|------------|---------|
| Total Employees | `COUNTROWS(employees)` | Total number of employees in the dataset. |
| Attrition Count | `CALCULATE(COUNTROWS(employees), employees[attrition_flag] = 1)` | Total number of employees who have left the company. |
| Active Employees | `[Total Employees] - [Attrition Count]` | Number of current employees. |
| Attrition Rate % | `DIVIDE([Attrition Count], [Total Employees])` | Percentage of employees who have left the company. |
| Avg Monthly Income | `AVERAGE(compensation[monthly_income])` | Average monthly income across employees. |
| Avg Income - Leavers | `CALCULATE([Avg Monthly Income], employees[attrition_flag] = 1)` | Average monthly income for employees who left. |
| Avg Income - Stayers | `CALCULATE([Avg Monthly Income], employees[attrition_flag] = 0)` | Average monthly income for employees who stayed. |
| Overtime Employees | `CALCULATE(COUNTROWS(employees), employees[over_time] = "Yes")` | Total number of employees working overtime. |
| Attrition Rate % - Overtime | `CALCULATE([Attrition Rate %], employees[over_time] = "Yes")` | Attrition rate among employees working overtime. |
| Attrition Rate % - No Overtime | `CALCULATE([Attrition Rate %], employees[over_time] = "No")` | Attrition rate among employees not working overtime. |
| Attrition by Overtime Gap (pp) | `[Attrition Rate % - Overtime] - [Attrition Rate % - No Overtime]` | Difference in attrition rate between overtime and no overtime employees. |
| Avg Tenure (Years) | `AVERAGE(employees[years_at_company])` | Average number of years employees have been at the company. |
| Avg Job Satisfaction | `AVERAGE(satisfaction[job_satisfaction])` | Average job satisfaction score (1-4). |
| Avg Years Since Promotion | `AVERAGE(employees[years_since_last_promotion])` | Average number of years since the last promotion. |
| Attrition Rate vs Company | `[Attrition Rate %] - CALCULATE([Attrition Rate %], ALL(employees))` | Comparison of a segment's attrition rate against the overall company rate. |

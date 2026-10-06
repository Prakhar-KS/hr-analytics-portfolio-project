# HR Analytics Dashboard

## Project Overview
This project is an end-to-end HR analytics data pipeline and visualization suite that analyzes employee attrition, compensation, and satisfaction. It leverages a dataset of 1470 employees (from the IBM HR Analytics Employee Attrition & Performance Kaggle dataset) to uncover the drivers behind employee turnover.

The project demonstrates a modern data stack architecture:
1. **Python (Pandas)**: Data extraction, cleaning, normalization, and relational structuring.
2. **SQL (SQLite / SQL Server)**: Relational schema creation, data loading, and advanced analytical queries using CTEs and Window Functions.
3. **Power BI**: A semantic model utilizing DAX for metrics calculation and interactive dashboarding.

## Architecture & Data Pipeline
The ELT (Extract, Load, Transform) pipeline works as follows:
- **Raw Data**: A single flat file (`data/raw/raw_hr_data.csv`).
- **Data Transformation (`src/etl_pipeline.py`)**: The raw data is validated, cleaned (removing duplicates and low-variance columns like `StandardHours`), and structured into five normalized CSV tables (`departments.csv`, `job_roles.csv`, `employees.csv`, `compensation.csv`, `satisfaction.csv`) stored in `data/clean/`.
- **Database Load (`src/load_to_sql.py`)**: Creates a normalized relational schema (`sql/schema.sql`) and loads the data into a database. (Fallback logic is in place to utilize SQLite if SQL Server is unavailable).
- **Analysis Execution (`src/run_analysis.py`)**: Runs advanced analytical queries (`sql/advanced_analysis.sql`) and outputs findings into the `docs/` folder.
- **Power BI Semantic Model**: Hosted locally in `HR_Dashboard.pbix`, defining relationships and custom DAX measures for rich reporting.

## Key Business Insights

Based on our advanced SQL/Pandas analysis (`docs/query_results_q*.csv`), several key findings have emerged regarding employee attrition:

### 1. Departmental Attrition (Q1 Results)
- **Sales is the highest-risk department**: With an attrition rate of **20.6%**, Sales outpaces the company average. Despite having a smaller headcount than R&D, Sales accounts for ~38.8% of all employees who leave the company.
- **R&D has high retention**: Research & Development exhibits the lowest attrition rate at just **13.8%**, indicating a relatively stable working environment compared to other divisions.

### 2. Compensation as a Retention Driver (Q2 Results)
- Across almost all departments, placing employees in the lowest income quartile results in dramatically higher attrition.
- For example, in **Sales**, employees in Quartile 1 have a **31.25%** attrition rate, which sharply drops to **16.0%** in Quartile 2.
- In **Human Resources**, Quartile 1 attrition reaches an alarming **37.5%**, suggesting that entry-level or poorly compensated HR roles are highly volatile.

### 3. The Overtime Burnout Effect (Q3 Results)
- **Early-tenure employees working overtime are at severe risk**: Employees with 0-2 years of tenure who work overtime have a shocking **50.9%** attrition rate, compared to just 20.5% for those in the same cohort who do not work overtime (a risk ratio of **2.47x**).
- This single cohort accounts for **102 leavers**, making it the single largest driver of attrition in the company. Burnout from overtime hits newest employees the hardest.

## Setup Instructions

### Environment
1. Ensure you have Python 3.9+ installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline
1. **Run ETL**: `python src/etl_pipeline.py`
2. **Load to SQL**: `python src/load_to_sql.py`
3. **Run Analysis**: `python src/run_analysis.py`

### Power BI
Open `HR_Dashboard.pbix` in Power BI Desktop to view the semantic model. It includes 15 DAX measures structured under a dedicated `_Measures` table, calculating metrics such as Average Age, Attrition Rate %, Average Monthly Income, and Average Job Satisfaction.

## Repository Structure
- `/data`: Contains raw and clean CSV files (git-ignored).
- `/src`: Python scripts for ETL, DB load, and analysis execution.
- `/sql`: SQL schema definition and advanced analytical queries.
- `/docs`: Output folder for query results and analysis reports.
- `/powerbi`: DAX measure documentation (`dax_measures.md`).
- `HR_Dashboard.pbix`: Power BI semantic model (git-ignored).

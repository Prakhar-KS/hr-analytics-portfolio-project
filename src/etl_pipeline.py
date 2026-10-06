import pandas as pd
import numpy as np
import logging
import re
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def to_snake_case(name: str) -> str:
    """Convert PascalCase or camelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(' ', '_')

def load_data(filepath: Path) -> pd.DataFrame:
    logger.info(f"Loading data from {filepath}")
    return pd.read_csv(filepath)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Standardizing column names...")
    df.columns = [to_snake_case(col) for col in df.columns]
    
    # Specific renames
    rename_map = {'employee_number': 'employee_id'}
    df.rename(columns=rename_map, inplace=True)
    
    logger.info("Stripping whitespace from strings...")
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    logger.info("Handling nulls...")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].median()
            else:
                fill_val = df[col].mode()[0]
            logger.info(f"Filled {null_count} nulls in {col} with {fill_val}")
            df[col].fillna(fill_val, inplace=True)
            
    logger.info("Dropping duplicates by employee_id...")
    initial_rows = len(df)
    df.drop_duplicates(subset=['employee_id'], inplace=True)
    if initial_rows - len(df) > 0:
        logger.info(f"Dropped {initial_rows - len(df)} duplicates")
        
    logger.info("Dropping constant/useless columns...")
    drop_cols = [c for c in ['employee_count', 'over18', 'standard_hours'] if c in df.columns]
    df.drop(columns=drop_cols, inplace=True)
    
    logger.info("Validating categorical values...")
    assert set(df['attrition'].unique()).issubset({'Yes', 'No'}), "Invalid values in attrition"
    assert set(df['over_time'].unique()).issubset({'Yes', 'No'}), "Invalid values in over_time"
    
    logger.info("Adding computed columns...")
    df['attrition_flag'] = np.where(df['attrition'] == 'Yes', 1, 0)
    
    # Age band
    bins_age = [0, 24, 34, 44, 54, 150]
    labels_age = ['<25', '25-34', '35-44', '45-54', '55+']
    df['age_band'] = pd.cut(df['age'], bins=bins_age, labels=labels_age, right=True)
    
    # Tenure band
    bins_tenure = [-1, 2, 5, 10, 20, 150]
    labels_tenure = ['0-2', '3-5', '6-10', '11-20', '20+']
    df['tenure_band'] = pd.cut(df['years_at_company'], bins=bins_tenure, labels=labels_tenure, right=True)
    
    return df

def split_and_save(df: pd.DataFrame, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. departments
    departments = df[['department']].drop_duplicates().reset_index(drop=True)
    departments['department_id'] = departments.index + 1
    departments.rename(columns={'department': 'department_name'}, inplace=True)
    
    # Merge back to get department_id
    df = df.merge(departments, left_on='department', right_on='department_name', how='left')
    
    # 2. job_roles
    job_roles = df[['job_role', 'department_id']].drop_duplicates().reset_index(drop=True)
    job_roles['job_role_id'] = job_roles.index + 1
    
    # Merge back
    df = df.merge(job_roles, on=['job_role', 'department_id'], how='left')
    job_roles.rename(columns={'job_role': 'job_role_name'}, inplace=True)
    
    # 3. employees
    emp_cols = ['employee_id', 'age', 'age_band', 'gender', 'marital_status', 'education', 
                'education_field', 'department_id', 'job_role_id', 'job_level', 'business_travel', 
                'over_time', 'attrition', 'attrition_flag', 'distance_from_home', 'num_companies_worked', 
                'total_working_years', 'years_at_company', 'tenure_band', 'years_in_current_role', 
                'years_since_last_promotion', 'years_with_curr_manager', 'training_times_last_year']
    employees = df[emp_cols]
    
    # 4. compensation
    comp_cols = ['employee_id', 'monthly_income', 'daily_rate', 'hourly_rate', 'monthly_rate', 
                 'percent_salary_hike', 'stock_option_level', 'performance_rating']
    compensation = df[comp_cols]
    
    # 5. satisfaction
    sat_cols = ['employee_id', 'environment_satisfaction', 'job_satisfaction', 
                'relationship_satisfaction', 'work_life_balance', 'job_involvement']
    satisfaction = df[sat_cols]
    
    # Save CSVs
    logger.info("Saving split datasets to CSV...")
    departments.to_csv(output_dir / 'departments.csv', index=False)
    job_roles.to_csv(output_dir / 'job_roles.csv', index=False)
    employees.to_csv(output_dir / 'employees.csv', index=False)
    compensation.to_csv(output_dir / 'compensation.csv', index=False)
    satisfaction.to_csv(output_dir / 'satisfaction.csv', index=False)
    
    # Integrity assertions
    assert len(employees) == 1470, f"Expected 1470 employees, got {len(employees)}"
    assert not employees['department_id'].isnull().any(), "Orphan foreign key: department_id"
    assert not employees['job_role_id'].isnull().any(), "Orphan foreign key: job_role_id"
    assert not employees['employee_id'].isnull().any(), "Nulls in employee_id"
    logger.info("Integrity checks passed successfully.")

def main():
    root_dir = Path(__file__).parent.parent
    raw_path = root_dir / 'data' / 'raw' / 'raw_hr_data.csv'
    clean_dir = root_dir / 'data' / 'clean'
    
    df = load_data(raw_path)
    df = clean_data(df)
    split_and_save(df, clean_dir)

if __name__ == "__main__":
    main()

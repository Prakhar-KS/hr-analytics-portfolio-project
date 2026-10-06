IF DB_ID('HRAnalytics') IS NULL
BEGIN
    CREATE DATABASE HRAnalytics;
END
GO

USE HRAnalytics;
GO

-- Drop tables if they exist
IF OBJECT_ID('satisfaction', 'U') IS NOT NULL DROP TABLE satisfaction;
IF OBJECT_ID('compensation', 'U') IS NOT NULL DROP TABLE compensation;
IF OBJECT_ID('employees', 'U') IS NOT NULL DROP TABLE employees;
IF OBJECT_ID('job_roles', 'U') IS NOT NULL DROP TABLE job_roles;
IF OBJECT_ID('departments', 'U') IS NOT NULL DROP TABLE departments;
GO

CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE job_roles (
    job_role_id INT PRIMARY KEY,
    job_role_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    age INT,
    age_band VARCHAR(20),
    gender VARCHAR(20),
    marital_status VARCHAR(50),
    education INT,
    education_field VARCHAR(100),
    department_id INT NOT NULL,
    job_role_id INT NOT NULL,
    job_level INT,
    business_travel VARCHAR(50),
    over_time VARCHAR(10),
    attrition VARCHAR(10),
    attrition_flag INT CHECK (attrition_flag IN (0,1)),
    distance_from_home INT,
    num_companies_worked INT,
    total_working_years INT,
    years_at_company INT,
    tenure_band VARCHAR(20),
    years_in_current_role INT,
    years_since_last_promotion INT,
    years_with_curr_manager INT,
    training_times_last_year INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (job_role_id) REFERENCES job_roles(job_role_id)
);

CREATE TABLE compensation (
    employee_id INT PRIMARY KEY,
    monthly_income INT,
    daily_rate INT,
    hourly_rate INT,
    monthly_rate INT,
    percent_salary_hike INT,
    stock_option_level INT,
    performance_rating INT CHECK (performance_rating IN (1,2,3,4)),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE satisfaction (
    employee_id INT PRIMARY KEY,
    environment_satisfaction INT CHECK (environment_satisfaction IN (1,2,3,4)),
    job_satisfaction INT CHECK (job_satisfaction IN (1,2,3,4)),
    relationship_satisfaction INT CHECK (relationship_satisfaction IN (1,2,3,4)),
    work_life_balance INT CHECK (work_life_balance IN (1,2,3,4)),
    job_involvement INT CHECK (job_involvement IN (1,2,3,4)),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Create Indexes
CREATE INDEX IX_employees_department_id ON employees(department_id);
CREATE INDEX IX_employees_job_role_id ON employees(job_role_id);
CREATE INDEX IX_employees_attrition_flag ON employees(attrition_flag);
GO

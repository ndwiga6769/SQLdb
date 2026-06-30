-- Retrieve the first name, last name, and email of all customers. Order the results alphabetically by last name.
-- Concepts: SELECT, ORDER BY

select first_name,last_name,email 
from select import select

from equity_bank.customers
order by 2 asc

-- Filtering with WHERE
-- Find all accounts where the account type is 'Savings' and the balance is greater than 100,000.

select * from equity_bank.accounts
where account_type = 'Savings'
and balance > 100000


-- 3. DISTINCT
-- List all unique cities where Equity Bank has branches.
-- Concepts: DISTINCT

select distinct city from equity_bank.accounts

-- Show the top 10 accounts with the highest balances. 
-- Display account ID, account type, and balance.

select account_id,account_type,balance 
from equity_bank.accounts
order by balance desc
limit 10

-- hiw many customers are registerd at the bank
select count(distinct customer_id) from equity_bank.customers

-- Find all loans issued between 1st January 2023 and 31st December 2023.

select * from equity_bank.loans
where issued_date between '2023-01-01'  and '2023-12-31'

-- Find all customers who do not have an email address recorded.
select * from equity_bank.customers
where email is null

--Find all customers whose first name starts with the letter 'C' and whose email ends with '@mail.com
select * from equity_bank.customers
where first_name like 'C%' and email like '%@mail.com'

--What is the total amount deposited across all transactions of type 'Deposit'?

select sum(amount) 
from equity_bank.transactions
where transaction_type = 'Deposit'

-- List all branches and rename the columns to Branch Name and Location in the result.

select branch_name as Branch_name, city as locations from equity_bank.branches

-- Q12. Filtering Loan Status
-- How many loans currently have a status of 'Defaulted'?
select count(*) 
from equity_bank.loans
where loan_status = 'Defaulted'

# -- Q13. Date Functions
# -- List all customers who were born after 1st January 1990.
# -- Show their full name and date of birth.

select first_name,last_name,date_of_birth
from equity_bank.customers
where date_of_birth > '1980-01-01'

-- What is the smallest and largest transaction amount ever recorded?
select max(amount) as maximum_ammount, Min(amount) as minimum_amount from equity_bank.transactions

-- Q15. ORDER BY with Multiple Columns
-- List all transactions ordered by transaction date (most recent first),
-- and for transactions on the same date, order by amount (highest first).

-- Q12. GROUP BY with HAVING on Aggregates
-- Which branches have a total account balance of more than 5,000,000?
-- Show the branch name and total balance.
-- Concepts: JOIN, GROUP BY, SUM, HAVING

select b.branch_name,sum(a.balance)
from equity_bank.accounts a
Join equity_bank.branches b
on a.branch_id = b.branch_id
group by 1
Having sum(a.balance) > 5000000

# -- Q11. Multiple JOINs
# -- Show each transaction along with the account type it was made
# -- from and the city of the branch that account belongs to.
# -- Concepts: 3-table JOIN (transactions → accounts → branches)


select t.transaction_id,a.account_type,b.city,b.branch_name
from equity_bank.transactions t
left join equity_bank.accounts a
on t.account_id = a.account_id
left join equity_bank.branches b
on a.branch_id = b.branch_id

# -- Q12. GROUP BY with HAVING on Aggregates
# -- Which branches have a total account balance of more
# -- than 5,000,000? Show the branch name and total balance.
# -- Concepts: JOIN, GROUP BY, SUM, HAVING

SELECT b.branch_id,b.branch_name, ROUND(sum(coalesce(a.balance,0)),0) as total_balance
FROM equity_bank.accounts a
join equity_bank.branches b
on a.branch_id = b.branch_id
group by b.branch_id,b.branch_name
-- every non-aggregated selected column must be included in the GROUP BY.
having sum(coalesce(a.balance,0)) > 5000000
order by b.branch_id asc

# -- Q13. Loan Repayment Analysis
# -- For each loan, calculate the total amount repaid so far.
# -- Show loan ID, original loan amount, total repaid, and 
# -- how much is still outstanding (loan amount minus total repaid).
# -- Concepts: JOIN, SUM, arithmetic in SELECT


SELECT L.loan_id,L.loan_amount AS Original_amount,COALESCE(sum(R.amount_paid),0),(L.loan_amount - COALESCE(sum(R.amount_paid),0)) as Outstanding_balance
	FROM equity_bank.loans L
	LEFT JOIN equity_bank.loan_repayments R
	ON L.loan_id = R.loan_id
	group by L.loan_id,L.loan_amount

# -- Q14. DISTINCT with JOIN
# -- List all customers who have made at least one 'Withdrawal' transaction. 
# -- Show customer full name only, no duplicates.
# -- Concepts: DISTINCT, JOIN across 3 tables, WHERE

SELECT DISTINCT CONCAT(C.first_name,' ',C.last_name) AS Full_Name
	FROM equity_bank.customers C
	INNER JOIN equity_bank.accounts A
	ON C.customer_id = A.customer_id
	INNER JOIN equity_bank.transactions T
	ON T.account_id = A.account_id
	WHERE T.transaction_type = 'Withdrawal'

# -- Q15. Grouping by Time Period
# -- How many transactions were made per month in the last year?
# -- Show the month (formatted as YYYY-MM) and the transaction count,
# -- ordered chronologically.
# -- Concepts: DATE_TRUNC or TO_CHAR, GROUP BY, ORDER BY

SELECT 
    TO_CHAR(DATE_TRUNC('month', transaction_date), 'YYYY-MM') AS month,
    COUNT(*) AS transaction_count
FROM equity_bank.transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY DATE_TRUNC('month', transaction_date);

# -- Q1. Window Function — RANK
# -- Rank all customers by their total account balance (sum of all their accounts). Show full name, 
# -- total balance, and their rank. Customers with equal balances should share the same rank.
# -- Concepts: SUM, GROUP BY, RANK() OVER (ORDER BY)

select CONCAT(C.first_name, ' ', C.last_name) AS full_name,SUM(A.balance) AS total_balance, RANK() OVER(order by SUM (A.balance)  DESC ) AS BALANCE_RANK
from equity_bank.accounts A
join equity_bank.customers C
ON A.customer_id = C.customer_id
group by 
C.customer_id,
CONCAT(C.first_name, ' ', C.last_name)

# -- Q2. Running Total
# -- For each account, show every transaction along with a
# -- running total of the amount transacted over time (ordered by transaction date).
# -- Concepts: SUM() OVER (PARTITION BY ... ORDER BY) — window frame


SELECT
    *,
    SUM(amount) OVER (
        PARTITION BY account_id
        ORDER BY transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM equity_bank.transactions;



select *, SUM(amount) 
			OVER( PARTITION BY account_id order by transaction_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)	
from equity_bank.transactions

# -- a running total should not be partitioned by date this breaks the running totaL
# -- Unbounded preceding means from thhe first row to the current row

# -- Q3. CTE — Loan Default Rate
# -- Using a CTE, calculate the default rate per branch — i.e. 
# -- what percentage of loans belonging to customers at each branch are in 'Defaulted' status.
# -- Show branch name and default rate (%).
# -- Concepts: CTE, JOIN, GROUP BY, CASE or FILTER, percentage calculation


WITH loan_accounts as (
			select  C.customer_id,L.loan_id,L.loan_status,B.branch_id,B.branch_name
				from equity_bank.customers C
				JOIN equity_bank.loans L
				ON C.customer_id = L.customer_id
				JOIN equity_bank.accounts A
				ON A.customer_id = L.customer_id
				JOIN equity_bank.branches B
				ON B.branch_id = A.branch_id
				)

select branch_name,ROUND(
						100.0 * SUM(
								CASE 
										WHEN loan_status = 'Defaulted' THEN 1
										ELSE 0
									END	
									) / COUNT(*),2
						)	as default_percent_rate
from loan_accounts
GROUP BY branch_name

# -- Q4. Correlated Subquery
# -- For each customer, find the most recent transaction date
# -- across all their accounts. Show customer full name and that 
# -- date — without using any JOIN (use a correlated subquery instead).
# -- Concepts: Correlated subquery, MAX

SELECT
    c.first_name || ' ' || c.last_name AS full_name,
    (
        SELECT MAX(t.transaction_date)
        FROM equity_bank.transactions t
        WHERE t.account_id IN (
            SELECT a.account_id
            FROM equity_bank.accounts a
            WHERE a.customer_id = c.customer_id
        )
    ) AS most_recent_transaction
FROM equity_bank.customers c;

# -- Q5. DENSE_RANK with PARTITION
# -- Within each branch, rank accounts by balance from 
# -- highest to lowest. Show branch name, account ID, 
# -- balance, and rank. Gaps in ranking should not appear between ties.

select B.branch_name,A.account_id,A.balance,DENSE_RANK()  OVER(PARTITION BY A.branch_id ORDER BY A.BALANCE DESC) 

from equity_bank.accounts A
join equity_bank.branches B
ON A.branch_id = B.branch_id
group by   B.branch_name,A.account_id


SELECT
    B.branch_name,
    D.acctmgr,
    COALESCE(SUM(D.sanct_lim_kes), 0) AS disbursed_amnt
FROM disbursement_listing D
JOIN branch_summary B
    ON CAST(B.sol_id AS INT) = CAST(D.sol_id AS INT)
GROUP BY
    B.branch_name,
    D.acctmgr
ORDER BY disbursed_amnt DESC
LIMIT 5;

-- 3. Officer Performance Outlier Analysis
-- Using officer_grade_performance, list all
-- officers who exceeded 100% on new_loans_pct_achievement
-- but fell below 50% on topups_pct_achievement.

select officer_name,new_loans_pct_achievement,topups_pct_achievement
from officer_grade_performance
where new_loans_pct_achievement > 1 and  topups_pct_achievement < 0.5

-- 4. Product-Level Loan Statistics
-- For each product code in disbursement_listing, compute:
-- Average dis_amt
-- Average instalments
-- Count of loans
-- Order by average disbursement descending.

select product,
ROUND(AVG(instalments),0) AS avg_dis_amt,
ROUND(AVG(dis_amt),0) AS avg_instalments,
COUNT(*)
from disbursement_listing
GROUP BY product
ORDER BY avg_dis_amt DESC;

-- 5. Repeat Customer Loan Analysis
-- Find all customers (cif_id) who appear
-- more than once in disbursement_listing, along with:
-- Number of loans
-- Total dis_amt per customer

SELECT cif_id,count(*) as cif_count,sum(dis_amt)
FROM disbursement_listing
group by cif_id
Having count(*) > 1

-- 6. Top 3 Loans per Branch (Window Function)
-- Using a window function, rank each loan within 
-- its sol_id by dis_amt descending, and return only the top 3 loans per branch.
with loan_ranking as (
				select sol_id,product,dis_amt,account_name,employer_name,
				rank() over(partition by sol_id order by dis_amt DESC) as ranked_loans
				from disbursement_listing
				)
select L.*,B.branch_name
from loan_ranking L
join branch_summary B
ON cast(L.sol_id as int ) = CAST (B.sol_id as int)
where ranked_loans = 1
ORDER BY L.dis_amt desc

-- SELECT * from disbursement_listing




7 WITH loan_disbursed as (
  SELECT
        id,
        cust_dob,
        acct_opn_date,
        dis_amt,
        DATE_PART('YEAR',AGE(acct_opn_date,cust_dob)) as customer_age
    FROM disbursement_listing
	)
select 
		CASE WHEN customer_age  < 25 THEN 'Under 25'
			 WHEN customer_age BETWEEN 25 AND 35 THEN '25-35'
			 WHEN customer_age BETWEEN 36 AND 50 THEN '36-50'
			 ELSE '50+'
			 END AS age_range,count(*) as loan_count
FROM loan_disbursed
group by 1
order by loan_count desc


-- 8. Loan Size Classification (CASE)
-- Classify each loan in disbursement_listing as:
-- Small (<100,000)
-- Medium (100,000–999,999)
-- Large (≥1,000,000)
-- Using sanct_lim, then count loans and sum dis_amt per category.

select CASE WHEN dis_amt < 100000 THEN 'small'
		 	WHEN dis_amt between 100000 and 999999 THEN 'MEDIUM'
			WHEN dis_amt >= 1000000 THEN 'large'
		end as loan_classification,count(*) loan_count,sum(dis_amt) as sum_loan
from disbursement_listing
group by 1
order by loan_count DESC

-- 11. Regional Achievement Ranking
-- Using region_summary, calculate 
-- each region’s achievement ratio:
-- total_disbursement / (new_loan_sanct_lim_kes + topup_sanct_lim_kes)
-- Rank regions by that ratio.

select region,ROUND(total_disbursement / new_loan_sanct_lim_kes + topup_sanct_lim_kes,0)
from region_summary
group by region
ORDER BY ROUND(total_disbursement / new_loan_sanct_lim_kes + topup_sanct_lim_kes,0) DESC


-- 12. Peak Disbursement Day — May 2026
-- Find the day of the month in May 2026 
-- with the highest total dis_amt across all branches in disbursement_listing.

SELECT 
acct_opn_date,ROUND(SUM(dis_amt),0)
from disbursement_listing
GROUP BY 1
ORDER BY SUM(dis_amt) DESC

-- 14. Gender-Based Loan Analysis
-- For each gender calculate:
-- Total disbursement amount
-- Average sanctioned limit
-- Ratio of New_Loan to Top_Up status counts

select gender, ROUND(COALESCE(SUM(dis_amt),0),0) as disbursement_amount, 
ROUND(COALESCE(AVG(sanct_lim_kes),0),0),
ROUND (COUNT (CASE WHEN status = 'New_Loan' THEN 1 END)::NUMERIC
/
	COUNT(CASE WHEN status = 'Top_Up' THEN 1 END),3) AS NEW_VS_TOPUP_RATIO 
from disbursement_listing
GROUP BY gender


-- 19. Top Employers by Loan Value
-- For each employer_name (excluding NULLs),
-- find the top employer by total dis_amt,
-- but only include employers with at least 5 loans.

select employer_name,COALESCE(SUM(dis_amt),0) as loan_sum ,count(*)
from disbursement_listing
WHERE EMPLOYER_NAME IS NOT NULL
group by employer_name
Having count(*) > 5
order by COALESCE(SUM(dis_amt),0) desc

-- 20. Repayment vs Disbursement Validation
-- Using instalments and rep_perd_mths, calculate:
-- instalments × rep_perd_mths
-- Compare to dis_amt and flag loans where 
-- repayment exceeds 3× disbursement.

SELECT instalments,rep_perd_mths,(instalments * rep_perd_mths) as Principal_interest ,dis_amt,
CASE WHEN instalments * rep_perd_mths > dis_amt * 3
	 THEN 'LOAN_FLAGGED'
	 ELSE 'OKAY'
	 END AS VALIDATION_FLAG
from disbursement_listing
where instalments IS NOT NULL
	AND rep_perd_mths IS NOT NULL
	AND dis_amt IS NOT NULL
	AND instalments * rep_perd_mths > dis_amt * 3


-- 21. Growth Composition by Region
-- Using region_summary, compute the
-- proportion of total_growth_count coming from:
-- Top-ups
-- New loans


SELECT
    region,
    total_growth_count,
    (total_growth_count - topup_count) AS new_loan,
    topup_count,
    CONCAT(
        ROUND((topup_count * 100.0 / total_growth_count), 2),
        '%'
    ) AS top_up_percentage,
    CONCAT(
        ROUND(((total_growth_count - topup_count) * 100.0 / total_growth_count), 2),
        '%'
    ) AS new_loan_percentage
FROM region_summary;




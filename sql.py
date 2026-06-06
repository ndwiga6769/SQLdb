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

select distinct city from equity_bank.branches

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

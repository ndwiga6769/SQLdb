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
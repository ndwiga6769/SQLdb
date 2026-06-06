Q1. First & Latest Loan per Customer
For each customer, find:

The date they opened their first loan account
The date of their most recent loan account

Show full name, CIF ID, first account date, and latest account date.
Include customers who appear only once.
sqlSELECT
    account_name,
    cif_id,
    MIN(acct_opn_date)  AS first_account_date,
    MAX(acct_opn_date)  AS latest_account_date
FROM   disbursement_listing
GROUP  BY account_name, cif_id
ORDER  BY first_account_date;

Q2. Branches with No Disbursements
The branch operations team wants to investigate inactive branches.
Find all branches that appear in branch_summary but have recorded
zero total disbursements. Show the branch name, SOL ID, and total count.
sqlSELECT sol_id, branch_name, total_count, total_disbursements

FROM   branch_summary
WHERE  total_disbursements = 0
   OR  total_disbursements IS NULL
ORDER  BY branch_name;

Q3. Gender Split by Loan Type
The analytics team wants to understand demographic patterns.
For each combination of gender and loan status (New_Loan vs Top_Up):

Count the number of loans
Sum the disbursed amount
Calculate the percentage share within that gender

sqlSELECT
    gender,
    status,
    COUNT(*)                                                AS loan_count,
    SUM(dis_amt)                                            AS total_disbursed,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER
          (PARTITION BY gender), 1)                         AS pct_within_gender
FROM   disbursement_listing
GROUP  BY gender, status
ORDER  BY gender, status;

Q4. Officers Who Handled Both New Loans and Top-Ups
Find account managers who disbursed at least one New_Loan and at
least one Top_Up during the period. Show their code, total loans,
and count of each type side by side.
sqlSELECT
    acctmgr,
    COUNT(*)                                         AS total_loans,
    COUNT(*) FILTER (WHERE status = 'New_Loan')      AS new_loans,
    COUNT(*) FILTER (WHERE status = 'Top_Up')        AS top_ups
FROM   disbursement_listing
GROUP  BY acctmgr
HAVING COUNT(*) FILTER (WHERE status = 'New_Loan') > 0
   AND COUNT(*) FILTER (WHERE status = 'Top_Up')   > 0
ORDER  BY total_loans DESC;

Q5. Repayment Period Distribution
Lending policy uses 6-, 12-, 24-, and 36-month tenures.
Show how many loans fall into each repayment period bucket,
the total amount disbursed per bucket, and the average loan size.
sqlSELECT
    rep_perd_mths,
    COUNT(*)              AS loan_count,
    SUM(dis_amt)          AS total_disbursed,
    ROUND(AVG(dis_amt), 0) AS avg_loan_size
FROM   disbursement_listing
GROUP  BY rep_perd_mths
ORDER  BY rep_perd_mths;

Q6. Top Employers by Total Amount Borrowed
HR compliance wants a list of the top 10 employers whose staff
have borrowed the most. Show employer name, number of employees
with active loans, and total amount disbursed. Exclude NULL employers.
sqlSELECT
    employer_name,
    COUNT(DISTINCT cif_id)  AS borrower_count,
    COUNT(*)                AS loan_count,
    SUM(dis_amt)            AS total_disbursed
FROM   disbursement_listing
WHERE  employer_name IS NOT NULL
GROUP  BY employer_name
ORDER  BY total_disbursed DESC
LIMIT  10;

Q7. Month-by-Month Disbursement Trend
Produce a simple monthly summary for May 2026 showing:

The week number within the month (week 1–5)
Number of loans opened
Total amount disbursed

sqlSELECT
    CEIL(EXTRACT(DAY FROM acct_opn_date) / 7.0)::INT  AS week_of_month,
    COUNT(*)                                           AS loans_opened,
    SUM(dis_amt)                                       AS total_disbursed
FROM   disbursement_listing
GROUP  BY 1
ORDER  BY 1;

Q8. Branch Performance vs Region Average
For each branch, show whether its total disbursements are above or
below the average for its region. Use a subquery to compute the
regional average from disbursement_listing then compare.
sqlSELECT
    b.sol_id,
    b.branch_name,
    b.total_disbursements,
    ROUND(ra.region_avg, 0)    AS region_avg,
    CASE
        WHEN b.total_disbursements >= ra.region_avg THEN 'Above average'
        ELSE 'Below average'
    END                        AS vs_region
FROM   branch_summary b
JOIN   (
           SELECT l.sol_id,
                  AVG(bs2.total_disbursements) OVER
                      (PARTITION BY l.region)   AS region_avg
           FROM   disbursement_listing  l
           JOIN   branch_summary        bs2
                  ON CAST(l.sol_id AS VARCHAR) = bs2.sol_id
           GROUP  BY l.sol_id, l.region, bs2.total_disbursements
       ) ra ON b.sol_id = ra.sol_id
ORDER  BY b.total_disbursements DESC;

Q9. Customers with Multiple Loans
Identify repeat borrowers — customers with more than one loan record
in the listing. Show their name, CIF ID, loan count, total borrowed,
and earliest loan date.
sqlSELECT
    account_name,
    cif_id,
    COUNT(*)              AS loan_count,
    SUM(dis_amt)          AS total_borrowed,
    MIN(acct_opn_date)    AS first_loan_date
FROM   disbursement_listing
GROUP  BY account_name, cif_id
HAVING COUNT(*) > 1
ORDER  BY loan_count DESC, total_borrowed DESC;

Q10. Channel Usage Summary
The digital team wants to know how many loans came through each
channel (e.g. BRANCH, MOBILE). Show channel, count, total disbursed,
and percentage of total loan count.
sqlSELECT
    TRIM(channel)                                     AS channel,
    COUNT(*)                                          AS loan_count,
    SUM(dis_amt)                                      AS total_disbursed,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM   disbursement_listing
GROUP  BY TRIM(channel)
ORDER  BY loan_count DESC;

Q11. Officers Below Target on Both New Loans and Top-Ups
Flag account managers who missed their targets on both loan types.
From officer_grade_performance, return officers where
new_loans_pct_achievement < 1 AND topups_pct_achievement < 1.
Show name, grade, and both achievement percentages.
sqlSELECT
    officer_name,
    grade,
    ROUND(new_loans_pct_achievement  * 100, 1) AS new_loan_ach_pct,
    ROUND(topups_pct_achievement     * 100, 1) AS topup_ach_pct,
    ROUND(disbursements_pct_achievement * 100, 1) AS overall_ach_pct
FROM   officer_grade_performance
WHERE  new_loans_pct_achievement < 1
  AND  topups_pct_achievement    < 1
ORDER  BY overall_ach_pct;

Q12. Sanction Limit vs Disbursed Amount Gap
Some loans are sanctioned for more than was actually disbursed.
Find all loans where sanct_lim_kes > dis_amt, showing the
borrower, the gap amount, and gap as a percentage of the sanction limit.
sqlSELECT
    account_name,
    sanct_lim_kes,
    dis_amt,
    (sanct_lim_kes - dis_amt)                                AS gap_amount,
    ROUND((sanct_lim_kes - dis_amt) * 100.0
          / NULLIF(sanct_lim_kes, 0), 1)                     AS gap_pct
FROM   disbursement_listing
WHERE  sanct_lim_kes > dis_amt
ORDER  BY gap_amount DESC;

Q13. Youngest and Oldest Borrowers per Branch
For each branch (sol_id), find:

The youngest borrower's name and age at disbursement
The oldest borrower's name and age at disbursement

sqlWITH ages AS (
    SELECT
        sol_id,
        account_name,
        EXTRACT(YEAR FROM AGE(acct_opn_date, cust_dob::date))::INT AS age_at_loan
    FROM disbursement_listing
    WHERE cust_dob IS NOT NULL
),
ranked AS (
    SELECT *,
        MIN(age_at_loan) OVER (PARTITION BY sol_id) AS min_age,
        MAX(age_at_loan) OVER (PARTITION BY sol_id) AS max_age
    FROM ages
)
SELECT sol_id, account_name, age_at_loan,
    CASE WHEN age_at_loan = min_age THEN 'Youngest'
         WHEN age_at_loan = max_age THEN 'Oldest' END AS category
FROM ranked
WHERE age_at_loan = min_age OR age_at_loan = max_age
ORDER BY sol_id, category;

Q14. Region with Highest Top-Up Recovery Rate
From region_summary, compute the payoff recovery rate for top-ups
as topup_payoffs / topup_sanct_lim_kes. Rank regions from
best to worst recovery.
sqlSELECT
    region,
    topup_payoffs,
    topup_sanct_lim_kes,
    ROUND(topup_payoffs * 100.0
          / NULLIF(topup_sanct_lim_kes, 0), 2)  AS recovery_rate_pct,
    RANK() OVER (
        ORDER BY topup_payoffs
                 / NULLIF(topup_sanct_lim_kes, 0) DESC
    )                                            AS recovery_rank
FROM   region_summary
ORDER  BY recovery_rank;

Q15. Loans Opened on Weekends
Some loan officers processed applications on Saturdays or Sundays.
Find all such loans, show the borrower, branch, amount, and the
day of week name.
sqlSELECT
    account_name,
    sol_id,
    dis_amt,
    TO_CHAR(acct_opn_date, 'Day')   AS day_name,
    acct_opn_date
FROM   disbursement_listing
WHERE  EXTRACT(DOW FROM acct_opn_date) IN (0, 6)
ORDER  BY acct_opn_date;


Advanced Questions

Q16. Consecutive Loan Gaps per Customer
For customers with multiple loans, calculate the number of days
between each successive loan. Show name, CIF ID, each loan date,
the previous loan date, and the gap in days. Flag gaps longer than
180 days as "Dormant return".
sqlWITH ordered AS (
    SELECT
        account_name, cif_id, acct_opn_date, dis_amt,
        LAG(acct_opn_date) OVER (
            PARTITION BY cif_id
            ORDER BY acct_opn_date
        ) AS prev_loan_date
    FROM disbursement_listing
)
SELECT
    account_name, cif_id,
    prev_loan_date,
    acct_opn_date                                           AS current_loan_date,
    (acct_opn_date - prev_loan_date)                        AS gap_days,
    CASE
        WHEN (acct_opn_date - prev_loan_date) > 180 THEN 'Dormant return'
        ELSE 'Regular'
    END                                                     AS customer_pattern
FROM   ordered
WHERE  prev_loan_date IS NOT NULL
ORDER  BY gap_days DESC NULLS LAST;

Q17. Officer Rank Change — New Loans vs Top-Ups
Rank officers by new loan achievement and again by top-up achievement.
Show where an officer's rank improved or worsened when switching
from new-loan to top-up performance. Highlight those who rank
top-5 in one metric but bottom-5 in the other.
sqlWITH ranked AS (
    SELECT
        officer_name, grade,
        ROUND(new_loans_pct_achievement  * 100, 1) AS nl_pct,
        ROUND(topups_pct_achievement     * 100, 1) AS tu_pct,
        RANK() OVER (ORDER BY new_loans_pct_achievement  DESC) AS nl_rank,
        RANK() OVER (ORDER BY topups_pct_achievement     DESC) AS tu_rank,
        COUNT(*) OVER ()                                        AS total_officers
    FROM officer_grade_performance
)
SELECT *,
    (nl_rank - tu_rank)   AS rank_swing,
    CASE
        WHEN nl_rank <= 5 AND tu_rank > total_officers - 5 THEN 'NL star / TU laggard'
        WHEN tu_rank <= 5 AND nl_rank > total_officers - 5 THEN 'TU star / NL laggard'
        ELSE 'Consistent'
    END                   AS profile
FROM ranked
ORDER BY ABS(nl_rank - tu_rank) DESC;

Q18. Rolling 3-Day Disbursement Total
Compute a 3-day rolling sum of disbursed amounts across all branches.
Show the loan date, that day's total, and the rolling 3-day window total.
This helps the treasury team monitor short-term liquidity outflows.
sqlWITH daily AS (
    SELECT
        acct_opn_date::date          AS loan_date,
        SUM(dis_amt)                  AS daily_total,
        COUNT(*)                      AS daily_count
    FROM  disbursement_listing
    GROUP BY acct_opn_date::date
)
SELECT
    loan_date,
    daily_count,
    daily_total,
    SUM(daily_total) OVER (
        ORDER BY loan_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )                                 AS rolling_3day_total
FROM  daily
ORDER BY loan_date;

Q19. Branch Contribution to Region Total (Hierarchical Share)
For each branch, calculate:

Its share of its region's disbursement total
Its share of the overall grand total

Use a single query with two levels of SUM() OVER () partitioning.
sqlWITH base AS (
    SELECT
        l.sol_id,
        b.branch_name,
        l.region,
        SUM(l.dis_amt)   AS branch_total
    FROM   disbursement_listing l
    JOIN   branch_summary       b
           ON CAST(l.sol_id AS VARCHAR) = b.sol_id
    GROUP  BY l.sol_id, b.branch_name, l.region
)
SELECT
    region,
    branch_name,
    branch_total,
    SUM(branch_total) OVER (PARTITION BY region)   AS region_total,
    SUM(branch_total) OVER ()                       AS grand_total,
    ROUND(branch_total * 100.0
          / SUM(branch_total) OVER (PARTITION BY region), 2)  AS pct_of_region,
    ROUND(branch_total * 100.0
          / SUM(branch_total) OVER (), 2)                     AS pct_of_grand_total
FROM   base
ORDER  BY region, branch_total DESC;

Q20. First Loan Ever per Officer (Career Milestone)
For each account manager, identify the very first loan they ever
processed — the customer name, amount, branch, and date.
If two loans share the exact same earliest timestamp, show both.
sqlWITH ranked AS (
    SELECT
        acctmgr,
        account_name,
        sol_id,
        dis_amt,
        rcre_time,
        RANK() OVER (
            PARTITION BY acctmgr
            ORDER BY rcre_time
        ) AS rn
    FROM disbursement_listing
)
SELECT
    acctmgr,
    account_name,
    sol_id,
    dis_amt,
    rcre_time   AS first_loan_time
FROM   ranked
WHERE  rn = 1
ORDER  BY acctmgr;

Q21. Customer Lifetime Value Projection
Estimate a simple lifetime value for each customer as:
total disbursed × average repayment months / 12.
Show name, loan count, total disbursed, average tenure, and
projected LTV. Rank by LTV descending.
sqlWITH ltv AS (
    SELECT
        account_name,
        cif_id,
        COUNT(*)                      AS loan_count,
        SUM(dis_amt)                  AS total_disbursed,
        ROUND(AVG(rep_perd_mths), 1)  AS avg_tenure_months,
        ROUND(SUM(dis_amt)
              * AVG(rep_perd_mths) / 12.0, 2)  AS projected_ltv
    FROM  disbursement_listing
    GROUP BY account_name, cif_id
)
SELECT *,
    RANK() OVER (ORDER BY projected_ltv DESC)  AS ltv_rank
FROM  ltv
ORDER BY projected_ltv DESC;

Q22. Detect Duplicate Applications on the Same Day
Flag cases where the same customer (cif_id) had more than one
loan application processed on the same date — a possible
duplicate-entry or fraud indicator. Show the CIF, name, date,
count of same-day applications, and total amount.
sqlSELECT
    cif_id,
    account_name,
    acct_opn_date::date       AS loan_date,
    COUNT(*)                  AS same_day_count,
    SUM(dis_amt)              AS same_day_total,
    STRING_AGG(account_num::TEXT, ', '
               ORDER BY rcre_time)  AS account_numbers
FROM   disbursement_listing
GROUP  BY cif_id, account_name, acct_opn_date::date
HAVING COUNT(*) > 1
ORDER  BY same_day_count DESC, same_day_total DESC;

Q23. Officer Efficiency Score (Composite Metric)
Build a composite efficiency score for each officer defined as:
(new_loans_pct_achievement * 0.4) + (topups_pct_achievement * 0.4) + (disbursements_pct_achievement * 0.2)
Rank officers overall and within their grade. Flag anyone scoring
above 1.0 (over-achieved on all fronts).
sqlWITH scores AS (
    SELECT
        officer_name, grade, acctmgr,
        ROUND(
            (new_loans_pct_achievement  * 0.4 +
             topups_pct_achievement     * 0.4 +
             disbursements_pct_achievement * 0.2) * 100
        , 1)                                                   AS efficiency_score
    FROM officer_grade_performance
)
SELECT
    officer_name, grade, acctmgr, efficiency_score,
    RANK() OVER (ORDER BY efficiency_score DESC)               AS overall_rank,
    RANK() OVER (PARTITION BY grade ORDER BY efficiency_score DESC) AS grade_rank,
    CASE WHEN efficiency_score > 100 THEN 'Over-achiever'
         WHEN efficiency_score >= 80  THEN 'On track'
         ELSE 'Needs support'
    END                                                        AS performance_band
FROM scores
ORDER BY efficiency_score DESC;

Q24. Unpaid Top-Up Balance (Take-Home Exposure)
topup_take_home in officer_net_growth represents the portion
of top-up funds not yet paid off. Identify the top 5 officers
with the highest take-home exposure, and show what percentage
of their total top-up book it represents.
sqlSELECT
    officer_name,
    branch_name,
    topup_sanct_lim,
    topup_payoff,
    topup_take_home,
    ROUND(topup_take_home * 100.0
          / NULLIF(topup_sanct_lim, 0), 2)         AS exposure_pct,
    RANK() OVER (ORDER BY topup_take_home DESC)     AS exposure_rank
FROM   officer_net_growth
ORDER  BY topup_take_home DESC
LIMIT  5;

Q25. Month-End vs Mid-Month Disbursement Patterns
Divide the month into three periods: early (days 1–10),
mid (days 11–20), and late (days 21–31). For each period
show disbursement count, total, and average. Then highlight
which period carried the highest average loan size.
sqlWITH periods AS (
    SELECT
        dis_amt,
        CASE
            WHEN EXTRACT(DAY FROM acct_opn_date) BETWEEN 1  AND 10 THEN 'Early (1-10)'
            WHEN EXTRACT(DAY FROM acct_opn_date) BETWEEN 11 AND 20 THEN 'Mid   (11-20)'
            ELSE                                                         'Late  (21-31)'
        END AS period
    FROM disbursement_listing
),
agg AS (
    SELECT
        period,
        COUNT(*)              AS loan_count,
        SUM(dis_amt)          AS total_disbursed,
        ROUND(AVG(dis_amt),0) AS avg_loan_size
    FROM periods
    GROUP BY period
)
SELECT *,
    CASE WHEN avg_loan_size = MAX(avg_loan_size) OVER ()
         THEN 'Highest avg' END   AS highlight
FROM agg
ORDER BY period;

Q26. Cross-Region Officer Deployment
Find any account manager (acctmgr code) who processed loans
in more than one region — potentially covering multiple branches.
Show their code, list of regions served, and total loans per region.
sqlWITH mgr_regions AS (
    SELECT
        acctmgr,
        region,
        COUNT(*)     AS loans_in_region,
        SUM(dis_amt) AS amt_in_region
    FROM   disbursement_listing
    GROUP  BY acctmgr, region
),
multi AS (
    SELECT acctmgr
    FROM   mgr_regions
    GROUP  BY acctmgr
    HAVING COUNT(DISTINCT region) > 1
)
SELECT
    mr.acctmgr,
    mr.region,
    mr.loans_in_region,
    mr.amt_in_region
FROM   mgr_regions mr
WHERE  mr.acctmgr IN (SELECT acctmgr FROM multi)
ORDER  BY mr.acctmgr, mr.amt_in_region DESC;

Q27. Instalment-to-Disbursement Ratio Outliers
A healthy instalment should be roughly dis_amt / rep_perd_mths.
Flag loans where the actual instalment deviates by more than 15%
from this expected value — possible data entry errors or
non-standard pricing.
sqlWITH expected AS (
    SELECT
        account_num, account_name, acctmgr,
        dis_amt, rep_perd_mths, instalments,
        ROUND(dis_amt / NULLIF(rep_perd_mths, 0), 2)    AS expected_instalment,
        ROUND(ABS(instalments -
              dis_amt / NULLIF(rep_perd_mths, 0))
              * 100.0
              / NULLIF(dis_amt / NULLIF(rep_perd_mths,0), 0)
        , 1)                                             AS deviation_pct
    FROM disbursement_listing
    WHERE instalments IS NOT NULL AND rep_perd_mths > 0
)
SELECT *
FROM   expected
WHERE  deviation_pct > 15
ORDER  BY deviation_pct DESC;

Q28. Grade-Weighted Regional Targets
Each grade carries a different new-loan target (Grade 1 = 20M,
Grade 2 = 15M, Grade 3 = 10M). Using officer_grade_performance,
compute the total weighted target per region by joining to the
listing to determine which region each officer serves.
sqlWITH officer_region AS (
    SELECT
        l.acctmgr,
        l.region,
        COUNT(*) AS loans
    FROM   disbursement_listing l
    GROUP  BY l.acctmgr, l.region
),
primary_region AS (
    SELECT DISTINCT ON (acctmgr)
        acctmgr, region
    FROM   officer_region
    ORDER  BY acctmgr, loans DESC
)
SELECT
    pr.region,
    g.grade,
    COUNT(*)                     AS officer_count,
    SUM(g.new_loans_target)      AS total_new_loan_target,
    SUM(g.total_new_loans)       AS total_new_loan_actual,
    ROUND(SUM(g.total_new_loans) * 100.0
          / NULLIF(SUM(g.new_loans_target),0), 1)  AS region_ach_pct
FROM   officer_grade_performance g
JOIN   primary_region            pr USING (acctmgr)
GROUP  BY pr.region, g.grade
ORDER  BY pr.region, g.grade;

Q29. Worst-to-Best Recovery Trajectory (Payoff Quartiles)
Divide all top-up loans in officer_net_growth into four quartiles
based on payoff amount. For each quartile show:

Payoff range (min and max)
Average take-home exposure
Officer names in that quartile

sqlWITH quartiles AS (
    SELECT
        officer_name,
        branch_name,
        topup_payoff,
        topup_take_home,
        NTILE(4) OVER (ORDER BY topup_payoff)    AS payoff_quartile
    FROM officer_net_growth
)
SELECT
    payoff_quartile,
    MIN(topup_payoff)                           AS min_payoff,
    MAX(topup_payoff)                           AS max_payoff,
    ROUND(AVG(topup_take_home), 0)              AS avg_take_home_exposure,
    STRING_AGG(officer_name, ', '
               ORDER BY topup_payoff)           AS officers
FROM   quartiles
GROUP  BY payoff_quartile
ORDER  BY payoff_quartile;

Q30. Full Portfolio Health Dashboard (Single Query)
Produce a one-row-per-region summary that combines data from all
five tables to show: loan count, total disbursed, officer count,
average achievement %, top-up recovery rate, and growth value.
sqlWITH listing_agg AS (
    SELECT region,
           COUNT(*)      AS loan_count,
           SUM(dis_amt)  AS total_disbursed
    FROM   disbursement_listing
    GROUP  BY region
),
officer_agg AS (
    SELECT pr.region,
           COUNT(DISTINCT g.acctmgr)                         AS officer_count,
           ROUND(AVG(g.disbursements_pct_achievement)*100,1) AS avg_ach_pct
    FROM   officer_grade_performance g
    JOIN   (
               SELECT DISTINCT ON (acctmgr) acctmgr, region
               FROM   disbursement_listing
               ORDER  BY acctmgr,
                         COUNT(*) OVER (PARTITION BY acctmgr, region) DESC
           ) pr USING (acctmgr)
    GROUP  BY pr.region
)
SELECT
    r.region,
    la.loan_count,
    la.total_disbursed,
    oa.officer_count,
    oa.avg_ach_pct,
    ROUND(r.topup_payoffs * 100.0
          / NULLIF(r.topup_sanct_lim_kes,0), 1)   AS topup_recovery_pct,
    r.total_growth_value
FROM   region_summary       r
LEFT   JOIN listing_agg     la USING (region)
LEFT   JOIN officer_agg     oa USING (region)
ORDER  BY la.total_disbursed DESC;
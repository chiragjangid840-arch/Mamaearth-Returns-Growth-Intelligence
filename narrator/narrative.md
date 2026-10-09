# Mamaearth Returns & Growth Intelligence

## Situation
The cleaned dataset contains **175 orders**, generating total revenue of **₹97,358.30**, with an average order value of **₹556.33**. The analysis examines order returns, payment behavior, data quality, and monthly revenue trends.

## Complication
A total of **44 orders were returned**, representing a return rate of **25.14%**. Quantity analysis identified **2 outlier orders**, O0011 and O0098. These orders were flagged for analysis rather than deleted from the cleaned dataset.

## Resolution
Prioritize investigation of high-return customer segments and review the reasons behind returned orders. Monitor monthly revenue using the outlier-corrected trend, and use the verified metrics to guide decisions. Further investigation is needed before attributing returns to any specific cause.

## Key Verified Findings

| Metric | Result |
|---|---:|
| Raw orders | 180 |
| Cleaned orders | 175 |
| Total revenue | ₹97,358.30 |
| Average order value | ₹556.33 |
| Returned orders | 44 |
| Overall return rate | 25.14% |
| Unique customers | 44 |
| Unique products | 16 |
| Flagged quantity outliers | 2 |
| Missing discounts after cleaning | 0 |
| Missing ratings after cleaning | 0 |

## Monthly Revenue Insight
After excluding the two flagged quantity outliers from the monthly revenue calculation, **March 2026** was the peak month, with revenue of **₹20,318.90**.

## One-Line Business Takeaway
**Focus on reducing returns through segment-level investigation while tracking revenue trends using outlier-corrected data.**

## Generation Mode
Offline fallback — the AI service was not used. The narrative was generated from the verified metrics stored in `findings.json`.

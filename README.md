# Mamaearth Returns & Growth Intelligence

## Project Overview

This project analyzes Mamaearth order data to understand sales performance, customer behavior, product performance, and returns.

The project uses SQL, Python/Pandas, visualizations, and a GenAI narrative layer.

## Project Structure

- data/
- analysis/
- narrator/
- sql/
- visualizations/
- README.md

## SQL Analysis

The SQL analysis covers:

- Total orders and revenue
- Average order value
- Rated and unrated orders
- Customers with no orders
- Return rates by city
- Top customers by revenue
- Revenue by product category
- Acquisition sources
- Loyalty tiers

## Python / Pandas Analysis

The Python analysis includes:

- Data cleaning
- Missing value handling
- Payment method standardization
- Duplicate checks
- Outlier analysis
- Revenue calculation
- Return rate analysis
- Customer and product analysis
- Payment method analysis
- City and city-tier analysis
- Correlation analysis
- Monthly trend analysis

## Key Results

- Total orders: 180
- Cleaned revenue: INR 98,389.25
- Average order value: INR 546.61
- Returned orders: 45
- Overall return rate: 25.00%
- Unique customers with orders: 44
- Unique products: 16
- Highest return city: Jaipur - 42.11%
- COD return rate: 43.64%
- Highest-risk segment: COD + Tier 2 - 54.55%

## Visualizations

The project contains:

1. Return rate by payment method
2. Monthly revenue trend

Both visualizations are stored in the visualizations folder.

## GenAI Narrative

The GenAI layer uses verified analysis results stored in findings.json.

The workflow is:

Verified Analysis
-> findings.json
-> prompt.txt
-> Gemini API
-> narrative.md

The AI is instructed to use only verified findings and not invent statistics.

## How to Run

Install the required packages:

pip install pandas numpy matplotlib google-genai

Run the analysis:

python analysis/clean_and_eda.py

Generate visualizations:

python analysis/visualize.py

Generate the narrative:

python narrator/generate_narrative.py

## Conclusion

The analysis shows that returns are an important business issue. COD orders and Tier 2 COD customers have comparatively higher return rates. These findings can help the business focus return-reduction efforts on higher-risk payment and customer segments.

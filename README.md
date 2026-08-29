# Personalized Ad/Product Recommender

A collaborative-filtering recommendation engine that suggests products to
users based on their browsing/purchase history and the behavior of similar
users — the same core technique behind "customers who viewed this also
viewed..." style recommendation systems.

## What it does

1. **Data**: simulated browsing/purchase history for 50 users across 25
   products in 5 categories (Electronics, Fashion, Sports, Books, Home).
2. **User-Product Matrix**: builds an interaction matrix where each cell is
   an "interest score" — view count, plus a bonus if the product was
   purchased.
3. **Collaborative Filtering (the AI/ML core)**: computes user-user
   **cosine similarity** using numpy, to find which users have the most
   similar interest patterns.
4. **Recommendation Generation**: for each user, finds their most similar
   users and recommends products those users engaged with that the target
   user hasn't seen yet, ranked by a weighted score.
5. **SQL Analysis**: loads everything into SQLite and runs queries to
   report on recommendation coverage, most-recommended products, and
   category-level purchase behavior.
6. **Output**: `recommendation_output.xlsx` with the full browsing history,
   per-user recommendations, and 5 analysis tables — ready for Power BI.

No external ML library is used — cosine similarity is implemented directly
with numpy so the core logic is fully visible and easy to explain.

## Project structure

```
personalized-ad-recommender/
├── generate_data.py                 # creates the raw dataset (run first)
├── browsing_history_raw.xlsx        # raw browsing/purchase history
├── recommendations.sql              # SQL queries used in the analysis
├── recommender.py                   # main script — builds the model, runs SQL, exports results
├── recommender.db                   # SQLite database (created when you run recommender.py)
└── recommendation_output.xlsx       # final output — import THIS into Power BI
```

## How to run it

```bash
pip install pandas numpy openpyxl
python generate_data.py     # creates data/browsing_history_raw.xlsx
python recommender.py       # builds the recommender, runs SQL, exports results
```

Sample run output: **50 users, 25 products, 150 personalized recommendations
generated (3 per user).**

## Building the Power BI dashboard

1. Power BI Desktop → **Get Data** → **Excel** → select `recommendation_output.xlsx`
2. Load all sheets
3. Suggested visuals:
   - Bar chart: **Most Recommended Products**
   - Card: total recommendations / users covered (**Recommendation Coverage**)
   - Pie/donut chart: **Category Distribution**
   - Table: **Top Similar User Pairs**
   - Bar chart: **Purchase Rate by Category**
4. Title: "Personalized Recommendation Dashboard"

## How the recommendation logic works

- Each user's browsing history becomes a row of "interest scores" across
  every product (views + a purchase bonus).
- Cosine similarity compares each pair of users' score vectors — a value
  close to 1 means two users have very similar interests, close to 0 means
  unrelated.
- For each user, the model looks at their 5 most similar users and
  recommends products from that group weighted by similarity, excluding
  anything the user has already viewed.

## Tech stack

Python (pandas, numpy) · collaborative filtering (cosine similarity) · SQL
(SQLite) · Excel · Power BI

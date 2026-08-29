"""
Personalized Ad/Product Recommender — Main Script
----------------------------------------------------
What this does, step by step:

  1. Loads raw browsing/purchase history from data/browsing_history_raw.xlsx
  2. Builds a USER-PRODUCT interaction matrix (rows = users, columns = products,
     values = an "interest score" combining view count + purchase)
  3. Computes USER-USER SIMILARITY using cosine similarity — this is the core
     AI/ML technique behind collaborative filtering (the same idea used by
     "customers who viewed this also viewed..." style recommendation engines)
  4. For each user, finds their most similar users and recommends products
     those similar users engaged with that the target user hasn't seen yet
  5. Loads everything into SQLite and runs SQL queries for reporting
  6. Exports all results to Excel — ready for Power BI

No external ML library is required — cosine similarity is implemented with
plain numpy, so the technique is fully visible and easy to explain.
"""

import sqlite3
import numpy as np
import pandas as pd

RAW_FILE = "data/browsing_history_raw.xlsx"
DB_FILE = "recommender.db"
SQL_FILE = "recommendations.sql"
OUTPUT_FILE = "recommendation_output.xlsx"

TOP_N_SIMILAR_USERS = 5
TOP_N_RECOMMENDATIONS = 3


def load_data():
    df = pd.read_excel(RAW_FILE)
    df = df.dropna()
    return df


def build_interaction_matrix(df):
    """
    Builds a user x product matrix. Each cell = an 'interest score':
    view_count, plus a bonus of +5 if the user purchased that product.
    This score is what the similarity calculation is based on.
    """
    df = df.copy()
    df["interest_score"] = df["view_count"] + df["purchased"].apply(
        lambda x: 5 if x == "Yes" else 0
    )

    matrix = df.pivot_table(
        index="user_id",
        columns="product_id",
        values="interest_score",
        aggfunc="sum",
        fill_value=0,
    )
    return matrix


def cosine_similarity_matrix(matrix):
    """
    Computes user-user cosine similarity using plain numpy.
    Cosine similarity measures how similar two users' interest patterns
    are, regardless of overall activity level — this is the standard
    technique behind collaborative filtering recommendation systems.
    """
    values = matrix.values
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9  # avoid divide-by-zero for inactive users
    normalized = values / norms

    similarity = normalized @ normalized.T
    sim_df = pd.DataFrame(similarity, index=matrix.index, columns=matrix.index)
    return sim_df


def generate_recommendations(matrix, similarity):
    """
    For each user: find their most similar users, then recommend products
    those similar users engaged with that the target user has NOT
    interacted with yet, ranked by combined interest score.
    """
    recommendations = []

    for user in matrix.index:
        similar_users = (
            similarity[user]
            .drop(user)
            .sort_values(ascending=False)
            .head(TOP_N_SIMILAR_USERS)
        )

        # weighted score: sum of (similar user's interest in product * how similar they are)
        candidate_scores = pd.Series(0.0, index=matrix.columns)
        for other_user, sim_score in similar_users.items():
            candidate_scores += matrix.loc[other_user] * sim_score

        # remove products the target user has already interacted with
        already_seen = matrix.loc[user]
        candidate_scores = candidate_scores[already_seen == 0]

        top_recs = candidate_scores.sort_values(ascending=False).head(
            TOP_N_RECOMMENDATIONS
        )

        for rank, (product_id, score) in enumerate(top_recs.items(), start=1):
            recommendations.append({
                "user_id": user,
                "recommended_product_id": product_id,
                "rank": rank,
                "recommendation_score": round(score, 2),
                "most_similar_user": similar_users.index[0],
                "similarity_score": round(similar_users.iloc[0], 3),
            })

    return pd.DataFrame(recommendations)


def save_to_sqlite(df_history, df_recommendations):
    conn = sqlite3.connect(DB_FILE)
    df_history.to_sql("browsing_history", conn, if_exists="replace", index=False)
    df_recommendations.to_sql("recommendations", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded data into {DB_FILE} (tables: browsing_history, recommendations)")


def split_sql_queries():
    with open(SQL_FILE, "r") as f:
        content = f.read()
    raw_statements = content.split(";")
    queries = []
    for stmt in raw_statements:
        lines = [
            line for line in stmt.split("\n")
            if line.strip() and not line.strip().startswith("--")
        ]
        cleaned = "\n".join(lines).strip()
        if cleaned:
            queries.append(cleaned)
    return queries


def run_queries_and_export(df_history, df_recommendations, product_lookup):
    conn = sqlite3.connect(DB_FILE)
    queries = split_sql_queries()

    sheet_names = [
        "Most Recommended Products",
        "Recommendation Coverage",
        "Category Distribution",
        "Top Similar User Pairs",
        "Purchase Rate by Category",
    ]

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        # raw + recommendations first
        df_history.to_excel(writer, sheet_name="Browsing History", index=False)

        recs_with_names = df_recommendations.merge(
            product_lookup, left_on="recommended_product_id", right_on="product_id"
        ).drop(columns=["product_id"])
        recs_with_names.to_excel(writer, sheet_name="User Recommendations", index=False)

        # then each SQL query result
        for name, query in zip(sheet_names, queries):
            result = pd.read_sql_query(query, conn)
            result.to_excel(writer, sheet_name=name, index=False)
            print(f"  -> {name}: {len(result)} rows")

    conn.close()
    print(f"\nAll results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    print("Step 1: Loading browsing history...")
    df = load_data()
    product_lookup = df[["product_id", "product_name", "category"]].drop_duplicates()

    print("Step 2: Building user-product interaction matrix...")
    matrix = build_interaction_matrix(df)
    print(f"  Matrix shape: {matrix.shape[0]} users x {matrix.shape[1]} products")

    print("Step 3: Computing user-user cosine similarity...")
    similarity = cosine_similarity_matrix(matrix)

    print("Step 4: Generating personalized recommendations...")
    recommendations = generate_recommendations(matrix, similarity)
    print(f"  Generated {len(recommendations)} recommendations "
          f"({TOP_N_RECOMMENDATIONS} per user)")

    print("Step 5: Loading into SQLite...")
    save_to_sqlite(df, recommendations)

    print("Step 6: Running SQL queries and exporting to Excel...")
    run_queries_and_export(df, recommendations, product_lookup)

    print("\nDone! Open recommendation_output.xlsx and import it into Power BI.")

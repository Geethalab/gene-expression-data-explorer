import sqlite3
from pathlib import Path


# --------------------------------------------------
# Database location
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE = PROJECT_ROOT / "database" / "gene_expression.db"


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# --------------------------------------------------
# Get summary for one gene
# --------------------------------------------------

def get_gene_summary(gene_symbol):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        SELECT
            g.gene_symbol,

            COUNT(e.expression_value)
                AS expressing_cells,

            ROUND(
                100.0 * COUNT(e.expression_value)
                / (SELECT COUNT(*) FROM cells),
                2
            ) AS percent_cells,

            ROUND(
                AVG(e.expression_value),
                2
            ) AS mean_expression,

            MAX(e.expression_value)
                AS max_expression

        FROM expression e

        JOIN genes g
            ON e.gene_id = g.gene_id

        WHERE g.gene_symbol = ?

        GROUP BY g.gene_symbol;
    """

    cursor.execute(query, (gene_symbol,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return dict(result)


# --------------------------------------------------
# Get all available genes
# --------------------------------------------------

def get_genes():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            gene_id,
            gene_symbol
        FROM genes
        ORDER BY gene_symbol;
        """
    )

    results = cursor.fetchall()

    connection.close()

    return [dict(row) for row in results]


# --------------------------------------------------
# Test the database functions
# --------------------------------------------------

# --------------------------------------------------
# Get database statistics
# --------------------------------------------------

def get_database_stats():

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        SELECT
            (SELECT COUNT(*) FROM study) AS studies,
            (SELECT COUNT(*) FROM samples) AS samples,
            (SELECT COUNT(*) FROM genes) AS genes,
            (SELECT COUNT(*) FROM cells) AS cells,
            (SELECT COUNT(*) FROM expression)
                AS expression_records;
    """

    cursor.execute(query)

    result = cursor.fetchone()

    connection.close()

    return dict(result)


if __name__ == "__main__":

    print("Testing database connection...")
    print()

    # Test 1: ABCB1
    result = get_gene_summary("ABCB1")

    print("ABCB1 summary:")
    print(result)

    print()

    # Test 2: ABCG2
    result = get_gene_summary("ABCG2")

    print("ABCG2 summary:")
    print(result)

    print()

    # Test 3: Count available genes
    genes = get_genes()

    print(
        f"Total genes available: {len(genes)}"
    )

    print()

    print("Database functions working successfully.")

def get_gene_by_sample(gene_symbol):
    conn = sqlite3.connect("database/gene_expression_v2.db")
    cursor = conn.cursor()

    query = """
    SELECT
        s.sample_id,
        s.population,
        s.treatment,
        s.culture,
        COUNT(e.expression_value),
        ROUND(AVG(e.expression_value), 2),
        MAX(e.expression_value)
    FROM expression e
    JOIN genes g ON e.gene_id = g.gene_id
    JOIN samples s ON e.sample_id = s.sample_id
    WHERE g.gene_symbol = ?
    GROUP BY s.sample_id
    ORDER BY s.sample_id;
    """

    cursor.execute(query, (gene_symbol,))
    results = cursor.fetchall()

    conn.close()
    return results

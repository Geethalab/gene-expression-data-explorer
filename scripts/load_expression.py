import sqlite3
import tarfile
import gzip
import io
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TAR_FILE = PROJECT_ROOT / "data" / "GSE266356_RAW.tar"
DATABASE = PROJECT_ROOT / "database" / "gene_expression.db"

MATRIX_FILE = (
    "GSM8245469_doxorubicin_attached_matrix.mtx.gz"
)

SAMPLE_ID = 2


# --------------------------------------------------
# Open database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

print("Loading sparse expression matrix...")


# --------------------------------------------------
# Read matrix directly from TAR archive
# --------------------------------------------------

with tarfile.open(TAR_FILE, "r") as tar:

    member = tar.getmember(MATRIX_FILE)

    compressed_file = tar.extractfile(member)

    if compressed_file is None:
        raise FileNotFoundError(
            f"Could not find {MATRIX_FILE}"
        )

    with gzip.GzipFile(fileobj=compressed_file) as gz:

        text_stream = io.TextIOWrapper(
            gz,
            encoding="utf-8"
        )

        # Skip Matrix Market comments
        line = text_stream.readline()

        while line.startswith("%"):
            line = text_stream.readline()

        # Matrix dimensions
        rows, columns, non_zero = map(
            int,
            line.strip().split()
        )

        print(
            f"Matrix dimensions: "
            f"{rows} genes × {columns} cells"
        )

        print(
            f"Expected non-zero values: {non_zero}"
        )

        # --------------------------------------------------
        # Load expression records
        # --------------------------------------------------

        batch = []

        processed = 0

        for line in text_stream:

            if not line.strip():
                continue

            gene_index, cell_index, value = map(
                int,
                line.strip().split()
            )

            # Matrix Market uses 1-based indices
            gene_id = gene_index
            cell_id = cell_index

            batch.append(
                (
                    SAMPLE_ID,
                    cell_id,
                    gene_id,
                    value
                )
            )

            processed += 1

            # Insert in batches
            if len(batch) >= 10000:

                cursor.executemany(
                    """
                    INSERT INTO expression (
                        sample_id,
                        cell_id,
                        gene_id,
                        expression_value
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    batch
                )

                connection.commit()

                batch.clear()

            # Progress message
            if processed % 100000 == 0:

                print(
                    f"Processed {processed:,} "
                    f"expression values..."
                )

        # Insert remaining records

        if batch:

            cursor.executemany(
                """
                INSERT INTO expression (
                    sample_id,
                    cell_id,
                    gene_id,
                    expression_value
                )
                VALUES (?, ?, ?, ?)
                """,
                batch
            )

            connection.commit()


# --------------------------------------------------
# Verify
# --------------------------------------------------

cursor.execute(
    """
    SELECT COUNT(*)
    FROM expression
    WHERE sample_id = ?
    """,
    (SAMPLE_ID,)
)

count = cursor.fetchone()[0]

print(
    f"Expression records loaded: {count:,}"
)

connection.close()

print("Expression database loading complete.")

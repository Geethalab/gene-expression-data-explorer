from flask import Flask, render_template, request
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.database import (
    get_gene_summary,
    get_genes,
    get_database_stats,
    get_gene_by_sample
)

from scripts.plot import create_gene_plot

app = Flask(__name__, template_folder="templates")


@app.route("/", methods=["GET"])
def index():

    genes = get_genes()
    print("GENES:", genes[:3])  
   
    database_stats = get_database_stats()
    print("DATABASE STATS:", database_stats)

    gene_summary = None
    gene_samples = None
    plot_file = None
    searched_gene = ""

    gene = request.args.get("gene", "").strip()

    if gene:
        searched_gene = gene.upper()

        gene_summary = get_gene_summary(searched_gene)
        gene_samples = get_gene_by_sample(searched_gene)

        print("GENE:", searched_gene)
        print("SUMMARY:", gene_summary)
        print("SAMPLES:", gene_samples)

        if gene_samples:
            plot_file = create_gene_plot(
                searched_gene,
                gene_samples
            )
            print("PLOT:", plot_file)

    return render_template(
        "index.html",
        genes=genes,
        database_stats=database_stats,
        gene_summary=gene_summary,
        gene_samples=gene_samples,
        searched_gene=searched_gene,
        plot_file=plot_file
    )
from flask import Response
import csv

@app.route("/download")
def download():

    gene = request.args.get("gene", "").strip().upper()

    if not gene:
        return "No gene selected"

    gene_samples = get_gene_by_sample(gene)

    def generate():
        yield "Population,Treatment,Culture,Cells,Mean,Max\n"

        for row in gene_samples:
            yield f"{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={gene}_data.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)

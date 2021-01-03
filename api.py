import re
from src.searcher import Searcher
from argparse import ArgumentParser
from flask import Flask, flash, render_template, redirect, request, send_from_directory


searcher = None
app = Flask(__name__)    


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods = ["GET"])
def search():
    query = request.args.get("query", "").strip()
    query_result = searcher.search(query)
    return render_template("search.html",
                           search_result = query_result,
                           query = query)

if __name__ == "__main__":
    parser = ArgumentParser(description = "Model trainer")
    parser.add_argument("--index_folder", help = "path to index folder", required = True)
    args = parser.parse_args()

    searcher = Searcher(args.index_folder)
    app.run(host = "0.0.0.0", port = 8000, debug = True, threaded = False, processes = 1)
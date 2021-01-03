import json, os, errno
import pandas as pd
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import Phrase
from tqdm import tqdm
from argparse import ArgumentParser

tqdm.pandas()

def maybe_create_folder(folder):
    try:
        os.makedirs(folder)
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


def str_to_list(string):
    try:
        return json.loads(string.replace("'", '"'))
    except: return None

def process_subj_list(subj_list: list) -> str:
    return ",".join(subj_list)

def process_data(_df):
    df = _df.copy()
    df.subjects = df.subjects.progress_apply(lambda x: str_to_list(x))
    df = df.dropna()
    df.subjects = df.subjects.progress_apply(process_subj_list)
    df.categories = df.categories.progress_apply(lambda x: ", ".join(x.split(" ")))
    df = df.reset_index(drop = True)
    return df



def write_index(writer, df):
    for index in tqdm(range((len(df))), desc = "Indexing data"):
        row = df.loc[index]
        writer.add_document(arxiv_id = row.arxiv_id,
                            subjects = row.subjects, 
                            categories = row.categories, 
                            sentence = row.sentence)

    writer.commit()



if __name__ == "__main__":
    parser = ArgumentParser(description = "Create index")
    parser.add_argument("--index_folder", help = "to where the index will be saved", required = True)
    parser.add_argument("--data_path", help = "path to processed data", required = True)
    args = parser.parse_args()

    schema = Schema(arxiv_id = ID(stored = True),
                    subjects = TEXT, 
                    categories = STORED, 
                    sentence = STORED)

    INDEX_FOLDER = args.index_folder
    DATA_PATH = args.data_path

    maybe_create_folder(INDEX_FOLDER)
    ix = create_in(INDEX_FOLDER, schema)
    writer = ix.writer()

    df = pd.read_csv(DATA_PATH, dtype = str)
    df = process_data(df)

    write_index(writer, df)
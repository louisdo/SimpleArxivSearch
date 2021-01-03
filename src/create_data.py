"""Create a small dataset from the big one"""
import os, re
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser

def process_cate(row):
    res = []
    cats = row.categories.split(" ")
    for cat in cats:
        cat = cat.split(".")[0]
        res.append(cat)
    return " ".join(list(set(res)))


def unicodetoascii(text):

    TEXT = (text.
    		replace('\\xe2\\x80\\x99', "'").
            replace('\\xc3\\xa9', 'e').
            replace('\\xe2\\x80\\x90', '-').
            replace('\\xe2\\x80\\x91', '-').
            replace('\\xe2\\x80\\x92', '-').
            replace('\\xe2\\x80\\x93', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x94', '-').
            replace('\\xe2\\x80\\x98', "'").
            replace('\\xe2\\x80\\x9b', "'").
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9c', '"').
            replace('\\xe2\\x80\\x9d', '"').
            replace('\\xe2\\x80\\x9e', '"').
            replace('\\xe2\\x80\\x9f', '"').
            replace('\\xe2\\x80\\xa6', '...').
            replace('\\xe2\\x80\\xb2', "'").
            replace('\\xe2\\x80\\xb3', "'").
            replace('\\xe2\\x80\\xb4', "'").
            replace('\\xe2\\x80\\xb5', "'").
            replace('\\xe2\\x80\\xb6', "'").
            replace('\\xe2\\x80\\xb7', "'").
            replace('\\xe2\\x81\\xba', "+").
            replace('\\xe2\\x81\\xbb', "-").
            replace('\\xe2\\x81\\xbc', "=").
            replace('\\xe2\\x81\\xbd', "(").
            replace('\\xe2\\x81\\xbe', ")"))
    return TEXT



def process_abstract(row):
    abstract = row.abstract.lower()
    abstract = re.sub(r'(\S)\n(\S)',r'\1 \2',abstract)
    abstract = unicodetoascii(abstract)
    abstract = re.sub(r'\$.+?\$','<equation>',abstract)
    abstract = re.sub(r'-*\+*\d+\.*\d*%*','<number>',abstract)
    abstract = re.sub(r'\(*<number>\)*(\s*\S{1}\s*\(*<number>\)*)*','<number>',abstract)
    abstract = re.sub(r'(\S)*\^(<number>)',r'<unit>',abstract)
    abstract = re.sub(r'((<number>)+[a-z]+)|([a-z]+(<number>)+)\S*','<alpha>',abstract)
    abstract = re.sub(r'\S+[_^]\S+','<equation>',abstract)
    abstract = re.sub(r'\S*\\[^\\\']\S+','<equation>',abstract)
    abstract = re.sub(r'\S+\s*([=+><]|>=|=>|<=|=<|=)\s*\S+','<equation>',abstract)
    abstract = re.sub(r'<equation>\s*-\s*<equation>','<equation>',abstract)

    return abstract


if __name__ == "__main__":
    parser = ArgumentParser(description = "Create data")
    parser.add_argument("--savefile", help = "to where the data will be saved", required = True)
    parser.add_argument("--num_dpoints", type = int, help = "number of data points to get", required = True)
    args = parser.parse_args()

    ARXIV_DATA = "../data/arxiv-metadata-oai-snapshot.json"
    SAMPLE_EACH_BATCH = 10
    SUBSET = ["id", "abstract", "title", "categories"]
    SAVEFILE = args.savefile
    NUM_POINTS = args.num_dpoints
    count = 0

    chunks = pd.read_json(ARXIV_DATA, lines=True, chunksize = 100, dtype = str)
    with tqdm(total = NUM_POINTS) as pbar:
        for c in chunks:
            c = c.dropna(subset = SUBSET)[SUBSET]
            c = c.sample(SAMPLE_EACH_BATCH)
            c["categories"] = c.apply(process_cate, axis = 1)
            c["abstract"] = c.apply(process_abstract, axis = 1)
            count += SAMPLE_EACH_BATCH
            if not os.path.exists(SAVEFILE): c.to_csv(SAVEFILE, index = False)
            else: c.to_csv(SAVEFILE, mode = "a", header = False, index = False)
            pbar.update(SAMPLE_EACH_BATCH)
            if count >= NUM_POINTS: break
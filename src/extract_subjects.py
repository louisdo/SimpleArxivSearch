"""Split abstract into sentences and extract subjects from those sentences"""

import spacy, os
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser

tqdm.pandas()

class SubjectExtractor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.allowed_dep = ["subj", "nsubj"]
        
    def _process_sentence(self, sentence):
        res = sentence.replace(".", "")
        res = res.replace(", ", ",")
        return res.lower()

    @staticmethod
    def split_abstract(_abstract):
        passage = _abstract.replace("\n", " ")
        sentences = passage.split(".")
        sentences = [sen.strip() for sen in sentences]
        return [sen for sen in sentences if sen != ""]
    
    def __call__(self, _sentence):
        subjects = []
        sentence = self._process_sentence(_sentence)
        doc = self.nlp(sentence)
        all_obj_toks = [tok for tok in doc if tok.dep_ in self.allowed_dep]
        for tok in all_obj_toks:
            found = str(doc[tok.left_edge.i : tok.right_edge.i + 1]).split(",")
            subjects.extend(item.strip() for item in found)
        return subjects


def save_data():
    global all_ids, all_sentences, all_cates, all_subjects
    new_df = pd.DataFrame()
    new_df["arxiv_id"] = all_ids
    new_df["sentence"] = all_sentences
    new_df["categories"] = all_cates
    new_df["subjects"] = all_subjects

    if not os.path.exists(SAVEFILE):
        new_df.to_csv(SAVEFILE, index = False)
    else:
        new_df.to_csv(SAVEFILE, mode = "a", header = False, index = False)

    all_ids = []
    all_sentences = []
    all_cates = []
    all_subjects = []
    del new_df


def get_subj_sen(row):
    abstract = row.abstract
    cate = row.categories
    sentences = SubjectExtractor.split_abstract(abstract)
    arxiv_id = row.id

    for sen in sentences:
        subjs = extractor(sen)
        if len(subjs) == 0: continue
        all_sentences.append(sen)
        all_cates.append(cate)
        all_subjects.append(subjs)
        all_ids.append(arxiv_id)

    if len(all_sentences) >= BATCH_SIZE:
        save_data()




if __name__ == "__main__":
    parser = ArgumentParser(description = "Extract subjects")
    parser.add_argument("--data_path", help = "path to data to process", required = True)
    parser.add_argument("--savefile", help = "to where the processed data will be saved", required = True)
    args = parser.parse_args()
    

    DATA_PATH = args.data_path
    SAVEFILE = args.savefile
    BATCH_SIZE = 1000
    df = pd.read_csv(DATA_PATH, dtype = str)

    extractor = SubjectExtractor()

    all_sentences = []
    all_cates = []
    all_subjects = []
    all_ids = []

    df.progress_apply(get_subj_sen, axis = 1)
    
    if len(all_sentences) > 0:
        save_data()
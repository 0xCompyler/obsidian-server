from . import file_handler
import os
import re
import docx
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity

DUMP_DIR = os.path.join(os.getcwd(), "DUMP")


def cache_assignments(course_code: str, assignment_id: str):
    """Downloads all the answers to an assignment to DUMP

    Args:
        course_code (str): course code of the assignment
        assignment_id (str): assignment id 
    """

    files_list = file_handler.list_files("obsidian")
    BASE_STR = f"{course_code}/assignment/{assignment_id}/answers/"
    answers_list = [file.key for file in files_list if file.key.startswith(BASE_STR)]
    
    for file in answers_list:
        if file_handler.download_files("obsidian", file):
            print(f"[LOG] Downloaded {file.split('/')[-1]}")
        

def word_to_str(path: str):
    doc = docx.Document(path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)

    return ' '.join(fullText)



def plag_util(doc_id, files_list):
    #* read all files with .docx
    #* create a list of dict
    #* create pd.DataFrame
    file_content = []
    for file in files_list:
        temp_dict = {
            "content": word_to_str(os.path.join(DUMP_DIR, file)),
            "name": file.split('.')[0]
        }
        file_content.append(temp_dict)

    documents_df = pd.DataFrame(file_content)
    stop_words_english=stopwords.words('english')
    documents_df['content'] = documents_df["content"].apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stop_words_english))


    tfidf = TfidfVectorizer(max_features = 64)
    tfidf.fit(documents_df["content"])

    vectors = tfidf.transform(documents_df["content"])

    similarity_matrix = cosine_similarity(vectors, vectors)
    similar_ix=np.argsort(similarity_matrix[doc_id])[::-1]

    result = []
    
    for ix in similar_ix:
        if ix==doc_id:
            continue
        name_sim_dict = {
        "name": documents_df.iloc[ix]['name'],
        "sim_score": str(similarity_matrix[doc_id][ix]*100)
        }
        result.append(name_sim_dict)
    return result


def check_plagiarism():
    files_list = os.listdir(DUMP_DIR)
    files_list = [f for f in  files_list if f[-4:] == 'docx']

    results = []

    for ctr, file in enumerate(files_list):
        temp_dict = {
            "name": file.split('.')[0],
            "result": plag_util(ctr, files_list)
        }
        results.append(temp_dict)
    
    for file in files_list:
        os.remove(os.path.join(DUMP_DIR, file))

    return results



def keyword_checker(keywords: list):
    files_list = os.listdir(DUMP_DIR)
    files_list = [f for f in  files_list if f[-4:] == 'docx']

    results = []

    for f in files_list:
        temp_dict = {}
        name = f.split('.')[0]

        temp_dict['name'] = name
        content = word_to_str(os.path.join(DUMP_DIR, f))
        true_count = 0
        false_count = 0
        for word in keywords:
            if word in content:
                temp_dict[word] = "true"
                true_count += 1
            else:
                temp_dict[word] = "false"
                false_count += 1
        
        temp_dict['present'] = true_count
        temp_dict['absent'] = false_count
        results.append(temp_dict)

    for file in files_list:
        os.remove(os.path.join(DUMP_DIR, file))

    return results



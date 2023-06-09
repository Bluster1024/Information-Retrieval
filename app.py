'''
Code for the Flask App

Contributor: Ziming Xu, Jiafan He, Kirsten, Yunbin Tu
'''
from typing import List
from utils import load_resume, load_csv
from gpt import GPT
from gpt_ranking import Rerank
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from search import BM25_standard_analyzer_search, BM25_english_analyzer_search, search_by_ids

app = Flask(__name__)
PER_PAGE = 8
gptAPI = GPT()
app.config['UPLOAD_FOLDER'] = "./corpus_data"
# query = ""
pdf = None

# home page
@app.route("/")
def home():
    return render_template("home.html")


# result page
#contributor: Ziming Xu, Jiafan He
@app.route("/results", methods=["POST"])
def results():
    global pdf
    '''
    Result page that returns searched documents and GPT comment
    '''
    # TODO:
    query = request.form["query"]
    pdf = request.files["file"]
    if query == "":
        return render_template('home.html')
    answer = "NONE - "
    answer += "Upload your resume for recommended jobs based on your query, and for the option/ability to rerank your results. "
    answer += "If you upload a file now, you must click the search button again. "
    answer += "Then, you can click the AI Rerank button at the bottom of the list to generate an AI based reranking of your results. "
    most_frequent_skills = None
    if pdf:
        filename = secure_filename(pdf.filename)
        pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        resume = load_resume(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        prompt = "What are the most suitable jobs based on this resume: " + resume
        answer = gptAPI.getResponse(prompt) + " You can enter these into the search bar to find possible listings. "
        answer += "You can also click the AI Rerank button at the bottom of the list to generate an AI based reranking of your results. "
    if query:
        most_frequent_skills = required_skills_process(gptAPI.getResponse("Identify skills that are most frequently required by employers for " + query))
    matched_docs = BM25_standard_analyzer_search(query)
    return render_template('results.html',
                           page_id=0,
                           is_last=True,
                           docs=matched_docs,
                           query=query,
                           answer = answer,
                           most_frequent_skills = most_frequent_skills
                           )

'''
Contributor: Kirsten, Ziming Xu
Website directs to this page if the user hits the "AI Rerank" labeled button.
'''
@app.route("/reranked_results", methods=["POST"])
def reranked_results():
    global pdf
    '''
    Result page that returns result documents that have been reranked through cosine similarity, and generated GPT comments
    '''
    # TODO:
    # initializes some variables
    answer = None
    query = request.form["query"]
    reranked_ind = []
    reranked_matches = []
    # generates results through the originally used method
    matched_docs = BM25_standard_analyzer_search(query)
    # if the user has uploaded a pdf of the resume
    if pdf:
        filename = secure_filename(pdf.filename)
        resume = load_resume(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # generates recommended job searches based on the resume uploaded
        prompt = "What are the most suitable jobs based on this resume: " + resume
        answer = gptAPI.getResponse(prompt) + " You can enter these into the search bar to find possible listings. "
        # sends a message to the user giving some information about the results
        answer += "Below are also the reranked results of your original query. They are ranked in order of which postings matched your resume best."
        # calls on the reranker and passes the path of the file containing information about the results and the resume uploaded
        gpt_reranking = Rerank("./corpus_data/query_results.csv", resume)
        # gets the indices of the new order of reranked results - skips the 1st one as that would be the resume
        reranked_ind = gpt_reranking.indices_of_nearest_neighbors[1:]
        # creates a list to store the results in - done for easier accessing/reranking 
        list_docs = []
        # goes through every hit/result generated by the query and adds it to the list in the same order
        for hit in matched_docs:
            list_docs.append(hit)
        # goes through the list of indexes of the best matches done by reranking - accesses those results from the index, adds them to the reranked list in the new order
        for ind in reranked_ind:
            reranked_matches.append(list_docs[ind])
    else:
        # generates a message for the user if they clicked the rerank button but didn't provide a resume to compare results to
        answer = "NONE - RESULTS HAVE NOT BEEN RERANKED. There is no resume to compare your results to. " 
        answer += "Upload your resume and resubmit your query, then you can click the AI Rerank button at the bottom of the page after to have it rerank the results of your typed query. "
        answer += "You must upload your resume everytime you enter a new search if you want to use the AI Reranking feature."
        # sets reranked messages to the original ranking
        reranked_matches = matched_docs
    # generates a message from chatGPT informing the user of skills often required by employers for jobs of the given query
    if query:
        most_frequent_skills = required_skills_process(gptAPI.getResponse("Identify skills that are most frequently required by employers for " + query))
    # deletes the result csv file for the current given query
    os.remove("./corpus_data/query_results.csv")
    return render_template('results.html',
                           page_id=0,
                           is_last=True,
                           docs=reranked_matches,
                           query=query,
                           answer = answer,
                           most_frequent_skills = most_frequent_skills
                           )

# "next page" to show more results
@app.route("/results/<int:page_id>", methods=["POST"])
def next_page(page_id):
    # TODO:
    return


def string_to_int_list(s: str) -> List[int]:
    s = s[1:-1]
    return [int(num.replace("'", "")) for num in s.split(',')]


def slice(list: List, page_id: int, per_page: int) -> List:
    return list[page_id * PER_PAGE: min(len(list), (page_id + 1) * PER_PAGE)]


def required_skills_process(skills: str) -> str:
    index = skills.index("1")
    return skills[index:]


# document page
# contributor: Jiafan He
@app.route("/doc_data/<int:doc_id>")
def doc_data(doc_id):
    '''
    Document page that returns matched doc
    '''
    # TODO:
    document = search_by_ids("job_posting", [doc_id], 8)[0]
    return render_template("doc.html", document=document)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

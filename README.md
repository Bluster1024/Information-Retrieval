# Information-Retrieval
Final Project for COSI132a - Information Retrieval --- ChatGPT Job Search Engine
created by Ziming Xu, Jiafan He, Kirsten Tapalla, Yunbin Tu

Google Doc for Design:
https://docs.google.com/document/d/1Sbf95iD2irQPIrFikL26B-8QzEZfoAwzdPwyAQI5zJc/edit

Google Slides:
https://docs.google.com/presentation/d/12I_tTYuDChPN_23LzLDvwwOCTjgRwC3dTY1Tcbo0Sk8/edit#slide=id.g23e94a77bfb_0_297


# System Design
This is an application that integrates Chat-GPT to help people find suitable jobs.
We used elasticsearch to rank the searched jobs from user query.
Users can upload their resume and search for jobs ranked by Chat-GPT. 
Chat-GPT will provide information regarding recommended jobs and required skills, etc.
Users can also rerank the original searched results based on Chat-GPT's analysis of the resume.

<b>Documents:</b><br/>
*corpus_data*                 - job postings data and sample resumes for testing<br/>
*embedding_service*           - embedding service required documents <br/>
*es_service*                  - elastic search (7.10.2) service required documents <br/>
*templates*                   - html webpage templates <br/>
*.gitignore*                  - gitignore file <br/>
*app.py*                      - the Flask application python file<br/>
*example_query.py*            - example query adopted from previous assignments for reference<br/>
*gpt_ranking.py*              - GPT reranking module<br/>
*gpt.py*                      - GPT API (gpt-3.5-turbo) connection module<br/>
*load_es_index.py*            - file to load elastic search indices<br/>
*README.md*                   - this file<br/>
*requirements.txt*            - requirements to be installed before running the app<br/>
*search.py*                   - to search for stored indices in the database<br/>
*utils.py*                    - Utility functions to load documents/csv files/resumes<br/>


# Setup Instructions 
1. Unzip the project zip file
2. Activate Environment by running conda activate cosi132a
3. Download ES from https://www.elastic.co/downloads/past-releases/elasticsearch-7-10-2. 
And put the downloaded “elasticsearch-7.10.2” into the unziped folder
4. cd to the project folder
5. Run pip install -r requirements.txt
6. Run the following on command line to start ES engine: 
        cd elasticsearch-7.10.2/
        ./bin/elasticsearch
7. On another terminal window, run the following to start embedding service:
        python -m embedding_service.server --embedding sbert  --model all-mpnet-base-v2
8. Load the indices by running:
        python load_es_index.py --index_name job_posting --corpus_folder_path ./corpus_data/data_job_posts.csv
9. Initialize your API key registered from https://platform.openai.com/account/api-keys
10. Store your APIKEY locally (Only need to do once), and GPT will fetch the key from local environment:
    On Mac:
        export APIKEY="......."  # in bash
    On Windows:
        $env:APIKEY="....." # in powershell
11. Run python app.py to use the app! 

Note: you can use the samples resumes in corpus_data folder for testing instead of uploading your own! 


# Explaining API in Elastic Search

elastic search returns the total hits, max score, and other basic information.
![1](https://user-images.githubusercontent.com/60807383/236937626-f0a4cf37-55cc-48e7-83c0-38b43af4a09a.png)

for explanation, it gives detailed weight for every token and every part of the formula.

 ![2](https://user-images.githubusercontent.com/60807383/236937635-db51833e-2097-48f9-b202-9d5bb974484c.png)


# Test Results

The bottleneck for response time is in the Chatgpt API calling, while the Elasticsearch part performs fast searches. Therefore, the speed of testing on the entire dataset is nearly as fast as testing on the subset.

Query accounting assistant with Elasticsearch:
![3](/TestResults/accounting%20assistant1.png)

Query accounting assistant with Chatgpt Reranking:
![4](/TestResults/accounting%20assistant2.png)

Query civil engineer with Elasticsearch:
![5](/TestResults/civil%20engineer%201.png)

Query civil engineer with Chatgpt Reranking:
![6](/TestResults/civil%20engineer%202.png)

Query electrician with Elasticsearch:
![7](/TestResults/electrician1.png)

Query electrician with Chatgpt Reranking:
![8](/TestResults/electrician2.png)

Query front end developer with Elasticsearch:
![9](/TestResults/front%20end%20developer1.png)

Query front end developer with Chatgpt Reranking:
![10](/TestResults/front%20end%20developer2.png)

Query office assistant with Elasticsearch:
![11](/TestResults/office%20assistant1.png)

Query office assistant with Chatgpt Reranking:
![12](/TestResults/office%20assistant2.png)

 # Chat-GPT Reranking
<b>How It Works:</b><br/>
The Chat-GPT reranking relies on the OpenAI embeddings model in order to rerank the original list of results to show which ones best fit the resume submitted by the user. In order to accomplish it, what was deemed important information from the job listings were all combined and turned into 1 string for each listing and then added to a list. At the end of the list the user's information from their resume was then added on after as well. The list of strings are then turned into a list of embeddings, and then cosine similarity is used to compare which job postings best match the resume. A new list is returned based on the index order of which ones are deemed most similar. For the embedding creation, cosine similarity reranking, and indexing of the reranked results, OpenAI actually has built in functions that easily allow us to do this and rerank the original list of results. <br/>
The harder part of implementing the reranking was getting the results to be shown in the new order they were supposed to be in and adding the original results into the CSV file to be used when generating the embeddings. This is due to the fact that the results of elasticsearch are returned as Response and Hit objects, which made it difficult to go through the results in an easy way. Going through and getting Hit objects made it harder to obtain the data so that we could add it to the CSV file that was passed into the reranking module/class, but it was resolved by turning the results into dictionaries. Then to resolve reordering the results, we had to parse through the original list of results and add them to a different list so that they could be accessed through their index, since the built in function from OpenAI returns the reranked order of the results based on the index that they are in for the list of strings and embeddings. 

from flask import Flask, render_template, request
import os
import sys
from nytimesarticle import articleAPI

api = articleAPI('21f26d6caead1fbfcba777fd34564bb4:2:74628573')
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_folder)

# def get_raw_articles(query, filtered_query):
# 	articles = api.search( q = query, 
# 		fq = {'headline': filtered_query, 'source':['Reuters','AP', 'The New York Times']}, 
# 		begin_date = 20111231 )
# 	return articles

def parse_articles(articles):
    # This function takes in a response to the NYT api and parses
    # the articles into a list of dictionaries
    
    news = []
    for i in articles['response']['docs']:
        dic = {}
        dic['id'] = i['_id']
        dic['headline'] = i['headline']['main'].encode("utf8")
        dic['url'] = i['web_url']
        if i['snippet'] is not None:
            dic['snippet'] = i['snippet'].encode("utf8")
        if i['abstract'] is not None:
            dic['abstract'] = i['abstract'].encode("utf8")
        if i['lead_paragraph'] is not None:
        	dic['lead_paragraph'] = i['lead_paragraph'].encode("utf8")
        dic['type'] = i['type_of_material']
        dic['date'] = i['pub_date'][0:10] # cutting time of day.

        # subject
        subjects = []
        for x in range(0,len(i['keywords'])):
            if 'subject' in i['keywords'][x]['name']:
                subjects.append(i['keywords'][x]['value'])
        dic['subjects'] = subjects   
        news.append(dic)
    return(news) 

def retrieve_all(query, filtered_query, date):
    # This function accepts a year in string format (e.g.'1980')
    # and a query (e.g.'Amnesty International') and it will 
    # return a list of parsed articles (in dictionaries)
    # for that year.
    #
    all_articles = []
    for i in range(0,10): #NYT limits pager to first 100 pages. But rarely will you find over 100 pages of results anyway.
        articles = api.search(q = query,
               fq = {'headline': filtered_query, 'source':['Reuters','AP', 'The New York Times']},
               begin_date = date + '0101',
               end_date = date + '1231',
               sort='oldest',
               page = str(i))
        articles = parse_articles(articles)
        all_articles += articles
    return(all_articles)


@app.route('/')
def index():
	return render_template('index.html') # index is search page dashboard

@app.route('/search', methods=['POST'])
def search():
	query = request.form['article_name']
	filtered_query = request.form['article_name']
	date = request.form['date']
	articles = retrieve_all(query, filtered_query, date)
	return render_template('dashboard.html', articles=articles)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8000, debug=True)
from flask import Flask, render_template, request
import os
import random
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text, phrases):
    scores = []

    for phrase in phrases:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text, phrase])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        scores.append(score)

    if scores:
        return round((sum(scores) / len(scores)) * 100, 2)
    return 0


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def extract_text_from_docx(path):
    doc = Document(path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + " "
    return text


def extract_random_phrases(text, num_phrases=5, phrase_length=6):
    words = text.split()
    phrases = []

    if len(words) < phrase_length:
        return phrases

    for _ in range(num_phrases):
        start = random.randint(0, len(words) - phrase_length)
        phrase = " ".join(words[start:start + phrase_length])
        phrases.append(phrase)

    return phrases
import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def search_web(phrase, max_results=3):
    # Try DuckDuckGo (best effort)
    try:
        query = phrase.replace(" ", "+")
        url = f"https://html.duckduckgo.com/html/?q={query}"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []

        for a in soup.find_all("a", class_="result__a"):
            href = a.get("href")
            if href:
                links.append(href)
            if len(links) == max_results:
                break

        return links

    except:
        return []




@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        extracted_text = extract_text_from_docx(filepath)
        phrases = extract_random_phrases(extracted_text)
        search_results = {}
        for phrase in phrases:
            urls = search_web(phrase)
            search_results[phrase] = urls
        plagiarism_score = calculate_similarity(extracted_text, phrases)



        return render_template(
            "result.html",
            text=extracted_text,
            phrases=phrases,
            results=search_results,
            score=plagiarism_score


)


    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

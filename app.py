from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import nltk
from nltk.corpus import wordnet
import numpy as np

# Before running, install:
# pip install flask flask-cors transformers nltk numpy
# python -m nltk.downloader wordnet punkt

nltk.download('wordnet')
nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# Summarizer pipeline (BART)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

variants = ["A", "B", "C"]
variant_successes = {v: 1 for v in variants}
variant_failures = {v: 1 for v in variants}

def generate_summary(content):
    if not content or not isinstance(content, str):
        return None
    try:
        summary = summarizer(content, max_length=60, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception:
        return None

def enrich_text(text):
    if not text or not isinstance(text, str):
        return ""
    tokens = nltk.word_tokenize(text)
    enriched_tokens = []
    for word in tokens:
        synonyms = wordnet.synsets(word)
        if synonyms:
            lemmas = synonyms[0].lemma_names()
            if lemmas:
                syn = lemmas[0].replace('_', ' ')
                if syn.lower() != word.lower():
                    word = f"{word} ({syn})"
        enriched_tokens.append(word)
    return " ".join(enriched_tokens)

def select_variant_mab():
    best_variant = None
    best_score = -1
    for variant in variants:
        alpha = variant_successes[variant]
        beta = variant_failures[variant]
        sample = np.random.beta(alpha, beta)
        if sample > best_score:
            best_score = sample
            best_variant = variant
    return best_variant

def update_variant_reward(variant, reward):
    if variant not in variants or reward not in [0, 1]:
        return False
    if reward == 1:
        variant_successes[variant] += 1
    else:
        variant_failures[variant] += 1
    return True

# BrainRank scoring logic — improved but simple and safe
def brainrank_score(title, description):
    # Length score for title (ideal 5-15 words)
    title_len = len(title.split())
    if title_len < 5:
        title_score = (title_len / 5) * 30
    elif title_len > 15:
        title_score = max(0, 30 - (title_len - 15)*2)
    else:
        title_score = 30

    # Length score for description (ideal 20-60 words)
    desc_len = len(description.split())
    if desc_len < 20:
        desc_score = (desc_len / 20) * 40
    elif desc_len > 60:
        desc_score = max(0, 40 - (desc_len - 60))
    else:
        desc_score = 40

    # Simple keyword presence scoring (keywords: AI, data, machine learning)
    keywords = ['ai', 'data', 'machine learning']
    content_lower = (title + " " + description).lower()
    keyword_hits = sum(content_lower.count(k) for k in keywords)
    keyword_score = min(keyword_hits, 5) * 6  # max 30 points

    total = title_score + desc_score + keyword_score
    total = min(max(total, 0), 100)
    return round(total, 2)

@app.route('/generate_meta', methods=['POST'])
def generate_meta():
    data = request.get_json()
    content = data.get('content', '')
    summary = generate_summary(content)
    if summary:
        return jsonify({'meta_description': summary})
    else:
        return jsonify({'error': 'Summarization failed'}), 500

@app.route('/enrich_meta', methods=['POST'])
def enrich_meta():
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')

    if not title and not description:
        return jsonify({'error': 'Title or description required'}), 400

    enriched_title = enrich_text(title) if title else ""
    enriched_description = enrich_text(description) if description else ""

    return jsonify({
        'enriched_title': enriched_title,
        'enriched_description': enriched_description
    })

@app.route('/select_variant', methods=['GET'])
def select_variant():
    selected = select_variant_mab()
    return jsonify({'selected_variant': selected})

@app.route('/update_variant', methods=['POST'])
def update_variant():
    data = request.get_json()
    variant = data.get('variant')
    reward = data.get('reward')
    success = update_variant_reward(variant, reward)
    if success:
        return jsonify({'message': f'Variant {variant} updated with reward {reward}.'})
    else:
        return jsonify({'error': 'Invalid variant or reward.'}), 400

@app.route('/score', methods=['POST'])
def score():
    data = request.get_json()
from flask_cors import CORS
from transformers import pipeline
import nltk
from nltk.corpus import wordnet
import numpy as np

# Make sure you have these installed:
# pip install flask flask-cors transformers torch nltk numpy
# Run once to download nltk data:
# python -m nltk.downloader wordnet punkt

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# Initialize summarizer once
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("Error loading summarization pipeline:", e)
    summarizer = None

variants = ["A", "B", "C"]
variant_successes = {v: 1 for v in variants}
variant_failures = {v: 1 for v in variants}

def generate_summary(content):
    if not content or not isinstance(content, str) or summarizer is None:
        return None
    try:
        summary = summarizer(content, max_length=60, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("Summarization error:", e)
        return None

def enrich_text(text):
    if not text or not isinstance(text, str):
        return ""
    try:
        tokens = nltk.word_tokenize(text)
        enriched_tokens = []
        for word in tokens:
            synonyms = wordnet.synsets(word)
            if synonyms:
                lemmas = synonyms[0].lemma_names()
                if lemmas:
                    syn = lemmas[0].replace('_', ' ')
                    if syn.lower() != word.lower():
                        word = f"{word} ({syn})"
            enriched_tokens.append(word)
        return " ".join(enriched_tokens)
    except Exception as e:
        print("Enrich text error:", e)
        return text

def select_variant_mab():
    best_variant = None
    best_score = -1
    for variant in variants:
        alpha = variant_successes[variant]
        beta = variant_failures[variant]
        sample = np.random.beta(alpha, beta)
        if sample > best_score:
            best_score = sample
            best_variant = variant
    return best_variant

def update_variant_reward(variant, reward):
    if variant not in variants or reward not in [0, 1]:
        return False
    if reward == 1:
        variant_successes[variant] += 1
    else:
        variant_failures[variant] += 1
    return True

def brainrank_score(title, description):
    title_len = len(title.split())
    if title_len < 5:
        title_score = (title_len / 5) * 30
    elif title_len > 15:
        title_score = max(0, 30 - (title_len - 15)*2)
    else:
        title_score = 30

    desc_len = len(description.split())
    if desc_len < 20:
        desc_score = (desc_len / 20) * 40
    elif desc_len > 60:
        desc_score = max(0, 40 - (desc_len - 60))
    else:
        desc_score = 40

    keywords = ['ai', 'data', 'machine learning']
    content_lower = (title + " " + description).lower()
    keyword_hits = sum(content_lower.count(k) for k in keywords)
    keyword_score = min(keyword_hits, 5) * 6  # max 30 points

    total = title_score + desc_score + keyword_score
    total = min(max(total, 0), 100)
    return round(total, 2)

@app.route('/generate_meta', methods=['POST'])
def generate_meta():
    try:
        data = request.get_json(force=True)
        content = data.get('content', '')
        summary = generate_summary(content)
        if summary:
            return jsonify({'meta_description': summary})
        else:
            return jsonify({'error': 'Summarization failed'}), 500
    except Exception as e:
        return jsonify({'error': f'Invalid request or internal error: {str(e)}'}), 400

@app.route('/enrich_meta', methods=['POST'])
def enrich_meta():
    try:
        data = request.get_json(force=True)
        title = data.get('title', '')
        description = data.get('description', '')
        if not title and not description:
            return jsonify({'error': 'Title or description required'}), 400
        enriched_title = enrich_text(title) if title else ""
        enriched_description = enrich_text(description) if description else ""
        return jsonify({
            'enriched_title': enriched_title,
            'enriched_description': enriched_description
        })
    except Exception as e:
        return jsonify({'error': f'Invalid request or internal error: {str(e)}'}), 400

@app.route('/select_variant', methods=['GET'])
def select_variant():
    selected = select_variant_mab()
    return jsonify({'selected_variant': selected})

@app.route('/update_variant', methods=['POST'])
def update_variant():
    try:
        data = request.get_json(force=True)
        variant = data.get('variant')
        reward = data.get('reward')
        success = update_variant_reward(variant, reward)
        if success:
            return jsonify({'message': f'Variant {variant} updated with reward {reward}.'})
        else:
            return jsonify({'error': 'Invalid variant or reward.'}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request or internal error: {str(e)}'}), 400

@app.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json(force=True)
        title = data.get('title', '')
        description = data.get('description', '')
        score = brainrank_score(title, description)
        return jsonify({'score': score})
    except Exception as e:
        return jsonify({'error': f'Invalid request or internal error: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

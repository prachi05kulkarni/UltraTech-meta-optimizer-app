from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

variant_rewards = {
    "Variant A": {"clicks": 1, "views": 1},
    "Variant B": {"clicks": 1, "views": 1},
    "Variant C": {"clicks": 1, "views": 1},
}

@app.route("/generate_meta", methods=["POST"])
def generate_meta():
    data = request.get_json()
    content = data.get("content", "")
    if not content.strip():
        return jsonify({"error": "No content provided"}), 400

    sentences = content.split(".")
    best_line = max(sentences, key=lambda x: len(x.split()), default="").strip()
    if len(best_line) < 20:
        best_line = "This content provides valuable information."
    return jsonify({"meta_description": best_line})

@app.route("/enrich_meta", methods=["POST"])
def enrich_meta():
    data = request.get_json()
    title = data.get("title", "")
    description = data.get("description", "")
    enriched_title = f"{title} - Learn More" if title else ""
    enriched_description = f"{description} Improve your understanding today!" if description else ""
    return jsonify({
        "enriched_title": enriched_title,
        "enriched_description": enriched_description
    })

@app.route("/select_variant", methods=["GET"])
def select_variant():
    scores = {}
    for variant, stats in variant_rewards.items():
        score = stats["clicks"] / stats["views"]
        scores[variant] = score + random.uniform(0, 0.1)
    selected = max(scores, key=scores.get)
    variant_rewards[selected]["views"] += 1
    return jsonify({"selected_variant": selected})

@app.route("/update_variant", methods=["POST"])
def update_variant():
    data = request.get_json()
    variant = data.get("variant")
    reward = data.get("reward", 0)
    if variant in variant_rewards:
        variant_rewards[variant]["clicks"] += reward
        return jsonify({"message": f"Reward for {variant} updated."})
    return jsonify({"error": "Invalid variant"}), 400

@app.route("/score", methods=["POST"])
def score():
    data = request.get_json()
    title = data.get("meta_title", "")
    description = data.get("meta_description", "")
    content = data.get("content", "")

    title_words = set(title.lower().split())
    desc_words = set(description.lower().split())
    content_words = set(content.lower().split())

    total_meta_words = title_words | desc_words
    intersection = total_meta_words & content_words
    union = total_meta_words | content_words

    semantic_score = len(intersection) / len(union) if union else 0
    brainrank_score = round(semantic_score * 100, 2)

    return jsonify({
        "semantic_score": round(semantic_score, 2),
        "brainrank_score": brainrank_score
    })

if __name__ == "__main__":
    app.run(debug=True)

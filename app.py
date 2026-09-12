from flask import Flask, request, jsonify
from flask_cors import CORS

from db import (
    get_entrepreneur_by_id,
    insert_match
)

from matcher import match_schemes


app = Flask(__name__)
CORS(app)


@app.route("/api/match", methods=["POST"])
def match():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No input data provided"
        }), 400

    required_fields = [
        "gender",
        "caste",
        "business_type",
        "annual_revenue"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "success": False,
            "error": "Missing fields",
            "fields": missing_fields
        }), 400

    matches = match_schemes(data)

    return jsonify({
        "success": True,
        "matches": matches
    })


@app.route("/api/get-matches/<int:en_id>", methods=["GET"])
def get_matches(en_id):

    entrepreneur = get_entrepreneur_by_id(en_id)

    if not entrepreneur:
        return jsonify({
            "success": False,
            "error": "Entrepreneur not found"
        }), 404

    matches = match_schemes(entrepreneur)

    return jsonify({
        "success": True,
        "entrepreneur": entrepreneur,
        "matches": matches
    })


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "message": "AI Scheme Matcher backend is running"
    })


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
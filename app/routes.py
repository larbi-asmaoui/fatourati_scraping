from flask import Blueprint, jsonify, request
from app.services.scraping_service import scrape_data

main = Blueprint('main', __name__)


# @main.route('/scrape?', methods=['POST'])
# def scrape():
#     num_contrat = request.json.get('num_contrat', '')
#     if not num_contrat:
#         return jsonify({"error": "num_contrat is required"}), 400
#
#     try:
#         data = scrape_data(num_contrat)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@main.route('/scrape', methods=['GET'])
def scrape():
    num_contrat = request.args.get('num_contrat', '')
    if not num_contrat or not num_contrat.isdigit():
        return jsonify({"error": "Numero contrat est invalide"}), 400

    try:
        data = scrape_data(num_contrat)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
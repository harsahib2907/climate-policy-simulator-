"""
National Policy Command Centre (NPCC) - Backend API with Urban Impact Visualization
Flask server with routes for policy simulation, AI news generation, and image generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from io import BytesIO
import base64

# Import core engine
from backend.core.engine import PolicyEngine
from backend.core.image_generator import UrbanImpactGenerator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize Policy Engine
policy_engine = PolicyEngine()

# Initialize Urban Impact Generator
urban_generator = UrbanImpactGenerator()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBE1ok5qIXh9mOLl2fgVLXzAeKAJlhmWBU")
genai.configure(api_key=GEMINI_API_KEY)


@app.route('/api/init', methods=['GET'])
def initialize_dashboard():
    """
    GET /api/init
    Returns the 2026 baseline state for dashboard initialization
    """
    try:
        baseline_state = policy_engine.get_baseline_state()
        return jsonify({
            "success": True,
            "data": baseline_state
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/calculate', methods=['POST'])
def calculate_policy_impact():
    """
    POST /api/calculate
    Calculate fiscal cost and temperature mitigation based on policy inputs
    """
    try:
        # Get JSON payload
        policy_inputs = request.get_json()

        if not policy_inputs:
            return jsonify({
                "success": False,
                "error": "Missing policy inputs"
            }), 400

        # Calculate impacts using policy engine
        results = policy_engine.calculate_impacts(policy_inputs)

        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/news', methods=['POST'])
def generate_news_headline():
    """
    POST /api/news
    Generate AI-powered news headline based on current policy configuration
    """
    try:
        # Get JSON payload
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Missing input data"
            }), 400

        # Extract policy levels
        ev_level = data.get("ev_adoption", 0)
        renewable_level = data.get("renewable_energy", 0)
        carbon_tax_level = data.get("carbon_tax", 0)
        reforestation_level = data.get("reforestation", 0)
        public_transport_level = data.get("public_transport", 0)
        industrial_controls_level = data.get("industrial_controls", 0)
        green_buildings_level = data.get("green_buildings", 0)
        waste_management_level = data.get("waste_management", 0)

        # Optional context
        temp_change = data.get("temperature_change", 0)
        fiscal_cost = data.get("fiscal_cost", 0)

        # Construct prompt for Gemini
        prompt = f"""You are a senior government press secretary in the year 2035. 
Write a professional, confident 1-sentence headline announcing the results of the national climate policy program.

Current Policy Implementation Levels (0-100 scale):
- EV Adoption Incentives: {ev_level}%
- Renewable Energy Expansion: {renewable_level}%
- Carbon Tax Implementation: {carbon_tax_level}%
- Reforestation Programs: {reforestation_level}%
- Public Transport Expansion: {public_transport_level}%
- Industrial Emission Controls: {industrial_controls_level}%
- Green Building Standards: {green_buildings_level}%
- Waste Management & Recycling: {waste_management_level}%

Additional Context:
- Temperature mitigation achieved: {temp_change}°C
- Total fiscal investment: ${fiscal_cost}B

Write ONE headline that sounds like it came from a government press conference. Be specific, use numbers when relevant, and convey a sense of achievement or urgency depending on the policy levels.

Examples of good headlines:
- "Prime Minister Announces Historic Climate Victory as National Emissions Drop 32% Below 2020 Levels"
- "Government Commits $180B to Renewable Energy Revolution, Targeting 75% Clean Grid by 2040"
- "Treasury Reports $50B Revenue Gain from Carbon Tax as Industries Pivot to Green Technologies"

Your headline:"""

        # Call Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        headline = response.text.strip()

        # Remove quotes if present
        if headline.startswith('"') and headline.endswith('"'):
            headline = headline[1:-1]
        if headline.startswith("'") and headline.endswith("'"):
            headline = headline[1:-1]

        return jsonify({
            "success": True,
            "data": {
                "headline": headline,
                "policy_summary": {
                    "ev_adoption": ev_level,
                    "renewable_energy": renewable_level,
                    "carbon_tax": carbon_tax_level,
                    "reforestation": reforestation_level,
                    "public_transport": public_transport_level,
                    "industrial_controls": industrial_controls_level,
                    "green_buildings": green_buildings_level,
                    "waste_management": waste_management_level,
                    "temperature_impact": temp_change,
                    "fiscal_cost": fiscal_cost
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AI generation failed: {str(e)}"
        }), 500


@app.route('/api/urban-impact/generate', methods=['POST'])
def generate_urban_impact():
    """
    POST /api/urban-impact/generate
    Generate before/after urban impact comparison using Stable Diffusion

    Request Body:
        {
            "baseline_image": "base64_encoded_image" (optional),
            "policy_inputs": {
                "ev_adoption": 0-100,
                "renewable_energy": 0-100,
                ...
            },
            "city_description": "modern city skyline",
            "style": "photorealistic" or "artistic"
        }

    Response:
        {
            "success": true,
            "data": {
                "baseline_image": "base64_encoded_image",
                "impact_image": "base64_encoded_image",
                "description": "Generated visualization description"
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request data"
            }), 400

        # Extract parameters
        policy_inputs = data.get("policy_inputs", {})
        city_description = data.get("city_description", "urban cityscape")
        style = data.get("style", "photorealistic")
        baseline_image_b64 = data.get("baseline_image")

        # Calculate policy impact summary
        calculation = policy_engine.calculate_impacts(policy_inputs)

        # Generate images
        result = urban_generator.generate_comparison(
            policy_inputs=policy_inputs,
            calculation_result=calculation,
            city_description=city_description,
            style=style,
            baseline_image_b64=baseline_image_b64
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Image generation failed: {str(e)}"
        }), 500


@app.route('/api/urban-impact/quick-generate', methods=['POST'])
def quick_generate_urban_impact():
    """
    POST /api/urban-impact/quick-generate
    Quick generation without baseline image - generates both baseline and impact

    Request Body:
        {
            "policy_inputs": {...},
            "scenario": "coastal_city" | "industrial_city" | "suburban" | "megacity"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request data"
            }), 400

        policy_inputs = data.get("policy_inputs", {})
        scenario = data.get("scenario", "modern_city")

        # Calculate impacts
        calculation = policy_engine.calculate_impacts(policy_inputs)

        # Generate quick comparison
        result = urban_generator.quick_generate(
            policy_inputs=policy_inputs,
            calculation_result=calculation,
            scenario=scenario
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Quick generation failed: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    GET /health
    Simple health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "service": "NPCC Backend API",
        "version": "2.0.0",
        "features": {
            "policy_simulation": True,
            "ai_headlines": True,
            "urban_impact_visualization": True
        }
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Run Flask development server
    # Production: Use gunicorn or uwsgi
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
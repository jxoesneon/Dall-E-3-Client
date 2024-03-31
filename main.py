import os
import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
from functools import wraps
from generate_image import generate_image
from datetime import datetime
import requests as RQuest
# Initialize app and load .env file (if present)
app = Flask(__name__)
load_dotenv()  # Load environment variables from a .env file
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
# Define a decorator to require API key
def require_api_key(fn):
    @wraps(fn)
    def check_api_key(*args, **kwargs):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key  # Set the API key directly
            return fn(*args, **kwargs)  # noqa: F823
        else:
            # Check if .env file exists (optional)
            if not os.path.exists(".env"):
                with open(".env", "x", encoding="utf-8") as f:
                    text = 'OPENAI_API_KEY=""'
                    f.write(text)
            # Handle missing API key (e.g., redirect to modal for input)
            flash("Missing API Key!", category="error")
            return render_template("index.html")
    return check_api_key


def key_in_storage():
    return os.getenv("OPENAI_API_KEY") != ""


@app.route("/save-api-key", methods=["POST"])
def save_key():
    user_key = request.form.get("apiKey")

    # Update .env file with the new API key
    updated_content = ""
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                # Skip lines that don't start with 'OPENAI_API_KEY='
                if not line.startswith("OPENAI_API_KEY="):
                    updated_content += line
    updated_content += f'OPENAI_API_KEY="{user_key}"\n'

    with open(".env", "w", encoding="utf-8") as f:
        f.write(updated_content)

    flash("Successfully saved the API Key", category="success")
    return render_template("index.html", key_in_storage=True)


@app.route("/", methods=["GET", "POST"])
@require_api_key
def index():
    # Handle first request
    if request.method == "GET":
        in_storage = key_in_storage()
        if not in_storage:
            flash('There is no OpenAI API Key set, use the "API Key" button to set it')
        return render_template("index.html", key_in_storage=in_storage)


@app.route("/generate", methods=["POST"])
@require_api_key
def generate():
    in_storage = key_in_storage()
    # Get the prompt from the form
    prompt = request.form["prompt"]

    try:
        # Generate the image using the separate function
        image_url = generate_image(prompt)
    except openai.error.Error as e:
        error_message = str(e)
        return render_template("index.html", error=error_message, prompt=prompt)
    try:
        response = RQuest.get(image_url, stream=True)
        now = datetime.now()
        filename = "img/generated/"+ now.strftime("%Y-%m-%d_%H%M%S") + ".png"
        with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        print(f"Image saved successfully as: {filename}")

    except Exception as e:
        print(f"Error fetching image: {e}")

    # Return the generated image URL to the template
    return render_template("index.html", image_url=image_url, prompt=prompt, key_in_storage=in_storage)


# Run the Flask app (for development)
if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import json
import html
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')

# Load and clean the JSON data
with open('questions_by_date.json', 'r', encoding='utf-8') as file:
    questions_by_date = json.load(file)

def clean_html_entities(data):
    if isinstance(data, dict):
        return {key: clean_html_entities(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_html_entities(element) for element in data]
    elif isinstance(data, str):
        return html.unescape(data)
    else:
        return data

questions_by_date = clean_html_entities(questions_by_date)

@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        day = int(request.form.get("day_of_birth", 0))
        month = int(request.form.get("month_of_birth", 0))

        error_message = None

        if month < 1 or month > 12:
            error_message = "Incorrect month added. Please enter a valid month."
        elif month in [4, 6, 9, 11] and day > 30:
            error_message = "Incorrect date added. Please enter a valid date."
        elif month == 2 and day > 29:
            error_message = "Incorrect date added. Please enter a valid date."
        elif month in [1, 3, 5, 7, 8, 10, 12] and day > 31:
            error_message = "Incorrect date added. Please enter a valid date."
        elif day < 1 or day > 31:
            error_message = "Day must be between 1 and 31."

        if error_message:
            return render_template("index.html", error=error_message)

        date_key = f"{month:02d}-{day:02d}"
        question_data = questions_by_date.get(date_key)
        if question_data:
            question = question_data.get("question")
            options = question_data.get("incorrect_answers", []) + [question_data.get("correct_answer")]
            options.sort()
            return render_template("index.html", success=True, question=question, options=options,
                                   correct_answer=question_data.get("correct_answer"),
                                   day_of_birth=day, month_of_birth=month)

        error_message = "No question found for the given date."
        return render_template("index.html", error=error_message)

    return render_template("index.html")

@app.route("/riddle", methods=["POST"])
def receive_answer():
    user_answer = request.form.get("answer")
    correct_answer = request.form.get("correct_answer")

    feedback = ""
    feedback_class = ""

    if user_answer and correct_answer:
        if user_answer == correct_answer:
            feedback = "Correct! Well done."
            feedback_class = "flashy"
        else:
            feedback = f"Incorrect. The correct answer is: {correct_answer}"
            feedback_class = "flashy"

        day = int(request.form.get("day_of_birth", 0))
        month = int(request.form.get("month_of_birth", 0))
        date_key = f"{month:02d}-{day:02d}"
        question_data = questions_by_date.get(date_key)

        if question_data:
            question = question_data.get("question")
            options = question_data.get("incorrect_answers", []) + [question_data.get("correct_answer")]
            options.sort()
            return render_template("index.html", success=True, question=question, options=options,
                                   correct_answer=correct_answer, feedback=feedback, feedback_class=feedback_class,
                                   day_of_birth=day, month_of_birth=month)

    return redirect(url_for('hello'))

if __name__ == "__main__":
    app.run(debug=True)

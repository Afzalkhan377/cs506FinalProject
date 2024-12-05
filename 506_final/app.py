from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

# Create static directory for plots
PLOT_DIR = "static/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Sample DataFrame mimicking gym data
data = pd.DataFrame({
    'Timeslots': ["6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM",
                  "6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM"],
    'Crowdedness': [2, 3, 4, 5, 4, 3, 1, 2, 3, 4, 3, 2],
    'Day': ["Monday", "Monday", "Monday", "Monday", "Monday", "Monday",
            "Tuesday", "Tuesday", "Tuesday", "Tuesday", "Tuesday", "Tuesday"]
})

# Function to create plots
def create_visualizations():
    # Plot 1: Average Crowdedness Per Timeslot
    avg_crowdedness = data.groupby('Timeslots')['Crowdedness'].mean()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=avg_crowdedness.index, y=avg_crowdedness.values, color='orange')
    plt.title('Average Crowdedness Per Timeslot')
    plt.xlabel('Timeslot')
    plt.ylabel('Average Crowdedness Rating')
    plt.savefig(os.path.join(PLOT_DIR, "avg_crowdedness.png"))
    plt.close()

    # Plot 2: Frequency of Weekly Gym Visits
    visit_data = {
        "Frequency": ["0 - 2 times", "3 - 5 times", "More than 5 times"],
        "Count": [40, 35, 25]
    }
    visits_df = pd.DataFrame(visit_data)
    plt.figure(figsize=(8, 6))
    sns.barplot(x="Frequency", y="Count", data=visits_df, color="skyblue")
    plt.title("Frequency of Weekly Gym Visits")
    plt.xlabel("Weekly Visit Frequency")
    plt.ylabel("Number of Respondents")
    plt.savefig(os.path.join(PLOT_DIR, "weekly_visits.png"))
    plt.close()

    # Plot 3: Influence of Weather on Gym Attendance
    weather_data = {"Yes": 70, "No": 30}
    plt.figure(figsize=(8, 6))
    plt.pie(weather_data.values(), labels=weather_data.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Influence of Weather on Gym Attendance")
    plt.savefig(os.path.join(PLOT_DIR, "weather_influence.png"))
    plt.close()

# Generate visualizations when the app starts
create_visualizations()

# Function to find the best time and day
def find_best_time(user_days, user_timeslots):
    filtered_data = data[(data['Day'].isin(user_days)) & (data['Timeslots'].isin(user_timeslots))]
    if filtered_data.empty:
        filtered_data = data[data['Day'].isin(user_days)] if user_days else data
        if filtered_data.empty:
            filtered_data = data[data['Timeslots'].isin(user_timeslots)] if user_timeslots else data
    if filtered_data.empty:
        filtered_data = data
    avg_crowdedness_user_selection = (
        filtered_data.groupby(['Day', 'Timeslots'])['Crowdedness']
        .mean()
        .reset_index()
    )
    if avg_crowdedness_user_selection.empty:
        return None, None, None
    best_combination = avg_crowdedness_user_selection.loc[
        avg_crowdedness_user_selection['Crowdedness'].idxmin()
    ]
    return best_combination['Day'], best_combination['Timeslots'], best_combination['Crowdedness']

@app.route("/", methods=["GET", "POST"])
def index():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timeslots = ["6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM"]
    suggestion = None
    if request.method == "POST":
        selected_days = request.form.getlist("days")
        selected_timeslots = request.form.getlist("timeslots")
        user_days = selected_days if selected_days else days
        user_timeslots = selected_timeslots if selected_timeslots else timeslots
        best_day, best_timeslot, best_crowdedness = find_best_time(user_days, user_timeslots)
        if best_day and best_timeslot:
            suggestion = {"day": best_day, "timeslot": best_timeslot, "crowdedness": round(best_crowdedness, 2)}
        else:
            suggestion = "No matching data found."
    return render_template("index.html", days=days, timeslots=timeslots, suggestion=suggestion)

@app.route("/visualizations")
def visualizations():
    plots = [
        {"file": "avg_crowdedness.png", "desc": "Average crowdedness for each timeslot."},
        {"file": "weekly_visits.png", "desc": "Weekly visit frequency of gym attendees."},
        {"file": "weather_influence.png", "desc": "Impact of weather on gym attendance."},
        {"file": "attendants_per_timeslot.png", "desc": "Number of attendants per timeslot."},
        {"file": "exam_effect.png", "desc": "Effect of exams on gym visits."},
        {"file": "frequency_workout_days.png", "desc": "Frequency of workout days by respondents."}
    ]
    return render_template("visualizations.html", plots=plots)
@app.route("/predictions")
def predictions():
    # Model results from the notebook
    models = [
        {"name": "Logistic Regression", "accuracy": 0.54, "precision": 0.50, "recall": 0.50, "f1": 0.50},
        {"name": "Random Forest Classifier", "accuracy": 0.69, "precision": 0.67, "recall": 0.67, "f1": 0.67},
        {"name": "Gradient Boosting", "accuracy": 0.62, "precision": 0.57, "recall": 0.67, "f1": 0.62},
        {"name": "Support Vector Machine (SVM)", "accuracy": 0.73, "precision": 0.73, "recall": 0.73, "f1": 0.73},
        {"name": "K-Nearest Neighbors", "accuracy": 0.54, "precision": 0.54, "recall": 0.54, "f1": 0.54},
        {"name": "Neural Network", "accuracy": 0.69, "precision": 0.69, "recall": 0.69, "f1": 0.69},
    ]
    return render_template("predictions.html", models=models)


if __name__ == "__main__":
    app.run(debug=True)

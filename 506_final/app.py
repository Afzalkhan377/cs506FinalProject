from flask import Flask, render_template, request
import os
import pandas as pd

app = Flask(__name__)

# Sample DataFrame mimicking gym data
data = pd.DataFrame({
    'Timeslots': ["6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM",
                  "6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM"],
    'Crowdedness': [2, 3, 4, 5, 4, 3, 1, 2, 3, 4, 3, 2],
    'Day': ["Monday", "Monday", "Monday", "Monday", "Monday", "Monday",
            "Tuesday", "Tuesday", "Tuesday", "Tuesday", "Tuesday", "Tuesday"]
})

# Function to find the best time and day
def find_best_time(user_days, user_timeslots):
    # Filter data based on user-selected days and timeslots
    filtered_data = data[(data['Day'].isin(user_days)) & (data['Timeslots'].isin(user_timeslots))]
    
    # If no matches, expand the search to just user_days or user_timeslots
    if filtered_data.empty:
        filtered_data = data[data['Day'].isin(user_days)] if user_days else data
        if filtered_data.empty:
            filtered_data = data[data['Timeslots'].isin(user_timeslots)] if user_timeslots else data

    # If still no matches, use the entire dataset
    if filtered_data.empty:
        filtered_data = data

    # Calculate average crowdedness for each day and timeslot combination
    average_crowdedness_user_selection = (
        filtered_data.groupby(['Day', 'Timeslots'])['Crowdedness']
        .mean()
        .reset_index()
    )

    # Check if there are valid combinations
    if average_crowdedness_user_selection.empty:
        return None, None, None

    # Find the best combination
    best_combination = average_crowdedness_user_selection.loc[
        average_crowdedness_user_selection['Crowdedness'].idxmin()
    ]

    return best_combination['Day'], best_combination['Timeslots'], best_combination['Crowdedness']

@app.route("/", methods=["GET", "POST"])
def index():
    # List of available days and timeslots
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timeslots = ["6 AM to 9 AM", "9 AM to 12 PM", "12 PM to 3 PM", "3 PM to 6 PM", "6 PM to 9 PM", "9 PM to 11 PM"]

    suggestion = None

    if request.method == "POST":
        # Get user selections
        selected_days = request.form.getlist("days")
        selected_timeslots = request.form.getlist("timeslots")

        # Default to all data if no selections are made
        user_days = selected_days if selected_days else days
        user_timeslots = selected_timeslots if selected_timeslots else timeslots

        # Find the best time and day
        best_day, best_timeslot, best_crowdedness = find_best_time(user_days, user_timeslots)
        if best_day and best_timeslot:
            suggestion = {
                "day": best_day,
                "timeslot": best_timeslot,
                "crowdedness": round(best_crowdedness, 2)
            }
        else:
            suggestion = "No matching data found."

    return render_template(
        "index.html",
        days=days,
        timeslots=timeslots,
        suggestion=suggestion,
    )


if __name__ == "__main__":
    app.run(debug=True)

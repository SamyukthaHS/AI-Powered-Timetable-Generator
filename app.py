from flask import Flask, render_template, request
import random

app = Flask(__name__)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Step 1: Generate timetable function
def generate_timetable(teachers, teacher_subject_map, subjects, time_slots, classrooms, lunch_break_slot):
    # Initialize the timetable structure
    timetable = {day: {slot: None for slot in time_slots} for day in DAYS}

    # Assign teachers to their respective subjects
    for day in DAYS:
        for slot in time_slots:
            if slot == lunch_break_slot:
                timetable[day][slot] = "Lunch Break"
                continue

            # Select a random subject
            available_subjects = [
                subj for subj in subjects if subj["hours"] > 0
            ]
            if not available_subjects:
                continue

            # Select a subject and a teacher
            subject = random.choice(available_subjects)
            teacher = random.choice([
                t for t in teachers if subject["name"] in teacher_subject_map.get(t, [])
            ])

            # Assign the subject and teacher to the slot
            timetable[day][slot] = f"{subject['name']} - {teacher}"
            subject["hours"] -= 1

    return timetable

# Step 2: Index route for input and timetable generation
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Parse teacher names
            teachers = request.form["teachers"].split(",")

            # Parse time slots
            time_slots = request.form["time_slots"].split(",")

            # Parse classrooms
            classrooms = request.form["classrooms"].split(",")

            # Parse lunch break slot
            lunch_break_slot = request.form["lunch_break"]

            # Parse subjects
            subjects = []
            for i in range(len(request.form.getlist("subject_name"))):
                subject = {
                    "name": request.form.getlist("subject_name")[i].strip(),
                    "hours": int(request.form.getlist("subject_hours")[i]),
                    "is_lab": request.form.getlist("is_lab")[i].lower() == "yes",
                    "continuous_count": int(request.form.getlist("continuous_count")[i]),
                    "lab_classroom": request.form.getlist("lab_classroom")[i].strip() or None,
                }
                subjects.append(subject)

            # Parse teacher-subject mapping
            teacher_subject_map = {}
            teacher_names = request.form.getlist("teacher_name")
            teacher_subjects = request.form.getlist("teacher_subjects")

            for i in range(len(teacher_names)):
                teacher_subject_map[teacher_names[i].strip()] = [
                    subject.strip() for subject in teacher_subjects[i].split(",")
                ]

            # Generate timetable
            timetable = generate_timetable(
                teachers, teacher_subject_map, subjects, time_slots, classrooms, lunch_break_slot
            )

            # Pass generated timetable to template and ask if user wants to generate another
            return render_template(
                "timetable.html",
                timetable=timetable,
                time_slots=time_slots,
                regenerate=True
            )

        except Exception as e:
            return f"Error: {str(e)}", 400

    return render_template("index.html")

# Step 3: Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

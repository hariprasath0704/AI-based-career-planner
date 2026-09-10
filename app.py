import os
import json
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from models import db, User, StudentProfile, PlacementGoal, Subject, AcademicTask, Skill, StudentSkill, DailyPlan, Project, StudySession, Recommendation
from database_init import initialize_database, seed_sample_student
import recommendation as ai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pathpilot-super-secret-key-18273645'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pathpilot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize and seed database
with app.app_context():
    initialize_database(app)
    seed_sample_student(app)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_student():
    if 'user_id' not in session:
        return None
    user = db.session.get(User, session['user_id'])
    if not user:
        return None
    if not user.profile:
        # Create a default profile if missing
        profile = StudentProfile(user_id=user.id, name=user.username)
        db.session.add(profile)
        db.session.flush()
        
        goal = PlacementGoal(student_profile_id=profile.id)
        db.session.add(goal)
        
        # Link all preseeded skills
        skills = Skill.query.all()
        for s in skills:
            ss = StudentSkill(student_profile_id=profile.id, skill_id=s.id, status='Not Started')
            db.session.add(ss)
            
        db.session.commit()
    return user.profile

@app.context_processor
def inject_student_context():
    student = get_current_student()
    return dict(
        student=student,
        current_student=student,
        streak_count=student.streak if student else 0
    )

def update_streak(profile):
    today = date.today()
    if profile.last_active == today:
        return
    elif profile.last_active == today - timedelta(days=1):
        profile.streak += 1
    else:
        # If they missed a day, streak resets to 1
        profile.streak = 1
    profile.last_active = today
    db.session.commit()

# Context processor to expose profile details (streak, completed tasks count) to sidebar layout
@app.context_processor
def inject_student():
    if 'user_id' in session:
        student = get_current_student()
        if student:
            # Count completed academic tasks
            comp_tasks = AcademicTask.query.filter_by(student_profile_id=student.id, completion_pct=100).count()
            # Count completed skills
            comp_skills = StudentSkill.query.filter_by(student_profile_id=student.id, status='Completed').count()
            return {
                'current_student': student,
                'streak_count': student.streak,
                'completed_tasks_count': comp_tasks,
                'completed_skills_count': comp_skills
            }
    return {}

# 1. AUTH ROUTES
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('login.html', register=True)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('login.html', register=True)
            
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already exists.', 'danger')
            return render_template('login.html', register=True)
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        session['user_id'] = user.id
        flash('Account registered successfully! Please set up your student profile.', 'success')
        return redirect(url_for('profile_setup'))
        
    return render_template('login.html', register=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            student = get_current_student()
            update_streak(student)
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html', register=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# 2. MAIN ROUTES
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    student = get_current_student()
    update_streak(student)
    
    # Calculate placement score & weak areas
    readiness_score, breakdown, weak_areas = ai.calculate_readiness_score(student)
    
    # Total tasks progress
    all_tasks = student.tasks
    pending_tasks = [t for t in all_tasks if t.completion_pct < 100]
    completed_tasks = [t for t in all_tasks if t.completion_pct == 100]
    
    # Roadmap skills breakdown
    skills = student.skills
    comp_skills_count = sum(1 for s in skills if s.status == 'Completed')
    pract_skills_count = sum(1 for s in skills if s.status == 'Practicing')
    learn_skills_count = sum(1 for s in skills if s.status == 'Learning')
    total_skills = len(skills)
    
    # Top upcoming academic deadlines (within next 7 days)
    today = date.today()
    upcoming_tasks = [t for t in pending_tasks if t.deadline >= today]
    upcoming_tasks.sort(key=lambda t: t.deadline)
    
    # Active daily schedule for today
    todays_plan = DailyPlan.query.filter_by(student_profile_id=student.id, date=today).all()
    
    return render_template('dashboard.html',
                           student=student,
                           readiness_score=readiness_score,
                           breakdown=breakdown,
                           weak_areas=weak_areas[:3],
                           pending_tasks=pending_tasks,
                           completed_tasks=completed_tasks,
                           upcoming_tasks=upcoming_tasks[:4],
                           todays_plan=todays_plan,
                           comp_skills_count=comp_skills_count,
                           pract_skills_count=pract_skills_count,
                           learn_skills_count=learn_skills_count,
                           total_skills=total_skills)

# 3. "WHAT SHOULD I DO NOW" API
@app.route('/api/what-should-i-do-now')
@login_required
def what_should_i_do_now():
    student = get_current_student()
    rec = ai.get_what_should_i_do_now(student)
    return jsonify(rec)


# 4. PROFILE ROUTE
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_setup():
    student = get_current_student()
    goals = student.goals
    
    if request.method == 'POST':
        # Update profile
        student.name = request.form.get('name', '').strip()
        student.department = request.form.get('department', '').strip()
        student.year = int(request.form.get('year', 1))
        student.semester = int(request.form.get('semester', 1))
        student.cgpa = float(request.form.get('cgpa', 0.0))
        student.arrears = int(request.form.get('arrears', 0))
        student.daily_available_hours = float(request.form.get('daily_available_hours', 2.0))
        
        # Update goal
        if not goals:
            goals = PlacementGoal(student_profile_id=student.id)
            db.session.add(goals)
        goals.target_role = request.form.get('target_role', '').strip()
        goals.target_company = request.form.get('target_company', '').strip()
        goals.target_salary = float(request.form.get('target_salary', 0.0) or 0.0)
        
        db.session.commit()
        flash('Student profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('profile.html', student=student, goals=goals)


# 5. ACADEMIC PLANNER ROUTES
@app.route('/academics', methods=['GET', 'POST'])
@login_required
def academics():
    student = get_current_student()
    
    # Handlers for adding custom subjects
    if request.method == 'POST' and 'add_subject' in request.form:
        subject_name = request.form.get('subject_name', '').strip()
        credits = int(request.form.get('credits', 3))
        target_grade = request.form.get('target_grade', 'A')
        
        if subject_name:
            # Check duplicates
            exists = Subject.query.filter_by(student_profile_id=student.id, name=subject_name).first()
            if not exists:
                subj = Subject(
                    student_profile_id=student.id,
                    name=subject_name,
                    progress_pct=0.0,
                    credits=credits,
                    target_grade=target_grade
                )
                db.session.add(subj)
                db.session.commit()
                flash(f'Subject "{subject_name}" added!', 'success')
            else:
                flash('Subject already exists.', 'warning')
        return redirect(url_for('academics'))
        
    # Handler for adding custom task
    if request.method == 'POST' and 'add_task' in request.form:
        subject_id = request.form.get('subject_id')
        topic = request.form.get('topic', '').strip()
        task_type = request.form.get('task_type', 'Study')
        deadline_str = request.form.get('deadline', '')
        difficulty = int(request.form.get('difficulty', 3))
        importance = int(request.form.get('importance', 3))
        
        if not topic or not deadline_str:
            flash('Topic and Deadline are required for the task.', 'danger')
            return redirect(url_for('academics'))
            
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        
        # Calculate dynamic priority score
        today = date.today()
        days_rem = (deadline - today).days
        urgency = max(0, 10 - days_rem) if days_rem >= 0 else 12
        priority_score = float(urgency + difficulty * 1.5 + importance * 1.5)

        task = AcademicTask(
            student_profile_id=student.id,
            subject_id=subject_id if subject_id else None,
            topic=topic,
            task_type=task_type,
            deadline=deadline,
            difficulty=difficulty,
            importance=importance,
            completion_pct=0,
            priority_score=priority_score
        )
        db.session.add(task)
        db.session.commit()
        
        # Re-evaluate subject progress percentage
        if subject_id:
            recalculate_subject_progress(subject_id)
            
        flash('Academic task added successfully!', 'success')
        return redirect(url_for('academics'))
        
    # List tasks and calculate priority category (High/Medium/Low)
    subjects = Subject.query.filter_by(student_profile_id=student.id).all()
    tasks = AcademicTask.query.filter_by(student_profile_id=student.id).all()
    
    # Dynamically sort tasks into priority lists based on score
    high_priority = []
    med_priority = []
    low_priority = []
    today = date.today()
    
    for t in tasks:
        # Calculate days remaining for template display
        t.days_remaining = (t.deadline - today).days
        
        # Re-calculate priority score
        days_rem = t.days_remaining
        urgency = max(0, 10 - days_rem) if days_rem >= 0 else 12
        work_rem = ((100 - t.completion_pct) / 100.0) * 8
        t.priority_score = float(urgency + t.difficulty * 1.5 + t.importance * 1.5 + work_rem)
        
        if t.completion_pct == 100:
            # Done
            continue
            
        if t.priority_score >= 18.0:
            high_priority.append(t)
        elif t.priority_score >= 12.0:
            med_priority.append(t)
        else:
            low_priority.append(t)
            
    # Sort lists
    high_priority.sort(key=lambda x: x.priority_score, reverse=True)
    med_priority.sort(key=lambda x: x.priority_score, reverse=True)
    low_priority.sort(key=lambda x: x.priority_score, reverse=True)
    
    return render_template('academics.html',
                           subjects=subjects,
                           high_priority=high_priority,
                           med_priority=med_priority,
                           low_priority=low_priority,
                           all_tasks=tasks,
                           today=today)

@app.route('/academics/subject/update/<int:subject_id>', methods=['POST'])
@login_required
def update_subject(subject_id):
    student = get_current_student()
    subj = Subject.query.filter_by(id=subject_id, student_profile_id=student.id).first()
    if subj:
        prog = float(request.form.get('progress_pct', subj.progress_pct))
        subj.progress_pct = max(0.0, min(100.0, prog))
        subj.credits = int(request.form.get('credits', subj.credits))
        subj.target_grade = request.form.get('target_grade', subj.target_grade)
        db.session.commit()
        flash(f'Subject "{subj.name}" updated!', 'success')
    return redirect(url_for('academics'))

@app.route('/academics/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    student = get_current_student()
    subj = Subject.query.filter_by(id=subject_id, student_profile_id=student.id).first()
    if subj:
        db.session.delete(subj)
        db.session.commit()
        flash('Subject deleted.', 'info')
    return redirect(url_for('academics'))

@app.route('/academics/task/log-study/<int:task_id>', methods=['POST'])
@login_required
def log_task_study(task_id):
    student = get_current_student()
    minutes = int(request.form.get('minutes', 30))
    task = AcademicTask.query.filter_by(id=task_id, student_profile_id=student.id).first()
    if task:
        add_pct = int((minutes / 30.0) * 20)
        task.completion_pct = min(100, task.completion_pct + add_pct)
        
        sess = StudySession(
            student_profile_id=student.id,
            subject_id=task.subject_id,
            date=date.today(),
            duration_minutes=minutes
        )
        db.session.add(sess)
        db.session.commit()
        
        if task.subject_id:
            recalculate_subject_progress(task.subject_id)
            
        flash(f'Logged {minutes}m study session for "{task.topic}"! Task progress: {task.completion_pct}%.', 'success')
    return redirect(url_for('academics'))

@app.route('/academics/task/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    student = get_current_student()
    task = AcademicTask.query.filter_by(id=task_id, student_profile_id=student.id).first()
    
    if task:
        task.completion_pct = 100
        # Log study session automatically
        duration = 45 if task.difficulty <= 2 else (60 if task.difficulty <= 4 else 90)
        session_log = StudySession(
            student_profile_id=student.id,
            subject_id=task.subject_id,
            date=date.today(),
            duration_minutes=duration
        )
        db.session.add(session_log)
        db.session.commit()
        
        if task.subject_id:
            recalculate_subject_progress(task.subject_id)
            
        flash(f'Task "{task.topic}" completed! Logged a {duration}m study session.', 'success')
    return redirect(url_for('academics'))

@app.route('/academics/task/update-progress', methods=['POST'])
@login_required
def update_task_progress():
    student = get_current_student()
    task_id = request.form.get('task_id')
    progress = int(request.form.get('progress_pct', 0))
    
    task = AcademicTask.query.filter_by(id=task_id, student_profile_id=student.id).first()
    if task:
        task.completion_pct = max(0, min(100, progress))
        db.session.commit()
        if task.subject_id:
            recalculate_subject_progress(task.subject_id)
        flash(f'Updated "{task.topic}" progress to {progress}%.', 'success')
    return redirect(url_for('academics'))

@app.route('/academics/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    student = get_current_student()
    task = AcademicTask.query.filter_by(id=task_id, student_profile_id=student.id).first()
    if task:
        sub_id = task.subject_id
        db.session.delete(task)
        db.session.commit()
        if sub_id:
            recalculate_subject_progress(sub_id)
        flash('Task deleted.', 'info')
    return redirect(url_for('academics'))

def recalculate_subject_progress(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        return
    tasks = AcademicTask.query.filter_by(subject_id=subject_id).all()
    if not tasks:
        subject.progress_pct = 0.0
    else:
        subject.progress_pct = sum(t.completion_pct for t in tasks) / len(tasks)
    db.session.commit()


# 6. SKILL ROADMAP ROUTE
@app.route('/skills')
@login_required
def skills():
    student = get_current_student()
    # List skills by category
    student_skills = StudentSkill.query.filter_by(student_profile_id=student.id).all()
    
    # Categorize skills for roadmap visualization
    roadmap = {
        'Programming': [],
        'Core CS': [],
        'Development': [],
        'AIML': [],
        'Placement': []
    }
    
    for ss in student_skills:
        cat = ss.skill.category
        if cat in roadmap:
            roadmap[cat].append(ss)
            
    return render_template('skills.html', roadmap=roadmap)

@app.route('/api/skills/update', methods=['POST'])
@login_required
def update_skill_status():
    student = get_current_student()
    data = request.json
    skill_id = data.get('skill_id')
    new_status = data.get('status')
    
    if new_status not in ['Not Started', 'Learning', 'Practicing', 'Completed']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
    s_skill = StudentSkill.query.filter_by(student_profile_id=student.id, skill_id=skill_id).first()
    if s_skill:
        old_status = s_skill.status
        s_skill.status = new_status
        
        # Log study session if marked completed/practicing
        if new_status in ['Practicing', 'Completed'] and old_status != new_status:
            duration = 30 if new_status == 'Practicing' else 60
            session_log = StudySession(
                student_profile_id=student.id,
                skill_id=skill_id,
                date=date.today(),
                duration_minutes=duration
            )
            db.session.add(session_log)
            
        db.session.commit()
        return jsonify({'success': True, 'new_status': new_status})
    return jsonify({'success': False, 'error': 'Skill mapping not found'}), 404


# 7. DAILY PLANNER ROUTES
@app.route('/planner', methods=['GET', 'POST'])
@login_required
def planner():
    student = get_current_student()
    today = date.today()
    
    # Handle save or request generation
    if request.method == 'POST':
        hours = float(request.form.get('available_hours', student.daily_available_hours))
        
        # Update profile preference
        student.daily_available_hours = hours
        db.session.commit()
        
        # Generate new daily plans
        generated_slots = ai.generate_daily_schedule(student, hours)
        
        # Clear existing daily plan for today
        DailyPlan.query.filter_by(student_profile_id=student.id, date=today).delete()
        
        # Write to db
        for slot in generated_slots:
            dp = DailyPlan(
                student_profile_id=student.id,
                date=today,
                time_slot=slot['time_slot'],
                activity=slot['activity'],
                task_id=slot['task_id'],
                skill_id=slot['skill_id'],
                is_completed=False
            )
            db.session.add(dp)
        db.session.commit()
        flash('Daily study schedule dynamically generated and saved for today!', 'success')
        return redirect(url_for('planner'))

    todays_plan = DailyPlan.query.filter_by(student_profile_id=student.id, date=today).all()
    return render_template('planner.html', todays_plan=todays_plan, available_hours=student.daily_available_hours)

@app.route('/api/planner/complete/<int:plan_id>', methods=['POST'])
@login_required
def complete_plan_slot(plan_id):
    student = get_current_student()
    plan = DailyPlan.query.filter_by(id=plan_id, student_profile_id=student.id).first()
    
    if plan:
        plan.is_completed = True
        
        # Create study session duration automatically
        # Extract slot minutes
        try:
            # Example time slot: "05:00 PM - 05:45 PM"
            times = plan.time_slot.split(' - ')
            t1 = datetime.strptime(times[0], "%I:%M %p")
            t2 = datetime.strptime(times[1], "%I:%M %p")
            delta = t2 - t1
            duration = int(delta.seconds / 60)
        except Exception:
            duration = 45 # Default to 45 mins
            
        session_log = StudySession(
            student_profile_id=student.id,
            subject_id=plan.task.subject_id if plan.task else None,
            skill_id=plan.skill_id,
            date=date.today(),
            duration_minutes=duration
        )
        
        # If linked to an academic task, update its progress slightly
        if plan.task:
            plan.task.completion_pct = min(100, plan.task.completion_pct + 25)
            if plan.task.subject_id:
                recalculate_subject_progress(plan.task.subject_id)
                
        # If linked to a skill, elevate status from Not Started -> Learning -> Practicing -> Completed
        if plan.skill_id:
            s_skill = StudentSkill.query.filter_by(student_profile_id=student.id, skill_id=plan.skill_id).first()
            if s_skill:
                status_chain = {'Not Started': 'Learning', 'Learning': 'Practicing', 'Practicing': 'Completed', 'Completed': 'Completed'}
                s_skill.status = status_chain.get(s_skill.status, 'Completed')

        db.session.add(session_log)
        db.session.commit()
        return jsonify({'success': True, 'duration': duration})
    return jsonify({'success': False, 'error': 'Schedule item not found'}), 404


# 8. PROJECTS TRACKER ROUTE
@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    student = get_current_student()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        tech = request.form.get('technology', '').strip()
        desc = request.form.get('description', '').strip()
        git = request.form.get('github_link', '').strip()
        demo = request.form.get('live_demo_link', '').strip()
        status = request.form.get('status', 'In Progress')
        comp = int(request.form.get('completion_pct', 0))
        
        if not name:
            flash('Project name is required.', 'danger')
            return redirect(url_for('projects'))
            
        default_milestones = [
            {"title": "Setup Repository & System Architecture", "completed": True},
            {"title": "Implement Core Modules & API Routes", "completed": comp >= 50},
            {"title": "Testing, Deployment & Documentation", "completed": comp == 100}
        ]
            
        proj = Project(
            student_profile_id=student.id,
            name=name,
            technology=tech,
            description=desc,
            github_link=git,
            live_demo_link=demo,
            status=status,
            completion_pct=comp,
            start_date=date.today(),
            milestones_json=json.dumps(default_milestones)
        )
        db.session.add(proj)
        db.session.commit()
        flash(f'Project "{name}" added successfully!', 'success')
        return redirect(url_for('projects'))
        
    # Job-specific AI recommended projects
    target_role = student.goals.target_role if student.goals else "Software Engineer"
    recommended_projs = ai.get_project_recommendations(target_role)
    
    # Parse milestones for each project
    parsed_projects = []
    for p in student.projects:
        try:
            p.milestones = json.loads(p.milestones_json or '[]')
        except Exception:
            p.milestones = []
        parsed_projects.append(p)
    
    return render_template('projects.html', projects=parsed_projects, recommendations=recommended_projs)

@app.route('/projects/adopt-blueprint', methods=['POST'])
@login_required
def adopt_blueprint():
    student = get_current_student()
    title = request.form.get('name', '').strip()
    tech = request.form.get('tech', '').strip()
    desc = request.form.get('desc', '').strip()
    
    if title:
        default_milestones = [
            {"title": "Setup Repository & Dev Environment", "completed": False},
            {"title": "Build Backend Models & Logic", "completed": False},
            {"title": "Develop Responsive User Interface", "completed": False},
            {"title": "Write README & Deploy Demonstration", "completed": False}
        ]
        proj = Project(
            student_profile_id=student.id,
            name=title,
            technology=tech,
            description=desc,
            github_link='',
            live_demo_link='',
            status='In Progress',
            completion_pct=0,
            start_date=date.today(),
            milestones_json=json.dumps(default_milestones)
        )
        db.session.add(proj)
        db.session.commit()
        flash(f'Adopted blueprint "{title}" into your active portfolio!', 'success')
        
    return redirect(url_for('projects'))

@app.route('/projects/update/<int:project_id>', methods=['POST'])
@login_required
def update_project(project_id):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_profile_id=student.id).first()
    if proj:
        proj.name = request.form.get('name', proj.name).strip()
        proj.technology = request.form.get('technology', proj.technology).strip()
        proj.description = request.form.get('description', proj.description).strip()
        proj.github_link = request.form.get('github_link', proj.github_link).strip()
        proj.live_demo_link = request.form.get('live_demo_link', proj.live_demo_link).strip()
        proj.status = request.form.get('status', proj.status)
        comp = int(request.form.get('completion_pct', proj.completion_pct))
        proj.completion_pct = max(0, min(100, comp))
        db.session.commit()
        flash(f'Project "{proj.name}" updated!', 'success')
    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>/milestone/add', methods=['POST'])
@login_required
def add_milestone(project_id):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_profile_id=student.id).first()
    title = request.form.get('milestone_title', '').strip()
    if proj and title:
        try:
            milestones = json.loads(proj.milestones_json or '[]')
        except Exception:
            milestones = []
        milestones.append({"title": title, "completed": False})
        
        # Recalculate completion pct
        done = sum(1 for m in milestones if m.get('completed'))
        proj.completion_pct = int((done / len(milestones)) * 100)
        proj.milestones_json = json.dumps(milestones)
        db.session.commit()
        flash('Milestone added!', 'success')
    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>/milestone/toggle/<int:m_idx>', methods=['POST'])
@login_required
def toggle_milestone(project_id, m_idx):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_profile_id=student.id).first()
    if proj:
        try:
            milestones = json.loads(proj.milestones_json or '[]')
        except Exception:
            milestones = []
        if 0 <= m_idx < len(milestones):
            milestones[m_idx]['completed'] = not milestones[m_idx].get('completed', False)
            
            # Recalculate completion pct
            if len(milestones) > 0:
                done = sum(1 for m in milestones if m.get('completed'))
                proj.completion_pct = int((done / len(milestones)) * 100)
                if proj.completion_pct == 100:
                    proj.status = 'Completed'
            
            proj.milestones_json = json.dumps(milestones)
            db.session.commit()
    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>/milestone/delete/<int:m_idx>', methods=['POST'])
@login_required
def delete_milestone(project_id, m_idx):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_profile_id=student.id).first()
    if proj:
        try:
            milestones = json.loads(proj.milestones_json or '[]')
        except Exception:
            milestones = []
        if 0 <= m_idx < len(milestones):
            milestones.pop(m_idx)
            if len(milestones) > 0:
                done = sum(1 for m in milestones if m.get('completed'))
                proj.completion_pct = int((done / len(milestones)) * 100)
            proj.milestones_json = json.dumps(milestones)
            db.session.commit()
    return redirect(url_for('projects'))

@app.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_profile_id=student.id).first()
    if proj:
        db.session.delete(proj)
        db.session.commit()
        flash('Project deleted.', 'info')
    return redirect(url_for('projects'))


# 9. RESUME TRACKER ROUTE
@app.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    student = get_current_student()
    goals = student.goals
    
    if not goals:
        goals = PlacementGoal(student_profile_id=student.id)
        db.session.add(goals)
        db.session.commit()

    if request.method == 'POST':
        # Checklist keys
        checklist_items = ['Summary', 'Education', 'Work', 'Projects', 'Skills']
        resume_dict = {}
        for item in checklist_items:
            resume_dict[item] = True if request.form.get(item) == 'on' else False
            
        # Calculate Resume Score (out of 100)
        items_checked = sum(1 for v in resume_dict.values() if v)
        goals.resume_score = int((items_checked / len(checklist_items)) * 100)
        goals.resume_json = json.dumps(resume_dict)
        db.session.commit()
        flash('Resume checklist status updated!', 'success')
        return redirect(url_for('resume'))
        
    resume_data = {}
    try:
        resume_data = json.loads(goals.resume_json or '{}')
    except Exception:
        pass
        
    return render_template('resume.html', goals=goals, resume_data=resume_data)


# 10. AI RECOMMENDATIONS PAGE
@app.route('/recommendations')
@login_required
def recommendations():
    student = get_current_student()
    recs = ai.get_ai_recommendations(student)
    return render_template('recommendations.html', recs=recs)


# 11. ANALYTICS & LOGGING ROUTES
@app.route('/analytics')
@login_required
def analytics():
    student = get_current_student()
    subjects = Subject.query.filter_by(student_profile_id=student.id).all()
    skills = StudentSkill.query.filter_by(student_profile_id=student.id).all()
    return render_template('analytics.html', subjects=subjects, skills=skills)

@app.route('/api/study/log', methods=['POST'])
@login_required
def log_study_session():
    student = get_current_student()
    subj_id = request.form.get('subject_id')
    skill_id = request.form.get('skill_id')
    duration = int(request.form.get('duration_minutes', 0))
    
    if duration <= 0:
        flash('Please enter a valid study duration.', 'danger')
        return redirect(url_for('analytics'))
        
    session_log = StudySession(
        student_profile_id=student.id,
        subject_id=int(subj_id) if subj_id else None,
        skill_id=int(skill_id) if skill_id else None,
        date=date.today(),
        duration_minutes=duration
    )
    db.session.add(session_log)
    
    # Dynamic streak increase
    update_streak(student)
    db.session.commit()
    flash(f'Logged {duration} minutes of study session. Keep the streak active!', 'success')
    return redirect(url_for('analytics'))

@app.route('/api/analytics/data')
@login_required
def analytics_data():
    student = get_current_student()
    
    # 1. Study hours last 7 days
    today = date.today()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    days_labels = [d.strftime("%a") for d in days]
    
    study_hours_data = []
    for d in days:
        sessions_on_day = StudySession.query.filter_by(student_profile_id=student.id, date=d).all()
        total_mins = sum(s.duration_minutes for s in sessions_on_day)
        study_hours_data.append(round(total_mins / 60.0, 2))

    # 2. Skill categories progress
    categories = ['Programming', 'Core CS', 'Development', 'AIML', 'Placement']
    skills = student.skills
    cat_counts = {cat: 0 for cat in categories}
    cat_completed = {cat: 0 for cat in categories}
    
    for s in skills:
        cat = s.skill.category
        if cat in cat_counts:
            cat_counts[cat] += 1
            if s.status == 'Completed':
                cat_completed[cat] += 1
                
    cat_growth_data = []
    for cat in categories:
        pct = (cat_completed[cat] / cat_counts[cat] * 100) if cat_counts[cat] > 0 else 0
        cat_growth_data.append(round(pct, 1))

    # 3. Subject Progress Data
    subjects = student.subjects
    subject_names = [sub.name for sub in subjects]
    subject_progress = [sub.progress_pct for sub in subjects]

    # 4. Placement score history mockup over 6 weeks
    readiness_score, _, _ = ai.calculate_readiness_score(student)
    # Generate static historic growth ending with current score
    readiness_over_time = [
        max(20.0, readiness_score - 30.0),
        max(25.0, readiness_score - 20.0),
        max(35.0, readiness_score - 15.0),
        max(45.0, readiness_score - 8.0),
        max(50.0, readiness_score - 3.0),
        readiness_score
    ]
    weeks_labels = ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Today']

    return jsonify({
        'days_labels': days_labels,
        'study_hours': study_hours_data,
        'skill_categories': categories,
        'skill_progress': cat_growth_data,
        'subject_names': subject_names,
        'subject_progress': subject_progress,
        'weeks_labels': weeks_labels,
        'readiness_history': readiness_over_time
    })

# 12. DOWNLOAD REPORT ROUTE
@app.route('/download-report')
@login_required
def download_report():
    report_path = os.path.join(app.root_path, 'PROJECT_REPORT.md')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True, download_name='PathPilot_Project_Report.md')
    flash('Project report file not found.', 'warning')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    import sys
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    
    # Run server on selected port
    app.run(debug=True, port=port)

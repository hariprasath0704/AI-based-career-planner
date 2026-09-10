from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships
    profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), default='Computer Science')
    year = db.Column(db.Integer, default=1)
    semester = db.Column(db.Integer, default=1)
    cgpa = db.Column(db.Float, default=0.0)
    arrears = db.Column(db.Integer, default=0)
    daily_available_hours = db.Column(db.Float, default=2.0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, default=datetime.utcnow().date)

    # Relationships
    goals = db.relationship('PlacementGoal', backref='student', uselist=False, cascade="all, delete-orphan")
    subjects = db.relationship('Subject', backref='student', cascade="all, delete-orphan")
    tasks = db.relationship('AcademicTask', backref='student', cascade="all, delete-orphan")
    skills = db.relationship('StudentSkill', backref='student', cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='student', cascade="all, delete-orphan")
    sessions = db.relationship('StudySession', backref='student', cascade="all, delete-orphan")
    recommendations = db.relationship('Recommendation', backref='student', cascade="all, delete-orphan")
    daily_plans = db.relationship('DailyPlan', backref='student', cascade="all, delete-orphan")


class PlacementGoal(db.Model):
    __tablename__ = 'placement_goals'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    target_role = db.Column(db.String(100), default='Software Engineer')
    target_company = db.Column(db.String(100), default='Any')
    target_salary = db.Column(db.Float, default=500000.0)  # in annual currency
    resume_score = db.Column(db.Integer, default=0)
    resume_json = db.Column(db.Text, default='{}')  # stores checklist items: education, work, projects, summary, format, etc.


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    progress_pct = db.Column(db.Float, default=0.0)
    credits = db.Column(db.Integer, default=3)
    target_grade = db.Column(db.String(10), default='A')
    
    tasks = db.relationship('AcademicTask', backref='subject', cascade="all, delete-orphan")


class AcademicTask(db.Model):
    __tablename__ = 'academic_tasks'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=True)
    topic = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), default='Study')  # Assignment, Exam, Revision, Practical
    deadline = db.Column(db.Date, nullable=False)
    difficulty = db.Column(db.Integer, default=3)  # Scale 1-5
    completion_pct = db.Column(db.Integer, default=0)  # 0 to 100
    importance = db.Column(db.Integer, default=3)  # Scale 1-5
    priority_score = db.Column(db.Float, default=0.0)


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Programming, Core CS, Development, AIML, Placement


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), default='Not Started')  # Not Started, Learning, Practicing, Completed

    # Relationship to ease skill queries
    skill = db.relationship('Skill')


class DailyPlan(db.Model):
    __tablename__ = 'daily_plans'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)  # "05:00 - 05:45"
    activity = db.Column(db.String(200), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('academic_tasks.id', ondelete='SET NULL'), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    technology = db.Column(db.String(100))
    description = db.Column(db.Text)
    github_link = db.Column(db.String(200))
    live_demo_link = db.Column(db.String(200))
    status = db.Column(db.String(50), default='In Progress')  # Idea, In Progress, Testing, Completed
    completion_pct = db.Column(db.Integer, default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    milestones_json = db.Column(db.Text, default='[]')  # stores json list of milestones


class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    recommendation_type = db.Column(db.String(50))  # DailyTask, WeeklyPlan, SkillGap, NextTopic
    priority = db.Column(db.String(20))  # High, Medium, Low
    priority_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.Date, default=datetime.utcnow().date)

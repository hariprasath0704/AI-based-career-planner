import sys
from datetime import datetime, timedelta, date
from flask import Flask
from models import db, User, StudentProfile, PlacementGoal, Subject, AcademicTask, Skill, StudentSkill, Project, StudySession, DailyPlan

SKILLS_SEED = [
    # Programming
    {"name": "Python/Java", "category": "Programming"},
    {"name": "OOP", "category": "Programming"},
    {"name": "Arrays", "category": "Programming"},
    {"name": "Strings", "category": "Programming"},
    {"name": "Linked Lists", "category": "Programming"},
    {"name": "Stack", "category": "Programming"},
    {"name": "Queue", "category": "Programming"},
    {"name": "Trees", "category": "Programming"},
    {"name": "Graphs", "category": "Programming"},
    {"name": "Dynamic Programming", "category": "Programming"},
    
    # Core CS
    {"name": "DBMS", "category": "Core CS"},
    {"name": "Operating Systems", "category": "Core CS"},
    {"name": "Computer Networks", "category": "Core CS"},
    {"name": "Software Engineering", "category": "Core CS"},
    
    # Development
    {"name": "HTML", "category": "Development"},
    {"name": "CSS", "category": "Development"},
    {"name": "JavaScript", "category": "Development"},
    {"name": "Git/GitHub", "category": "Development"},
    {"name": "Backend", "category": "Development"},
    {"name": "APIs", "category": "Development"},
    
    # AIML
    {"name": "Python", "category": "AIML"},
    {"name": "NumPy", "category": "AIML"},
    {"name": "Pandas", "category": "AIML"},
    {"name": "Matplotlib", "category": "AIML"},
    {"name": "Machine Learning", "category": "AIML"},
    {"name": "Deep Learning", "category": "AIML"},
    {"name": "NLP", "category": "AIML"},
    {"name": "Projects", "category": "AIML"},
    
    # Placement
    {"name": "Aptitude", "category": "Placement"},
    {"name": "Logical Reasoning", "category": "Placement"},
    {"name": "Coding", "category": "Placement"},
    {"name": "Resume", "category": "Placement"},
    {"name": "Technical Interview", "category": "Placement"},
    {"name": "HR Interview", "category": "Placement"},
    {"name": "Mock Interviews", "category": "Placement"}
]

def initialize_database(app):
    with app.app_context():
        db.create_all()
        
        # Ensure SQLite table column migrations
        from sqlalchemy import text
        try:
            with db.engine.connect() as conn:
                # Subjects
                res = conn.execute(text("PRAGMA table_info(subjects);")).fetchall()
                cols = [r[1] for r in res]
                if 'credits' not in cols:
                    conn.execute(text("ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3;"))
                if 'target_grade' not in cols:
                    conn.execute(text("ALTER TABLE subjects ADD COLUMN target_grade VARCHAR(10) DEFAULT 'A';"))
                
                # Projects
                res = conn.execute(text("PRAGMA table_info(projects);")).fetchall()
                cols = [r[1] for r in res]
                if 'live_demo_link' not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN live_demo_link VARCHAR(200);"))
                if 'status' not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR(50) DEFAULT 'In Progress';"))
                if 'milestones_json' not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN milestones_json TEXT DEFAULT '[]';"))
                conn.commit()
        except Exception as e:
            print("DB migration check notice:", e)

        # Check if skills are already seeded
        if Skill.query.count() == 0:
            print("Seeding skills metadata...")
            for s in SKILLS_SEED:
                skill = Skill(name=s["name"], category=s["category"])
                db.session.add(skill)
            db.session.commit()
            print("Skills metadata seeded successfully!")
        else:
            print("Skills metadata already exists.")

def seed_sample_student(app):
    with app.app_context():
        # Check if a sample student already exists
        if User.query.filter_by(username='student').first() is not None:
            print("Sample student 'student' already exists. Skipping student seeding.")
            return

        print("Seeding sample student data...")
        # Create User
        user = User(username='student', email='student@pathpilot.edu')
        user.set_password('student123')
        db.session.add(user)
        db.session.flush() # Populate user.id
        
        # Create StudentProfile
        profile = StudentProfile(
            user_id=user.id,
            name="Hari Prasad",
            department="Computer Science & Engineering",
            year=3,
            semester=5,
            cgpa=8.2,
            arrears=0,
            daily_available_hours=3.5,
            streak=5,
            last_active=date.today() - timedelta(days=1)
        )
        db.session.add(profile)
        db.session.flush() # Populate profile.id
        
        # Create PlacementGoal
        goal = PlacementGoal(
            student_profile_id=profile.id,
            target_role="Software Engineer",
            target_company="Google",
            target_salary=1800000.0,
            resume_score=60,
            resume_json='{"Summary": true, "Education": true, "Work": false, "Projects": true, "Skills": false}'
        )
        db.session.add(goal)
        
        # Link skills with statuses matching the example description
        # (weak Java Arrays and upcoming DBMS exam, some completed skills)
        skills = Skill.query.all()
        for s in skills:
            status = 'Not Started'
            if s.category == 'Programming':
                if s.name in ['Python/Java', 'OOP']:
                    status = 'Completed'
                elif s.name in ['Arrays']:
                    status = 'Learning'  # Weak Java/Python Arrays
                elif s.name in ['Strings', 'Linked Lists']:
                    status = 'Practicing'
            elif s.category == 'Core CS':
                if s.name in ['DBMS', 'Software Engineering']:
                    status = 'Learning' # Needs work
                elif s.name in ['Operating Systems']:
                    status = 'Practicing'
            elif s.category == 'Development':
                if s.name in ['HTML', 'CSS']:
                    status = 'Completed'
                elif s.name in ['Git/GitHub']:
                    status = 'Practicing'
            elif s.category == 'AIML':
                if s.name in ['Python']:
                    status = 'Completed'
                elif s.name in ['NumPy', 'Pandas']:
                    status = 'Learning'
            elif s.category == 'Placement':
                if s.name in ['Aptitude', 'Resume']:
                    status = 'Practicing'
                    
            ss = StudentSkill(student_profile_id=profile.id, skill_id=s.id, status=status)
            db.session.add(ss)
            
        # Create Sample Subjects
        dbms = Subject(student_profile_id=profile.id, name="Database Management Systems", progress_pct=40.0)
        dsa = Subject(student_profile_id=profile.id, name="Data Structures & Algorithms", progress_pct=60.0)
        ml_sub = Subject(student_profile_id=profile.id, name="Machine Learning Essentials", progress_pct=25.0)
        db.session.add_all([dbms, dsa, ml_sub])
        db.session.flush()
        
        # Create Sample Academic Tasks
        t1 = AcademicTask(
            student_profile_id=profile.id,
            subject_id=dbms.id,
            topic="SQL Joins & Subqueries",
            task_type="Revision",
            deadline=date.today() + timedelta(days=2),
            difficulty=4, # Hard
            completion_pct=40, # DBMS exam approaching & progress only 40%
            importance=5
        )
        t2 = AcademicTask(
            student_profile_id=profile.id,
            subject_id=dsa.id,
            topic="Implementing Binary Search Tree",
            task_type="Assignment",
            deadline=date.today() + timedelta(days=5),
            difficulty=3,
            completion_pct=80,
            importance=3
        )
        t3 = AcademicTask(
            student_profile_id=profile.id,
            subject_id=ml_sub.id,
            topic="Linear Regression Model Training",
            task_type="Assignment",
            deadline=date.today() + timedelta(days=10),
            difficulty=2,
            completion_pct=20,
            importance=4
        )
        db.session.add_all([t1, t2, t3])
        
        # Create Sample Projects
        p1 = Project(
            student_profile_id=profile.id,
            name="Personal Portfolio Website",
            technology="HTML, CSS, JavaScript, GitHub Pages",
            description="Responsive web portfolio displaying personal credentials and completed class projects.",
            github_link="https://github.com/hariprasad/portfolio",
            completion_pct=100,
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=45)
        )
        p2 = Project(
            student_profile_id=profile.id,
            name="E-Commerce Bookstore",
            technology="Python, Flask, SQLite, Bootstrap",
            description="Basic web store with user cart, dynamic books listing, and database inventory administration.",
            github_link="https://github.com/hariprasad/bookstore",
            completion_pct=50,
            start_date=date.today() - timedelta(days=20),
            end_date=None
        )
        db.session.add_all([p1, p2])
        
        # Create Study Sessions (Last 7 days data for Analytics)
        for i in range(1, 8):
            sess_date = date.today() - timedelta(days=i)
            # Add academic sessions
            s1 = StudySession(
                student_profile_id=profile.id,
                subject_id=dbms.id,
                date=sess_date,
                duration_minutes=45 + (i % 3) * 15
            )
            s2 = StudySession(
                student_profile_id=profile.id,
                subject_id=dsa.id,
                date=sess_date,
                duration_minutes=30 + (i % 2) * 30
            )
            db.session.add_all([s1, s2])
            
        db.session.commit()
        print("Sample student data seeded successfully!")

if __name__ == '__main__':
    # Build a temp app to run script directly from console
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pathpilot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    initialize_database(app)
    seed_sample_student(app)

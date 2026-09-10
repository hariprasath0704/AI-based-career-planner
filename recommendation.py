import numpy as np
import pandas as pd
from datetime import datetime, date
from sklearn.metrics.pairwise import cosine_similarity
from models import Skill, StudentSkill, AcademicTask, Project, PlacementGoal, Subject

# Define Career Profiles mapping target roles to skill categories and specific skills
# This acts as our 'AI template corpus' to compute career alignment using Cosine Similarity
CAREER_PROFILES = {
    'Software Engineer': {
        'Programming': 1.0,
        'Core CS': 1.0,
        'Development': 0.7,
        'AIML': 0.3,
        'Placement': 1.0,
        'core_skills': ['Python/Java', 'OOP', 'Arrays', 'Strings', 'Linked Lists', 'Stack', 'Queue', 'Trees', 'DBMS', 'Operating Systems', 'Aptitude', 'Resume', 'Technical Interview']
    },
    'Data Scientist': {
        'Programming': 0.9,
        'Core CS': 0.7,
        'Development': 0.4,
        'AIML': 1.0,
        'Placement': 0.8,
        'core_skills': ['Python/Java', 'Python', 'NumPy', 'Pandas', 'Matplotlib', 'Machine Learning', 'Deep Learning', 'NLP', 'Aptitude', 'Resume', 'Technical Interview']
    },
    'Machine Learning Engineer': {
        'Programming': 0.9,
        'Core CS': 0.8,
        'Development': 0.5,
        'AIML': 1.0,
        'Placement': 0.8,
        'core_skills': ['Python/Java', 'OOP', 'Python', 'NumPy', 'Pandas', 'Machine Learning', 'Deep Learning', 'NLP', 'Arrays', 'Aptitude', 'Resume', 'Technical Interview']
    },
    'Web Developer': {
        'Programming': 0.8,
        'Core CS': 0.7,
        'Development': 1.0,
        'AIML': 0.2,
        'Placement': 0.8,
        'core_skills': ['HTML', 'CSS', 'JavaScript', 'Git/GitHub', 'Backend', 'APIs', 'DBMS', 'OOP', 'Aptitude', 'Resume', 'Technical Interview']
    },
    'Cloud Engineer': {
        'Programming': 0.7,
        'Core CS': 0.9,
        'Development': 0.8,
        'AIML': 0.3,
        'Placement': 0.8,
        'core_skills': ['Git/GitHub', 'Backend', 'APIs', 'DBMS', 'Operating Systems', 'Computer Networks', 'Aptitude', 'Resume', 'Technical Interview']
    }
}

DEFAULT_PROFILE = {
    'Programming': 0.7,
    'Core CS': 0.7,
    'Development': 0.7,
    'AIML': 0.5,
    'Placement': 0.7,
    'core_skills': ['Python/Java', 'OOP', 'Arrays', 'DBMS', 'Operating Systems', 'HTML', 'CSS', 'Aptitude', 'Resume']
}

def get_career_profile(role):
    for key in CAREER_PROFILES:
        if key.lower() in role.lower() or role.lower() in key.lower():
            return CAREER_PROFILES[key]
    return DEFAULT_PROFILE

def calculate_readiness_score(student):
    """
    Calculates Placement Readiness Score (0-100) using weights:
    - Academics: 20%
    - Core skills (Programming & CS): 30%
    - Applied skills (Development & AIML): 20%
    - Placement preparation (15%)
    - Projects & Resume (15%)
    
    Uses standard data normalization and returns structural breakdown of strengths/weaknesses.
    """
    # 1. Academics (20 points max)
    # CGPA (15 points): Linear scale from 5.0 to 10.0
    cgpa = student.cgpa if student.cgpa else 0.0
    cgpa_score = max(0.0, ((cgpa - 5.0) / 5.0) * 15.0) if cgpa >= 5.0 else 0.0
    # Arrears deduction (5 points): Start at 5, deduct 1.5 per active arrear, floor at 0
    arrear_score = max(0.0, 5.0 - (student.arrears * 1.5))
    academic_total = cgpa_score + arrear_score

    # Fetch all skills
    student_skills = student.skills
    if not student_skills:
        return 0, {"Academics": 0, "Core Skills": 0, "Applied Skills": 0, "Placement Prep": 0, "Projects": 0}, []

    # Map status to weights
    status_weights = {
        'Completed': 1.0,
        'Practicing': 0.7,
        'Learning': 0.4,
        'Not Started': 0.0
    }

    # Group skills by category
    categories = ['Programming', 'Core CS', 'Development', 'AIML', 'Placement']
    cat_scores = {cat: [] for cat in categories}
    
    for s_skill in student_skills:
        cat = s_skill.skill.category
        if cat in cat_scores:
            weight = status_weights.get(s_skill.status, 0.0)
            cat_scores[cat].append(weight)

    # Calculate average weight per category
    avg_cat_scores = {}
    for cat, weights in cat_scores.items():
        avg_cat_scores[cat] = np.mean(weights) if weights else 0.0

    # 2. Core Skills (30 points max): Programming (15) and Core CS (15)
    core_score = (avg_cat_scores['Programming'] * 15.0) + (avg_cat_scores['Core CS'] * 15.0)

    # 3. Applied Skills (20 points max): Development (10) and AIML (10)
    applied_score = (avg_cat_scores['Development'] * 10.0) + (avg_cat_scores['AIML'] * 10.0)

    # 4. Placement Prep (15 points max)
    placement_score = avg_cat_scores['Placement'] * 15.0

    # 5. Projects & Resume (15 points max)
    # Resume completed sections (5 points max)
    resume_completed = 0.0
    if student.goals:
        import json
        try:
            resume_data = json.loads(student.goals.resume_json or '{}')
            # 5 items checklist: Summary, Education, Work/Experience, Projects, SkillList
            completed_items = sum(1 for k, v in resume_data.items() if v is True or v == "true")
            resume_completed = (completed_items / 5.0) * 5.0
        except Exception:
            resume_completed = 0.0

    # Projects completed count & progress (10 points max)
    project_score = 0.0
    if student.projects:
        proj_count = len(student.projects)
        avg_proj_prog = np.mean([p.completion_pct for p in student.projects])
        # Up to 4 points for count (2 pts each, max 4), up to 6 points for completion
        count_points = min(4.0, proj_count * 2.0)
        completion_points = (avg_proj_prog / 100.0) * 6.0
        project_score = count_points + completion_points
    
    projects_resume_total = resume_completed + project_score

    # Total Score Calculation
    total_score = academic_total + core_score + applied_score + placement_score + projects_resume_total
    total_score = min(100.0, max(0.0, float(total_score)))

    # Identify Weak Areas (Categories with average completion < 60%)
    weak_areas = []
    # 1. Academics
    if cgpa < 7.5 or student.arrears > 0:
        academic_perf = (cgpa / 10.0 * 100) - (student.arrears * 10)
        weak_areas.append(('Academics', max(0, academic_perf)))
        
    # 2. Skill Categories
    for cat in categories:
        score_pct = avg_cat_scores[cat] * 100.0
        if score_pct < 65.0:
            weak_areas.append((cat, score_pct))

    # Sort weak areas: lowest score first
    weak_areas.sort(key=lambda x: x[1])

    breakdown = {
        "Academics": float(round(academic_total, 1)),
        "Core Skills": float(round(core_score, 1)),
        "Applied Skills": float(round(applied_score, 1)),
        "Placement Prep": float(round(placement_score, 1)),
        "Projects & Resume": float(round(projects_resume_total, 1))
    }

    return round(total_score, 1), breakdown, [w[0] for w in weak_areas]


def calculate_career_alignment(student):
    """
    Computes a similarity score between student's completed skills vector and the target career template vector.
    Uses Scikit-learn Cosine Similarity.
    """
    if not student.goals or not student.skills:
        return 0.0

    target_role = student.goals.target_role or 'Software Engineer'
    profile = get_career_profile(target_role)
    
    # Get all active skills ordered
    skills_list = Skill.query.order_by(Skill.id).all()
    if not skills_list:
        return 0.0
        
    # Create target template vector
    # 1.0 for core skills, 0.5 for categories match, 0.1 otherwise
    target_vec = []
    for s in skills_list:
        val = 0.1
        if s.name in profile['core_skills']:
            val = 1.0
        elif s.category in profile:
            val = profile[s.category]
        target_vec.append(val)
        
    # Create student skill vector
    status_weights = {
        'Completed': 1.0,
        'Practicing': 0.7,
        'Learning': 0.4,
        'Not Started': 0.0
    }
    
    student_skill_map = {ss.skill_id: ss.status for ss in student.skills}
    student_vec = []
    for s in skills_list:
        status = student_skill_map.get(s.id, 'Not Started')
        student_vec.append(status_weights[status])
        
    # Calculate cosine similarity using scikit-learn
    target_vec = np.array(target_vec).reshape(1, -1)
    student_vec = np.array(student_vec).reshape(1, -1)
    
    sim = cosine_similarity(target_vec, student_vec)[0][0]
    return float(round(sim * 100, 1))


def get_what_should_i_do_now(student):
    """
    Analyzes pending tasks and roadmaps to output the SINGLE highest priority action.
    Priority = deadline + importance + weakness + career relevance
    """
    options = []
    today = date.today()

    # 1. Gather unfinished Academic Tasks
    for task in student.tasks:
        if task.completion_pct < 100:
            # Urgency score (up to 15 points)
            days_remaining = (task.deadline - today).days
            if days_remaining < 0:
                urgency = 15.0  # Overdue
            else:
                urgency = max(0.0, 15.0 - (days_remaining * 1.5))
                
            # Importance (up to 10 points)
            importance = task.importance * 2.0
            
            # Difficulty (up to 10 points)
            difficulty = task.difficulty * 2.0
            
            # Work remaining (up to 10 points)
            work_rem = ((100 - task.completion_pct) / 100.0) * 10.0
            
            # Career relevance (up to 10 points)
            career_rel = 0.0
            if student.goals:
                target_role = student.goals.target_role.lower()
                subj_name = task.subject.name.lower() if task.subject else ""
                # Simple check if subject keyword is in target role or vice versa
                if any(kw in target_role for kw in ['developer', 'software', 'engineer']) and any(sk in subj_name for sk in ['dbms', 'os', 'network', 'oops', 'dsa', 'data structure', 'java', 'python', 'c++']):
                    career_rel = 10.0
                elif any(kw in target_role for kw in ['data', 'ml', 'machine', 'ai']) and any(sk in subj_name for sk in ['python', 'ml', 'ai', 'math', 'stat', 'dbms']):
                    career_rel = 10.0

            total_score = urgency + importance + difficulty + work_rem + career_rel
            
            # Create recommendation block
            est_time = 45 if task.difficulty <= 2 else (60 if task.difficulty <= 4 else 90)
            reason = f"Your task '{task.topic}' is only {task.completion_pct}% completed. "
            if days_remaining < 0:
                reason += "It is currently OVERDUE!"
            elif days_remaining == 0:
                reason += "It is due TODAY."
            else:
                reason += f"It has an upcoming deadline in {days_remaining} days."
                
            benefit = f"Completing this will raise your {task.subject.name if task.subject else 'academic'} progress and secure internal assessment grades."
            
            options.append({
                'name': f"Complete {task.task_type}: {task.subject.name if task.subject else 'Task'} - {task.topic}",
                'type': 'academic',
                'task_id': task.id,
                'skill_id': None,
                'reason': reason,
                'estimated_time': est_time,
                'score': total_score,
                'benefit': benefit,
                'priority': 'High' if total_score > 35 else ('Medium' if total_score > 20 else 'Low')
            })

    # 2. Gather Incomplete Skills from Roadmap
    readiness, _, weak_areas = calculate_readiness_score(student)
    target_role = student.goals.target_role if student.goals else "Software Engineer"
    profile = get_career_profile(target_role)
    
    for s_skill in student.skills:
        if s_skill.status != 'Completed':
            # Base score by status
            status_scores = {'Not Started': 12.0, 'Learning': 9.0, 'Practicing': 5.0}
            score = status_scores.get(s_skill.status, 5.0)
            
            # Career relevance (up to 20 points)
            is_core = s_skill.skill.name in profile['core_skills']
            is_cat_match = s_skill.skill.category in profile
            career_rel = 20.0 if is_core else (10.0 if is_cat_match else 0.0)
            score += career_rel
            
            # Weakness priority (up to 15 points)
            weakness_score = 0.0
            if s_skill.skill.category in weak_areas:
                # Rank of weakness
                idx = weak_areas.index(s_skill.skill.category)
                weakness_score = max(5.0, 15.0 - (idx * 3.0)) # Higher priority for weaker areas
            score += weakness_score
            
            # Estimated time to practice
            est_time = 30 if s_skill.status == 'Practicing' else (45 if s_skill.status == 'Learning' else 60)
            
            reason = f"Your target career role is {target_role}. You have this skill marked as '{s_skill.status}' in your roadmap."
            if is_core:
                reason += f" '{s_skill.skill.name}' is highly core to landing job placements at your target companies."
            if s_skill.skill.category in weak_areas:
                reason += f" Additionally, your performance in {s_skill.skill.category} is currently one of your weakest areas."

            benefit = f"Practicing this will directly bridge your placement skill gap and increase your career readiness score."

            options.append({
                'name': f"Study Skill: {s_skill.skill.name} ({s_skill.skill.category})",
                'type': 'skill',
                'task_id': None,
                'skill_id': s_skill.skill.id,
                'reason': reason,
                'estimated_time': est_time,
                'score': score,
                'benefit': benefit,
                'priority': 'High' if score > 32 else ('Medium' if score > 18 else 'Low')
            })

    # Sort options
    if not options:
        return {
            'name': "Review placement dashboard and update skills",
            'reason': "You are all caught up! There are no pending academic tasks or skills to learn.",
            'estimated_time': 20,
            'priority': 'Low',
            'benefit': "Ensure your profile reflects your latest progress.",
            'score': 0.0
        }
        
    options.sort(key=lambda x: x['score'], reverse=True)
    return options[0]


def get_ai_recommendations(student):
    """
    Returns a structured recommendation object containing:
    1. Daily Recommended Tasks (list)
    2. Weekly Learning Plan
    3. Weak Skill Identification
    4. Placement Skill Gap
    5. Recommended Next Topic
    """
    readiness, breakdown, weak_areas = calculate_readiness_score(student)
    target_role = student.goals.target_role if student.goals else "Software Engineer"
    profile = get_career_profile(target_role)

    # 1. Placement Skill Gap (Skills that are not started or learning but core to job role)
    skill_gap = []
    weak_skills = []
    
    # Map student skills
    student_skills_map = {ss.skill_id: ss for ss in student.skills}
    all_skills = Skill.query.all()
    
    for skill in all_skills:
        ss = student_skills_map.get(skill.id)
        status = ss.status if ss else 'Not Started'
        
        # Skill Gap check
        if status in ['Not Started', 'Learning'] and skill.name in profile['core_skills']:
            skill_gap.append({
                'name': skill.name,
                'category': skill.category,
                'status': status
            })
            
        # Weak Skill check (Learning or Practicing in weak categories)
        if status in ['Not Started', 'Learning', 'Practicing'] and skill.category in weak_areas:
            weak_skills.append({
                'name': skill.name,
                'category': skill.category,
                'status': status
            })

    # 2. Daily Recommended Tasks
    daily_recs = []
    # Grab the top "What Should I Do Now" task
    top_task = get_what_should_i_do_now(student)
    if top_task:
        daily_recs.append(top_task)
        
    # Get 2 other distinct tasks if possible
    # Let's write an algorithm to find next best options
    all_options = []
    today = date.today()
    for task in student.tasks:
        if task.completion_pct < 100 and (not top_task or top_task.get('task_id') != task.id):
            days_remaining = (task.deadline - today).days
            score = max(0, 10 - days_remaining) + task.importance * 2 + task.difficulty * 2
            all_options.append({
                'name': f"Study {task.subject.name if task.subject else 'Academic'}: {task.topic}",
                'reason': f"Due in {days_remaining} days. Completion is {task.completion_pct}%.",
                'estimated_time': 45 if task.difficulty <= 3 else 60,
                'priority': 'High' if score > 20 else 'Medium',
                'benefit': f"Improves academic standings in {task.subject.name if task.subject else 'course'}.",
                'score': score
            })
            
    for ss in student.skills:
        if ss.status != 'Completed' and (not top_task or top_task.get('skill_id') != ss.skill.id):
            is_core = ss.skill.name in profile['core_skills']
            score = (15 if is_core else 5) + (10 if ss.status == 'Learning' else 5)
            all_options.append({
                'name': f"Practice {ss.skill.name}",
                'reason': f"Core career skill for {target_role} currently marked as '{ss.status}'.",
                'estimated_time': 30 if ss.status == 'Practicing' else 45,
                'priority': 'Medium' if score > 15 else 'Low',
                'benefit': f"Bridges placement gap for target roles.",
                'score': score
            })
            
    all_options.sort(key=lambda x: x['score'], reverse=True)
    daily_recs.extend(all_options[:2])

    # 3. Weekly Learning Plan
    # Monday to Sunday mapping of focus areas
    weekly_plan = [
        {"day": "Monday", "focus": "Core Academics", "action": "Complete upcoming assignments and review weak subject topics."},
        {"day": "Tuesday", "focus": f"{profile.get('core_skills')[0] if profile.get('core_skills') else 'Programming'} Skill Drill", "action": "Practice core language syntax, basic programs, and OOP concepts."},
        {"day": "Wednesday", "focus": "Data Structures & Algorithms", "action": "Solve 1-2 coding problems related to Arrays, Strings, or Stacks/Queues."},
        {"day": "Thursday", "focus": "Core Computer Science Concepts", "action": "Revise DBMS SQL queries or Operating System memory management concepts."},
        {"day": "Friday", "focus": "Target Projects Development", "action": "Add details or code a feature in your github portfolio projects."},
        {"day": "Saturday", "focus": "Aptitude & Technical Mock Tests", "action": "Take an online aptitude assessment or practice logical reasoning."},
        {"day": "Sunday", "focus": "Resume Refinement & Planning", "action": "Update resume details and plan out available hours for the next week."}
    ]

    # 4. Recommended Next Topic
    next_topic = "DSA: Arrays & Sorting"
    if skill_gap:
        next_topic = f"{skill_gap[0]['category']}: {skill_gap[0]['name']}"
    elif weak_skills:
        next_topic = f"{weak_skills[0]['category']}: {weak_skills[0]['name']}"

    return {
        'readiness_score': readiness,
        'career_alignment': calculate_career_alignment(student),
        'breakdown': breakdown,
        'weak_areas': weak_areas,
        'skill_gap': skill_gap[:5],
        'weak_skills': weak_skills[:5],
        'daily_recs': daily_recs,
        'weekly_plan': weekly_plan,
        'next_topic': next_topic
    }


def generate_daily_schedule(student, available_hours):
    """
    Dynamically generates study timeline.
    Example: 3 hours available -> 5:00-5:45 (Academics), 5:45-6:30 (Roadmap Skill), etc.
    """
    total_minutes = int(available_hours * 60)
    # Define slots of 45 mins study + 15 mins break, or adjust if total time is small
    slot_duration = 45
    break_duration = 15
    
    slots = []
    current_time = datetime.strptime("17:00", "%H:%M") # Starts at 5:00 PM
    
    # Priority checklist for slots:
    # 1. Urgent Academic Task
    # 2. Key Roadmap Skill (weak or core)
    # 3. Project Work
    # 4. Placement prep / DSA practice
    # Let's fetch recommendations to get task items
    recs = get_ai_recommendations(student)
    recs_pool = recs['daily_recs']
    
    task_idx = 0
    remaining_minutes = total_minutes
    
    while remaining_minutes >= 30:
        # Determine actual study slot duration (cannot exceed remaining_minutes)
        study_time = min(slot_duration, remaining_minutes)
        
        # Pull activity from pool
        if task_idx < len(recs_pool):
            activity_item = recs_pool[task_idx]
            activity_name = activity_item['name']
            task_id = activity_item.get('task_id')
            skill_id = activity_item.get('skill_id')
            task_idx += 1
        else:
            # Fallbacks
            if task_idx == len(recs_pool):
                activity_name = "Work on target portfolio projects"
                task_id, skill_id = None, None
                task_idx += 1
            elif task_idx == len(recs_pool) + 1:
                activity_name = "Revise general Aptitude or mock interviews"
                task_id, skill_id = None, None
                task_idx += 1
            else:
                activity_name = "Self study and review notes"
                task_id, skill_id = None, None
                
        start_str = current_time.strftime("%I:%M %p")
        current_time += pd.Timedelta(minutes=study_time)
        end_str = current_time.strftime("%I:%M %p")
        
        slots.append({
            'time_slot': f"{start_str} - {end_str}",
            'activity': activity_name,
            'task_id': task_id,
            'skill_id': skill_id,
            'is_break': False
        })
        
        remaining_minutes -= study_time
        
        # Add break if we have sufficient time left
        if remaining_minutes >= 20:
            break_time = min(break_duration, remaining_minutes)
            start_str = current_time.strftime("%I:%M %p")
            current_time += pd.Timedelta(minutes=break_time)
            end_str = current_time.strftime("%I:%M %p")
            
            slots.append({
                'time_slot': f"{start_str} - {end_str}",
                'activity': "Short Break (Stretch / Hydrate)",
                'task_id': None,
                'skill_id': None,
                'is_break': True
            })
            remaining_minutes -= break_time
            
    return slots


def get_project_recommendations(target_role):
    """
    Returns placement-oriented project recommendations mapped to career tracks.
    """
    role = target_role.lower()
    
    web_projects = [
        {
            'name': 'AI-Powered PathPilot Planner',
            'tech': 'Flask, SQLite, Chart.js, Pandas, Scikit-learn',
            'desc': 'A personalized study planner utilizing machine learning to compute placement readiness scores and suggest subjects.',
            'difficulty': 'Medium',
            'benefit': 'Demonstrates full-stack development, database schema design, and algorithms for score forecasting.'
        },
        {
            'name': 'Collaborative Real-time Kanban Board',
            'tech': 'Node.js, Express, Socket.io, React, MongoDB',
            'desc': 'A drag-and-drop workflow tracking board with live synchronization across users.',
            'difficulty': 'Hard',
            'benefit': 'Highlights WebSocket knowledge, React state management, and real-time backend orchestration.'
        },
        {
            'name': 'RESTful API Mocking Dashboard',
            'tech': 'Python, Django, PostgreSQL, Docker',
            'desc': 'A developer tool to define custom endpoints and return mock JSON data with latency simulation.',
            'difficulty': 'Medium',
            'benefit': 'Demonstrates API design principles, database optimization, and software containerization.'
        }
    ]
    
    data_projects = [
        {
            'name': 'Predictive Health Indicator Analysis',
            'tech': 'Python, Pandas, Scikit-learn, Seaborn',
            'desc': 'A classification model predicting disease risks using patient records and testing performance with random forests.',
            'difficulty': 'Medium',
            'benefit': 'Highlights data preprocessing pipelines, feature engineering, and model cross-validation metrics.'
        },
        {
            'name': 'Stock Market Sentiment Dashboard',
            'tech': 'Python, NLP, NLTK, Streamlit, APIs',
            'desc': 'Aggregates news headlines via web-scraping/APIs and runs sentiment analysis to output trading indicators.',
            'difficulty': 'Hard',
            'benefit': 'Shows proficiency in text mining, natural language processing, and interactive data apps.'
        },
        {
            'name': 'Customer Segmentation Engine',
            'tech': 'Python, NumPy, Scikit-learn (K-Means), Matplotlib',
            'desc': 'Uses unsupervised learning to group customers by shopping behavior datasets and builds profiles.',
            'difficulty': 'Easy',
            'benefit': 'Demonstrates unsupervised clustering, dimensionality reduction, and commercial intelligence mapping.'
        }
    ]

    general_projects = [
        {
            'name': 'Multithreaded Cache Web Proxy Server',
            'tech': 'C/C++, TCP/IP Sockets, Thread Pools',
            'desc': 'A proxy server that caches HTTP requests locally and handles concurrent client connections safely using threads.',
            'difficulty': 'Hard',
            'benefit': 'Validates low-level programming capability, operating system synchronization, and computer network protocols.'
        },
        {
            'name': 'Database Query Parser & Indexer',
            'tech': 'Java / Python, OOP, Trees, File I/O',
            'desc': 'Parses simplified SQL select/insert statements and uses B-Trees to index files for quick lookup performance.',
            'difficulty': 'Medium',
            'benefit': 'Showcases understanding of data structures, OOP architecture, and index serialization.'
        }
    ]
    
    if any(kw in role for kw in ['data', 'ml', 'machine', 'ai', 'analytics']):
        return data_projects
    elif any(kw in role for kw in ['web', 'frontend', 'backend', 'fullstack', 'cloud']):
        return web_projects
    else:
        # Default combination
        return [web_projects[0], data_projects[0], general_projects[1]]

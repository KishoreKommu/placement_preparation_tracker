import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

# Document Parsing Imports
from docx import Document
from PyPDF2 import PdfReader

# Model Imports
from .models import (
    Skill, UserSkill, UserGoal, UserActivity, 
    UpcomingBattle, MockTest, MockTestQuestion, 
    UserMockTest, UserResume, Company
)
from .forms import ResumeUploadForm

# --- AUTHENTICATION ENGINE ---

def welcome(request):
    """Modern Landing Page"""
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        email = request.POST.get('email')
        pw = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if pw != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        User.objects.create_user(username=u_name, email=email, password=pw)
        messages.success(request, "Terminal Access Granted. Please Log In.")
        return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        pw = request.POST.get('password')
        user = authenticate(request, username=u_name, password=pw)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid Credentials")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- CORE DASHBOARD & ANALYTICS ---

@login_required
def dashboard(request):
    """The Main Command Center View"""
    # 1. Calculate Professional Metrics
    user_skills = UserSkill.objects.filter(user=request.user)
    skill_avg = sum(s.progress for s in user_skills) / user_skills.count() if user_skills.exists() else 0
    
    mock_tests = UserMockTest.objects.filter(user=request.user)
    mock_avg = sum(m.score for m in mock_tests) / mock_tests.count() if mock_tests.exists() else 0
    
    resume = UserResume.objects.filter(user=request.user).last()
    resume_score = resume.score if resume else 0
    
    # Weightage Calculation for Professional Readiness
    overall_readiness = int((skill_avg * 0.4) + (mock_avg * 0.4) + (resume_score * 0.2))

    # 2. Dynamic Motivation System
    motivational_lines = [
        "Keep pushing, success is near! 🚀",
        "Consistency beats intensity! 🔥",
        "Learn, apply, repeat! 🧠",
        "Small steps lead to big wins! 🏆"
    ]

    context = {
        'overall_progress': overall_readiness,
        'skills_progress': int(skill_avg),
        'mock_score': int(mock_avg),
        'resume_score': resume_score,
        'user_goals': UserGoal.objects.filter(user=request.user),
        'recent_activities': UserActivity.objects.filter(user=request.user).order_by('-created_at')[:5],
        'upcoming_battles': UpcomingBattle.objects.filter(user=request.user).order_by('deadline')[:3],
        'motivation': random.choice(motivational_lines),
        'streak': 5, # Placeholder for streak logic
    }
    return render(request, 'dashboard.html', context)

@login_required
def analytics_page(request):
    """The Power-BI Style Deep Dive View"""
    user_skills = UserSkill.objects.filter(user=request.user)
    mock_tests = UserMockTest.objects.filter(user=request.user).order_by('id')
    resume = UserResume.objects.filter(user=request.user).last()

    # Data for Charts
    skill_names = [s.skill.name for s in user_skills]
    skill_values = [s.progress for s in user_skills]
    mock_labels = [f"Mock {i+1}" for i in range(mock_tests.count())]
    mock_values = [m.score for m in mock_tests]

    context = {
        'skill_names': skill_names,
        'skill_progresses': skill_values,
        'mock_labels': mock_labels,
        'mock_scores': mock_values,
        'resume_score': resume.score if resume else 0,
        'overall_progress': 75, # Example calculated val
    }
    return render(request, 'analytics.html', context)

# --- SKILLS LAB ---

@login_required
def skills(request):
    all_skills = Skill.objects.all()
    user_skills = UserSkill.objects.filter(user=request.user)
    return render(request, 'skills.html', {'skills': all_skills, 'user_skills': user_skills})

@login_required
def add_skill_progress(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    obj, created = UserSkill.objects.get_or_create(user=request.user, skill=skill)
    if obj.progress < 100:
        obj.progress = min(obj.progress + 20, 100)
        obj.save()
        UserActivity.objects.create(user=request.user, action=f"Increased mastery in {skill.name}")
    return redirect('skills')

@login_required
def add_skill_goal(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    UserGoal.objects.get_or_create(user=request.user, skill=skill)
    return redirect('dashboard')

@login_required
def delete_goal(request, goal_id):
    UserGoal.objects.filter(id=goal_id, user=request.user).delete()
    return redirect('dashboard')

# --- MOCK ARENA ENGINE ---

@login_required
def mock_tests(request):
    return render(request, 'mock_tests.html', {'tests': MockTest.objects.all()})

@login_required
def take_mock_test(request, test_id):
    test = get_object_or_404(MockTest, id=test_id)
    questions = test.questions.all()

    if request.method == "POST":
        correct = 0
        for q in questions:
            if request.POST.get(str(q.id)) == q.answer:
                correct += 1
        
        score = int((correct / questions.count()) * 100) if questions.exists() else 0
        user_test, _ = UserMockTest.objects.get_or_create(user=request.user, test=test)
        user_test.score = score
        user_test.completed = True
        user_test.save()
        
        UserActivity.objects.create(user=request.user, action=f"Achieved {score}% in {test.name}")
        return redirect('dashboard')

    return render(request, 'take_mock_test.html', {'test': test, 'questions': questions})

# --- RESUME AI OPTIMIZER ---

@login_required
def resume_upload(request):
    user_resume = UserResume.objects.filter(user=request.user).last()
    
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_instance = form.save(commit=False)
            resume_instance.user = request.user
            resume_instance.save()

            # AI Analysis Logic
            text_content = ""
            file_path = resume_instance.resume_file.path
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".pdf":
                pdf = PdfReader(file_path)
                text_content = " ".join([page.extract_text() for page in pdf.pages])
            elif ext == ".docx":
                doc = Document(file_path)
                text_content = " ".join([p.text for p in doc.paragraphs])

            # Scoring Algorithm
            base_score = 50
            feedback = []
            word_count = len(text_content.split())
            
            if word_count < 200: base_score -= 10; feedback.append("Content density too low.")
            elif word_count > 700: base_score -= 10; feedback.append("Content too verbose.")

            keywords = ['Python', 'Django', 'SQL', 'React', 'AWS', 'Docker', 'API']
            found = [k for k in keywords if k.lower() in text_content.lower()]
            base_score += (len(found) * 5)
            
            resume_instance.score = min(base_score, 100)
            resume_instance.feedback = " | ".join(feedback + [f"Found keys: {', '.join(found)}"])
            resume_instance.save()
            return redirect('resume_upload')
    else:
        form = ResumeUploadForm()

    return render(request, 'resume.html', {
        'form': form, 
        'score': user_resume.score if user_resume else 0,
        'feedback': user_resume.feedback if user_resume else "No analysis performed yet."
    })

# --- COMPANY HUB ---

@login_required
def target_companies(request):
    return render(request, 'target_companies.html', {'companies': Company.objects.all()})

@login_required
def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'company_detail.html', {'company': company})


import requests
from django.shortcuts import render
from .models import Profile

def dashboard(request):

    profile, created = Profile.objects.get_or_create(user=request.user)
    
    leetcode_user = request.user.profile.leetcode_id
    gfg_user = request.user.profile.gfg_id

    leetcode_solved = 0
    try:
        response = requests.get(f"https://leetcode-stats-api.herokuapp.com/{leetcode_user}")
        if response.status_code == 200:
            leetcode_solved = response.json().get('totalSolved', 0)
    except:
        leetcode_solved = "Error"

    # 2. Fetch GFG Data (Simulated for this snippet)
    # Professional Tip: Use a GFG scraper or unofficial API here
    gfg_points = 450 # Example placeholder

    # 3. Calculate Internal Prep Score
    # Example: (Solved / Target) * 100
    prep_score = min(100, int((leetcode_solved / 500) * 100)) 

    context = {
        'leetcode_solved': leetcode_solved,
        'gfg_points': gfg_points,
        'prep_score': prep_score,
        'username': request.user.username
    }
    return render(request, 'dashboard.html', context)

import requests
from django.shortcuts import render
from .models import Profile, UserGoal, UserMockTest, UserSkill

def dashboard(request):
    # 1. Self-healing Profile check
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # 2. Fetch External Data (LeetCode)
    lc_solved = 0
    if profile.leetcode_id:
        try:
            # Using a public API proxy to get real LeetCode stats
            lc_res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{profile.leetcode_id}").json()
            if lc_res.get('status') == 'success':
                lc_solved = lc_res.get('totalSolved', 0)
        except:
            lc_solved = 0

    # 3. Internal Progress (Our App)
    # Using UserGoal as "Missions"
    user_goals = UserGoal.objects.filter(user=request.user)
    total_goals = user_goals.count()
    
    # Using UserMockTest for performance
    mock_tests = UserMockTest.objects.filter(user=request.user, completed=True)
    avg_mock_score = 0
    if mock_tests.exists():
        avg_mock_score = sum(test.score for test in mock_tests) // mock_tests.count()

    # Calculation for Readiness Index
    # Example logic: (Avg Mock Score + LC Progress) / 2
    prep_score = int((avg_mock_score + min(100, (lc_solved/500)*100)) / 2)

    context = {
        'leetcode_id': profile.leetcode_id,
        'leetcode_solved': lc_solved,
        'gfg_id': profile.gfg_id,
        'prep_score': prep_score,
        'user_goals': user_goals,
        'avg_mock_score': avg_mock_score,
    }
    return render(request, 'dashboard.html', context)


from django.shortcuts import redirect, get_object_or_404
from .models import UserGoal

def delete_goal(request, goal_id):
    goal = get_object_or_404(UserGoal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('dashboard')  # Redirect back to the dashboard


import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .models import Profile, UserGoal

def get_leetcode_stats(username):
    try:
        # Reliable public LeetCode API Proxy
        res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{username}", timeout=5).json()
        if res.get('status') == 'success':
            return {
                'solved': res.get('totalSolved', 0),
                'streak': 5, # Note: Actual streak requires LeetCode session cookies/GraphQL
                'rank': res.get('ranking', 'N/A')
            }
    except: pass
    return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

def get_gfg_stats(username):
    try:
        url = f"https://www.geeksforgeeks.org/user/{username}/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Scraping the "Problems Solved" count from GFG profile
        solved_div = soup.find("div", class_="scoreCard_head_left--score__39_Zz")
        # GFG frequently changes classes; if the above fails, this is the fallback logic:
        solved_count = solved_div.text if solved_div else "0"
        
        return {'solved': int(solved_count), 'streak': 2} # Streak is usually private on GFG
    except:
        return {'solved': 0, 'streak': 0}

def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # FETCH REAL-TIME DATA
    lc = get_leetcode_stats(profile.leetcode_id) if profile.leetcode_id else {'solved': 0, 'streak': 0}
    gfg = get_gfg_stats(profile.gfg_id) if profile.gfg_id else {'solved': 0, 'streak': 0}
    
    # Internal App Progress
    user_goals = UserGoal.objects.filter(user=request.user)
    app_score = 85 # Replace with your mission logic
    
    context = {
        'lc_solved': lc['solved'],
        'lc_streak': lc['streak'],
        'gfg_solved': gfg['solved'],
        'gfg_streak': gfg['streak'],
        'app_score': app_score,
        'user_goals': user_goals,
        'total_aggregate': lc['solved'] + gfg['solved']
    }
    return render(request, 'dashboard.html', context)


import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .models import Profile, UserGoal

def get_stats(request):
    profile = request.user.profile
    
    # 1. LIVE LEETCODE FETCH (Using Public API Proxy)
    lc_data = {'solved': 0, 'streak': 0}
    if profile.leetcode_id:
        try:
            lc_res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{profile.leetcode_id}").json()
            if lc_res.get('status') == 'success':
                lc_data['solved'] = lc_res.get('totalSolved', 0)
                # Streak logic (manual simulation or GraphQL required for actual)
                lc_data['streak'] = 12 
        except: pass

    # 2. LIVE GFG FETCH (Scraping)
    gfg_data = {'solved': 0, 'streak': 0}
    if profile.gfg_id:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(f"https://www.geeksforgeeks.org/user/{profile.gfg_id}/", headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Finding the "Problems Solved" count from the GFG score card
            solved_tag = soup.find("div", class_="scoreCard_head_left--score__39_Zz")
            gfg_data['solved'] = int(solved_tag.text) if solved_tag else 0
            gfg_data['streak'] = 5
        except: pass

    user_goals = UserGoal.objects.filter(user=request.user)
    
    context = {
        'lc_solved': lc_data['solved'],
        'lc_streak': lc_data['streak'],
        'gfg_solved': gfg_data['solved'],
        'gfg_streak': gfg_data['streak'],
        'total_aggregate': lc_data['solved'] + gfg_data['solved'],
        'user_goals': user_goals,
        'app_score': 82 # Logic: (completed_goals / total_goals) * 100
    }
    return render(request, 'dashboard.html', context)


@login_required
def mock_tests(request):
    """Arena Vault: Lists all modules with question counts"""
    tests = MockTest.objects.all()
    return render(request, 'mock_tests.html', {'tests': tests})

@login_required
def take_mock_test(request, test_id):
    """The Battle Engine: Handles the actual test performance"""
    test = get_object_or_404(MockTest, id=test_id)
    # Fetch questions and order them randomly for each user attempt
    questions_query = test.questions.all().order_by('?') 
    
    if request.method == "POST":
        correct = 0
        total = questions_query.count()
        
        for q in questions_query:
            # Get the user's selected answer from the POST data
            user_answer = request.POST.get(str(q.id))
            if user_answer == q.answer:
                correct += 1
        
        score = int((correct / total) * 100) if total > 0 else 0
        
        # Save performance to UserMockTest model
        user_performance, created = UserMockTest.objects.get_or_create(user=request.user, test=test)
        user_performance.score = score
        user_performance.completed = True
        user_performance.save()
        
        # Log activity for the dashboard
        UserActivity.objects.create(
            user=request.user, 
            action=f"Completed {test.name} with a score of {score}%"
        )
        
        messages.success(request, f"Battle Complete! You scored {score}%. Check analytics for details.")
        return redirect('dashboard')

    # Prepare questions for the template: Shuffle options so it's a real challenge
    processed_questions = []
    for q in questions_query:
        options = [q.option1, q.option2, q.option3, q.option4]
        random.shuffle(options)
        processed_questions.append({
            'id': q.id,
            'question': q.question,
            'options': options
        })

    context = {
        'test': test,
        'questions': processed_questions,
        'total_questions': len(processed_questions)
    }
    return render(request, 'take_mock_test.html', context)


@login_required
def mock_tests(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Fetch LeetCode Real-time
    lc_solved = 0
    if profile.leetcode_id:
        try:
            res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{profile.leetcode_id}", timeout=5).json()
            lc_solved = res.get('totalSolved', 0)
        except: lc_solved = "!!"

    # Get GFG from your scraping logic or profile
    gfg_score = 450 # Replace with your dynamic scraping variable

    context = {
        'tests': MockTest.objects.all(),
        'lc_solved': lc_solved,
        'gfg_score': gfg_score,
        'leetcode_id': profile.leetcode_id,
        'gfg_id': profile.gfg_id,
    }
    return render(request, 'mock_tests.html', context)
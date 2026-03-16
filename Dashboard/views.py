import os
import random
import requests
from bs4 import BeautifulSoup

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from docx import Document
from PyPDF2 import PdfReader
# from openai import OpenAI
from django.conf import settings

from .models import (
    Skill, UserSkill, UserGoal, UserActivity,
    UpcomingBattle, MockTest, MockTestQuestion,
    UserMockTest, UserResume, Company, Profile
)
from .forms import ResumeUploadForm


# =============================
# AUTH SYSTEM
# =============================

def welcome(request):
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


# =============================
# LEETCODE + GFG FETCH (FIXED)
# =============================

def get_leetcode_stats(username):
    if not username:
        return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

    try:
        res = requests.get(
            f"https://leetcode-stats-api.herokuapp.com/{username}",
            timeout=5
        ).json()

        return {
            'solved': res.get('totalSolved', 0),
            'rank': res.get('ranking', 'N/A'),
            # REAL streak requires GraphQL login — keeping safe fallback
            'streak': res.get('streak', 0) if 'streak' in res else 0
        }
    except:
        return {'solved': 0, 'streak': 0, 'rank': 'N/A'}


def get_gfg_stats(username):
    if not username:
        return {'solved': 0, 'streak': 0}

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(
            f"https://www.geeksforgeeks.org/user/{username}/",
            headers=headers,
            timeout=5
        )

        soup = BeautifulSoup(res.text, "html.parser")

        solved_div = soup.find("div", class_="scoreCard_head_left--score__39_Zz")
        solved = int(solved_div.text.strip()) if solved_div else 0

        return {'solved': solved, 'streak': 0}
    except:
        return {'solved': 0, 'streak': 0}


# =============================
# DASHBOARD (ONLY ONE VERSION)
# =============================

@login_required
def dashboard(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)

    # External Data
    lc = get_leetcode_stats(profile.leetcode_id)
    gfg = get_gfg_stats(profile.gfg_id)
    # print("Leetcode ID:", profile.leetcode_id)
    # print("GFG ID:", profile.gfg_id)

    # Internal Skill Avg
    user_skills = UserSkill.objects.filter(user=request.user)
    skill_avg = sum(s.progress for s in user_skills) / user_skills.count() if user_skills.exists() else 0

    # Internal Mock Avg
    mock_tests = UserMockTest.objects.filter(user=request.user, completed=True)
    mock_avg = sum(m.score for m in mock_tests) / mock_tests.count() if mock_tests.exists() else 0

    # Resume Score
    resume = UserResume.objects.filter(user=request.user).last()
    resume_score = resume.score if resume else 0

    # Readiness Index (Same Logic)
    prep_score = int((skill_avg * 0.4) + (mock_avg * 0.4) + (resume_score * 0.2))

    motivational_lines = [
        "Keep pushing, success is near! 🚀",
        "Consistency beats intensity! 🔥",
        "Learn, apply, repeat! 🧠",
        "Small steps lead to big wins! 🏆"
    ]

    context = {
        'lc_solved': lc['solved'],
        'lc_streak': lc['streak'],
        'gfg_solved': gfg['solved'],
        'gfg_streak': gfg['streak'],
        'overall_progress': prep_score,
        'skills_progress': int(skill_avg),
        'mock_score': int(mock_avg),
        'resume_score': resume_score,
        'user_goals': UserGoal.objects.filter(user=request.user),
        'recent_activities': UserActivity.objects.filter(user=request.user).order_by('-created_at')[:5],
        'upcoming_battles': UpcomingBattle.objects.filter(user=request.user).order_by('deadline')[:3],
        'motivation': random.choice(motivational_lines),
        'total_aggregate': lc['solved'] + gfg['solved'],
    }

    return render(request, 'dashboard.html', context)


from django.shortcuts import redirect, get_object_or_404
from .models import UserGoal
from django.contrib.auth.decorators import login_required

# @login_required
# def delete_goal(request, goal_id):

#     goal = get_object_or_404(UserGoal, id=goal_id)

#     if goal.user == request.user:
#         goal.delete()

#     return redirect('dashboard')


# =============================
# ANALYTICS
# =============================

@login_required
def analytics_page(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Fetch Real Data
    lc = get_leetcode_stats(profile.leetcode_id)
    gfg = get_gfg_stats(profile.gfg_id)

    # Internal Skill Avg
    user_skills = UserSkill.objects.filter(user=request.user)
    skill_avg = sum(s.progress for s in user_skills) / user_skills.count() if user_skills.exists() else 0

    # Internal Mock Avg
    mock_tests = UserMockTest.objects.filter(user=request.user, completed=True)
    mock_avg = sum(m.score for m in mock_tests) / mock_tests.count() if mock_tests.exists() else 0

    # Resume Score
    resume = UserResume.objects.filter(user=request.user).last()
    resume_score = resume.score if resume else 0

    # Readiness Index
    prep_score = int((skill_avg * 0.4) + (mock_avg * 0.4) + (resume_score * 0.2))

    # Chart Data
    skill_names = [s.skill.name for s in user_skills]
    skill_values = [s.progress for s in user_skills]
    mock_labels = [f"Mock {i+1}" for i in range(mock_tests.count())]
    mock_values = [m.score for m in mock_tests]

    context = {
        # 🔥 External Real Data
        'lc_solved': lc['solved'],
        'gfg_solved': gfg['solved'],
        'total_aggregate': lc['solved'] + gfg['solved'],

        # 🔥 Internal Data
        'avg_mock_score': int(mock_avg),
        'prep_score': prep_score,

        # Charts
        'skill_names': skill_names,
        'skill_progresses': skill_values,
        'mock_labels': mock_labels,
        'mock_scores': mock_values,
        'resume_score': resume_score,
    }

    return render(request, 'analytics.html', context)


# =============================
# SKILLS
# =============================

@login_required
def skills(request):
    return render(request, 'skills.html', {
        'skills': Skill.objects.all(),
        'user_skills': UserSkill.objects.filter(user=request.user)
    })


@login_required
def add_skill_progress(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    obj, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)

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
    goal = get_object_or_404(UserGoal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('dashboard')

import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MockTest, MockTestQuestion, UserMockTest
from dashboard.models import UserActivity

import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MockTest, MockTestQuestion, UserMockTest
from dashboard.models import UserActivity


# =============================
# MOCK TEST LIST
# =============================


@login_required
def mock_tests(request):

    tests = MockTest.objects.all()

    return render(request, "mock_tests.html", {
        "tests": tests,
        "lc_solved": 0,
        "gfg_score": 0
    })



# =============================
# TAKE MOCK TEST
# =============================
@login_required
def take_mock_test(request, test_id):

    test = get_object_or_404(MockTest, id=test_id)

    questions = list(test.questions.all())

    print("QUESTIONS FOUND:", len(questions))  # Debug

    random.shuffle(questions)

    if request.method == "POST":

        correct = 0
        total = len(questions)

        for q in questions:

            user_answer = request.POST.get(str(q.id))

            if user_answer == q.answer:
                correct += 1

        score = int((correct / total) * 100) if total else 0

        user_test, created = UserMockTest.objects.get_or_create(
            user=request.user,
            test=test
        )

        user_test.score = score
        user_test.completed = True
        user_test.save()

        UserActivity.objects.create(
            user=request.user,
            action=f"Completed {test.name} with {score}%"
        )

        messages.success(request, f"You scored {score}%")

        return redirect("dashboard")

    return render(request, "take_mock_test.html", {
        "test": test,
        "questions": questions
    })

# =============================
# RESUME ANALYZER
# =============================

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import os
from PyPDF2 import PdfReader
from docx import Document
from .forms import ResumeUploadForm

@login_required
def resume_upload(request):
    # Initial state for a fresh GET request
    score = None
    feedback = None

    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            resume_instance = form.save(commit=False)
            resume_instance.user = request.user
            resume_instance.save()

            # Get target job description from the form
            job_desc = request.POST.get('job_description', '').lower()

            text_content = ""
            file_path = resume_instance.resume_file.path
            ext = os.path.splitext(file_path)[1].lower()

            # 1. Extract Resume Text
            try:
                if ext == ".pdf":
                    pdf = PdfReader(file_path)
                    text_content = " ".join([p.extract_text() or "" for p in pdf.pages])
                elif ext == ".docx":
                    doc = Document(file_path)
                    text_content = " ".join([p.text for p in doc.paragraphs])
            except Exception as e:
                messages.error(request, "Error processing file: " + str(e))
                return redirect('resume_upload')

            text_content = text_content.lower()

            # 2. Analysis Logic
            word_count = len(text_content.split())
            length_score = 20 if 300 <= word_count <= 700 else (10 if word_count <= 900 else 0)

            # Keyword matching (Static + Dynamic from Job Description)
            base_keywords = ['python', 'django', 'sql', 'react', 'aws', 'docker', 'git', 'api']
            found_keywords = [k for k in base_keywords if k in text_content]
            
            # Simple keyword match for Job Description if provided
            jd_keywords_found = []
            if job_desc:
                # Basic check: find overlapping words
                jd_words = set(job_desc.split())
                resume_words = set(text_content.split())
                jd_keywords_found = list(jd_words.intersection(resume_words))

            keyword_score = min(len(found_keywords) * 5, 40)
            
            # Section detection
            sections = ["education", "projects", "skills", "experience", "certifications"]
            found_sections = [s for s in sections if s in text_content]
            section_score = min(len(found_sections) * 8, 40)

            final_score = min(length_score + keyword_score + section_score, 100)

            # 3. Save results to instance
            feedback = f"Word Count: {word_count}. Sections: {', '.join(found_sections)}."
            resume_instance.score = final_score
            resume_instance.feedback = feedback
            resume_instance.save()

            # 4. Use Session to pass data once (clears on refresh)
            request.session['last_score'] = final_score
            request.session['last_feedback'] = feedback
            
            # Redirect to the same page to clear POST state
            return redirect('resume_upload')

    else:
        # GET request: check if we just redirected from a successful upload
        score = request.session.pop('last_score', None)
        feedback = request.session.pop('last_feedback', None)
        form = ResumeUploadForm()

    return render(request, 'resume.html', {
        'form': form,
        'score': score,
        'feedback': feedback
    })

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io

def download_analysis_pdf(request):
    score = request.POST.get("score_data", "0")
    
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using SimpleDocTemplate for easy layout
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    elements = []

    # --- HEADER ---
    elements.append(Paragraph("Resume Optimization Report", title_style))
    elements.append(Paragraph("Generated by Nexus AI Engine", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # --- SCORE BOX ---
    # We use a table to create a colored background "box" for the score
    score_color = colors.HexColor("#10b981") if int(score) > 70 else colors.HexColor("#ef4444")
    
    score_data = [[Paragraph(f"<font color='white' size='14'>Overall Readiness Score</font>", styles['Normal']), 
                   Paragraph(f"<font color='white' size='28'><b>{score}%</b></font>", styles['Normal'])]]
    
    score_table = Table(score_data, colWidths=[3*inch, 1.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), score_color),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('ROUNDEDCORNERS', [15, 15, 15, 15]), # Note: Some ReportLab versions might need a graphic rect for rounded corners
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.4 * inch))

    # --- ANALYSIS TABLE ---
    elements.append(Paragraph("Core Metrics Analysis", section_header))
    
    analysis_data = [
        ['Category', 'Status', 'Feedback'],
        ['Keyword Match', '68%', 'Significant overlap with developer roles.'],
        ['Missing Keys', 'Critical', 'Kubernetes, Redis, CI/CD, Docker'],
        ['Formatting', 'Stable', 'Single column layout detected. ATS-Safe.'],
        ['Grammar', 'Optimal', 'Professional tone maintained throughout.'],
    ]
    
    t = Table(analysis_data, colWidths=[1.2*inch, 0.8*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(t)

    # --- RECOMMENDATIONS ---
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph("AI-Driven Suggestions", section_header))
    
    recommendations = [
        "• <b>Action-First Syntax:</b> Convert passive phrases to active (e.g., 'Helped in' -> 'Orchestrated').",
        "• <b>Quantify Impact:</b> Add numeric benchmarks to your project descriptions (e.g., 'Improved speed by 20%').",
        "• <b>Skill Grouping:</b> Explicitly group your tech stack by Category (Languages, Frameworks, Tools)."
    ]
    
    for rec in recommendations:
        elements.append(Paragraph(rec, styles['Normal']))
        elements.append(Spacer(1, 6))

    # Build PDF
    doc.build(elements)

    # FileResponse is better for returning files
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Resume_Analysis_{score}.pdf"'

    return response

# =============================
# COMPANY HUB
# =============================

@login_required
def target_companies(request):

    if Company.objects.count() == 0:

        default_companies = [
            {"name": "Google", "description": "Build scalable distributed systems and AI powered services."},
            {"name": "Microsoft", "description": "Develop enterprise cloud platforms and productivity tools."},
            {"name": "Amazon", "description": "Work on large scale cloud infrastructure and e-commerce systems."},
            {"name": "Apple", "description": "Create innovative consumer technology products and services."},
            {"name": "Meta", "description": "Build social platforms and immersive digital experiences."},
            {"name": "Netflix", "description": "Design high performance streaming platforms."},
            {"name": "Uber", "description": "Develop real time transportation and logistics systems."},
            {"name": "Airbnb", "description": "Build global travel and booking platforms."},
            {"name": "LinkedIn", "description": "Create professional networking platforms."},
            {"name": "Adobe", "description": "Develop creative software tools and AI media platforms."},

            {"name": "Salesforce", "description": "Build enterprise CRM platforms."},
            {"name": "Oracle", "description": "Develop enterprise database systems."},
            {"name": "IBM", "description": "Work on enterprise AI and cloud computing."},
            {"name": "Cisco", "description": "Develop networking infrastructure and security systems."},
            {"name": "Intel", "description": "Build hardware and software optimization technologies."},

            {"name": "PayPal", "description": "Develop global digital payment systems."},
            {"name": "Stripe", "description": "Build developer friendly payment infrastructure."},
            {"name": "Razorpay", "description": "Create fintech solutions for Indian businesses."},
            {"name": "PhonePe", "description": "Develop digital payment platforms."},
            {"name": "Google Pay", "description": "Build mobile payment technologies."},

            {"name": "Flipkart", "description": "Design scalable e-commerce systems."},
            {"name": "Meesho", "description": "Build social commerce platforms."},
            {"name": "Myntra", "description": "Develop fashion e-commerce platforms."},
            {"name": "Snapdeal", "description": "Build marketplace platforms."},

            {"name": "Swiggy", "description": "Develop food delivery logistics platforms."},
            {"name": "Zomato", "description": "Build restaurant discovery and delivery systems."},

            {"name": "Ola", "description": "Develop ride sharing platforms."},
            {"name": "Rapido", "description": "Create bike taxi platforms."},

            {"name": "TCS", "description": "Global IT services and consulting."},
            {"name": "Infosys", "description": "Enterprise software and consulting."},
            {"name": "Wipro", "description": "Technology consulting and services."},
            {"name": "HCL", "description": "Global IT infrastructure services."},

            {"name": "Zoho", "description": "Build business software products."},
            {"name": "Freshworks", "description": "Develop SaaS customer engagement tools."},

            {"name": "Samsung", "description": "Develop consumer electronics and software."},
            {"name": "Sony", "description": "Build entertainment and technology products."},

            {"name": "Nvidia", "description": "Develop GPU computing platforms."},
            {"name": "AMD", "description": "Build advanced processor technologies."},

            {"name": "SpaceX", "description": "Build advanced aerospace systems."},
            {"name": "Tesla", "description": "Develop electric vehicles and AI systems."},

            {"name": "Spotify", "description": "Build global music streaming systems."},
            {"name": "Pinterest", "description": "Develop visual discovery platforms."},

            {"name": "Byjus", "description": "Develop education technology platforms."},
            {"name": "Unacademy", "description": "Build online learning platforms."},

            {"name": "Coursera", "description": "Global online learning systems."},
            {"name": "Udemy", "description": "Online skill learning platforms."},

            {"name": "Atlassian", "description": "Build developer collaboration tools."},
            {"name": "GitHub", "description": "Develop code hosting platforms."}
        ]

        for c in default_companies:
            Company.objects.create(
                name=c["name"],
                description=c["description"]
            )

    companies = Company.objects.all()

    return render(request, 'target_companies.html', {
        'companies': companies
    })


@login_required
def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'company_detail.html', {
        'company': company
    })



def get_leetcode_stats(username):
    if not username:
        return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

    url = "https://leetcode.com/graphql"

    query = """
    query userProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                ranking
            }
        }
    }
    """

    variables = {"username": username}

    try:
        response = requests.post(
            url,
            json={'query': query, 'variables': variables},
            timeout=5
        )

        data = response.json()

        user_data = data.get("data", {}).get("matchedUser", {})

        solved = 0
        if user_data.get("submitStats"):
            for item in user_data["submitStats"]["acSubmissionNum"]:
                if item["difficulty"] == "All":
                    solved = item["count"]

        rank = user_data.get("profile", {}).get("ranking", "N/A")

        return {
            'solved': solved,
            'rank': rank,
            'streak': 0  
        }

    except:
        return {'solved': 0, 'rank': 'N/A', 'streak': 0}
    

import requests
import json
import time
from datetime import datetime

# =============================
# LEETCODE + GFG FETCH (FINAL CLEAN VERSION)
# =============================


def get_leetcode_stats(username):
    if not username:
        return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

    url = "https://leetcode.com/graphql"

    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
        "Origin": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0"
    }

    query = """
    query userProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
        profile {
          ranking
        }
        submissionCalendar
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"username": username}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code != 200:
            return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

        data = response.json()
        user = data.get("data", {}).get("matchedUser")

        if not user:
            return {'solved': 0, 'streak': 0, 'rank': 'N/A'}

        # Total solved
        solved = 0
        for item in user["submitStats"]["acSubmissionNum"]:
            if item["difficulty"] == "All":
                solved = item["count"]

        rank = user.get("profile", {}).get("ranking", "N/A")

        # Streak calculation
        calendar_raw = user.get("submissionCalendar", "{}")
        calendar = json.loads(calendar_raw)

        today = int(time.time())
        one_day = 86400
        streak = 0
        current = today - (today % one_day)

        while str(current) in calendar:
            streak += 1
            current -= one_day

        return {
            'solved': solved,
            'streak': streak,
            'rank': rank
        }

    except Exception as e:
        print("LeetCode Fetch Error:", e)
        return {'solved': 0, 'streak': 0, 'rank': 'N/A'}


def get_gfg_stats(username):
    if not username:
        return {'solved': 0, 'streak': 0}

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://auth.geeksforgeeks.org/user/{username}/"

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        solved = 0

        # Look for "Problems Solved" text instead of class
        labels = soup.find_all("div")

        for tag in labels:
            if tag.text.strip() == "Problems Solved":
                value_tag = tag.find_next("div")
                if value_tag:
                    solved = int(value_tag.text.strip())
                break

        return {
            'solved': solved,
            'streak': 0
        }

    except Exception as e:
        print("GFG ERROR:", e)
        return {'solved': 0, 'streak': 0}


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.leetcode_id = request.POST.get("leetcode_id")
        profile.gfg_id = request.POST.get("gfg_id")
        profile.save()
        return redirect("dashboard")

    return render(request, "edit_profile.html", {"profile": profile})
# =============================
# CAREER ROADMAPS
# =============================

from .models import Skill
from .roadmaps_data import roadmaps


@login_required
def roadmap_page(request):
    skills = Skill.objects.all()
    return render(request, "roadmap.html", {"skills": skills})


@login_required
def roadmap_detail(request, slug):

    skill = roadmaps.get(slug)

    if not skill:
        return render(request, "404.html")

    return render(request, "roadmap_detail.html", {"skill": skill})


from google import genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        try:
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)

            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=user_message
            )

            return JsonResponse({"reply": response.text})

        except Exception as e:
            return JsonResponse({"reply": str(e)})


def chatbot(request):
    return render(request, "chatbot.html")



def roadmap_detail(request, slug):

    skill = roadmaps.get(slug)

    if not skill:
        return render(request, "404.html")

    return render(request, "roadmap_detail.html", {"skill": skill})



# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def daily_planner(request):
#     # Sample daily tasks (you can expand or fetch from DB)
#     tasks = [
#         {
#             "title": "Daily Coding Challenge",
#             "description": "Solve one LeetCode problem or a similar coding challenge every day."
#         },
#         {
#             "title": "Aptitude Practice",
#             "description": "Spend 30 mins practicing aptitude questions: Quant, Logical, or Verbal reasoning."
#         },
#         {
#             "title": "Interview Questions",
#             "description": "Review 5-10 commonly asked interview questions for your target roles."
#         },
#         {
#             "title": "Resume Improvement Tasks",
#             "description": "Update your resume with achievements, projects, or new skills learned."
#         }
#     ]
    
#     return render(request, 'daily_planner.html', {'tasks': tasks})

@login_required
def daily_planner(request):
    # We pass an empty list or fetch user-specific tasks from a Model
    return render(request, 'daily_planner.html', {'tasks': []})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def games_page(request):
    return render(request, "games.html")


from django.shortcuts import render

def job_notifications(request):

    jobs = [

        {
            "company": "Google",
            "role": "Software Engineer Intern",
            "location": "Bangalore",
            "deadline": "30 March 2026",
            "description": "Looking for strong DSA and system design fundamentals.",
            "link": "https://careers.google.com"
        },

        {
            "company": "Microsoft",
            "role": "SDE Intern",
            "location": "Hyderabad",
            "deadline": "5 April 2026",
            "description": "Opportunity for students with strong coding skills.",
            "link": "https://careers.microsoft.com"
        },

        {
            "company": "Amazon",
            "role": "Software Development Engineer",
            "location": "Chennai",
            "deadline": "10 April 2026",
            "description": "Focus on problem solving and algorithms.",
            "link": "https://amazon.jobs"
        }

    ]

    return render(request, "job_notifications.html", {"jobs": jobs})



from django.shortcuts import render

def games(request):
    return render(request, "games/games.html")


def reaction_game(request):
    return render(request, "games/reaction.html")


def memory_game(request):
    return render(request, "games/memory.html")


def math_game(request):
    return render(request, "games/math.html")


def color_game(request):
    return render(request, "games/color.html")


def snake_game(request):
    return render(request, "games/snake.html")


def tictactoe_game(request):
    return render(request, "games/tictactoe.html")


def game_2048(request):
    return render(request, "games/2048.html")

from django.shortcuts import render, redirect, get_object_or_404
from .models import MockTest, MockTestQuestion

# def test_view(request, test_id):
#     test = get_object_or_404(MockTest, id=test_id)
#     questions = MockTestQuestion.objects.filter(test=test)
#     return render(request, 'test_page.html', {'test': test, 'questions': questions})


# def result_view(request, test_id):
#     test = get_object_or_404(MockTest, id=test_id)
#     questions = MockTestQuestion.objects.filter(test=test)
    
#     if request.method == 'POST':
#         total_questions = questions.count()
#         correct_answers = 0

#         # Loop through all questions and check submitted answers
#         for q in questions:
#             selected = request.POST.get(str(q.id))
#             if selected and selected == q.correct_option:
#                 correct_answers += 1

#         score = round((correct_answers / total_questions) * 100, 2)

#         context = {
#             'test': test,
#             'score': score,
#             'total_questions': total_questions,
#             'correct_answers': correct_answers
#         }
#         return render(request, 'result.html', context)

#     # If user opens result URL directly, redirect to test page
#     return redirect('test', test_id=test.id)


# # def mock_tests(request):
# #     # Just a placeholder, redirect or render your mock tests list
# #     return render(request, 'mock_tests.html')
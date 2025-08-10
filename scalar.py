# app.py
import io
import random
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="Scaler AI — Masterclass -> Challenge -> Conversion",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# CSS Styling (minimal)
# -------------------------
st.markdown("""
<style>
body, .stApp { font-family: Inter, sans-serif; color: white; }

/* Header */
.header { 
    background: linear-gradient(135deg,#1e3c72 0%,#2a5298 100%); 
    color:white; 
    padding:22px; 
    border-radius:8px; 
    margin-bottom:18px;
}

/* Panels */
.panel { 
    background: white; 
    padding:18px; 
    border-radius:8px; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    color: #222222;
    # color: black;
    
}

/* Headings inside panels and metric containers */
.panel h3, .panel h4, .metric h4 {
    color: #222222 !important;
    font-weight: 700;
}
h4{
    color:black;
}

/* Challenge invite box */
.challenge-inv { 
    background: linear-gradient(135deg,#ff6b6b 0%,#ee5a24 100%); 
    color:white; 
    padding:18px; 
    border-radius:8px;
}

/* Metric box */
.metric { 
    background:white; 
    padding:14px; 
    border-radius:8px; 
    border-left: 4px solid #667eea; 
    margin-bottom:10px;
    color: #222222;
}

/* Code box */
.codebox { 
    background:#2c3e50; 
    color:#ecf0f1; 
    padding:12px; 
    border-radius:6px; 
    font-family: monospace; 
    white-space: pre-wrap;
}

/* Exit popup */
.exit-popup { 
    background: linear-gradient(135deg,#e74c3c 0%,#c0392b 100%); 
    color:white; 
    padding:18px; 
    border-radius:8px;
}

/* Email template */
.email-template {
    background: #f9f9f9;
    padding: 16px;
    border-radius: 8px;
    color: #222222;
}

.email-header {
    font-weight: 600;
    margin-bottom: 10px;
    color: #333333;
}

/* Chatbot container */
.chatbot-container {
    background: #f0f4f8;
    padding: 12px;
    border-radius: 8px;
    color: #222222;
}
</style>
""", unsafe_allow_html=True)
# -------------------------
# Helper functions (lightweight "AI")
# -------------------------
def extract_profile_from_resume(resume_text: str):
    """
    Simple keyword-based extractor. Returns dict with role, experience_years, skills, seniority.
    """
    if not resume_text:
        return None
    text = resume_text.lower()
    keywords = {
        'Software Engineer': ['python', 'java', 'react', 'javascript', 'backend', 'frontend', 'api', 'docker', 'kubernetes'],
        'Data Analyst': ['excel', 'tableau', 'power bi', 'sql', 'pandas', 'visualization', 'dashboard', 'reporting', 'rfm', 'eda'],
        'Data Scientist': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'ml', 'ai', 'pandas', 'numpy'],
        'Product Manager': ['product management', 'roadmap', 'stakeholder', 'user research', 'kpi', 'metrics'],
        'DevOps Engineer': ['aws', 'azure', 'ci/cd', 'terraform', 'jenkins', 'infrastructure']
    }
    scores = {}
    found_skills = set()
    for role, kwlist in keywords.items():
        count = 0
        for kw in kwlist:
            if kw in text:
                count += 1
                found_skills.add(kw)
        scores[role] = count
    # pick best role, but if ties or all zero, default to Data Analyst (per your ask)
    best_role = max(scores, key=scores.get)
    if scores[best_role] == 0:
        best_role = "Data Analyst"
    # experience approximation
    exp = 1
    if 'senior' in text or '5+' in text or '5 years' in text:
        exp = 6
    elif 'lead' in text or '3+' in text or '3 years' in text:
        exp = 4
    elif 'junior' in text or '1+' in text or '1 year' in text:
        exp = 2
    seniority = 'Senior' if exp >= 5 else 'Mid-level' if exp >= 3 else 'Junior'
    return {
        'role': best_role,
        'experience_years': exp,
        'skills': sorted(list(found_skills)),
        'seniority': seniority,
        'raw_text_preview': resume_text[:100].replace('\n', ' ') + ('...' if len(resume_text) > 100 else '')
    }

def generate_personalized_nuggets(profile: dict, masterclass_topic: str = "AI & Machine Learning"):
    """Return a small set of personalized popup nuggets for the user based on profile."""
    if not profile:
        return {}
    role = profile.get('role', 'Professional')
    seniority = profile.get('seniority', 'Junior')
    skills = profile.get('skills', [])[:5]
    nuggets = {
        'headline': f"{role} • {seniority} • {', '.join(skills) if skills else 'Skills not listed'}",
        'nugget_1': f"As a {role}, mastering {masterclass_topic} can help you build production-ready analytics & models faster.",
        'nugget_2': f"Focus on project-based learning — employers value delivered impact (dashboards, pipelines, ML features).",
        'cta': f"Join the 30-min challenge and earn up to 40% off our AI course — limited spots!"
    }
    # small personalization
    if role == "Data Analyst":
        nuggets['nugget_1'] = f"AI helps Data Analysts automate repetitive analysis and build predictive models — learn how in the masterclass."
        nuggets['extra_tip'] = "Try combining SQL + Python + visualization to demonstrate quick wins to stakeholders."
    return nuggets

def assign_random_team(user_name="You", participants=50):
    """Simulate random team assignment; returns team name and teammates."""
    team_names = ['AI Innovators', 'Code Crushers', 'Data Wizards', 'ML Masters', 'Tech Titans', 'Algorithm Aces']
    team = random.choice(team_names)
    # create random teammates
    teammates = []
    count = random.choice([2,3])  # team size excluding you (so final team 3-4)
    for i in range(count):
        teammates.append(random.choice([
            "Sarah K.", "Alex M.", "Priya S.", "John D.", "Maya R.", "David L.", "Lisa C.", "Mike R."
        ]))
    return team, teammates

def simulate_scoring(solution_text: str):
    """Simple heuristic scoring: length + keywords -> normalized 0-10"""
    if not solution_text or solution_text.strip() == "":
        return random.uniform(4.0, 6.5)  # low-ish if empty
    text = solution_text.lower()
    score = min(10.0, 3.0 + len(text.split()) * 0.03)  # base + length
    # keyword boosts
    for kw, boost in [('feature', 0.5), ('validation', 0.7), ('cross', 0.4), ('ensemble', 0.6), ('hyperparameter', 0.6)]:
        if kw in text:
            score += boost
    # small noise
    score += random.uniform(-0.5, 0.8)
    return round(max(0.0, min(10.0, score)), 1)

def discount_by_score(score: float):
    """Map score to discount tier"""
    if score >= 9.0:
        return {"tier": "🥇 40% OFF", "savings": "40%"}
    elif score >= 8.0:
        return {"tier": "🥈 30% OFF", "savings": "30%"}
    elif score >= 7.0:
        return {"tier": "🥉 20% OFF", "savings": "20%"}
    else:
        return {"tier": "🎯 15% OFF (Participant)", "savings": "15%"}

def generate_personalized_email(profile: dict, masterclass_topic: str, email_type: str):
    """Create a simple templated email using profile info."""
    name = profile.get('name', '[Name]')
    role = profile.get('role', 'Professional')
    seniority = profile.get('seniority', '')
    if email_type == "2 Hours Post-Exit":
        subject = f"That moment from today's {masterclass_topic} — don't let it fade"
        content = f"""Hi {name},

I noticed you attended the {masterclass_topic} masterclass. As a {seniority} {role}, now is the perfect time to convert that learning spark into a measurable skill.

Quick wins for you:
• Build a dashboard to demonstrate one business metric in 1 week.
• Use a small ML model to predict the next 30-day trend for a key KPI.

Your exclusive 40% discount is still available for a short time.

[CLAIM 40% OFF]

Best,
The Scaler AI Team
"""
    elif email_type == "24 Hours Later":
        subject = f"Your peers are already advancing — a reminder from Scaler AI"
        content = f"""Hi {name},

Yesterday's masterclass created momentum. Many {role.lower()}s like you have already started the challenge and secured priority access.

We saved a spot with a discount for {seniority} {role}s who take action.

[SECURE YOUR SPOT]

— Scaler AI"""
    else:
        subject = f"A note from your future self — keep building"
        content = f"""Hi {name},

Two weeks from now you'll be glad you acted. As a {role}, this program helps you move from analysis to impact.

[ENROLL NOW — FINAL REMINDER]

— The Scaler Team"""
    return {"subject": subject, "content": content}

# -------------------------
# Initialize session state
# -------------------------
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'masterclass_joined' not in st.session_state:
    st.session_state.masterclass_joined = False
if 'team_info' not in st.session_state:
    st.session_state.team_info = None
if 'challenge_score' not in st.session_state:
    st.session_state.challenge_score = None
if 'discount' not in st.session_state:
    st.session_state.discount = None
if 'exit_popup_shown' not in st.session_state:
    st.session_state.exit_popup_shown = False

# -------------------------
# Top header
# -------------------------
st.markdown('<div class="header"><h2>⚡ Scaler — Free AI Masterclass & Challenge Flow</h2><div style="opacity:0.9;">Upload your resume → Attend masterclass → Join challenge → Get discounts → Re-engage via email</div></div>', unsafe_allow_html=True)

# -------------------------
# Navigation - pages as selectbox
# -------------------------
pages = [
    "1 — Upload Resume",
    "2 — Attend Masterclass",
    "3 — Do the Challenge",
    "4 — Nuggets & Exit Intent",
    "5 — Re-engagement Emails"
]
page = st.selectbox("Go to page", pages)

# -------------------------
# Page 1: Upload Resume
# -------------------------
if page == "1 — Upload Resume":
    st.markdown('<div class="panel"><h3>Step 1 — Upload Resume</h3><p>We analyze your resume to detect profile and generate personalized pop-ups and nuggets during the flow.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        st.info("Upload a PDF/TXT/DOCX resume or paste resume text. For demo, you can paste the sample shown below.")
        uploaded_file = st.file_uploader("Upload resume (optional)", type=['pdf','txt','docx'])
        resume_text = ""
        if uploaded_file is not None:
            try:
                bytes_data = uploaded_file.read()
                # Try decode as text if small .txt or .pdf filename; fallback simple
                try:
                    resume_text = bytes_data.decode('utf-8', errors='ignore')
                except Exception:
                    # as a safe fallback show chunk
                    resume_text = str(bytes_data)[:2000]
                st.success("File loaded (text extraction is simplified in this prototype).")
            except Exception as e:
                st.error("Failed to read file. Paste text below instead.")
        else:
            resume_text = st.text_area("Or paste resume text here:", height=300, placeholder="Paste resume content...")
            if not resume_text:
                # show sample
                if st.button("Load sample resume"):
                    resume_text = """
JYOTIRADITYA SHARAD JADHAV
Data Analyst | Machine Learning Engineer
Pune, Maharashtra | example@gmail.com

EXPERIENCE
Data Analyst Intern (June 2024 - August 2024)
Kinesiis System Inc, Pune
• Hands-on with ML workflows: EDA, feature engineering, model evaluation
• Built Tableau dashboards, SQL reporting, automation scripts in Python

SKILLS
Python, SQL, Excel, Tableau, Power BI, Pandas, Numpy, Data Visualization, EDA
"""
                    st.experimental_rerun()

        if resume_text and st.button("🧠 Analyze Resume & Generate Profile"):
            with st.spinner("Analyzing resume..."):
                time.sleep(0.6)
                profile = extract_profile_from_resume(resume_text)
                # attach a name if available (very naive)
                profile['name'] = "Candidate"
                st.session_state.resume_data = profile
                st.success("Resume analyzed!")
    with col2:
        st.markdown('<div class="metric"><h4>Detected Profile</h4>', unsafe_allow_html=True)
        if st.session_state.resume_data:
            rd = st.session_state.resume_data
            st.markdown(f"**Role:** {rd['role']}  \n**Seniority:** {rd['seniority']}  \n**Experience (approx):** {rd['experience_years']} years")
            if rd.get('skills'):
                st.markdown("**Top skills detected:** " + ", ".join(rd['skills'][:8]))
            st.markdown("</div>", unsafe_allow_html=True)
            # show nuggets preview
            nuggets = generate_personalized_nuggets(rd, masterclass_topic="AI & Machine Learning")
            st.markdown('<div class="panel"><h4>Personalized nugget preview</h4>', unsafe_allow_html=True)
            st.write(nuggets.get('headline'))
            st.write("• " + nuggets.get('nugget_1'))
            if 'extra_tip' in nuggets:
                st.write("• " + nuggets.get('extra_tip'))
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("No resume analyzed yet. Upload or paste resume and click Analyze.", unsafe_allow_html=True)

# -------------------------
# Page 2: Attend Masterclass
# -------------------------
elif page == "2 — Attend Masterclass":
    st.markdown('<div class="panel"><h3>Step 2 — Attend Masterclass</h3><p>Simulate attending the AI masterclass. At the end, the instructor will announce a challenge and you can join.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-inv"><h3>Instructor Announcement</h3><p>Join our exclusive 30-minute challenge starting in 5 minutes — apply what you learned, compete with peers, win discounts up to 40%, limited to first 50 participants.</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        if not st.session_state.masterclass_joined:
            if st.button("🚀 JOIN THE LIVE CHALLENGE (Reserve a Spot)"):
                st.session_state.masterclass_joined = True
                team, teammates = assign_random_team()
                st.session_state.team_info = {'team': team, 'teammates': teammates}
                st.success("You're in! Discord invite simulated and team assigned.")
                st.info(f"Assigned Team: {team} — Teammates: {', '.join(teammates)}")
        else:
            st.success("You already joined the challenge.")
            if st.session_state.team_info:
                ti = st.session_state.team_info
                st.markdown(f"**Team:** {ti['team']}  \n**Teammates:** {', '.join(ti['teammates'])}")
    with col2:
        # show participation counter simulation
        participants = st.session_state.get('participants', 12)
        participants = min(50, participants + random.randint(0, 5))
        st.session_state['participants'] = participants
        st.markdown(f"<div class='metric'><h4>Live Participation</h4><h2 style='color:#27ae60'>{participants}/50</h2></div>", unsafe_allow_html=True)

# -------------------------
# Page 3: Do the Challenge
# -------------------------
elif page == "3 — Do the Challenge":
    st.markdown('<div class="panel"><h3>Step 3 — The 30-minute Challenge</h3><p>Work with your team and submit a solution. The system will score it and reveal a discount.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>Challenge Prompt</h4><p><strong>AI Masterclass Challenge:</strong> Optimize a customer segmentation pipeline — include feature ideas, validation strategy and a plan to productionize the model.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="codebox"># Hint: mention validation, feature engineering, and deployment considerations</div>', unsafe_allow_html=True)

    solution = st.text_area("Paste your team solution or write your plan here:", height=240, placeholder="Describe your approach: feature engineering, validation, model choice, deployment...")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Submit Solution for AI Review"):
            score = simulate_scoring(solution)
            st.session_state.challenge_score = score
            disc = discount_by_score(score)
            st.session_state.discount = disc
            st.success(f"Solution scored: {score}/10")
            st.info(f"Assigned discount tier: {disc['tier']}")
    with col2:
        if st.button("🧪 Quick Auto-Test (simulate)"):
            score = round(random.uniform(7.0, 9.5), 1)
            st.session_state.challenge_score = score
            disc = discount_by_score(score)
            st.session_state.discount = disc
            st.success(f"Quick test result: {score}/10 — {disc['tier']}")

    # show result if available
    if st.session_state.challenge_score:
        st.markdown('<div class="panel"><h4>Results & Offer</h4>', unsafe_allow_html=True)
        st.markdown(f"**Score:** {st.session_state.challenge_score}/10")
        st.markdown(f"**Discount:** {st.session_state.discount['tier']}")
        st.markdown("**Next steps:** Use the discount to claim a seat in the full AI Mastery Program. The offer is time-limited and tied to challenge participation.")
        if st.button("CLAIM DISCOUNT & ENROLL"):
            st.balloons()
            st.success("🎉 Enrollment processed. Confirmation email simulated.")
            st.info(f"You've used {st.session_state.discount['savings']} off. Welcome aboard!")

# -------------------------
# Page 4: Nuggets & Exit Intent
# -------------------------
elif page == "4 — Nuggets & Exit Intent":
    st.markdown('<div class="panel"><h3>Step 4 — Personalized Nuggets & Exit Recovery</h3><p>We show tailored popups and a chatbot to recover users who are about to leave.</p></div>', unsafe_allow_html=True)

    # require resume_data for personalization
    rd = st.session_state.get('resume_data')
    if not rd:
        st.warning("No resume/profile found. Go to Page 1 and upload/paste resume for personalized nuggets.")
        st.stop()

    nuggets = generate_personalized_nuggets(rd, masterclass_topic="AI & Machine Learning")
    st.markdown('<div class="metric"><h4>Personalized Nuggets</h4>', unsafe_allow_html=True)
    st.write("• " + nuggets.get('nugget_1'))
    if 'extra_tip' in nuggets:
        st.write("• " + nuggets.get('extra_tip'))
    st.write("• " + nuggets.get('cta'))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:12px;">', unsafe_allow_html=True)
    st.markdown('<div class="chatbot-container"><h4>Scaler AI Assistant</h4><p>Hi — I can create a tailored learning path for you based on your resume. Interested?</p></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✅ Yes, show learning path"):
            st.success("Personalized learning path created! (Simulated)")
            st.info("Suggested next module: 'Deploy ML Pipelines' — 6 weeks")
    with c2:
        if st.button("🤔 Tell me more"):
            st.info("We offer mentorship, career coaching, and hiring support for practitioners.")
    with c3:
        if st.button("🚪 I'm leaving"):
            st.warning("Ok — we'll follow up via email. Simulating exit intent popup...")
            st.session_state.exit_popup_shown = True

    if st.session_state.exit_popup_shown:
        st.markdown('<div class="exit-popup"><h3>⚠️ WAIT! Before you leave...</h3><p>As a Data Analyst, AI can help you deliver high-impact insights faster. Claim 40% OFF + 1:1 session — limited time.</p></div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("CLAIM 40% OFF NOW"):
                st.success("Enrollment processed (simulated). Confirmation email will be sent.")
                st.session_state.exit_popup_shown = False
        with col_b:
            if st.button("Maybe later"):
                st.info("No problem — we'll send a personalized follow-up email in 2 hours.")
                st.session_state.exit_popup_shown = False

# -------------------------
# Page 5: Re-engagement Emails
# -------------------------
elif page == "5 — Re-engagement Emails":
    st.markdown('<div class="panel"><h3>Step 5 — Personalized Re-engagement Emails</h3><p>Generate email templates for attendees who left without converting. These are personalized using the resume-derived profile.</p></div>', unsafe_allow_html=True)

    rd = st.session_state.get('resume_data')
    if not rd:
        st.warning("No resume/profile found. Go to Page 1 and upload/paste resume for personalized email generation.")
        st.stop()

    col1, col2 = st.columns([1,2])
    with col1:
        email_type = st.selectbox("Email type", ["2 Hours Post-Exit", "24 Hours Later", "Final Reminder (7 days)"])
        send_preview = st.button("Generate Email")
    with col2:
        if send_preview:
            template = generate_personalized_email(rd, masterclass_topic="AI & Machine Learning", email_type=email_type)
            st.markdown('<div class="email-template"><div class="email-header">', unsafe_allow_html=True)
            st.markdown(f"**To:** {rd.get('name', '[Name]')} • **Profile:** {rd.get('role')}, {rd.get('seniority')}")
            st.markdown(f"**Subject:** {template['subject']}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(template['content'].replace('\n', '<br>'), unsafe_allow_html=True)
            st.success("Email template generated — you can plug this into your email system (Mailchimp / Sendgrid).")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;padding:10px;'>Prototype — Local rule-based personalization. Replace lightweight logic with OpenAI/Claude + Document parsers for production.</div>", unsafe_allow_html=True)

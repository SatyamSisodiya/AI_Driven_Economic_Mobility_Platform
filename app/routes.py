from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import User, Skill, UserSkill, LearningResource, LearningPath, JobOpportunity, UserOpportunity, SkillGapAnalysis
from app.forms import UserProfileForm, SkillForm
from app.skills_analyzer import SkillsAnalyzer
from app.learning_recommender import LearningRecommender
from app.opportunity_finder import OpportunityFinder
from app.data_fetcher import update_all_data
from app import db
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Homepage"""
    return render_template('base.html')

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management"""
    form = UserProfileForm()
    
    # For demo, use user_id = 1
    user = User.query.get(1)
    
    if request.method == 'GET' and user:
        # Pre-populate form
        form.email.data = user.email
        form.name.data = user.name
        form.current_role.data = user.current_role
        form.experience_years.data = user.experience_years
        form.education_level.data = user.education_level
        form.location.data = user.location
        form.target_role.data = user.target_role
        form.target_salary.data = user.target_salary
    
    if form.validate_on_submit():
        if not user:
            user = User()
            db.session.add(user)
        
        user.email = form.email.data
        user.name = form.name.data
        user.current_role = form.current_role.data
        user.experience_years = form.experience_years.data
        user.education_level = form.education_level.data
        user.location = form.location.data
        user.target_role = form.target_role.data
        user.target_salary = form.target_salary.data
        
        db.session.commit()
        flash('Profile saved successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Get user skills
    skills = []
    if user:
        user_skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                               .join(UserSkill)\
                               .filter(UserSkill.user_id == user.id)\
                               .all()
        skills = [{'name': name, 'level': level} for name, level in user_skills]
    
    skill_form = SkillForm()
    return render_template('profile.html', form=form, skill_form=skill_form, skills=skills)

@main.route('/add_skill', methods=['POST'])
def add_skill():
    """Add a skill to user profile"""
    skill_form = SkillForm()
    
    if skill_form.validate_on_submit():
        # Get or create skill
        skill = Skill.query.filter_by(name=skill_form.skill_name.data).first()
        if not skill:
            skill = Skill(name=skill_form.skill_name.data, category='User Added')
            db.session.add(skill)
            db.session.flush()
        
        # Add to user (user_id = 1 for demo)
        user_skill = UserSkill.query.filter_by(user_id=1, skill_id=skill.id).first()
        if user_skill:
            user_skill.proficiency_level = skill_form.proficiency_level.data
        else:
            user_skill = UserSkill(
                user_id=1,
                skill_id=skill.id,
                proficiency_level=skill_form.proficiency_level.data
            )
            db.session.add(user_skill)
        
        db.session.commit()
        flash('Skill added successfully!', 'success')
    
    return redirect(url_for('main.profile'))

@main.route('/dashboard')
def dashboard():
    """Main dashboard"""
    user = User.query.get(1)  # Demo user
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Get recent analysis
    latest_analysis = SkillGapAnalysis.query.filter_by(user_id=1)\
                                           .order_by(SkillGapAnalysis.created_at.desc())\
                                           .first()
    
    # Get learning paths
    recommender = LearningRecommender()
    learning_paths = recommender.get_user_learning_paths(1)
    
    # Get opportunities
    finder = OpportunityFinder()
    recent_opportunities = finder.get_user_opportunities(1)[:5]
    
    # Get next actions
    next_actions = recommender.get_recommended_next_actions(1)
    
    # Get additional required data
    user_skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                           .join(UserSkill)\
                           .filter(UserSkill.user_id == user.id)\
                           .all()
    
    # Calculate learning progress
    learning_progress = sum([path.progress for path in learning_paths]) / len(learning_paths) if learning_paths else 0
    
    # Get job matches count
    job_matches = len(recent_opportunities)
    
    # Calculate market readiness from latest analysis
    market_readiness = float(latest_analysis.analysis_data.get('market_readiness', 0)) if latest_analysis else 0
    
    return render_template('dashboard.html', 
                         user=user,
                         user_skills=user_skills,
                         learning_progress=learning_progress,
                         job_matches=job_matches,
                         market_readiness=market_readiness,
                         learning_paths=learning_paths[:3],
                         recent_opportunities=recent_opportunities,
                         next_actions=next_actions[:3])

@main.route('/skills_analysis')
def skills_analysis():
    """Skill gap analysis page"""
    user = User.query.get(1)
    
    if not user or not user.target_role:
        flash('Please complete your profile and set a target role first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Run analysis
    analyzer = SkillsAnalyzer()
    analysis_result = analyzer.analyze_skill_gaps(1)
    
    if 'error' in analysis_result:
        flash(analysis_result['error'], 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('skills_analysis.html', 
                         analysis=analysis_result,
                         user=user)

@main.route('/learning_paths')
def learning_paths():
    """Learning paths page"""
    user = User.query.get(1)
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    recommender = LearningRecommender()
    paths = recommender.get_user_learning_paths(1)
    
    return render_template('learning_paths.html', 
                         learning_paths=paths,
                         user=user)

@main.route('/generate_learning_path', methods=['GET', 'POST'])
def generate_learning_path():
    """Generate new learning path"""
    if request.method == 'GET':
        # Handle GET request - show the form
        latest_analysis = SkillGapAnalysis.query.filter_by(user_id=1)\
                                               .order_by(SkillGapAnalysis.created_at.desc())\
                                               .first()
        if not latest_analysis:
            flash('Please complete a skills analysis first.', 'warning')
            return redirect(url_for('main.skills_analysis'))
        return render_template('generate_path.html', analysis=latest_analysis)

    # Handle POST request
    analysis_id = request.form.get('analysis_id')
    if not analysis_id:
        flash('No analysis selected.', 'error')
        return redirect(url_for('main.skills_analysis'))
    
    recommender = LearningRecommender()
    result = recommender.generate_learning_path(1, analysis_id=int(analysis_id))
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('Learning path generated successfully!', 'success')
    
    return redirect(url_for('main.learning_paths'))

@main.route('/update_progress', methods=['POST'])
def update_progress():
    """Update learning progress"""
    data = request.get_json()
    
    recommender = LearningRecommender()
    result = recommender.update_progress(
        1,  # user_id
        data['learning_path_id'],
        data['resource_id'],
        data.get('completed', True)
    )
    
    return jsonify(result)

@main.route('/opportunities')
def opportunities():
    """Opportunities page"""
    user = User.query.get(1)
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Get opportunities
    finder = OpportunityFinder()
    opportunity_data = finder.find_opportunities(1)
    
    # Get application statistics
    user_opps = UserOpportunity.query.filter_by(user_id=1).all()
    application_stats = {}
    for uo in user_opps:
        if uo.status in application_stats:
            application_stats[uo.status] += 1
        else:
            application_stats[uo.status] = 1

    return render_template('opportunities.html', 
                         opportunities=opportunity_data['opportunities'],
                         recommendations=opportunity_data['recommendations'],
                         application_stats=application_stats,
                         user=user)

@main.route('/update_opportunity_status', methods=['POST'])
def update_opportunity_status():
    """Update opportunity application status"""
    data = request.get_json()
    
    finder = OpportunityFinder()
    result = finder.update_opportunity_status(
        1,  # user_id
        data['opportunity_id'],
        data['status'],
        data.get('notes')
    )
    
    return jsonify(result)

@main.route('/update_path_status', methods=['POST'])
def update_path_status():
    """Update learning path status"""
    data = request.get_json()
    path_id = data.get('path_id')
    status = data.get('status')
    
    path = LearningPath.query.get(path_id)
    if path and path.user_id == 1:  # Check if path belongs to demo user
        path.status = status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Path not found'})

@main.route('/refresh_data')
def refresh_data():
    """Refresh all data from APIs"""
    try:
        update_all_data()
        flash('Data refreshed successfully!', 'success')
    except Exception as e:
        flash(f'Error refreshing data: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main.route('/api/skill_search')
def api_skill_search():
    """API endpoint for skill autocomplete"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    skills = Skill.query.filter(Skill.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'name': skill.name, 'id': skill.id} for skill in skills])
import pandas as pd
import numpy as np
from app.models import (User, UserSkill, Skill, LearningResource, 
                       LearningPath, LearningPathResource, SkillGapAnalysis)
from app import db
import json
from datetime import datetime, timedelta

class LearningRecommender:
    def __init__(self):
        pass
    
    def generate_learning_path(self, user_id, analysis_id=None, custom_skills=None):
        """Generate personalized learning pathway for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get skills to learn
        if analysis_id:
            analysis = SkillGapAnalysis.query.get(analysis_id)
            if not analysis:
                return {"error": "Analysis not found"}
            skill_gaps = json.loads(analysis.analysis_data)['skill_gaps']
        elif custom_skills:
            skill_gaps = self._create_skill_gaps_from_custom(custom_skills)
        else:
            return {"error": "No skills specified"}
        
        # Get user constraints
        constraints = self._get_user_constraints(user)
        
        # Create learning paths for each skill
        learning_paths = []
        for gap in skill_gaps:
            path = self._create_skill_learning_path(gap, constraints)
            if path:
                learning_paths.append(path)
        
        # Optimize schedule
        schedule = self._optimize_learning_schedule(learning_paths, constraints)
        
        # Calculate completion estimates
        completion_date = self._calculate_completion_date(schedule, constraints)
        
        # Save learning paths
        saved_path_ids = self._save_learning_paths(user_id, learning_paths)
        
        return {
            'learning_paths': learning_paths,
            'schedule': schedule,
            'estimated_completion': completion_date,
            'path_ids': saved_path_ids
        }
    
    def _get_user_constraints(self, user):
        """Get user's learning constraints and preferences"""
        return {
            'hours_per_week': 10,  # Default assumption
            'preferred_difficulty': 'intermediate',
            'max_cost': 500  # Default budget
        }
    
    def _create_skill_learning_path(self, skill_gap, constraints):
        """Create learning path for a specific skill"""
        skill_name = skill_gap['skill']
        current_level = skill_gap['current_level']
        target_level = skill_gap['required_level']
        
        # Get skill ID
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            return None
        
        # Get learning resources
        resources = LearningResource.query.filter_by(skill_id=skill.id).all()
        
        # If no resources found, create default ones
        if not resources:
            resources = self._create_default_resources(skill_name, skill.id)
        
        # Filter and sequence resources
        filtered_resources = self._filter_resources(resources, constraints, current_level, target_level)
        sequenced_resources = self._sequence_resources(filtered_resources, current_level, target_level)
        
        # Create milestones
        milestones = self._create_milestones(sequenced_resources, current_level, target_level)
        
        return {
            'skill': skill_name,
            'current_level': current_level,
            'target_level': target_level,
            'resources': [self._resource_to_dict(r) for r in sequenced_resources],
            'milestones': milestones,
            'total_hours': sum(r.duration_hours for r in sequenced_resources),
            'total_cost': sum(r.cost for r in sequenced_resources)
        }
    
    def _filter_resources(self, resources, constraints, current_level, target_level):
        """Filter resources based on user constraints"""
        filtered = []
        total_cost = 0
        
        for resource in resources:
            # Skip if too basic or too advanced
            if resource.difficulty_level == 'beginner' and current_level > 2:
                continue
            if resource.difficulty_level == 'advanced' and current_level < 3:
                continue
            
            # Check cost constraints
            if total_cost + resource.cost > constraints['max_cost']:
                continue
            
            filtered.append(resource)
            total_cost += resource.cost
        
        return filtered
    
    def _sequence_resources(self, resources, current_level, target_level):
        """Sequence resources in optimal learning order"""
        def sort_key(resource):
            difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            return (difficulty_map[resource.difficulty_level], -resource.rating if resource.rating else 0)
        
        return sorted(resources, key=sort_key)
    
    def _create_milestones(self, resources, current_level, target_level):
        """Create learning milestones"""
        milestones = []
        current_date = datetime.now()
        total_hours = sum(r.duration_hours for r in resources)
        hours_per_milestone = total_hours / 3  # Create 3 milestones
        
        accumulated_hours = 0
        milestone_count = 0
        
        for resource in resources:
            accumulated_hours += resource.duration_hours
            if accumulated_hours >= hours_per_milestone * (milestone_count + 1):
                milestone_count += 1
                milestones.append({
                    'title': f'Complete {resource.title}',
                    'description': f'Achieve proficiency level {current_level + milestone_count}',
                    'target_date': current_date + timedelta(days=int(accumulated_hours/2))  # Assume 2 hours per day
                })
        
        return milestones
    
    def _optimize_learning_schedule(self, learning_paths, constraints):
        """Create optimized weekly learning schedule"""
        hours_per_week = constraints['hours_per_week']
        schedule = []
        
        # Distribute hours based on priority
        total_hours = sum(path['total_hours'] for path in learning_paths)
        remaining_hours = hours_per_week
        
        for path in learning_paths:
            # Calculate hours per week for this path
            path_hours = (path['total_hours'] / total_hours) * hours_per_week
            
            schedule.append({
                'skill': path['skill'],
                'hours_per_week': min(path_hours, remaining_hours),
                'resources': path['resources'][:2],  # Show first 2 resources to start
                'priority': path.get('priority_score', 0.5)
            })
            
            remaining_hours -= path_hours
        
        return sorted(schedule, key=lambda x: x['priority'], reverse=True)
    
    def _calculate_completion_date(self, schedule, constraints):
        """Calculate estimated completion date"""
        total_hours = sum(path['total_hours'] for path in schedule)
        weeks_needed = total_hours / constraints['hours_per_week']
        
        return datetime.now() + timedelta(weeks=int(weeks_needed))
    
    def _save_learning_paths(self, user_id, learning_paths):
        """Save learning paths to database"""
        saved_paths = []
        
        for path in learning_paths:
            # Create learning path
            new_path = LearningPath(
                user_id=user_id,
                title=f"Master {path['skill']}",
                description=f"Path to achieve {path['skill']} proficiency level {path['target_level']}",
                estimated_duration_weeks=int(path['total_hours'] / 10),  # Assume 10 hours per week
                status='active'
            )
            db.session.add(new_path)
            db.session.flush()  # Get ID without committing
            
            # Add resources to path
            for idx, resource_data in enumerate(path['resources']):
                resource = LearningResource.query.get(resource_data['id'])
                if resource:
                    path_resource = LearningPathResource(
                        learning_path_id=new_path.id,
                        learning_resource_id=resource.id,
                        order_position=idx
                    )
                    db.session.add(path_resource)
            
            saved_paths.append(new_path.id)
        
        db.session.commit()
        return saved_paths
    
    def _resource_to_dict(self, resource):
        """Convert resource object to dictionary"""
        return {
            'id': resource.id,
            'title': resource.title,
            'provider': resource.provider,
            'url': resource.url,
            'duration_hours': resource.duration_hours,
            'cost': resource.cost,
            'difficulty_level': resource.difficulty_level,
            'rating': resource.rating
        }
    
    def get_user_learning_paths(self, user_id):
        """Get all learning paths for a user"""
        paths = LearningPath.query.filter_by(user_id=user_id).all()
        result = []
        
        for path in paths:
            # Get resources for this path
            resources = db.session.query(LearningResource)\
                                .join(LearningPathResource)\
                                .filter(LearningPathResource.learning_path_id == path.id)\
                                .order_by(LearningPathResource.order_position)\
                                .all()
            
            # Calculate progress
            completed_resources = db.session.query(LearningPathResource)\
                                         .filter_by(learning_path_id=path.id, completed=True)\
                                         .count()
            total_resources = len(resources)
            progress = (completed_resources / total_resources * 100) if total_resources > 0 else 0
            
            result.append({
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'progress': progress,
                'status': path.status,
                'resources': [self._resource_to_dict(r) for r in resources],
                'created_at': path.created_at,
                'estimated_completion': path.created_at + timedelta(weeks=path.estimated_duration_weeks)
            })
        
        return result
import json
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.tracker import DailyActivityTracker
from db.models.workout import ExerciseSet, Exercise, Workout
from utils import app_logger


class TrackerService:
    
    @staticmethod
    def create_daily_activity_tracker(user_id: int, tracker_data, db: Session):
        """Create a new daily activity tracker entry"""
        try:
            # Check if entry already exists for this user and date
            existing_tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == tracker_data.date
            ).first()
            
            if existing_tracker:
                return {
                    "status": "error",
                    "message": "Daily activity tracker already exists for this date. Use PUT to update."
                }
            
            # Convert workout_types_done list to JSON string
            workout_types_json = None
            if tracker_data.workout_types_done:
                workout_types_json = json.dumps(tracker_data.workout_types_done)
            
            # Calculate net calorie balance
            net_balance = tracker_data.calories_consumed - tracker_data.calories_burned_from_activity
            
            # Create new tracker entry
            tracker = DailyActivityTracker(
                user_id=user_id,
                date=tracker_data.date,
                total_exercises_done=tracker_data.total_exercises_done,
                total_sets_completed=tracker_data.total_sets_completed,
                total_weight_lifted=tracker_data.total_weight_lifted,
                total_reps_completed=tracker_data.total_reps_completed,
                total_workout_time=tracker_data.total_workout_time,
                calories_burned_from_activity=tracker_data.calories_burned_from_activity,
                calories_consumed=tracker_data.calories_consumed,
                protein_consumed_g=tracker_data.protein_consumed_g,
                carbs_consumed_g=tracker_data.carbs_consumed_g,
                fat_consumed_g=tracker_data.fat_consumed_g,
                fiber_consumed_g=tracker_data.fiber_consumed_g,
                net_calorie_balance=net_balance,
                workout_types_done=workout_types_json,
                notes=tracker_data.notes
            )
            
            db.add(tracker)
            db.commit()
            db.refresh(tracker)
            
            return {
                "status": "success",
                "message": "Daily activity tracker created successfully",
                "tracker_id": tracker.id,
                "date": tracker.date.isoformat(),
                "net_calorie_balance": tracker.net_calorie_balance
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in create_daily_activity_tracker: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def update_daily_activity_tracker(user_id: int, tracker_date: date, tracker_data, db: Session):
        """Update existing daily activity tracker entry"""
        try:
            # Find existing tracker
            tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == tracker_date
            ).first()
            
            if not tracker:
                return {
                    "status": "error",
                    "message": "Daily activity tracker not found for this date"
                }
            
            # Update fields that are provided
            update_data = tracker_data.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                if field == "workout_types_done" and value is not None:
                    # Convert list to JSON string
                    setattr(tracker, field, json.dumps(value))
                elif hasattr(tracker, field) and value is not None:
                    setattr(tracker, field, value)
            
            # Recalculate net calorie balance
            tracker.net_calorie_balance = tracker.calories_consumed - tracker.calories_burned_from_activity
            
            db.commit()
            db.refresh(tracker)
            
            return {
                "status": "success",
                "message": "Daily activity tracker updated successfully",
                "tracker_id": tracker.id,
                "date": tracker.date.isoformat(),
                "net_calorie_balance": tracker.net_calorie_balance
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in update_daily_activity_tracker: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_daily_activity_tracker(user_id: int, tracker_date: date, db: Session):
        """Get daily activity tracker for a specific date"""
        try:
            tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == tracker_date
            ).first()
            
            if not tracker:
                return None
            
            return tracker
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_daily_activity_tracker: {e}")
            return None
    
    @staticmethod
    def calculate_and_populate_activity_data(user_id: int, target_date: date, db: Session):
        """Calculate activity data from ExerciseSet data and populate tracker"""
        try:
            # Query all exercise sets for the user on the target date
            exercise_sets = db.query(
                ExerciseSet.weight,
                ExerciseSet.reps,
                ExerciseSet.time,
                Exercise.name.label('exercise_name'),
                Workout.workout_type,
                Workout.name.label('workout_name')
            ).join(
                Exercise, ExerciseSet.exercise_id == Exercise.id
            ).join(
                Workout, Exercise.workout_id == Workout.id
            ).filter(
                db.func.date(ExerciseSet.created_at) == target_date
            ).all()
            
            if not exercise_sets:
                return {
                    "status": "info",
                    "message": "No exercise data found for the specified date"
                }
            
            # Calculate workout statistics
            total_sets = len(exercise_sets)
            total_weight = sum(set_data.weight * set_data.reps for set_data in exercise_sets)
            total_reps = sum(set_data.reps for set_data in exercise_sets)
            total_time = sum(set_data.time for set_data in exercise_sets)
            
            # Get unique exercises and workout types
            unique_exercises = set(set_data.exercise_name for set_data in exercise_sets)
            unique_workout_types = set(set_data.workout_type.value for set_data in exercise_sets if set_data.workout_type)
            
            # Simple calorie calculation (this is a rough estimate)
            # Formula: (weight_lifted * reps * 0.05) + (time_in_minutes * 5)
            calories_burned = (total_weight * 0.05) + (total_time * 5)
            
            # Check if tracker already exists
            existing_tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == target_date
            ).first()
            
            if existing_tracker:
                # Update existing tracker with calculated workout data
                existing_tracker.total_exercises_done = len(unique_exercises)
                existing_tracker.total_sets_completed = total_sets
                existing_tracker.total_weight_lifted = total_weight
                existing_tracker.total_reps_completed = total_reps
                existing_tracker.total_workout_time = total_time
                existing_tracker.calories_burned_from_activity = calories_burned
                existing_tracker.workout_types_done = json.dumps(list(unique_workout_types))
                existing_tracker.net_calorie_balance = existing_tracker.calories_consumed - calories_burned
                
                db.commit()
                db.refresh(existing_tracker)
                
                return {
                    "status": "success",
                    "message": "Daily activity tracker updated with calculated data",
                    "tracker_id": existing_tracker.id,
                    "calculated_data": {
                        "total_exercises_done": len(unique_exercises),
                        "total_sets_completed": total_sets,
                        "total_weight_lifted": total_weight,
                        "total_reps_completed": total_reps,
                        "total_workout_time": total_time,
                        "calories_burned_from_activity": calories_burned,
                        "workout_types_done": list(unique_workout_types)
                    }
                }
            else:
                # Create new tracker with calculated data
                new_tracker = DailyActivityTracker(
                    user_id=user_id,
                    date=target_date,
                    total_exercises_done=len(unique_exercises),
                    total_sets_completed=total_sets,
                    total_weight_lifted=total_weight,
                    total_reps_completed=total_reps,
                    total_workout_time=total_time,
                    calories_burned_from_activity=calories_burned,
                    calories_consumed=0.0,  # Default, can be updated later
                    protein_consumed_g=0.0,
                    carbs_consumed_g=0.0,
                    fat_consumed_g=0.0,
                    fiber_consumed_g=0.0,
                    net_calorie_balance=-calories_burned,  # Negative because no food data yet
                    workout_types_done=json.dumps(list(unique_workout_types))
                )
                
                db.add(new_tracker)
                db.commit()
                db.refresh(new_tracker)
                
                return {
                    "status": "success",
                    "message": "Daily activity tracker created with calculated data",
                    "tracker_id": new_tracker.id,
                    "calculated_data": {
                        "total_exercises_done": len(unique_exercises),
                        "total_sets_completed": total_sets,
                        "total_weight_lifted": total_weight,
                        "total_reps_completed": total_reps,
                        "total_workout_time": total_time,
                        "calories_burned_from_activity": calories_burned,
                        "workout_types_done": list(unique_workout_types)
                    }
                }
                
        except Exception as e:
            app_logger.exceptionlogs(f"Error in calculate_and_populate_activity_data: {e}")
            db.rollback()
            return None

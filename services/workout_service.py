

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.workout import Workout, Exercise, ExerciseSet
from utils.enums import WorkoutType, ExerciseType
from utils import app_logger


class WorkoutService:
    
    @staticmethod
    def get_all_workouts(db: Session) -> List[Workout]:
        """Get all default workouts"""
        try:
            return db.query(Workout).filter(Workout.is_default == True).all()
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_all_workouts: {e}")
            return []
    
    @staticmethod
    def get_workout_exercises(workout_id: int, db: Session) -> List[Exercise]:
        """Get all exercises for a specific workout"""
        try:
            return db.query(Exercise).filter(Exercise.workout_id == workout_id).all()
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_workout_exercises: {e}")
            return []
    
    @staticmethod
    def create_exercise_set(user_id: int, exercise_id: int, set_data, db: Session):
        """Create a new exercise set for a user"""
        try:
            # Verify the exercise exists
            exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
            if not exercise:
                return None
            
            exercise_set = ExerciseSet(
                exercise_id=exercise_id,
                weight=set_data.weight,
                reps=set_data.reps,
                time=set_data.time
            )
            
            db.add(exercise_set)
            db.commit()
            db.refresh(exercise_set)
            
            return {
                "status": "success",
                "message": "Exercise set created successfully",
                "set_id": exercise_set.id,
                "exercise_id": exercise_id,
                "weight": exercise_set.weight,
                "reps": exercise_set.reps,
                "time": exercise_set.time
            }
        except Exception as e:
            app_logger.exceptionlogs(f"Error in create_exercise_set: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_daily_workout(user_id: int, workout_date: date, db: Session):
        """Get all exercises and sets performed by user on a specific date"""
        try:
            # If no date provided, use today's date
            if workout_date is None:
                workout_date = date.today()
            # Query to get all exercise sets for the user on the given date
            # Join ExerciseSet -> Exercise -> Workout to get complete workout data
            query = db.query(
                ExerciseSet.id.label('set_id'),
                ExerciseSet.weight,
                ExerciseSet.reps,
                ExerciseSet.time,
                ExerciseSet.created_at,
                Exercise.id.label('exercise_id'),
                Exercise.name.label('exercise_name'),
                Workout.id.label('workout_id'),
                Workout.name.label('workout_name'),
                Workout.workout_type
            ).join(
                Exercise, ExerciseSet.exercise_id == Exercise.id
            ).join(
                Workout, Exercise.workout_id == Workout.id
            ).filter(
                db.func.date(ExerciseSet.created_at) == workout_date
            )
            
            # If we want to filter by user, we need to add user tracking to ExerciseSet
            # For now, we'll get all sets for the date
            results = query.all()
            
            # Group results by workout and exercise
            workout_data = {}
            for result in results:
                workout_key = f"{result.workout_id}_{result.workout_name}"
                if workout_key not in workout_data:
                    workout_data[workout_key] = {
                        "workout_id": result.workout_id,
                        "workout_name": result.workout_name,
                        "workout_type": result.workout_type.value if result.workout_type else None,
                        "exercises": {}
                    }
                
                exercise_key = f"{result.exercise_id}_{result.exercise_name}"
                if exercise_key not in workout_data[workout_key]["exercises"]:
                    workout_data[workout_key]["exercises"][exercise_key] = {
                        "exercise_id": result.exercise_id,
                        "exercise_name": result.exercise_name,
                        "sets": []
                    }
                
                workout_data[workout_key]["exercises"][exercise_key]["sets"].append({
                    "set_id": result.set_id,
                    "weight": result.weight,
                    "reps": result.reps,
                    "time": result.time,
                    "created_at": result.created_at.isoformat()
                })
            
            # Convert to list format
            daily_workouts = []
            for workout_key, workout_info in workout_data.items():
                exercises_list = []
                for exercise_key, exercise_info in workout_info["exercises"].items():
                    exercises_list.append(exercise_info)
                
                workout_info["exercises"] = exercises_list
                daily_workouts.append(workout_info)
            
            return {
                "status": "success",
                "date": workout_date.isoformat(),
                "workouts": daily_workouts,
                "total_workouts": len(daily_workouts)
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_daily_workout: {e}")
            return None
    
    @staticmethod
    def populate_default_workouts_and_exercises(db: Session):
        """Populate default workouts and exercises - Admin function"""
        try:
            # Check if default workouts already exist
            existing_workouts = db.query(Workout).filter(Workout.is_default == True).count()
            if existing_workouts > 0:
                return {"status": "info", "message": "Default workouts already exist"}
            
            # Define exercises for each workout type
            workout_exercises = {
                WorkoutType.CHEST: [
                    "Bench Press", "Incline Bench Press", "Decline Bench Press", 
                    "Dumbbell Flyes", "Push-ups", "Chest Dips", "Cable Crossover",
                    "Incline Dumbbell Press", "Pec Deck Machine", "Diamond Push-ups"
                ],
                WorkoutType.BACK: [
                    "Pull-ups", "Lat Pulldown", "Barbell Rows", "Dumbbell Rows",
                    "Deadlifts", "T-Bar Rows", "Cable Rows", "Face Pulls",
                    "Reverse Flyes", "Hyperextensions"
                ],
                WorkoutType.LEGS: [
                    "Squats", "Leg Press", "Lunges", "Leg Curls", "Leg Extensions",
                    "Calf Raises", "Romanian Deadlifts", "Bulgarian Split Squats",
                    "Hip Thrusts", "Walking Lunges"
                ],
                WorkoutType.SHOULDERS: [
                    "Overhead Press", "Lateral Raises", "Front Raises", "Rear Delt Flyes",
                    "Arnold Press", "Upright Rows", "Shrugs", "Pike Push-ups",
                    "Cable Lateral Raises", "Reverse Pec Deck"
                ],
                WorkoutType.BICEPS: [
                    "Barbell Curls", "Dumbbell Curls", "Hammer Curls", "Preacher Curls",
                    "Cable Curls", "Concentration Curls", "21s", "Chin-ups",
                    "Incline Dumbbell Curls", "Cable Hammer Curls"
                ],
                WorkoutType.TRICEPS: [
                    "Close-Grip Bench Press", "Tricep Dips", "Overhead Tricep Extension",
                    "Tricep Pushdowns", "Diamond Push-ups", "Skull Crushers",
                    "Kickbacks", "Rope Pushdowns", "Bench Dips", "JM Press"
                ],
                WorkoutType.ABS: [
                    "Crunches", "Plank", "Russian Twists", "Leg Raises", "Bicycle Crunches",
                    "Mountain Climbers", "Dead Bug", "Hanging Knee Raises", "Ab Wheel",
                    "V-ups"
                ],
                WorkoutType.CARDIO: [
                    "Treadmill Running", "Cycling", "Elliptical", "Rowing Machine",
                    "Jump Rope", "Burpees", "High Knees", "Jumping Jacks",
                    "Stair Climbing", "Swimming"
                ]
            }
            
            created_workouts = []
            
            # Create workouts and exercises
            for workout_type, exercises in workout_exercises.items():
                # Create workout
                workout = Workout(
                    name=f"{workout_type.value} Workout",
                    workout_type=workout_type,
                    exercise_type=workout_type,  # Using same enum for now
                    is_default=True,
                    user_id=1  # Admin user ID - you might want to create an admin user
                )
                
                db.add(workout)
                db.flush()  # Get the ID without committing
                
                # Create exercises for this workout
                created_exercises = []
                for exercise_name in exercises:
                    exercise = Exercise(
                        name=exercise_name,
                        workout_id=workout.id,
                        user_id=1  # Admin user ID
                    )
                    db.add(exercise)
                    created_exercises.append(exercise_name)
                
                created_workouts.append({
                    "workout_id": workout.id,
                    "workout_name": workout.name,
                    "workout_type": workout_type.value,
                    "exercises_count": len(created_exercises),
                    "exercises": created_exercises
                })
            
            db.commit()
            
            return {
                "status": "success",
                "message": "Default workouts and exercises created successfully",
                "workouts_created": len(created_workouts),
                "data": created_workouts
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in populate_default_workouts_and_exercises: {e}")
            db.rollback()
            return None



from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import func
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
                func.date(ExerciseSet.created_at) == workout_date
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
    
    @staticmethod
    def generate_smart_ppl_workout(user_id: int, target_date: date, db: Session):
        """Generate smart PPL workout based on user's previous workout history"""
        try:
            yesterday = target_date - timedelta(days=1)
            yesterday_workout = WorkoutService.get_daily_workout(user_id, yesterday, db)
            
            # Simple PPL cycle logic
            workout_type = "push"  # Default to push if no previous workout
            
            # Check what user did yesterday and determine today's workout
            if yesterday_workout and yesterday_workout.get("workouts"):
                yesterday_types = []
                for workout in yesterday_workout["workouts"]:
                    workout_type_str = workout.get("workout_type", "").lower()
                    if "chest" in workout_type_str or "shoulder" in workout_type_str or "tricep" in workout_type_str:
                        yesterday_types.append("push")
                    elif "back" in workout_type_str or "bicep" in workout_type_str:
                        yesterday_types.append("pull")
                    elif "legs" in workout_type_str or "abs" in workout_type_str:
                        yesterday_types.append("legs")
                
                # PPL cycle: Push → Pull → Legs → Push → ...
                if "push" in yesterday_types:
                    workout_type = "pull"
                elif "pull" in yesterday_types:
                    workout_type = "legs"
                elif "legs" in yesterday_types:
                    workout_type = "push"
            
            # Generate workout based on determined type
            if workout_type == "push":
                return WorkoutService._generate_push_workout_sets(user_id, target_date, db)
            elif workout_type == "pull":
                return WorkoutService._generate_pull_workout_sets(user_id, target_date, db)
            elif workout_type == "legs":
                return WorkoutService._generate_legs_abs_workout_sets(user_id, target_date, db)
            else:
                return {
                    "status": "error",
                    "message": "Could not determine appropriate workout type"
                }
                
        except Exception as e:
            app_logger.exceptionlogs(f"Error in generate_smart_ppl_workout: {e}")
            return None
    
    @staticmethod
    def _generate_push_workout_sets(user_id: int, target_date: date, db: Session):
        """Generate Push workout sets (Chest, Shoulders, Triceps + Cardio)"""
        try:
            created_sets = []
            
            # Get exercises for each muscle group
            chest_exercises = WorkoutService._get_exercises_by_type(WorkoutType.CHEST, db)
            shoulder_exercises = WorkoutService._get_exercises_by_type(WorkoutType.SHOULDERS, db)
            triceps_exercises = WorkoutService._get_exercises_by_type(WorkoutType.TRICEPS, db)
            cardio_exercises = WorkoutService._get_exercises_by_type(WorkoutType.CARDIO, db)
            
            # Chest exercises
            if chest_exercises:
                # Bench Press - 4 sets
                bench_press = next((ex for ex in chest_exercises if "Bench Press" in ex.name), chest_exercises[0])
                sets_data = [
                    {'weight': 60.0, 'reps': 12, 'time': 0.0},
                    {'weight': 70.0, 'reps': 10, 'time': 0.0},
                    {'weight': 80.0, 'reps': 8, 'time': 0.0},
                    {'weight': 85.0, 'reps': 6, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, bench_press.id, sets_data, target_date, db)
                created_sets.extend(sets)
                
                # Incline Press - 3 sets
                incline_press = next((ex for ex in chest_exercises if "Incline" in ex.name), chest_exercises[1])
                sets_data = [
                    {'weight': 25.0, 'reps': 12, 'time': 0.0},
                    {'weight': 30.0, 'reps': 10, 'time': 0.0},
                    {'weight': 35.0, 'reps': 8, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, incline_press.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Shoulder exercises
            if shoulder_exercises:
                # Overhead Press - 4 sets
                overhead_press = next((ex for ex in shoulder_exercises if "Overhead Press" in ex.name), shoulder_exercises[0])
                sets_data = [
                    {'weight': 40.0, 'reps': 12, 'time': 0.0},
                    {'weight': 45.0, 'reps': 10, 'time': 0.0},
                    {'weight': 50.0, 'reps': 8, 'time': 0.0},
                    {'weight': 55.0, 'reps': 6, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, overhead_press.id, sets_data, target_date, db)
                created_sets.extend(sets)
                
                # Lateral Raises - 3 sets
                lateral_raises = next((ex for ex in shoulder_exercises if "Lateral Raises" in ex.name), shoulder_exercises[1])
                sets_data = [
                    {'weight': 12.0, 'reps': 15, 'time': 0.0},
                    {'weight': 15.0, 'reps': 12, 'time': 0.0},
                    {'weight': 15.0, 'reps': 10, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, lateral_raises.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Triceps exercises
            if triceps_exercises:
                # Tricep Pushdowns - 3 sets
                pushdowns = next((ex for ex in triceps_exercises if "Pushdowns" in ex.name), triceps_exercises[0])
                sets_data = [
                    {'weight': 30.0, 'reps': 15, 'time': 0.0},
                    {'weight': 35.0, 'reps': 12, 'time': 0.0},
                    {'weight': 40.0, 'reps': 10, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, pushdowns.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Cardio - 20 minutes
            if cardio_exercises:
                treadmill = next((ex for ex in cardio_exercises if "Treadmill" in ex.name), cardio_exercises[0])
                sets_data = [{'weight': 0.0, 'reps': 0, 'time': 20.0}]
                sets = WorkoutService._create_exercise_sets_for_date(user_id, treadmill.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            db.commit()
            
            return {
                "status": "success",
                "message": "Push workout generated successfully",
                "workout_type": "push",
                "date": target_date.isoformat(),
                "total_sets": len(created_sets),
                "exercises": ["Bench Press", "Incline Press", "Overhead Press", "Lateral Raises", "Tricep Pushdowns", "Cardio"]
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in _generate_push_workout_sets: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def _generate_pull_workout_sets(user_id: int, target_date: date, db: Session):
        """Generate Pull workout sets (Back, Biceps + Cardio)"""
        try:
            created_sets = []
            
            # Get exercises for each muscle group
            back_exercises = WorkoutService._get_exercises_by_type(WorkoutType.BACK, db)
            biceps_exercises = WorkoutService._get_exercises_by_type(WorkoutType.BICEPS, db)
            cardio_exercises = WorkoutService._get_exercises_by_type(WorkoutType.CARDIO, db)
            
            # Back exercises
            if back_exercises:
                # Pull-ups - 4 sets
                pullups = next((ex for ex in back_exercises if "Pull-ups" in ex.name), back_exercises[0])
                sets_data = [
                    {'weight': 0.0, 'reps': 8, 'time': 0.0},
                    {'weight': 0.0, 'reps': 6, 'time': 0.0},
                    {'weight': 0.0, 'reps': 5, 'time': 0.0},
                    {'weight': 0.0, 'reps': 4, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(pullups.id, sets_data, target_date, db)
                created_sets.extend(sets)
                
                # Barbell Rows - 4 sets
                barbell_rows = next((ex for ex in back_exercises if "Barbell Rows" in ex.name), back_exercises[1])
                sets_data = [
                    {'weight': 60.0, 'reps': 12, 'time': 0.0},
                    {'weight': 70.0, 'reps': 10, 'time': 0.0},
                    {'weight': 80.0, 'reps': 8, 'time': 0.0},
                    {'weight': 85.0, 'reps': 6, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(barbell_rows.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Biceps exercises
            if biceps_exercises:
                # Barbell Curls - 3 sets
                barbell_curls = next((ex for ex in biceps_exercises if "Barbell Curls" in ex.name), biceps_exercises[0])
                sets_data = [
                    {'weight': 30.0, 'reps': 12, 'time': 0.0},
                    {'weight': 35.0, 'reps': 10, 'time': 0.0},
                    {'weight': 40.0, 'reps': 8, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(barbell_curls.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Cardio - 20 minutes
            if cardio_exercises:
                cycling = next((ex for ex in cardio_exercises if "Cycling" in ex.name), cardio_exercises[1])
                sets_data = [{'weight': 0.0, 'reps': 0, 'time': 20.0}]
                sets = WorkoutService._create_exercise_sets_for_date(cycling.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            db.commit()
            
            return {
                "status": "success",
                "message": "Pull workout generated successfully",
                "workout_type": "pull",
                "date": target_date.isoformat(),
                "total_sets": len(created_sets),
                "exercises": ["Pull-ups", "Barbell Rows", "Barbell Curls", "Cardio"]
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in _generate_pull_workout_sets: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def _generate_legs_abs_workout_sets(user_id: int, target_date: date, db: Session):
        """Generate Legs + Abs workout sets (no cardio on leg day)"""
        try:
            created_sets = []
            
            # Get exercises for each muscle group
            leg_exercises = WorkoutService._get_exercises_by_type(WorkoutType.LEGS, db)
            abs_exercises = WorkoutService._get_exercises_by_type(WorkoutType.ABS, db)
            
            # Leg exercises
            if leg_exercises:
                # Squats - 4 sets
                squats = next((ex for ex in leg_exercises if "Squats" in ex.name), leg_exercises[0])
                sets_data = [
                    {'weight': 80.0, 'reps': 12, 'time': 0.0},
                    {'weight': 90.0, 'reps': 10, 'time': 0.0},
                    {'weight': 100.0, 'reps': 8, 'time': 0.0},
                    {'weight': 110.0, 'reps': 6, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(squats.id, sets_data, target_date, db)
                created_sets.extend(sets)
                
                # Leg Press - 3 sets
                leg_press = next((ex for ex in leg_exercises if "Leg Press" in ex.name), leg_exercises[1])
                sets_data = [
                    {'weight': 150.0, 'reps': 15, 'time': 0.0},
                    {'weight': 170.0, 'reps': 12, 'time': 0.0},
                    {'weight': 190.0, 'reps': 10, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(leg_press.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            # Abs exercises
            if abs_exercises:
                # Crunches - 3 sets
                crunches = next((ex for ex in abs_exercises if "Crunches" in ex.name), abs_exercises[0])
                sets_data = [
                    {'weight': 0.0, 'reps': 25, 'time': 0.0},
                    {'weight': 0.0, 'reps': 20, 'time': 0.0},
                    {'weight': 0.0, 'reps': 15, 'time': 0.0}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(crunches.id, sets_data, target_date, db)
                created_sets.extend(sets)
                
                # Plank - 3 sets
                plank = next((ex for ex in abs_exercises if "Plank" in ex.name), abs_exercises[1])
                sets_data = [
                    {'weight': 0.0, 'reps': 0, 'time': 1.0},
                    {'weight': 0.0, 'reps': 0, 'time': 1.2},
                    {'weight': 0.0, 'reps': 0, 'time': 1.5}
                ]
                sets = WorkoutService._create_exercise_sets_for_date(plank.id, sets_data, target_date, db)
                created_sets.extend(sets)
            
            db.commit()
            
            return {
                "status": "success",
                "message": "Legs + Abs workout generated successfully",
                "workout_type": "legs",
                "date": target_date.isoformat(),
                "total_sets": len(created_sets),
                "exercises": ["Squats", "Leg Press", "Crunches", "Plank"]
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in _generate_legs_abs_workout_sets: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def _get_exercises_by_type(workout_type: WorkoutType, db: Session):
        """Helper method to get exercises by workout type"""
        workout = db.query(Workout).filter(
            Workout.workout_type == workout_type,
            Workout.is_default == True
        ).first()
        
        if not workout:
            return []
        
        return db.query(Exercise).filter(Exercise.workout_id == workout.id).all()
    
    @staticmethod
    def _create_exercise_sets_for_date(user_id:int, exercise_id: int, sets_data: list, target_date: date, db: Session):
        """Helper method to create exercise sets for a specific date"""
        created_sets = []
        
        for set_data in sets_data:
            exercise_set = ExerciseSet(
                user_id=user_id,
                exercise_id=exercise_id,
                weight=set_data['weight'],
                reps=set_data['reps'],
                time=set_data['time'],
                created_at=target_date
            )
            db.add(exercise_set)
            created_sets.append({
                "exercise_id": exercise_id,
                "weight": set_data['weight'],
                "reps": set_data['reps'],
                "time": set_data['time']
            })
        
        return created_sets

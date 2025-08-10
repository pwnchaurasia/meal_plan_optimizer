import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_conn import get_db
from db.models.workout import Workout, Exercise, ExerciseSet
from utils.enums import WorkoutType

USER_ID = 1  # Change this to the target user ID
DAYS_BACK = 15  # Number of days to populate (including today)

def get_exercises_by_workout_type(workout_type: WorkoutType, db: Session):
    """Get all exercises for a specific workout type"""
    workout = db.query(Workout).filter(
        Workout.workout_type == workout_type,
        Workout.is_default == True
    ).first()
    
    if not workout:
        return []
    
    exercises = db.query(Exercise).filter(Exercise.workout_id == workout.id).all()
    return exercises


def create_exercise_sets(exercise_id: int, sets_data: list, target_date: date, db: Session):
    """Create multiple exercise sets for an exercise"""
    created_sets = []
    
    for set_data in sets_data:
        exercise_set = ExerciseSet(
            user_id=USER_ID,
            exercise_id=exercise_id,
            weight=set_data['weight'],
            reps=set_data['reps'],
            time=set_data['time'],
            created_at=target_date
        )
        db.add(exercise_set)
        created_sets.append(set_data)
    
    return created_sets


def generate_push_workout(target_date: date, db: Session):
    """Generate Push workout (Chest, Shoulders, Triceps + Cardio)"""
    workout_data = []
    
    # Chest exercises
    chest_exercises = get_exercises_by_workout_type(WorkoutType.CHEST, db)
    if chest_exercises:
        # Bench Press - 4 sets
        bench_press = next((ex for ex in chest_exercises if "Bench Press" in ex.name), chest_exercises[0])
        sets = [
            {'weight': 60.0, 'reps': 12, 'time': 0.0},
            {'weight': 70.0, 'reps': 10, 'time': 0.0},
            {'weight': 80.0, 'reps': 8, 'time': 0.0},
            {'weight': 85.0, 'reps': 6, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(bench_press.id, sets, target_date, db)
        workout_data.append({'exercise': bench_press.name, 'sets': created_sets})
        
        # Incline Dumbbell Press - 3 sets
        incline_press = next((ex for ex in chest_exercises if "Incline" in ex.name), chest_exercises[1])
        sets = [
            {'weight': 25.0, 'reps': 12, 'time': 0.0},
            {'weight': 30.0, 'reps': 10, 'time': 0.0},
            {'weight': 35.0, 'reps': 8, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(incline_press.id, sets, target_date, db)
        workout_data.append({'exercise': incline_press.name, 'sets': created_sets})
    
    # Shoulder exercises
    shoulder_exercises = get_exercises_by_workout_type(WorkoutType.SHOULDERS, db)
    if shoulder_exercises:
        # Overhead Press - 4 sets
        overhead_press = next((ex for ex in shoulder_exercises if "Overhead Press" in ex.name), shoulder_exercises[0])
        sets = [
            {'weight': 40.0, 'reps': 12, 'time': 0.0},
            {'weight': 45.0, 'reps': 10, 'time': 0.0},
            {'weight': 50.0, 'reps': 8, 'time': 0.0},
            {'weight': 55.0, 'reps': 6, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(overhead_press.id, sets, target_date, db)
        workout_data.append({'exercise': overhead_press.name, 'sets': created_sets})
        
        # Lateral Raises - 3 sets
        lateral_raises = next((ex for ex in shoulder_exercises if "Lateral Raises" in ex.name), shoulder_exercises[1])
        sets = [
            {'weight': 12.0, 'reps': 15, 'time': 0.0},
            {'weight': 15.0, 'reps': 12, 'time': 0.0},
            {'weight': 15.0, 'reps': 10, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(lateral_raises.id, sets, target_date, db)
        workout_data.append({'exercise': lateral_raises.name, 'sets': created_sets})
    
    # Triceps exercises
    triceps_exercises = get_exercises_by_workout_type(WorkoutType.TRICEPS, db)
    if triceps_exercises:
        # Tricep Pushdowns - 3 sets
        pushdowns = next((ex for ex in triceps_exercises if "Pushdowns" in ex.name), triceps_exercises[0])
        sets = [
            {'weight': 30.0, 'reps': 15, 'time': 0.0},
            {'weight': 35.0, 'reps': 12, 'time': 0.0},
            {'weight': 40.0, 'reps': 10, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(pushdowns.id, sets, target_date, db)
        workout_data.append({'exercise': pushdowns.name, 'sets': created_sets})
    
    # Cardio - 20 minutes
    cardio_exercises = get_exercises_by_workout_type(WorkoutType.CARDIO, db)
    if cardio_exercises:
        treadmill = next((ex for ex in cardio_exercises if "Treadmill" in ex.name), cardio_exercises[0])
        sets = [{'weight': 0.0, 'reps': 0, 'time': 20.0}]  # 20 minutes
        created_sets = create_exercise_sets(treadmill.id, sets, target_date, db)
        workout_data.append({'exercise': treadmill.name, 'sets': created_sets})
    
    return workout_data


def generate_pull_workout(target_date: date, db: Session):
    """Generate Pull workout (Back, Biceps + Cardio)"""
    workout_data = []
    
    # Back exercises
    back_exercises = get_exercises_by_workout_type(WorkoutType.BACK, db)
    if back_exercises:
        # Pull-ups - 4 sets
        pullups = next((ex for ex in back_exercises if "Pull-ups" in ex.name), back_exercises[0])
        sets = [
            {'weight': 0.0, 'reps': 8, 'time': 0.0},
            {'weight': 0.0, 'reps': 6, 'time': 0.0},
            {'weight': 0.0, 'reps': 5, 'time': 0.0},
            {'weight': 0.0, 'reps': 4, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(pullups.id, sets, target_date, db)
        workout_data.append({'exercise': pullups.name, 'sets': created_sets})
        
        # Barbell Rows - 4 sets
        barbell_rows = next((ex for ex in back_exercises if "Barbell Rows" in ex.name), back_exercises[1])
        sets = [
            {'weight': 60.0, 'reps': 12, 'time': 0.0},
            {'weight': 70.0, 'reps': 10, 'time': 0.0},
            {'weight': 80.0, 'reps': 8, 'time': 0.0},
            {'weight': 85.0, 'reps': 6, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(barbell_rows.id, sets, target_date, db)
        workout_data.append({'exercise': barbell_rows.name, 'sets': created_sets})
        
        # Lat Pulldown - 3 sets
        lat_pulldown = next((ex for ex in back_exercises if "Lat Pulldown" in ex.name), back_exercises[2])
        sets = [
            {'weight': 50.0, 'reps': 12, 'time': 0.0},
            {'weight': 55.0, 'reps': 10, 'time': 0.0},
            {'weight': 60.0, 'reps': 8, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(lat_pulldown.id, sets, target_date, db)
        workout_data.append({'exercise': lat_pulldown.name, 'sets': created_sets})
    
    # Biceps exercises
    biceps_exercises = get_exercises_by_workout_type(WorkoutType.BICEPS, db)
    if biceps_exercises:
        # Barbell Curls - 3 sets
        barbell_curls = next((ex for ex in biceps_exercises if "Barbell Curls" in ex.name), biceps_exercises[0])
        sets = [
            {'weight': 30.0, 'reps': 12, 'time': 0.0},
            {'weight': 35.0, 'reps': 10, 'time': 0.0},
            {'weight': 40.0, 'reps': 8, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(barbell_curls.id, sets, target_date, db)
        workout_data.append({'exercise': barbell_curls.name, 'sets': created_sets})
        
        # Hammer Curls - 3 sets
        hammer_curls = next((ex for ex in biceps_exercises if "Hammer Curls" in ex.name), biceps_exercises[1])
        sets = [
            {'weight': 20.0, 'reps': 12, 'time': 0.0},
            {'weight': 22.5, 'reps': 10, 'time': 0.0},
            {'weight': 25.0, 'reps': 8, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(hammer_curls.id, sets, target_date, db)
        workout_data.append({'exercise': hammer_curls.name, 'sets': created_sets})
    
    # Cardio - 20 minutes
    cardio_exercises = get_exercises_by_workout_type(WorkoutType.CARDIO, db)
    if cardio_exercises:
        cycling = next((ex for ex in cardio_exercises if "Cycling" in ex.name), cardio_exercises[1])
        sets = [{'weight': 0.0, 'reps': 0, 'time': 20.0}]  # 20 minutes
        created_sets = create_exercise_sets(cycling.id, sets, target_date, db)
        workout_data.append({'exercise': cycling.name, 'sets': created_sets})
    
    return workout_data


def generate_legs_abs_workout(target_date: date, db: Session):
    """Generate Legs + Abs workout (no cardio on leg day)"""
    workout_data = []
    
    # Leg exercises
    leg_exercises = get_exercises_by_workout_type(WorkoutType.LEGS, db)
    if leg_exercises:
        # Squats - 4 sets
        squats = next((ex for ex in leg_exercises if "Squats" in ex.name), leg_exercises[0])
        sets = [
            {'weight': 80.0, 'reps': 12, 'time': 0.0},
            {'weight': 90.0, 'reps': 10, 'time': 0.0},
            {'weight': 100.0, 'reps': 8, 'time': 0.0},
            {'weight': 110.0, 'reps': 6, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(squats.id, sets, target_date, db)
        workout_data.append({'exercise': squats.name, 'sets': created_sets})
        
        # Leg Press - 3 sets
        leg_press = next((ex for ex in leg_exercises if "Leg Press" in ex.name), leg_exercises[1])
        sets = [
            {'weight': 150.0, 'reps': 15, 'time': 0.0},
            {'weight': 170.0, 'reps': 12, 'time': 0.0},
            {'weight': 190.0, 'reps': 10, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(leg_press.id, sets, target_date, db)
        workout_data.append({'exercise': leg_press.name, 'sets': created_sets})
        
        # Leg Curls - 3 sets
        leg_curls = next((ex for ex in leg_exercises if "Leg Curls" in ex.name), leg_exercises[2])
        sets = [
            {'weight': 40.0, 'reps': 15, 'time': 0.0},
            {'weight': 45.0, 'reps': 12, 'time': 0.0},
            {'weight': 50.0, 'reps': 10, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(leg_curls.id, sets, target_date, db)
        workout_data.append({'exercise': leg_curls.name, 'sets': created_sets})
        
        # Calf Raises - 4 sets
        calf_raises = next((ex for ex in leg_exercises if "Calf Raises" in ex.name), leg_exercises[3])
        sets = [
            {'weight': 60.0, 'reps': 20, 'time': 0.0},
            {'weight': 70.0, 'reps': 18, 'time': 0.0},
            {'weight': 80.0, 'reps': 15, 'time': 0.0},
            {'weight': 90.0, 'reps': 12, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(calf_raises.id, sets, target_date, db)
        workout_data.append({'exercise': calf_raises.name, 'sets': created_sets})
    
    # Abs exercises
    abs_exercises = get_exercises_by_workout_type(WorkoutType.ABS, db)
    if abs_exercises:
        # Crunches - 3 sets
        crunches = next((ex for ex in abs_exercises if "Crunches" in ex.name), abs_exercises[0])
        sets = [
            {'weight': 0.0, 'reps': 25, 'time': 0.0},
            {'weight': 0.0, 'reps': 20, 'time': 0.0},
            {'weight': 0.0, 'reps': 15, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(crunches.id, sets, target_date, db)
        workout_data.append({'exercise': crunches.name, 'sets': created_sets})
        
        # Plank - 3 sets (time-based)
        plank = next((ex for ex in abs_exercises if "Plank" in ex.name), abs_exercises[1])
        sets = [
            {'weight': 0.0, 'reps': 0, 'time': 1.0},  # 1 minute
            {'weight': 0.0, 'reps': 0, 'time': 1.2},  # 1.2 minutes
            {'weight': 0.0, 'reps': 0, 'time': 1.5}   # 1.5 minutes
        ]
        created_sets = create_exercise_sets(plank.id, sets, target_date, db)
        workout_data.append({'exercise': plank.name, 'sets': created_sets})
        
        # Russian Twists - 3 sets
        russian_twists = next((ex for ex in abs_exercises if "Russian Twists" in ex.name), abs_exercises[2])
        sets = [
            {'weight': 0.0, 'reps': 30, 'time': 0.0},
            {'weight': 0.0, 'reps': 25, 'time': 0.0},
            {'weight': 0.0, 'reps': 20, 'time': 0.0}
        ]
        created_sets = create_exercise_sets(russian_twists.id, sets, target_date, db)
        workout_data.append({'exercise': russian_twists.name, 'sets': created_sets})
    
    return workout_data


def populate_ppl_data(user_id: int, days_back: int = 15):
    """Populate PPL workout data for the specified number of days back"""
    print(f" Starting PPL workout data population for user {user_id}")
    print(f"  Generating data for {days_back} days back from today")
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        total_workouts = 0
        total_sets = 0
        
        # Generate data for each day
        for i in range(days_back):
            target_date = date.today() - timedelta(days=i)
            day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
            
            workout_data = []
            
            if day_of_week == 0:  # Monday - Push
                print(f"  {target_date} (Monday) - Push Day")
                workout_data = generate_push_workout(target_date, db)
            elif day_of_week == 1:  # Tuesday - Pull
                print(f"  {target_date} (Tuesday) - Pull Day")
                workout_data = generate_pull_workout(target_date, db)
            elif day_of_week == 2:  # Wednesday - Legs + Abs
                print(f"  {target_date} (Wednesday) - Legs + Abs Day")
                workout_data = generate_legs_abs_workout(target_date, db)
            elif day_of_week == 3:  # Thursday - Push
                print(f"  {target_date} (Thursday) - Push Day")
                workout_data = generate_push_workout(target_date, db)
            elif day_of_week == 4:  # Friday - Pull
                print(f"{target_date} (Friday) - Pull Day")
                workout_data = generate_pull_workout(target_date, db)
            elif day_of_week == 5:  # Saturday - Legs + Abs
                print(f"{target_date} (Saturday) - Legs + Abs Day")
                workout_data = generate_legs_abs_workout(target_date, db)
            else:  # Sunday - Rest Day
                print(f"{target_date} (Sunday) - Rest Day 😴")
                continue
            
            if workout_data:
                total_workouts += 1
                day_sets = sum(len(exercise['sets']) for exercise in workout_data)
                total_sets += day_sets
                
                print(f"Created {len(workout_data)} exercises with {day_sets} sets")
                for exercise in workout_data:
                    print(f"      • {exercise['exercise']}: {len(exercise['sets'])} sets")
        
        # Commit all changes
        db.commit()
        
        print(f"PPL workout data population completed!")
        print(f"Summary:")
        print(f"   • Total workout days: {total_workouts}")
        print(f"   • Total exercise sets: {total_sets}")
        print(f"   • Date range: {date.today() - timedelta(days=days_back-1)} to {date.today()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


def main():
    """Main function"""
    print("PPL Workout Data Population Script")
    print("=" * 50)
    
    # You can modify these parameters
    USER_ID = 1  # Change this to the target user ID
    DAYS_BACK = 15  # Number of days to populate (including today)
    
    print(f"Target User ID: {USER_ID}")
    print(f"Days to populate: {DAYS_BACK}")
    print()
    
    success = populate_ppl_data(USER_ID, DAYS_BACK)
    
    if success:
        print("Script completed successfully!")
        print("Next steps:")
        print("1. Use the workout APIs to view the generated data")
        print("2. Use the tracker API to calculate activity data from this workout data")
        print("3. Example: POST /tracker/calculate-activity-data?target_date=2024-01-15")
        return 0
    else:
        print("Script failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

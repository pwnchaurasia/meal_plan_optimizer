import sys
import os
from sqlalchemy.orm import Session

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_conn import get_db
from services.workout_service import WorkoutService


def main():
    """Main function to populate default workouts and exercises"""
    print("Starting to populate default workouts and exercises...")
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        result = WorkoutService.populate_default_workouts_and_exercises(db)
        
        if result:
            print(f"{result['message']}")
            
            if result['status'] == 'success':
                print(f"Total workouts created: {result['workouts_created']}")
                print("\nWorkout Details:")
                
                for workout in result['data']:
                    print(f"{workout['workout_name']} ({workout['workout_type']})")
                    print(f"{workout['exercises_count']} exercises:")
                    for exercise in workout['exercises']:
                        print(f"        • {exercise}")
                    print()
            
            elif result['status'] == 'info':
                print("Default workouts already exist in the database.")
        
        else:
            print("Failed to populate workouts and exercises")
            return 1
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return 1
    
    finally:
        db.close()
    
    print("Script completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

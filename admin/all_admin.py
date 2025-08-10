from sqladmin import ModelView

from db.models import User, UserProfile, DailyActivityTracker, ExerciseSet, Workout, Exercise


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]
    # column_exclude_list = [User.workout]


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.id, UserProfile.gender]


class ExerciseSetAdmin(ModelView, model=ExerciseSet):
    column_list = [ExerciseSet.id,
                   ExerciseSet.user_id,
                   ExerciseSet.exercise_id,
                   ExerciseSet.weight,
                   ExerciseSet.reps,
                   ExerciseSet.time,
                   ExerciseSet.created_at]
    page_size = 50
    column_default_sort = ('created_at', True)




class WorkoutAdmin(ModelView, model=Workout):
    column_list = [
        Workout.id,
        Workout.name,
        Workout.workout_type,
        Workout.exercise_type,
        Workout.is_default,
        Workout.user_id
    ]

class ExerciseAdmin(ModelView, model=Exercise):
    column_list = [
        Exercise.id,
        Exercise.user_id,
        Exercise.name,
        Exercise.workout_id
    ]



class DailyActivityTrackerAdmin(ModelView, model=DailyActivityTracker):
    column_list = [DailyActivityTracker.id,
                   DailyActivityTracker.date,
                   DailyActivityTracker.total_exercises_done,
                   DailyActivityTracker.total_sets_completed,
                   DailyActivityTracker.total_weight_lifted,
                   DailyActivityTracker.total_reps_completed,
                   DailyActivityTracker.total_workout_time,
                   DailyActivityTracker.calories_burned_from_activity,
                   DailyActivityTracker.calories_consumed
                   ]






admin_views = [UserAdmin,
               UserProfileAdmin,
               DailyActivityTrackerAdmin,
               ExerciseSetAdmin,
               WorkoutAdmin,
               ExerciseAdmin]
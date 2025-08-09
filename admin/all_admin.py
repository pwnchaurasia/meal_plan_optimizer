from sqladmin import ModelView

from db.models import User, UserProfile, DailyActivityTracker


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]
    # column_exclude_list = [User.workout]


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.id, UserProfile.gender]



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
               DailyActivityTrackerAdmin]
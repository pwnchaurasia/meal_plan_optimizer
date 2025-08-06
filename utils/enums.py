import enum

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class WorkoutType(enum.Enum):
    ABS = "ABS"
    BACK = "CHEST"
    BICEPS = "BICEPS"
    CARDIO = "cardio"
    CHEST = "CHEST"
    LEGS = "LEGS"
    SHOULDERS = "SHOULDERS"
    TRICEPS = "TRICEPS"


class ExerciseType(enum.Enum):
    WEIGHT_AND_RESP = "WEIGHT_AND_RESP"
    REPS = "REPS"
    TIME = "TIME"
    DISTANCE = "DISTANCE"
    DISTANCE_AND_TIME = "DISTANCE_AND_TIME"


class GoalAchievementTimeFrameType(enum.Enum):
    SLOW = "SLOW"
    AVERAGE = "AVERAGE"
    FAST = "FAST"


class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class FoodPreferenceType(enum.Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    FLEXITARIAN = "flexitarian"
    LACTO_VEGETARIAN = "lacto_vegetarian"
    OVO_VEGETARIAN = "ovo_vegetarian"
    LACTO_OVO_VEGETARIAN = "lacto_ovo_vegetarian"
    PALEO = "paleo"
    KETO = "keto"
    RAW_FOOD = "raw_food"
    MEDITERRANEAN = "mediterranean"


class FitnessProvider(enum.Enum):
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    APPLE_HEALTH = "apple_health"
    MANUAL = "manual"
### How to run the code


#### Steps

1. delete the database
2. restart server it will migrate and make the tables

##### Auth

1. Use postman to request for OTP and verify to create the user in db.
2. The auth token will be used to for all other apis

##### User
1. run `CREATE_USER_PROFILE` to create user profile
2. run `CREATE_FITNESS_GOAL` to create user's fitness goals

##### Workouts

1. By default admin will give some workouts and exercises in that workout
2. run `python populate_workouts.py`
3. You can also use api to create a specific dates workout set `GENERATE_SMART_PPL_FOR_DATE` or 
4. To create user's exercise set data for last 15 days including today, `python populate_ppl_workout_data.py`
5. This will create workout set for user


#### Tracker

1. Make sure user's exercise set data exists.
2. run `CALCULATE_ACTIVITY_DATA` in `tracker` to create daily activity data.
3. 


#### Meal Plan
1. Make sure ollama server is running
2. run `CREATE_MEAL_PLAN_FOR_DATE` to create meal plan
3. run `GET_MY_MEALS_FOR_DATE` to see the generated meal plan for that day




## Meal Plan Optimizer

`You can't manage what you can't measure.`

Meal Plan optimizer helps you to be in track with your health goals.
It suggests you meals after tracking your daily activity and lifestyle choices.
Save your meal preference and grocery inventory to get meals suggestions.

### Unique Value proposition

1. Grocery Inventory: Upload the image of the bill, or manually enter what you bought.
2. Activity Tracking: Connect with different health bands and watches to get the detail of your health
3. Workout Progress: Track your workout.


### Assumptions:

- to prepare the meal plan we will be using sleep data of day 1 and then suggesting the meals on day 3rd day
- 



### Technical Strategy

#### API Layer
1. FastAPI-based REST API with automatic OpenAPI documentation
2. Authentication using Mobile number,
3. Registration only happens after a successful otp verification
4. JWT-based authentication

#### Business Logic
1. User Profile Manager
2. Workout Logger
3. Integration with 3rd party apps for logging more detailed data


### Datalayer


1. PostgreSQL: Primary database for user profiles, recipes, meal plans, and health data
2. Redis: 
3. External APIs:

`Note: for local dev I have used sqllite`


### Data Flow Architecture




### Folder structure:

- api: contains all the endpoints
- db: 
  - db/schemas: schema for request and response
  - db/models: Models for interacting with database
- images: all the images in the md file
- integrations: 3rd party integration for   
- services: all the business logic




### High level Architecture

<p align="center">
<img src="images/high_arch.png" width="55%">
</p>




```mermaid







```



### Compliance

1. GDPR: Allow customer to export their data and delete it if they want
2. API Security: OAuth2/JWT authentication
3. 


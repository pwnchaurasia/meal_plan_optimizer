# 🍽️ AI-Powered Meal Planning System

## Overview

A comprehensive meal planning engine that generates personalized meal plans using Large Language Models (LLMs). The system considers user preferences, fitness goals, activity levels, and dietary restrictions to create optimal nutrition plans.

## 🚀 Key Features

### ✅ **Intelligent Meal Generation**
- **LLM-Powered**: Uses OpenAI GPT-4, Anthropic Claude, or local Ollama models
- **Personalized**: Considers user profile, dietary preferences, and restrictions
- **Activity-Aware**: Adjusts calories based on workout data from daily activity tracker
- **Nutritionally Balanced**: Calculates optimal macronutrient ratios

### ✅ **Flexible Configuration**
- **Multiple LLM Providers**: OpenAI, Anthropic, or local Ollama
- **Custom Calorie Targets**: Override default calculations
- **Dietary Accommodations**: Vegetarian, vegan, gluten-free, allergies
- **Cooking Preferences**: Skill level, prep time, cuisine preferences

### ✅ **Real-time Generation**
- **Fast Response**: Optimized for interview demos
- **Update Capability**: Regenerate plans when user data changes
- **Duplicate Prevention**: Checks existing plans before generation

## 🏗️ Architecture

### **Database Models**
```
MealPlan
├── id, user_id, date
├── Nutritional Targets (calories, protein, carbs, fat, fiber)
├── Calculated Totals
├── Generation Metadata (LLM used, time, prompt)
└── Relationships to Meals

Meal
├── id, meal_plan_id, meal_type
├── Basic Info (name, description, cuisine)
├── Nutritional Info (complete breakdown)
├── Cooking Info (prep time, difficulty, ingredients)
├── Dietary Flags (vegetarian, vegan, etc.)
└── User Interaction (rating, notes, favorite)
```

### **Service Layer**
```
MealPlanningService
├── generate_meal_plan() - Main generation logic
├── _gather_user_data() - Collect user preferences
├── _calculate_nutrition_targets() - Smart calorie calculation
├── _get_activity_data() - Workout-based adjustments
└── _save_meal_plan_to_db() - Database persistence

LLMService
├── generate_meal_plan() - Multi-provider LLM calls
├── _generate_with_openai() - OpenAI GPT integration
├── _generate_with_anthropic() - Claude integration
├── _generate_with_ollama() - Local LLM integration
└── create_meal_plan_prompt() - Intelligent prompt engineering
```

## 🔧 API Endpoints

### **Core Endpoints**

#### `POST /meal-plans/generate`
Generate complete meal plan for specific date
```json
{
  "target_date": "2024-01-15",
  "custom_calorie_target": 2200,
  "regenerate_if_exists": false
}
```

#### `GET /meal-plans/?target_date=2024-01-15`
Retrieve meal plan with complete details

#### `POST /meal-plans/quick-generate`
Quick generation with query parameters
```
POST /meal-plans/quick-generate?target_date=2024-01-15&custom_calories=2000&llm_provider=openai&regenerate=true
```

### **Demo Endpoints**

#### `POST /meal-plans/demo/generate-with-activity`
**Perfect for Interview Demo**
- Always regenerates for fresh results
- Shows activity-based calorie adjustment
- Demonstrates all system features
- Includes demo metadata in response

#### `GET /meal-plans/today`
Get today's meal plan with helpful suggestions

#### `GET /meal-plans/summary?target_date=2024-01-15`
Nutritional summary and generation stats

## 🤖 LLM Integration

### **Recommended Setup for Demo**

#### **Option 1: OpenAI GPT-4 (Recommended)**
```env
OPENAI_API_KEY=your-openai-api-key
```
- **Pros**: Reliable, fast, excellent nutrition knowledge
- **Cons**: Requires API key, costs money
- **Best for**: Interview demos, production

#### **Option 2: Anthropic Claude**
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
```
- **Pros**: Great at following complex instructions
- **Cons**: Requires API key, costs money

#### **Option 3: Local Ollama**
```env
OLLAMA_BASE_URL=http://localhost:11434
```
- **Pros**: Free, private, no API limits
- **Cons**: Requires local setup, slower
- **Models**: llama3.1:70b, llama3.1:8b

### **Prompt Engineering**
The system uses sophisticated prompts that include:
- Complete user profile and preferences
- Nutritional targets with percentages
- Activity data and calorie adjustments
- Dietary restrictions and allergies
- Cooking constraints and preferences
- Structured JSON response format

## 📊 Smart Calorie Calculation

### **Base Calculation**
1. **Fitness Goal**: Uses calculated_daily_calories from user's fitness goal
2. **Activity Adjustment**: Adds 60% of calories burned from workouts
3. **Custom Override**: Allows manual calorie target specification

### **Macronutrient Distribution**
- **Protein**: 25% (4 cal/g)
- **Carbohydrates**: 45% (4 cal/g)  
- **Fat**: 30% (9 cal/g)
- **Fiber**: 14g per 1000 calories

### **Example Calculation**
```
Base Calories: 1800 (from fitness goal)
Workout Burn: 400 calories
Activity Adjustment: 400 × 0.6 = 240 calories
Total Target: 1800 + 240 = 2040 calories

Protein: 2040 × 0.25 ÷ 4 = 127.5g
Carbs: 2040 × 0.45 ÷ 4 = 229.5g
Fat: 2040 × 0.30 ÷ 9 = 68g
Fiber: 2040 ÷ 1000 × 14 = 28.6g
```

## 🎯 Interview Demo Workflow

### **Setup Steps**
1. **Configure LLM**: Add OpenAI API key to .env
2. **Create User**: Register user with phone verification
3. **Set Profile**: Add dietary preferences, allergies, cooking skills
4. **Set Fitness Goal**: Define calorie targets and activity level
5. **Generate Workout**: Create workout data for demo day
6. **Generate Meal Plan**: Use demo endpoint

### **Demo Script**
```bash
# 1. Generate workout for demo day
POST /workouts/generate-smart-ppl-workout?target_date=2024-01-15

# 2. Calculate activity data
POST /tracker/calculate-activity-data?target_date=2024-01-15

# 3. Generate meal plan (shows activity integration)
POST /meal-plans/demo/generate-with-activity?target_date=2024-01-15

# 4. Show meal plan details
GET /meal-plans/?target_date=2024-01-15

# 5. Show nutritional summary
GET /meal-plans/summary?target_date=2024-01-15
```

### **Demo Talking Points**
1. **"Real-time AI Generation"** - Show LLM response time
2. **"Activity Integration"** - Explain calorie adjustment from workout
3. **"Personalization"** - Highlight dietary preferences consideration
4. **"Nutritional Accuracy"** - Show macro breakdown and targets
5. **"Flexibility"** - Demonstrate different LLM providers
6. **"Data Persistence"** - Show database storage and retrieval

## 🔄 System Integration

### **Data Flow**
```
User Profile → Fitness Goals → Daily Activity → LLM Prompt → Meal Plan → Database
     ↓              ↓              ↓              ↓           ↓          ↓
Preferences    Calorie Target   Adjustments   AI Response  Parsing   Storage
```

### **Dependencies**
- **User System**: Profile, preferences, allergies
- **Fitness System**: Goals, calorie calculations
- **Activity Tracker**: Workout data, calorie burn
- **LLM Services**: OpenAI/Anthropic/Ollama APIs

## 🚀 Quick Start

### **1. Environment Setup**
```bash
# Copy environment file
cp .env.example .env

# Add your OpenAI API key
OPENAI_API_KEY=your-actual-api-key-here
```

### **2. Database Migration**
```bash
# The new models will be created automatically
# MealPlan and Meal tables will be added
```

### **3. Test Generation**
```bash
# Quick test with default settings
POST /meal-plans/quick-generate

# Full demo with activity integration
POST /meal-plans/demo/generate-with-activity?target_date=2024-01-15
```

## 🎨 Response Examples

### **Successful Generation**
```json
{
  "status": "success",
  "message": "Meal plan generated successfully",
  "meal_plan_id": 1,
  "date": "2024-01-15",
  "target_calories": 2040,
  "total_calories": 2035,
  "meals_created": 5,
  "generation_time": 3.2,
  "llm_provider": "openai",
  "llm_model": "gpt-4"
}
```

### **Complete Meal Plan**
```json
{
  "id": 1,
  "date": "2024-01-15",
  "target_calories": 2040,
  "total_calories": 2035,
  "meals": [
    {
      "meal_type": "breakfast",
      "meal_name": "Protein-Packed Oatmeal Bowl",
      "calories": 420,
      "protein_g": 25,
      "ingredients": ["oats", "protein powder", "berries"],
      "instructions": ["Cook oats", "Mix protein", "Add toppings"],
      "prep_time_minutes": 10,
      "is_vegetarian": true
    }
  ]
}
```

## 🔧 Configuration Options

### **LLM Provider Settings**
```python
custom_config = {
    "llm_provider": "openai",  # openai, anthropic, ollama
    "model_name": "gpt-4",
    "temperature": 0.7,        # Creativity level
    "max_tokens": 4000,        # Response length
    "custom_calorie_target": 2200
}
```

### **Meal Plan Preferences**
```python
custom_preferences = {
    "cuisine_variety": True,
    "include_recipes": True,
    "consider_prep_time": True,
    "high_protein_focus": False
}
```

## 🎯 Perfect for Interviews

This system demonstrates:
- **AI Integration**: Real LLM usage with multiple providers
- **Complex Business Logic**: Nutrition calculations, activity integration
- **Database Design**: Proper relationships and data modeling
- **API Design**: RESTful endpoints with proper error handling
- **Real-time Processing**: Fast response times for demos
- **Scalability**: Flexible architecture for future enhancements

The meal planning system showcases advanced software engineering skills while solving a real-world problem with practical applications.

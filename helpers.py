"""
Helper functions for Cat Calorie Tracker
Contains all calculation, data management, and API functions
"""

import requests
import pandas as pd
from datetime import datetime

# Calorie Calculations
def calculate_resting_energy_requirement(weight_kg):
    """
    Calculate RER (Resting Energy Requirement) using the formula:
    RER = 70 * (weight in kg)^0.75
    
    Args:
        weight_kg (float): Cat's weight in kilograms
        
    Returns:
        float: Resting energy requirement in kcal/day
    """
    return 70 * (weight_kg ** 0.75)


def calculate_daily_energy_requirement(rer, activity_level, life_stage, body_condition):
    """
    Calculate DER (Daily Energy Requirement) based on cat's characteristics.
    DER = RER * multiplier (based on various factors)
    
    Args:
        rer (float): Resting energy requirement
        activity_level (str): Activity level (very_young, low, moderate, high)
        life_stage (str): Life stage (kitten, adult, senior)
        body_condition (str): Body condition (underweight, ideal, overweight)
        
    Returns:
        float: Daily energy requirement in kcal/day
    """
    multipliers = {
        'kitten_0_4_months': 2.5,
        'kitten_4_12_months': 2.0,
        'adult_neutered': 1.2,
        'adult_intact': 1.4,
        'adult_active': 1.6,
        'senior': 1.1,
        'weight_loss': 0.8,
        'weight_gain': 1.3
    }
    
    # Determine the appropriate multiplier based on characteristics
    if life_stage == 'kitten' and activity_level == 'very_young':
        multiplier = multipliers['kitten_0_4_months']
    elif life_stage == 'kitten':
        multiplier = multipliers['kitten_4_12_months']
    elif body_condition == 'overweight':
        multiplier = multipliers['weight_loss']
    elif body_condition == 'underweight':
        multiplier = multipliers['weight_gain']
    elif life_stage == 'senior':
        multiplier = multipliers['senior']
    elif activity_level == 'low':
        multiplier = multipliers['adult_neutered']
    elif activity_level == 'moderate':
        multiplier = multipliers['adult_intact']
    else:  # high activity
        multiplier = multipliers['adult_active']
    
    return rer * multiplier


def calculate_serving_size(food_calories_per_100g, target_calories, food_type='dry'):
    """
    Calculate serving size in grams and cups based on target calories.
    
    Args:
        food_calories_per_100g (float): Calories per 100g of the food
        target_calories (float): Target calorie amount for this serving
        food_type (str): Type of food ('dry' or 'wet')
        
    Returns:
        tuple: (grams_needed, cups) - serving size in grams and cups
    """
    # Calculate grams needed
    grams_needed = (target_calories / food_calories_per_100g) * 100
    
    # Convert to cups based on food type
    if food_type == 'dry':
        cups = grams_needed / 113  # ~113g per cup for dry food
    else:  # wet food
        cups = grams_needed / 227  # ~227g per cup for wet food
    
    return grams_needed, cups


def kg_to_lbs(weight_kg):
    """Convert kilograms to pounds"""
    return weight_kg * 2.20462


def lbs_to_kg(weight_lbs):
    """Convert pounds to kilograms"""
    return weight_lbs / 2.20462


def calculate_age_in_months(years, months):
    """
    Calculate total age in months from years and months.
    
    Args:
        years (int): Number of years
        months (int): Number of months
        
    Returns:
        int: Total age in months
    """
    return (years * 12) + months


def determine_life_stage(age_months):
    """
    Determine life stage based on age in months.
    
    Args:
        age_months (int): Age in months
        
    Returns:
        str: Life stage ('kitten', 'adult', or 'senior')
    """
    if age_months < 12:
        return 'kitten'
    elif age_months < 120:  # 10 years
        return 'adult'
    else:
        return 'senior'


def determine_activity_level_from_age(age_months):
    """
    Suggest activity level based on age.
    Very young kittens have highest energy needs.
    
    Args:
        age_months (int): Age in months
        
    Returns:
        str: Suggested activity level
    """
    if age_months <= 4:
        return 'very_young'
    elif age_months < 12:
        return 'high'  # Older kittens are very active
    elif age_months < 84:  # Less than 7 years
        return 'moderate'
    else:
        return 'low'  # Older cats tend to be less active


def format_age_display(years, months):
    """
    Format age for display.
    
    Args:
        years (int): Number of years
        months (int): Number of months
        
    Returns:
        str: Formatted age string
    """
    if years == 0:
        return f"{months} month{'s' if months != 1 else ''}"
    elif months == 0:
        return f"{years} year{'s' if years != 1 else ''}"
    else:
        return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"


# Food Database Management
def load_default_food_database():
    """
    Load default food database with popular commercial cat food brands.
    Includes 25+ dry foods and 25+ wet foods covering major brands.
    
    Returns:
        dict: Dictionary with 'dry' and 'wet' food lists
    """
    default_foods = {
        'dry': [
            # Premium brands
            {'brand': 'Royal Canin Indoor Adult', 'calories_per_100g': 375},
            {'brand': 'Royal Canin Kitten', 'calories_per_100g': 400},
            {'brand': 'Royal Canin Senior', 'calories_per_100g': 365},
            {'brand': 'Hill\'s Science Diet Adult Indoor', 'calories_per_100g': 370},
            {'brand': 'Hill\'s Science Diet Kitten', 'calories_per_100g': 395},
            {'brand': 'Hill\'s Science Diet Senior 7+', 'calories_per_100g': 360},
            {'brand': 'Hill\'s Prescription Diet c/d', 'calories_per_100g': 373},
            {'brand': 'Purina Pro Plan Adult', 'calories_per_100g': 420},
            {'brand': 'Purina Pro Plan Kitten', 'calories_per_100g': 437},
            {'brand': 'Purina Pro Plan Weight Management', 'calories_per_100g': 329},
            {'brand': 'Blue Buffalo Wilderness Adult', 'calories_per_100g': 416},
            {'brand': 'Blue Buffalo Life Protection Adult', 'calories_per_100g': 385},
            {'brand': 'Blue Buffalo Kitten', 'calories_per_100g': 405},
            {'brand': 'Wellness CORE Grain-Free', 'calories_per_100g': 421},
            {'brand': 'Wellness Complete Health Adult', 'calories_per_100g': 390},
            {'brand': 'Orijen Cat & Kitten', 'calories_per_100g': 406},
            {'brand': 'Orijen Six Fish', 'calories_per_100g': 402},
            {'brand': 'Taste of the Wild Canyon River', 'calories_per_100g': 390},
            {'brand': 'Nutro Indoor Adult', 'calories_per_100g': 368},
            {'brand': 'Natural Balance Indoor', 'calories_per_100g': 375},
            
            # Mid-range brands
            {'brand': 'Iams ProActive Health Adult', 'calories_per_100g': 400},
            {'brand': 'Iams Kitten', 'calories_per_100g': 414},
            {'brand': 'Meow Mix Original Choice', 'calories_per_100g': 350},
            {'brand': 'Friskies Indoor Delights', 'calories_per_100g': 359},
            {'brand': 'Purina Cat Chow Naturals', 'calories_per_100g': 378},
            {'brand': 'Purina ONE Indoor Advantage', 'calories_per_100g': 389},
            {'brand': '9Lives Daily Essentials', 'calories_per_100g': 345},
            {'brand': 'Rachael Ray Nutrish Natural', 'calories_per_100g': 361},
            
            # Specialty diets
            {'brand': 'Royal Canin Urinary SO', 'calories_per_100g': 371},
            {'brand': 'Hill\'s Prescription Diet k/d', 'calories_per_100g': 380},
        ],
        'wet': [
            # Premium brands - Pate
            {'brand': 'Fancy Feast Classic Pate Chicken', 'calories_per_100g': 90},
            {'brand': 'Fancy Feast Classic Pate Turkey', 'calories_per_100g': 88},
            {'brand': 'Fancy Feast Classic Pate Beef', 'calories_per_100g': 92},
            {'brand': 'Sheba Perfect Portions Pate', 'calories_per_100g': 85},
            {'brand': 'Royal Canin Instinctive Loaf', 'calories_per_100g': 93},
            {'brand': 'Royal Canin Kitten Loaf', 'calories_per_100g': 105},
            {'brand': 'Hill\'s Science Diet Adult Savory Chicken', 'calories_per_100g': 100},
            {'brand': 'Hill\'s Science Diet Kitten Pate', 'calories_per_100g': 112},
            {'brand': 'Blue Buffalo Wilderness Chicken Pate', 'calories_per_100g': 105},
            {'brand': 'Blue Buffalo Tastefuls Pate', 'calories_per_100g': 95},
            
            # Premium brands - Chunks/Gravy
            {'brand': 'Fancy Feast Gravy Lovers', 'calories_per_100g': 78},
            {'brand': 'Friskies Classic Pate Mixed Grill', 'calories_per_100g': 95},
            {'brand': 'Friskies Gravy Sensations', 'calories_per_100g': 82},
            {'brand': 'Purina Pro Plan Savor Adult', 'calories_per_100g': 107},
            {'brand': 'Wellness CORE Grain-Free Pate', 'calories_per_100g': 110},
            {'brand': 'Wellness Complete Health Pate', 'calories_per_100g': 100},
            
            # Natural/Grain-free
            {'brand': 'Weruva Cats in the Kitchen', 'calories_per_100g': 75},
            {'brand': 'Tiki Cat Luau Succulent Chicken', 'calories_per_100g': 70},
            {'brand': 'Instinct Original Grain-Free', 'calories_per_100g': 108},
            {'brand': 'Nutro Perfect Portions Pate', 'calories_per_100g': 88},
            {'brand': 'Natural Balance Limited Ingredient', 'calories_per_100g': 92},
            
            # Value brands
            {'brand': 'Meow Mix Simple Servings', 'calories_per_100g': 84},
            {'brand': '9Lives Meaty Pate', 'calories_per_100g': 91},
            {'brand': 'Purina Cat Chow Pate', 'calories_per_100g': 90},
            {'brand': 'Iams Pate Adult', 'calories_per_100g': 98},
            
            # Specialty
            {'brand': 'Hill\'s Prescription Diet c/d', 'calories_per_100g': 94},
            {'brand': 'Royal Canin Urinary SO', 'calories_per_100g': 89},
            {'brand': 'Hill\'s Prescription Diet k/d', 'calories_per_100g': 102},
            {'brand': 'Royal Canin Recovery', 'calories_per_100g': 115},
        ]
    }
    return default_foods


def add_food_to_database(food_database, food_type, brand_name, calories_per_100g):
    """
    Add a new food item to the database.
    
    Args:
        food_database (dict): Current food database
        food_type (str): 'dry' or 'wet'
        brand_name (str): Brand/product name
        calories_per_100g (int): Calories per 100g
        
    Returns:
        dict: Updated food database
    """
    new_food = {
        'brand': brand_name,
        'calories_per_100g': calories_per_100g
    }
    food_database[food_type].append(new_food)
    return food_database


def get_food_by_brand(food_database, food_type, brand_name):
    """
    Get food item details by brand name.
    
    Args:
        food_database (dict): Food database
        food_type (str): 'dry' or 'wet'
        brand_name (str): Brand name to search for
        
    Returns:
        dict: Food item details or None if not found
    """
    for food in food_database.get(food_type, []):
        if food['brand'] == brand_name:
            return food
    return None


# API Integration
def fetch_pet_food_data(product_name):
    """
    Fetch pet food nutritional data from Open Pet Food Facts API.
    This API is specifically designed for pet food products.
    
    Args:
        product_name (str): Product name to search for
        
    Returns:
        dict: Product information including brand, name, and calories
              Returns None if not found or on error
    """
    try:
        # Use Open Pet Food Facts API (dedicated to pet food)
        url = "https://world.openpetfoodfacts.org/cgi/search.pl"
        params = {
            'search_terms': product_name,
            'search_simple': 1,
            'json': 1,
            'page_size': 20,  # Get more results for better matches
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('products'):
                # Filter for cat food specifically
                cat_foods = [
                    p for p in data['products']
                    if 'cat' in p.get('categories', '').lower() or
                       'cat' in p.get('product_name', '').lower()
                ]
                
                # Use cat food if found, otherwise use first result
                product = cat_foods[0] if cat_foods else data['products'][0]
                
                return {
                    'brand': product.get('brands', 'Unknown'),
                    'product_name': product.get('product_name', 'Unknown'),
                    'categories': product.get('categories', 'Unknown'),
                    'calories_per_100g': product.get('nutriments', {}).get('energy-kcal_100g', None),
                    'url': f"https://world.openpetfoodfacts.org/product/{product.get('code', '')}"
                }
        return None
    except Exception as e:
        print(f"API Error: {str(e)}")
        return None


# Cat Profile Management
def create_cat_profile(name, breed, weight_kg, age_years, age_months, life_stage, 
                      activity_level, body_condition, is_neutered):
    """
    Create a complete cat profile with calculated calorie requirements.
    
    Args:
        name (str): Cat's name
        breed (str): Cat's breed
        weight_kg (float): Weight in kilograms
        age_years (int): Age in years
        age_months (int): Age in months (0-11)
        life_stage (str): Life stage (kitten, adult, senior)
        activity_level (str): Activity level
        body_condition (str): Body condition
        is_neutered (bool): Spayed/neutered status
        
    Returns:
        dict: Complete cat profile with RER and DER calculated
    """
    total_age_months = calculate_age_in_months(age_years, age_months)
    rer = calculate_resting_energy_requirement(weight_kg)
    der = calculate_daily_energy_requirement(rer, activity_level, life_stage, body_condition)
    
    return {
        'name': name,
        'breed': breed,
        'weight_kg': weight_kg,
        'age_years': age_years,
        'age_months': age_months,
        'total_age_months': total_age_months,
        'life_stage': life_stage,
        'activity_level': activity_level,
        'body_condition': body_condition,
        'is_neutered': is_neutered,
        'rer': rer,
        'der': der,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def update_cat_profile(cat_profile, **kwargs):
    """
    Update cat profile and recalculate calories if weight or other factors change.
    
    Args:
        cat_profile (dict): Existing cat profile
        **kwargs: Fields to update
        
    Returns:
        dict: Updated cat profile
    """
    # Update provided fields
    for key, value in kwargs.items():
        if key in cat_profile or key in ['age_years', 'age_months']:
            cat_profile[key] = value
    
    # Recalculate total age if age components changed
    if 'age_years' in kwargs or 'age_months' in kwargs:
        cat_profile['total_age_months'] = calculate_age_in_months(
            cat_profile.get('age_years', 0),
            cat_profile.get('age_months', 0)
        )
    
    # Recalculate RER and DER if relevant fields changed
    if any(k in kwargs for k in ['weight_kg', 'activity_level', 'life_stage', 'body_condition', 'age_years', 'age_months']):
        cat_profile['rer'] = calculate_resting_energy_requirement(cat_profile['weight_kg'])
        cat_profile['der'] = calculate_daily_energy_requirement(
            cat_profile['rer'],
            cat_profile['activity_level'],
            cat_profile['life_stage'],
            cat_profile['body_condition']
        )
    
    return cat_profile


# Feeding Schedule Management
def create_meal(cat_name, meal_time, food_type, brand, food_calories_per_100g, 
               percentage_of_daily, daily_target_calories):
    """
    Create a meal entry with calculated serving sizes.
    
    Args:
        cat_name (str): Name of the cat
        meal_time (str): Time of meal (HH:MM format)
        food_type (str): 'dry' or 'wet'
        brand (str): Food brand name
        food_calories_per_100g (float): Calories per 100g of the food
        percentage_of_daily (float): Percentage of daily calories for this meal
        daily_target_calories (float): Cat's daily calorie target
        
    Returns:
        dict: Complete meal information with serving sizes
    """
    target_calories = (percentage_of_daily / 100) * daily_target_calories
    grams, cups = calculate_serving_size(food_calories_per_100g, target_calories, food_type)
    
    return {
        'cat_name': cat_name,
        'time': meal_time,
        'food_type': food_type,
        'brand': brand,
        'percentage': percentage_of_daily,
        'target_calories': target_calories,
        'grams': grams,
        'cups': cups
    }


def calculate_daily_totals(feeding_schedule, cat_name):
    """
    Calculate total daily calories and servings for a specific cat.
    
    Args:
        feeding_schedule (list): List of all meals
        cat_name (str): Name of cat to calculate for
        
    Returns:
        dict: Total calories, grams, cups, and meal count
    """
    cat_meals = [meal for meal in feeding_schedule if meal['cat_name'] == cat_name]
    
    if not cat_meals:
        return {
            'total_calories': 0,
            'total_grams': 0,
            'total_cups': 0,
            'meal_count': 0
        }
    
    return {
        'total_calories': sum(meal['target_calories'] for meal in cat_meals),
        'total_grams': sum(meal['grams'] for meal in cat_meals),
        'total_cups': sum(meal['cups'] for meal in cat_meals),
        'meal_count': len(cat_meals)
    }


def get_feeding_balance_status(total_calories, target_calories, threshold=50):
    """
    Determine if feeding schedule is balanced, over, or under target.
    
    Args:
        total_calories (float): Total daily calories from schedule
        target_calories (float): Target daily calories
        threshold (float): Acceptable difference threshold (default 50 kcal)
        
    Returns:
        tuple: (status, difference) where status is 'balanced', 'over', or 'under'
    """
    difference = total_calories - target_calories
    
    if abs(difference) <= threshold:
        return 'balanced', difference
    elif difference > 0:
        return 'over', difference
    else:
        return 'under', difference


def sort_meals_by_time(meals):
    """
    Sort meals by time of day.
    
    Args:
        meals (list): List of meal dictionaries
        
    Returns:
        list: Sorted list of meals
    """
    return sorted(meals, key=lambda x: x['time'])


# Data Formatting and Validation
def format_time_12hr(time_24hr):
    """
    Convert 24-hour time to 12-hour format with AM/PM.
    
    Args:
        time_24hr (str): Time in HH:MM format
        
    Returns:
        str: Time in 12-hour format with AM/PM
    """
    from datetime import datetime
    time_obj = datetime.strptime(time_24hr, "%H:%M")
    return time_obj.strftime("%I:%M %p")


def validate_weight(weight_kg):
    """
    Validate that weight is within reasonable range for cats.
    
    Args:
        weight_kg (float): Weight in kilograms
        
    Returns:
        tuple: (is_valid, message)
    """
    if weight_kg < 0.5:
        return False, "Weight seems too low. Please check the value."
    elif weight_kg > 15:
        return False, "Weight seems very high. Please verify."
    return True, "Weight is valid"


def validate_calories(calories_per_100g, food_type):
    """
    Validate calorie content is reasonable for food type.
    
    Args:
        calories_per_100g (float): Calories per 100g
        food_type (str): 'dry' or 'wet'
        
    Returns:
        tuple: (is_valid, message)
    """
    if food_type == 'dry':
        if calories_per_100g < 300 or calories_per_100g > 500:
            return False, "Dry food calories typically range 300-500 kcal/100g"
    else:  # wet food
        if calories_per_100g < 60 or calories_per_100g > 150:
            return False, "Wet food calories typically range 60-150 kcal/100g"
    return True, "Calories are valid"


# Analytics and Statistics
def get_food_type_breakdown(feeding_schedule, cat_name):
    """
    Calculate breakdown of calories by food type.
    
    Args:
        feeding_schedule (list): List of all meals
        cat_name (str): Name of cat to analyze
        
    Returns:
        dict: Calories by food type {'dry': X, 'wet': Y}
    """
    cat_meals = [meal for meal in feeding_schedule if meal['cat_name'] == cat_name]
    
    breakdown = {'dry': 0, 'wet': 0}
    for meal in cat_meals:
        breakdown[meal['food_type']] += meal['target_calories']
    
    return breakdown


def calculate_percentage_of_target(actual, target):
    """
    Calculate what percentage of target the actual value represents.
    
    Args:
        actual (float): Actual value
        target (float): Target value
        
    Returns:
        float: Percentage (0-100+)
    """
    if target == 0:
        return 0
    return (actual / target) * 100


# Export/Import Helpers
def export_cat_profile_to_dict(cat_profile):
    """
    Export cat profile to dictionary format for JSON serialization.
    
    Args:
        cat_profile (dict): Cat profile
        
    Returns:
        dict: Serializable dictionary
    """
    return cat_profile.copy()


def export_feeding_schedule_to_dataframe(feeding_schedule):
    """
    Convert feeding schedule to pandas DataFrame for analysis.
    
    Args:
        feeding_schedule (list): List of meals
        
    Returns:
        pd.DataFrame: Feeding schedule as DataFrame
    """
    if not feeding_schedule:
        return pd.DataFrame()
    return pd.DataFrame(feeding_schedule)
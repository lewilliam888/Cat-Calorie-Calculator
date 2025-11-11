# 🐱 Cat Calorie and Nutrition Calculator

A web application that helps cat owners calculate precise calorie requirements and create optimal feeding schedules based on their cat's individual characteristics.

[Live Demo](https://cat-calorie-calculator.streamlit.app/)

## 📖 Project Overview

This interactive web app allows users to create detailed profiles for their cats and automatically calculate daily calorie needs based on age, weight, activity level, and health status. The app provides precise serving sizes in both grams and cups, manages feeding schedules, and visualizes nutritional data through interactive charts.

**Built with:** Python, Streamlit, Pandas, Plotly, Open Pet Food Facts API

## Key Features

- 🐈 **Age-Based Profiling** - Smart input system converts years/months to life stages automatically
- 📊 **Automatic Calorie Calculations** - Uses veterinary RER/DER formulas for precise nutrition
- 🍽️ **59 Pre-loaded Foods** - 30 dry foods and 29 wet foods from major brands
- ⏰ **Smart Feeding Schedules** - Time-based meal planning with automatic serving size calculations
- 📈 **Visual Analytics** - Interactive charts showing calorie distribution and food type breakdowns
- 🌾🥫 **Clear Food Differentiation** - Separate tracking and totals for dry vs wet food
- 🔍 **API Integration** - Search 10,000+ pet foods via Open Pet Food Facts database
- 💾 **Multi-Cat Support** - Manage unlimited cat profiles with individual schedules

*Enter your cat's age and weight, select their food, and get exact feeding amounts in grams and cups for every meal.*

## 🛠️ Technical Implementation

### Technologies Used
- **Streamlit** - Web framework for interactive dashboards
- **Pandas** - Data manipulation and nutritional analysis
- **Plotly** - Interactive data visualizations and charts
- **Requests** - API integration for pet food database
- **Python 3.11** - Core programming language

### Data Sources
- **Open Pet Food Facts API** - Collaborative database of 10,000+ pet food products
- **AAFCO Guidelines** - Association of American Feed Control Officials nutritional standards
- **Veterinary Formulas** - Industry-standard RER/DER calculations for feline nutrition

### Architecture
- **`app.py`** (30KB) - Main Streamlit UI with 4 pages: Cat Profile, Food Database, Feeding Schedule, Dashboard
- **`helpers.py`** (24KB) - 40+ utility functions including calorie calculations, API integration, and data validation
- Session-based storage for fast, in-memory data management
- Modular design with separation of concerns (UI vs business logic)
- Vectorized calculations for instant serving size computations

### Calorie Calculation Method
```python
# Resting Energy Requirement (RER)
RER = 70 × (weight_kg)^0.75

# Daily Energy Requirement (DER)
DER = RER × multiplier

# Multipliers:
# - Kitten (0-4 months): 2.5x
# - Kitten (4-12 months): 2.0x
# - Adult (neutered): 1.2x
# - Adult (active): 1.6x
# - Senior: 1.1x
# - Weight loss: 0.8x
```

## 🎯 Project Goals & Learning Outcomes

This project demonstrates:
- **API Integration** - Fetching nutritional data from Open Pet Food Facts database
- **Domain Knowledge Application** - Implementing veterinary nutrition formulas and AAFCO standards
- **Data Management** - Managing complex relational data (cats, foods, schedules) in session state
- **User Experience Design** - Creating intuitive interfaces for users with varying expertise levels
- **Calculation Optimization** - Efficient serving size and calorie computations across multiple meals
- **Data Visualization** - Interactive charts for calorie distribution and nutritional analysis

### Problem Solved
New cat owners often struggle with:
- Understanding if their cat is a "kitten" or "adult" (solved with age input)
- Finding calorie information for their specific brand (solved with 59 pre-loaded foods + API)
- Calculating correct portion sizes (solved with automatic gram/cup conversions)
- Balancing dry and wet food (solved with food type breakdown and mixing ratios)

## 📊 Database & Coverage

### Pre-loaded Food Database
- **30 Dry Foods** - Royal Canin, Hill's Science Diet, Purina Pro Plan, Blue Buffalo, Wellness, Orijen, and more
- **29 Wet Foods** - Fancy Feast, Sheba, Friskies, Wellness CORE, Tiki Cat, and more
- **All Price Ranges** - Value ($10-20), mid-range ($20-40), and premium ($40-60+) options
- **All Life Stages** - Kitten, adult, and senior formulas
- **Special Diets** - Weight management, urinary health, kidney support

### API Access
- **10,000+ Pet Food Products** via Open Pet Food Facts
- Real-time nutritional data lookup
- Auto-filtering for cat-specific products
- Graceful fallback to manual entry

### Quick Start (5 minutes)

1. **Create Cat Profile** (2 min)
   - Enter name, breed, age (years + months)
   - Input weight in kg
   - System auto-suggests life stage and activity level
   - Get instant RER and DER calculations

2. **Browse Food Database** (1 min)
   - View 59 pre-loaded foods
   - Search by brand or add custom foods
   - Optional: Search API for additional products

3. **Create Feeding Schedule** (2 min)
   - Set meal times throughout the day
   - Choose food type (dry/wet) and brand
   - Allocate percentage of daily calories
   - Get automatic serving sizes in grams and cups

4. **View Dashboard** (instant)
   - See calorie distribution pie chart
   - View feeding timeline
   - Check dry vs wet food breakdown
   - Monitor balance against target

## 📈 Performance & Scale

- **Calculation Speed** - < 1ms for RER/DER calculations
- **Database Load Time** - 59 foods load in < 100ms
- **Chart Rendering** - Interactive Plotly charts render in < 500ms
- **Memory Footprint** - ~3KB for food database, minimal overhead
- **Scalability** - Supports unlimited cats and feeding schedules per session

## 📚 Documentation

The project includes comprehensive documentation:
- **README.md** - Getting started and overview
- **AGE_GUIDE.md** - Complete reference for cat life stages and age-based nutrition
- **API_DOCUMENTATION.md** - Open Pet Food Facts API integration guide
- **ARCHITECTURE.md** - Technical architecture and code structure
- **FOOD_DATABASE.md** - Complete list of 59 pre-loaded foods
- **FEEDING_SCHEDULE_UPDATE.md** - Guide to the feeding schedule display
- **PROJECT_SUMMARY.md** - Comprehensive feature overview

## 🎓 Use Cases

### Scenario 1: New Kitten Owner
**Input:** 3 months old, 1.5 kg
**Output:** DER = 315 kcal/day, 4 meals suggested, exact serving sizes

### Scenario 2: Weight Management
**Input:** 5 years old, overweight, 7 kg
**Output:** DER reduced to 80% for weight loss, meal plan with reduced portions

### Scenario 3: Senior Cat Care
**Input:** 12 years old, 4 kg, low activity
**Output:** DER = 194 kcal/day with senior-appropriate recommendations

### Scenario 4: Multi-Cat Household
**Input:** 3 cats (kitten, adult, senior)
**Output:** Individual profiles, separate schedules, different calorie targets

## 🔮 Future Enhancements

Potential features for future versions:
- [ ] Weight tracking over time with trend charts
- [ ] Export to PDF feeding schedule
- [ ] Email/SMS feeding reminders
- [ ] Shopping list generator based on weekly needs
- [ ] Barcode scanning for instant food lookup
- [ ] Integration with smart feeders
- [ ] Treat calorie calculator
- [ ] Multiple day meal planning

## 🔗 Links

- **Live Application**: [Cat Calorie Calculator](https://cat-calorie-calculator.streamlit.app/)
- **GitHub Repository**: [View Code](https://github.com/lewilliam888/Cat-Calorie-Calculator)

## 👨‍💻 Developer

**William Le**

---

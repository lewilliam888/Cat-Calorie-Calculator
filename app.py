import streamlit as st
import pandas as pd
from datetime import time
import plotly.graph_objects as go
import plotly.express as px

# Import helper functions
from helpers import (
    # Calculations
    calculate_resting_energy_requirement,
    calculate_daily_energy_requirement,
    calculate_serving_size,
    kg_to_lbs,
    calculate_age_in_months,
    determine_life_stage,
    determine_activity_level_from_age,
    format_age_display,
    
    # Food database
    load_default_food_database,
    add_food_to_database,
    get_food_by_brand,
    
    # API
    fetch_pet_food_data,
    
    # Cat profiles
    create_cat_profile,
    update_cat_profile,
    
    # Feeding schedule
    create_meal,
    calculate_daily_totals,
    get_feeding_balance_status,
    sort_meals_by_time,
    format_time_12hr,
    
    # Analytics
    get_food_type_breakdown,
    calculate_percentage_of_target,
    
    # Validation
    validate_weight,
    validate_calories,
)

# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="Cat Calorie Tracker",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================

if 'cats' not in st.session_state:
    st.session_state.cats = []

if 'feeding_schedule' not in st.session_state:
    st.session_state.feeding_schedule = []

if 'food_database' not in st.session_state:
    st.session_state.food_database = load_default_food_database()

# ==================== HEADER ====================

st.markdown('<h1 class="main-header">🐱 Cat Calorie Tracker</h1>', unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================

st.sidebar.title("Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Go to",
    ["🐈 Cat Profile", "🍽️ Food Database", "⏰ Feeding Schedule", "📊 Dashboard"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Start by creating a cat profile, then add foods to the database, and finally create a feeding schedule!")

# ==================== PAGE: CAT PROFILE ====================

if page == "🐈 Cat Profile":
    st.header("🐈 Cat Profile Management")
    st.markdown("Create and manage profiles for your cats with automatic calorie calculations.")
    
    with st.form("cat_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            cat_name = st.text_input("Cat's Name *", placeholder="e.g., Whiskers")
            cat_breed = st.text_input("Breed", placeholder="e.g., Domestic Shorthair")
            
            st.markdown("**Age**")
            age_col1, age_col2 = st.columns(2)
            with age_col1:
                age_years = st.number_input(
                    "Years",
                    min_value=0,
                    max_value=25,
                    value=2,
                    step=1,
                    help="How many years old is your cat?"
                )
            with age_col2:
                age_months = st.number_input(
                    "Months",
                    min_value=0,
                    max_value=11,
                    value=0,
                    step=1,
                    help="Additional months (0-11)"
                )
            
            # Calculate total age and determine life stage
            total_months = calculate_age_in_months(age_years, age_months)
            auto_life_stage = determine_life_stage(total_months)
            auto_activity = determine_activity_level_from_age(total_months)
            
            # Display age info
            age_display = format_age_display(age_years, age_months)
            if total_months < 12:
                st.info(f"🐱 {age_display} old - **Kitten** (needs higher calories)")
            elif total_months < 120:
                st.info(f"🐱 {age_display} old - **Adult cat**")
            else:
                st.info(f"🐱 {age_display} old - **Senior cat** (may need fewer calories)")
            
            weight_kg = st.number_input(
                "Weight (kg) *",
                min_value=0.5,
                max_value=15.0,
                value=4.5,
                step=0.1,
                help="Typical adult cats: 3.5-5.5 kg"
            )
            weight_lbs = kg_to_lbs(weight_kg)
            st.caption(f"≈ {weight_lbs:.2f} lbs")
        
        with col2:
            life_stage = st.selectbox(
                "Life Stage *",
                ["kitten", "adult", "senior"],
                index=["kitten", "adult", "senior"].index(auto_life_stage),
                help="Auto-selected based on age. Kitten: <1 year, Adult: 1-10 years, Senior: 10+ years"
            )
            
            activity_level = st.selectbox(
                "Activity Level *",
                ["very_young", "low", "moderate", "high"],
                index=["very_young", "low", "moderate", "high"].index(auto_activity),
                help="Auto-suggested based on age. very_young: kittens 0-4 months, low: indoor/older cats, moderate: normal activity, high: very active"
            )
            
            body_condition = st.selectbox(
                "Body Condition *",
                ["underweight", "ideal", "overweight"],
                index=1,
                help="Assess by feeling ribs and viewing from above"
            )
            is_neutered = st.checkbox("Spayed/Neutered", value=True)
        
        submitted = st.form_submit_button("💾 Save Profile & Calculate Calories", use_container_width=True)
        
        if submitted:
            if not cat_name:
                st.error("⚠️ Please enter a cat name.")
            else:
                # Validate weight
                is_valid, message = validate_weight(weight_kg)
                if not is_valid:
                    st.warning(f"⚠️ {message}")
                
                # Create profile
                cat_data = create_cat_profile(
                    name=cat_name,
                    breed=cat_breed or "Unknown",
                    weight_kg=weight_kg,
                    age_years=age_years,
                    age_months=age_months,
                    life_stage=life_stage,
                    activity_level=activity_level,
                    body_condition=body_condition,
                    is_neutered=is_neutered
                )
                
                # Check if cat already exists
                existing_index = next(
                    (i for i, c in enumerate(st.session_state.cats) if c['name'] == cat_name),
                    None
                )
                
                if existing_index is not None:
                    st.session_state.cats[existing_index] = cat_data
                    st.success(f"✅ Updated profile for **{cat_name}**!")
                else:
                    st.session_state.cats.append(cat_data)
                    st.success(f"✅ Added profile for **{cat_name}**!")
                
                st.rerun()
    
    # Display existing cats
    if st.session_state.cats:
        st.markdown("---")
        st.subheader("📋 Saved Cat Profiles")
        
        for idx, cat in enumerate(st.session_state.cats):
            # Get age display
            age_str = format_age_display(cat.get('age_years', 0), cat.get('age_months', 0))
            
            with st.expander(f"🐱 **{cat['name']}** - {cat['breed']} ({age_str})", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Age", age_str)
                    st.metric("Weight", f"{cat['weight_kg']:.2f} kg")
                    st.write(f"**Life Stage:** {cat['life_stage'].title()}")
                
                with col2:
                    st.metric("RER (Resting)", f"{cat['rer']:.0f} kcal/day")
                    st.write(f"**Activity:** {cat['activity_level'].replace('_', ' ').title()}")
                    st.write(f"**Neutered:** {'Yes' if cat['is_neutered'] else 'No'}")
                
                with col3:
                    st.metric("DER (Daily Target)", f"{cat['der']:.0f} kcal/day", 
                             help="This is your cat's daily calorie target")
                    st.write(f"**Body Condition:** {cat['body_condition'].title()}")
                
                col_a, col_b = st.columns([3, 1])
                with col_b:
                    if st.button(f"🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                        st.session_state.cats.pop(idx)
                        st.rerun()
    else:
        st.info("👆 No cat profiles yet. Create one above to get started!")

# ==================== PAGE: FOOD DATABASE ====================

elif page == "🍽️ Food Database":
    st.header("🍽️ Food Database")
    st.markdown("Manage your cat food database and search for nutritional information.")
    
    tab1, tab2, tab3 = st.tabs(["📖 View Foods", "➕ Add Food", "🔍 Search API"])
    
    # Tab 1: View Foods
    with tab1:
        food_type = st.radio("Food Type", ["dry", "wet"], horizontal=True)
        
        if st.session_state.food_database.get(food_type):
            df = pd.DataFrame(st.session_state.food_database[food_type])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total {food_type} foods: {len(df)}")
        else:
            st.info("No foods in database yet. Add some in the 'Add Food' tab!")
    
    # Tab 2: Add Food
    with tab2:
        with st.form("add_food_form"):
            new_food_type = st.selectbox("Food Type *", ["dry", "wet"])
            brand_name = st.text_input("Brand/Product Name *", placeholder="e.g., Royal Canin Indoor Adult")
            calories = st.number_input(
                "Calories per 100g *",
                min_value=50,
                max_value=600,
                value=370 if new_food_type == 'dry' else 95,
                help="Check the food packaging for nutritional information"
            )
            
            submitted = st.form_submit_button("➕ Add to Database", use_container_width=True)
            
            if submitted:
                if not brand_name:
                    st.error("⚠️ Please enter a brand name.")
                else:
                    # Validate calories
                    is_valid, message = validate_calories(calories, new_food_type)
                    if not is_valid:
                        st.warning(f"⚠️ {message}")
                    
                    # Add to database
                    st.session_state.food_database = add_food_to_database(
                        st.session_state.food_database,
                        new_food_type,
                        brand_name,
                        calories
                    )
                    st.success(f"✅ Added **{brand_name}** to {new_food_type} food database!")
                    st.rerun()
    
    # Tab 3: Search API
    with tab3:
        st.subheader("🔍 Search Open Pet Food Facts API")
        st.markdown("Search the dedicated pet food database with 10,000+ pet products.")
        st.info("💡 **Tip:** This API is specifically for pet food (cats, dogs, birds, fish). Search for brand names like 'Royal Canin', 'Purina', 'Hill's', etc.")
        
        search_term = st.text_input("Search for cat food product", placeholder="e.g., Royal Canin Indoor")
        
        if st.button("🔍 Search API", use_container_width=True):
            if search_term:
                with st.spinner("Searching Open Pet Food Facts database..."):
                    result = fetch_pet_food_data(search_term)
                    
                    if result and result['calories_per_100g']:
                        st.success("✅ Found cat food product!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Brand:** {result['brand']}")
                            st.write(f"**Product:** {result['product_name']}")
                            if result.get('categories'):
                                st.caption(f"Categories: {result['categories']}")
                        with col2:
                            st.metric("Calories", f"{result['calories_per_100g']} kcal/100g")
                            if result.get('url'):
                                st.markdown(f"[View on Open Pet Food Facts]({result['url']})")
                        
                        st.markdown("---")
                        food_type_choice = st.selectbox("Add as:", ["dry", "wet"])
                        
                        if st.button("➕ Add to Database"):
                            st.session_state.food_database = add_food_to_database(
                                st.session_state.food_database,
                                food_type_choice,
                                f"{result['brand']} - {result['product_name']}",
                                result['calories_per_100g']
                            )
                            st.success("✅ Added to database!")
                            st.rerun()
                    else:
                        st.warning("⚠️ No cat food results found with calorie information.")
                        st.info("💡 Try different search terms like:\n- Brand names: 'Purina', 'Royal Canin', 'Hill's'\n- Product types: 'dry cat food', 'wet cat food'\n- Or add the food manually in the 'Add Food' tab")
            else:
                st.warning("⚠️ Please enter a search term.")

# ==================== PAGE: FEEDING SCHEDULE ====================

elif page == "⏰ Feeding Schedule":
    st.header("⏰ Feeding Schedule")
    st.markdown("Create customized feeding schedules with calculated serving sizes.")
    
    if not st.session_state.cats:
        st.warning("⚠️ Please add a cat profile first!")
        if st.button("➕ Go to Cat Profile"):
            st.rerun()
    else:
        selected_cat = st.selectbox(
            "Select Cat *",
            [cat['name'] for cat in st.session_state.cats],
            help="Choose which cat to create a feeding schedule for"
        )
        
        cat_data = next(cat for cat in st.session_state.cats if cat['name'] == selected_cat)
        
        st.info(f"📊 Daily calorie target for **{selected_cat}**: **{cat_data['der']:.0f} kcal**")
        
        with st.form("feeding_schedule_form"):
            st.subheader("➕ Add Meal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                meal_time = st.time_input("Feeding Time *", value=time(8, 0))
                food_type = st.selectbox("Food Type *", ["dry", "wet"])
            
            with col2:
                if st.session_state.food_database.get(food_type):
                    food_brands = [f['brand'] for f in st.session_state.food_database[food_type]]
                    selected_brand = st.selectbox("Food Brand *", food_brands)
                    
                    # Get calories for selected brand
                    food_item = get_food_by_brand(st.session_state.food_database, food_type, selected_brand)
                    calories_per_100g = food_item['calories_per_100g']
                    
                    st.caption(f"💡 {calories_per_100g} kcal per 100g")
                    
                    percentage = st.slider(
                        "% of Daily Calories *",
                        0, 100, 25,
                        help="What percentage of daily calories should this meal provide?"
                    )
                else:
                    st.warning("⚠️ Add foods to database first!")
                    selected_brand = None
                    calories_per_100g = 0
                    percentage = 0
            
            submitted = st.form_submit_button("➕ Add Meal", use_container_width=True)
            
            if submitted and selected_brand:
                # Create meal using helper function
                meal = create_meal(
                    cat_name=selected_cat,
                    meal_time=meal_time.strftime("%H:%M"),
                    food_type=food_type,
                    brand=selected_brand,
                    food_calories_per_100g=calories_per_100g,
                    percentage_of_daily=percentage,
                    daily_target_calories=cat_data['der']
                )
                
                st.session_state.feeding_schedule.append(meal)
                st.success(f"✅ Added meal at {format_time_12hr(meal_time.strftime('%H:%M'))}")
                st.rerun()
        
        # Display feeding schedule
        if st.session_state.feeding_schedule:
            st.markdown("---")
            st.subheader("📅 Current Feeding Schedule")
            
            cat_meals = [
                meal for meal in st.session_state.feeding_schedule
                if meal['cat_name'] == selected_cat
            ]
            
            if cat_meals:
                # Sort by time
                cat_meals = sort_meals_by_time(cat_meals)
                
                for idx, meal in enumerate(cat_meals):
                    with st.expander(
                        f"🕐 **{format_time_12hr(meal['time'])}** - {meal['brand']} ({meal['food_type']})",
                        expanded=False
                    ):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Calories", f"{meal['target_calories']:.0f} kcal")
                        with col2:
                            st.metric("Amount", f"{meal['grams']:.1f}g")
                        with col3:
                            st.metric("Cups", f"{meal['cups']:.2f}")
                        with col4:
                            st.metric("% of Daily", f"{meal['percentage']:.0f}%")
                        
                        if st.button(f"🗑️ Remove Meal", key=f"remove_meal_{idx}"):
                            st.session_state.feeding_schedule.remove(meal)
                            st.rerun()
                
                # Calculate totals using helper function
                totals = calculate_daily_totals(st.session_state.feeding_schedule, selected_cat)
                status, difference = get_feeding_balance_status(totals['total_calories'], cat_data['der'])
                
                st.markdown("---")
                st.subheader("📊 Daily Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calories", f"{totals['total_calories']:.0f} kcal")
                with col2:
                    st.metric("Target Calories", f"{cat_data['der']:.0f} kcal")
                with col3:
                    st.metric("Difference", f"{difference:+.0f} kcal")
                with col4:
                    st.metric("Meals per Day", totals['meal_count'])
                
                # Balance status indicator
                if status == 'balanced':
                    st.success("✅ Feeding schedule is well-balanced!")
                elif status == 'over':
                    st.warning(f"⚠️ Feeding schedule exceeds target by {difference:.0f} kcal. Consider reducing portion sizes.")
                else:  # under
                    st.warning(f"⚠️ Feeding schedule is under target by {abs(difference):.0f} kcal. Consider increasing portions or adding another meal.")
            else:
                st.info("👆 No meals scheduled yet for this cat. Add meals above!")

# ==================== PAGE: DASHBOARD ====================

elif page == "📊 Dashboard":
    st.header("📊 Dashboard")
    st.markdown("Visual analytics and insights for your cat's feeding schedule.")
    
    if not st.session_state.cats:
        st.warning("⚠️ Please add a cat profile first!")
        if st.button("➕ Go to Cat Profile"):
            st.rerun()
    else:
        selected_cat = st.selectbox(
            "Select Cat *",
            [cat['name'] for cat in st.session_state.cats]
        )
        
        cat_data = next(cat for cat in st.session_state.cats if cat['name'] == selected_cat)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Weight", f"{cat_data['weight_kg']:.2f} kg", 
                     f"{kg_to_lbs(cat_data['weight_kg']):.1f} lbs")
        with col2:
            st.metric("RER", f"{cat_data['rer']:.0f} kcal/day")
        with col3:
            st.metric("DER", f"{cat_data['der']:.0f} kcal/day")
        with col4:
            cat_meals = [
                meal for meal in st.session_state.feeding_schedule
                if meal['cat_name'] == selected_cat
            ]
            total_meals = len(cat_meals)
            st.metric("Meals/Day", total_meals)
        
        if cat_meals:
            # Calorie distribution chart
            st.markdown("---")
            st.subheader("📈 Daily Calorie Distribution")
            
            meals_df = pd.DataFrame(cat_meals)
            meals_df['time_formatted'] = meals_df['time'].apply(format_time_12hr)
            
            fig = px.pie(
                meals_df,
                values='target_calories',
                names='time_formatted',
                title='Calorie Distribution by Meal Time',
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily schedule visualization
            st.subheader("🕐 Feeding Timeline")
            
            fig = go.Figure()
            
            for meal in cat_meals:
                hour, minute = map(int, meal['time'].split(':'))
                time_decimal = hour + minute/60
                
                fig.add_trace(go.Scatter(
                    x=[time_decimal],
                    y=[meal['target_calories']],
                    mode='markers+text',
                    marker=dict(size=20, color='#FF6B6B'),
                    text=f"{format_time_12hr(meal['time'])}<br>{meal['brand'][:20]}",
                    textposition="top center",
                    name=format_time_12hr(meal['time']),
                    showlegend=False
                ))
            
            fig.add_hline(
                y=cat_data['der'],
                line_dash="dash",
                annotation_text="Daily Target",
                line_color="green",
                annotation_position="right"
            )
            
            fig.update_layout(
                title="Feeding Schedule Throughout the Day",
                xaxis_title="Time of Day (24-hour)",
                yaxis_title="Calories (kcal)",
                xaxis=dict(range=[0, 24], tickmode='linear', tick0=0, dtick=2),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Food type breakdown
            st.subheader("🍖 Food Type Breakdown")
            
            food_breakdown = get_food_type_breakdown(st.session_state.feeding_schedule, selected_cat)
            
            col1, col2 = st.columns(2)
            with col1:
                dry_cals = food_breakdown.get('dry', 0)
                dry_pct = calculate_percentage_of_target(dry_cals, cat_data['der'])
                st.metric(
                    "Dry Food",
                    f"{dry_cals:.0f} kcal",
                    f"{dry_pct:.1f}% of daily"
                )
            with col2:
                wet_cals = food_breakdown.get('wet', 0)
                wet_pct = calculate_percentage_of_target(wet_cals, cat_data['der'])
                st.metric(
                    "Wet Food",
                    f"{wet_cals:.0f} kcal",
                    f"{wet_pct:.1f}% of daily"
                )
            
            # Totals
            totals = calculate_daily_totals(st.session_state.feeding_schedule, selected_cat)
            status, difference = get_feeding_balance_status(totals['total_calories'], cat_data['der'])
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Daily Grams", f"{totals['total_grams']:.1f}g")
            with col2:
                st.metric("Total Daily Cups", f"{totals['total_cups']:.2f}")
            with col3:
                pct_of_target = calculate_percentage_of_target(totals['total_calories'], cat_data['der'])
                st.metric("% of Target", f"{pct_of_target:.1f}%")
        
        else:
            st.info("ℹ️ No feeding schedule set up yet. Go to the Feeding Schedule page to add meals!")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🐱 Cat Calorie Tracker | Built with Streamlit & Python</p>
        <p style='font-size: 0.8em;'>Consult your veterinarian for professional dietary advice</p>
    </div>
""", unsafe_allow_html=True)
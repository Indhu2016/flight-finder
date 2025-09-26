import streamlit as st
from datetime import date as _date
from src.agents.route_agent import plan_best_routes
from src.tools.formatters import human_readable
from src.tools.emailer import send_itinerary_email
from src.tools.security import validate_email, sanitize_city_name, validate_numeric_input

st.set_page_config(page_title="Smart Travel Optimizer", page_icon="✈️", layout="centered")

st.title("✈️ Smart Travel Optimizer")
st.caption("Min time • Low cost • Big luggage • ≤2 connections")


col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("Origin", "Stuttgart")
with col2:
    destination = st.text_input("Destination", "Vienna")


d = st.date_input("Date", _date(2025, 10, 1))
bags = st.number_input("Min checked bags", min_value=0, max_value=5, value=2, step=1)
max_conn = st.slider("Max connections", 0, 2, 2)
w_time = st.slider("Weight: time", 0.0, 1.0, 0.6, 0.05)
w_cost = 1.0 - w_time

st.write(f"Weight: cost = {w_cost:.2f}")

email = st.text_input("Email results to (optional)")

if st.button("Search routes"):
    try:
        # Validate inputs
        clean_origin = sanitize_city_name(origin)
        clean_destination = sanitize_city_name(destination)
        
        if not validate_numeric_input(bags, 0, 10):
            st.error("Invalid number of bags. Must be between 0 and 10.")
            st.stop()
        
        if not validate_numeric_input(max_conn, 0, 5):
            st.error("Invalid number of connections. Must be between 0 and 5.")
            st.stop()
        
        if email and not validate_email(email):
            st.error("Invalid email address format.")
            st.stop()
        
        results = plan_best_routes(
            origin=clean_origin,
            destination=clean_destination,
            date=str(d),
            min_checked_bags=bags,
            max_connections=max_conn,
            w_time=w_time,
            w_cost=w_cost
        )
        
        if not results:
            st.warning("No matching routes. Try relaxing filters or changing date.")
        else:
            st.subheader("Top options")
            st.code(human_readable(results[:5]))
            
            if email:
                try:
                    send_itinerary_email(email, clean_origin, clean_destination, str(d), results)
                    st.success(f"Sent results to {email}")
                except Exception as e:
                    st.error(f"Failed to send email: {str(e)}")
                    
    except ValueError as e:
        st.error(f"Input validation error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

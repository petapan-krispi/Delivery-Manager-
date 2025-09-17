import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import tempfile

# Import actual business logic
from models.customer import Customer
from models.excel_manager import ExcelManager
from controllers.main_controller import MainController
from utils.printer import DeliverySlipPrinter
from utils.exporter import DataExporter

# Set page config
st.set_page_config(
    page_title="Delivery Manager",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state
    if 'controller' not in st.session_state:
        st.session_state.controller = MainController()
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'selected_customer' not in st.session_state:
        st.session_state.selected_customer = None
    
    controller = st.session_state.controller
    
    # Header
    st.title("🚚 Delivery Manager")
    st.markdown("---")
    
    # Simple Add Customer Button
    st.write("**Add New Customer:**")
    if st.button("➕ Add New Customer", type="primary"):
        st.write("Debug: Add button clicked!")
        st.session_state.show_add_form = True
        st.rerun()
    
    st.write(f"Debug: show_add_form = {st.session_state.show_add_form}")
    
    # Add customer form
    if st.session_state.show_add_form:
        st.header("➕ Add New Customer")
        st.write("Debug: Add form is showing!")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input("Phone Number *", placeholder="+1234567890")
                customer_name = st.text_input("Customer Name *", placeholder="John Doe")
                scheduled_delivery_time = st.text_input("Delivery Time", placeholder="10:00 AM")
            with col2:
                apartment_no = st.text_input("Apartment No", placeholder="Apt 101")
                address = st.text_input("Address *", placeholder="123 Main St")
                suburb = st.text_input("Suburb", placeholder="Downtown")
                postal_code = st.text_input("Postal Code", placeholder="12345")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                if st.form_submit_button("✅ Add Customer", type="primary"):
                    if phone and customer_name and address:
                        try:
                            new_customer = Customer(
                                phone=phone.strip(),
                                customer_name=customer_name.strip(),
                                scheduled_delivery_time=scheduled_delivery_time.strip(),
                                apartment_no=apartment_no.strip(),
                                address=address.strip(),
                                suburb=suburb.strip(),
                                postal_code=postal_code.strip()
                            )
                            
                            if controller.add_customer(new_customer):
                                st.success(f"Customer {new_customer.customer_name} added successfully!")
                                st.session_state.show_add_form = False
                                st.rerun()
                            else:
                                st.error("Failed to add customer")
                        except ValueError as e:
                            st.error(f"Validation error: {str(e)}")
                    else:
                        st.error("Please fill in all required fields (Phone, Name, Address)")
            with col_cancel:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_add_form = False
                    st.rerun()
    
    # Load and display customers
    st.markdown("---")
    st.header("📋 Customer List")
    
    # Load customers
    customers = controller.load_customers()
    st.write(f"**Found {len(customers)} customers**")
    
    if customers:
        # Create DataFrame for display
        customer_data = []
        for customer in customers:
            customer_data.append({
                'PHONE': customer.phone,
                'CUSTOMER NAME': customer.customer_name,
                'SCH   \nDEL': customer.scheduled_delivery_time,
                'APT\nNO': customer.apartment_no,
                'ADDRESS': customer.address,
                'SUBURB': customer.suburb,
                'PC': customer.postal_code
            })
        
        df = pd.DataFrame(customer_data)
        st.table(df)
    else:
        st.info("No customers found. Add some customers to get started!")

if __name__ == "__main__":
    main()

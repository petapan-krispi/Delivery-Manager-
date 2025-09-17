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
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""
    
    controller = st.session_state.controller
    
    # Header
    st.title("🚚 Delivery Manager")
    st.markdown("---")
    
    # Add Customer Button - Simple and working
    if st.button("➕ Add New Customer", type="primary"):
        st.session_state.show_add_form = True
        st.rerun()
    
    # Add customer form
    if st.session_state.show_add_form:
        st.header("➕ Add New Customer")
        
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
    
    # Search functionality
    st.markdown("---")
    st.header("🔍 Search Customers")
    search_term = st.text_input("Search customers:", value=st.session_state.search_term)
    if search_term != st.session_state.search_term:
        st.session_state.search_term = search_term
        controller.search_customers(search_term)
    else:
        controller.search_customers(search_term)
    
    # Load and display customers
    st.markdown("---")
    st.header("📋 Customer List")
    
    customers = controller.filtered_customers
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
        
        # Customer actions
        st.markdown("---")
        st.header("📊 Actions")
        
        # Customer selection dropdown
        customer_options = [f"{i+1}. {customer.customer_name} - {customer.phone}" for i, customer in enumerate(customers)]
        selected_index = st.selectbox("Select a customer:", range(len(customer_options)), format_func=lambda x: customer_options[x])
        
        # Action buttons
        col_edit, col_delete = st.columns(2)
        
        with col_edit:
            if st.button("✏️ Edit Selected", type="primary", use_container_width=True):
                if selected_index is not None:
                    st.session_state.selected_customer = customers[selected_index]
                    st.session_state.show_edit_form = True
                    st.rerun()
                else:
                    st.error("Please select a customer first!")
        
        with col_delete:
            if st.button("🗑️ Delete Selected", use_container_width=True):
                if selected_index is not None:
                    customer = customers[selected_index]
                    if controller.delete_customer(customer):
                        controller.load_customers()
                        st.success(f"Customer {customer.customer_name} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete customer")
        
        # Print button
        if st.button("🖨️ Print Delivery Label", use_container_width=True):
            if selected_index is not None:
                customer = customers[selected_index]
                pdf_data = controller.create_delivery_slip_pdf(customer)
                if pdf_data:
                    st.download_button(
                        label="📄 Download Delivery Label",
                        data=pdf_data,
                        file_name=controller.printer.get_delivery_slip_filename(customer),
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    # Edit customer form
    if st.session_state.show_edit_form and st.session_state.selected_customer:
        st.markdown("---")
        st.header("✏️ Edit Customer")
        customer = st.session_state.selected_customer
        
        with st.form("edit_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input("Phone Number *", value=customer.phone)
                customer_name = st.text_input("Customer Name *", value=customer.customer_name)
                scheduled_delivery_time = st.text_input("Delivery Time", value=customer.scheduled_delivery_time)
            with col2:
                apartment_no = st.text_input("Apartment No", value=customer.apartment_no)
                address = st.text_input("Address *", value=customer.address)
                suburb = st.text_input("Suburb", value=customer.suburb)
                postal_code = st.text_input("Postal Code", value=customer.postal_code)
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                if st.form_submit_button("✅ Save Changes", type="primary"):
                    if phone and customer_name and address:
                        try:
                            updated_customer = Customer(
                                phone=phone.strip(),
                                customer_name=customer_name.strip(),
                                scheduled_delivery_time=scheduled_delivery_time.strip(),
                                apartment_no=apartment_no.strip(),
                                address=address.strip(),
                                suburb=suburb.strip(),
                                postal_code=postal_code.strip()
                            )
                            
                            if controller.update_customer(customer, updated_customer):
                                controller.load_customers()
                                st.success(f"Customer {updated_customer.customer_name} updated successfully!")
                                st.session_state.show_edit_form = False
                                st.session_state.selected_customer = None
                                st.rerun()
                            else:
                                st.error("Failed to update customer")
                        except ValueError as e:
                            st.error(f"Validation error: {str(e)}")
                    else:
                        st.error("Please fill in all required fields (Phone, Name, Address)")
            with col_cancel:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_edit_form = False
                    st.session_state.selected_customer = None
                    st.rerun()
    
    else:
        st.info("No customers found. Add some customers to get started!")

if __name__ == "__main__":
    main()

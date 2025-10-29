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
    if 'selected_customers' not in st.session_state:
        st.session_state.selected_customers = []
    
    controller = st.session_state.controller
    
    # Header
    st.markdown("---")
    
    # LIVE SEARCH - updates automatically as you type (no Enter needed)
    search_term = st.text_input(
        "🔍 Search customers (live filtering):", 
        value="",
        key="live_search",
        placeholder="Type to search instantly..."
    )
    
    # Search happens automatically on every keystroke
    controller.search_customers(search_term)
        
    # Add Customer Button - under search
    if st.button("➕ Add New Customer", type="primary"):
        st.session_state.show_add_form = True
        st.rerun()
    
    # Add customer form (SCH DEL removed from UI but kept in backend)
    if st.session_state.show_add_form:
        st.header("➕ Add New Customer")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input("Phone Number *", placeholder="+1234567890")
                customer_name = st.text_input("Customer Name *", placeholder="John Doe")
                apartment_no = st.text_input("Apartment No", placeholder="Apt 101")
            with col2:
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
                                scheduled_delivery_time="",  # Keep empty in backend
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
    
    customers = controller.filtered_customers
    st.write(f"**Found {len(customers)} customers**")
    
    if customers:
        # Create DataFrame for display (SCH DEL removed)
        customer_data = []
        for customer in customers:
            customer_data.append({
                'PHONE': customer.phone,
                'CUSTOMER NAME': customer.customer_name,
                'APT NO': customer.apartment_no,
                'ADDRESS': customer.address,
                'SUBURB': customer.suburb,
                'PC': customer.postal_code
            })
        
        df = pd.DataFrame(customer_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Customer actions
        st.markdown("---")
        st.header("📊 Actions")
        
        # Single customer selection dropdown
        customer_options = [f"{i+1}. {customer.customer_name} - {customer.phone}" for i, customer in enumerate(customers)]
        selected_index = st.selectbox("Select a customer:", range(len(customer_options)), format_func=lambda x: customer_options[x])
        
        # Multi-select customers for batch operations
        st.markdown("### 🎯 Multi-Select Customers")
        st.write("Select multiple customers for batch printing:")
        
        # Checkboxes for each customer
        selected_customer_indices = []
        for i, customer in enumerate(customers):
            # Check if this customer is already selected
            is_selected = any(selected.phone == customer.phone and selected.customer_name == customer.customer_name 
                            for selected in st.session_state.selected_customers)
            
            if st.checkbox(f"{customer.customer_name} - {customer.phone}", 
                          value=is_selected, 
                          key=f"customer_{i}"):
                # Add to selection if not already there
                if not any(selected.phone == customer.phone and selected.customer_name == customer.customer_name 
                          for selected in st.session_state.selected_customers):
                    st.session_state.selected_customers.append(customer)
            else:
                # Remove from selection if unchecked
                st.session_state.selected_customers = [selected for selected in st.session_state.selected_customers 
                                                     if not (selected.phone == customer.phone and selected.customer_name == customer.customer_name)]
        
        # Update selected customers list (keep existing selections)
        for i, customer in enumerate(customers):
            if i in selected_customer_indices:
                if not any(selected.phone == customer.phone and selected.customer_name == customer.customer_name 
                          for selected in st.session_state.selected_customers):
                    st.session_state.selected_customers.append(customer)
        
        # Show selected customers count and clear button
        if st.session_state.selected_customers:
            col_count, col_clear = st.columns([3, 1])
            with col_count:
                st.write(f"**Selected {len(st.session_state.selected_customers)} customers:**")
                for customer in st.session_state.selected_customers:
                    st.write(f"• {customer.customer_name} - {customer.phone}")
            with col_clear:
                if st.button("🗑️ Clear Selection", use_container_width=True):
                    st.session_state.selected_customers = []
                    st.rerun()
        
        # Batch print buttons
        if st.session_state.selected_customers:
            col_print, col_pdf = st.columns(2)
            
            with col_print:
                if st.button("🖨️ Print Table View", type="primary", use_container_width=True):
                    # Create a combined table view
                    st.write("### 📄 Selected Customers Report")
                    
                    # Create table data for selected customers (SCH DEL removed)
                    selected_data = []
                    for customer in st.session_state.selected_customers:
                        selected_data.append({
                            'PHONE': customer.phone,
                            'CUSTOMER NAME': customer.customer_name,
                            'APT NO': customer.apartment_no,
                            'ADDRESS': customer.address,
                            'SUBURB': customer.suburb,
                            'PC': customer.postal_code
                        })
                    
                    # Display table
                    selected_df = pd.DataFrame(selected_data)
                    st.table(selected_df)
            
            with col_pdf:
                if st.button("📄 Print as PDF", type="secondary", use_container_width=True):
                    # Create PDF for selected customers
                    try:
                        pdf_data = controller.create_batch_delivery_slip_pdf(st.session_state.selected_customers)
                        if pdf_data:
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_data,
                                file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.error("Failed to create PDF")
                    except Exception as e:
                        st.error(f"Error creating PDF: {str(e)}")
        
        # Export options for selected customers
        if st.session_state.selected_customers:
            st.markdown("### 📤 Export Selected Customers")
            col_csv, col_excel = st.columns(2)
            
            with col_csv:
                csv_data = controller.export_to_csv(st.session_state.selected_customers)
                if csv_data:
                    st.download_button(
                        label="📥 Download Selected as CSV",
                        data=csv_data,
                        file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_excel:
                excel_data = controller.export_to_excel(st.session_state.selected_customers)
                if excel_data:
                    st.download_button(
                        label="📥 Download Selected as Excel",
                        data=excel_data,
                        file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        st.markdown("---")
        
        # Single Customer Actions
        st.markdown("### 👤 Single Customer Actions")
        
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
    
    # Edit customer form (SCH DEL removed from UI but kept in backend)
    if st.session_state.show_edit_form and st.session_state.selected_customer:
        st.markdown("---")
        st.header("✏️ Edit Customer")
        customer = st.session_state.selected_customer
        
        with st.form("edit_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input("Phone Number *", value=customer.phone)
                customer_name = st.text_input("Customer Name *", value=customer.customer_name)
                apartment_no = st.text_input("Apartment No", value=customer.apartment_no)
            with col2:
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
                                scheduled_delivery_time=customer.scheduled_delivery_time,  # Keep existing value
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
    
    # Export options
    st.markdown("---")
    st.header("📤 Export Data")
    
    col_csv, col_excel = st.columns(2)
    
    with col_csv:
        if st.button("📊 Export to CSV", use_container_width=True):
            csv_data = controller.export_to_csv(controller.customers)
            if csv_data:
                st.download_button(
                    label="📥 Download CSV File",
                    data=csv_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.error("Failed to export CSV")
    
    with col_excel:
        if st.button("📈 Export to Excel", use_container_width=True):
            excel_data = controller.export_to_excel(controller.customers)
            if excel_data:
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.error("Failed to export Excel")
    
    # Data management
    st.markdown("---")
    st.header("🔧 Data Management")
    
    col_refresh, col_backup = st.columns(2)
    
    with col_refresh:
        if st.button("🔄 Refresh Data", use_container_width=True):
            controller.load_customers()
            st.success("Data refreshed successfully!")
            st.rerun()
    
    with col_backup:
        if st.button("💾 Backup Data", use_container_width=True):
            if controller.backup_data():
                st.success("Backup created successfully!")
            else:
                st.error("Failed to create backup")
    
    

if __name__ == "__main__":
    main()
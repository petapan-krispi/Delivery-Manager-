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


def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'controller': MainController(),
        'show_add_form': False,
        'show_edit_form': False,
        'selected_customer': None,
        'selected_customers': []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_search_section(controller):
    """Render the search section with clear button."""
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Simple text input - updates on Enter or blur (tab/click outside)
        search_input = st.text_input(
            "🔍 Search customers (press Enter or Tab to filter):",
            key="search_box",
            placeholder="Type customer name, phone, suburb, or postal code..."
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Clear", use_container_width=True, help="Clear search filter"):
            # Clear the search box
            if 'search_box' in st.session_state:
                del st.session_state['search_box']
            st.rerun()
    
    # Apply search filter using the widget's current value
    search_value = st.session_state.get('search_box', '')
    controller.search_customers(search_value)
    
    # Show search hint
    if search_value:
        st.caption(f"🔎 Filtering by: **{search_value}**")


def render_add_customer_form(controller):
    """Render the add customer form."""
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
            submitted = st.form_submit_button("✅ Add Customer", type="primary")
            if submitted:
                if phone and customer_name and address:
                    try:
                        new_customer = Customer(
                            phone=phone.strip(),
                            customer_name=customer_name.strip(),
                            scheduled_delivery_time="",
                            apartment_no=apartment_no.strip(),
                            address=address.strip(),
                            suburb=suburb.strip(),
                            postal_code=postal_code.strip()
                        )
                        
                        if controller.add_customer(new_customer):
                            st.success(f"✅ Customer '{new_customer.customer_name}' added successfully!")
                            st.session_state.show_add_form = False
                            # Clear search if active
                            if 'search_box' in st.session_state:
                                del st.session_state['search_box']
                            st.rerun()
                        else:
                            st.error("❌ Failed to add customer")
                    except ValueError as e:
                        st.error(f"❌ Validation error: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields (Phone, Name, Address)")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_add_form = False
                st.rerun()


def render_customer_table(customers):
    """Render the customer data table."""
    customer_data = [
        {
            'PHONE': customer.phone,
            'CUSTOMER NAME': customer.customer_name,
            'APT NO': customer.apartment_no,
            'ADDRESS': customer.address,
            'SUBURB': customer.suburb,
            'PC': customer.postal_code
        }
        for customer in customers
    ]
    
    df = pd.DataFrame(customer_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_batch_actions(controller, customers):
    """Render multi-select customer actions."""
    st.markdown("### 🎯 Multi-Select Customers")
    st.write("Select multiple customers for batch operations:")
    
    # Create columns for better layout
    cols = st.columns(3)
    
    # Render checkboxes in columns
    for i, customer in enumerate(customers):
        col_idx = i % 3
        
        is_selected = any(
            selected.phone == customer.phone and 
            selected.customer_name == customer.customer_name
            for selected in st.session_state.selected_customers
        )
        
        with cols[col_idx]:
            if st.checkbox(
                f"{customer.customer_name}",
                value=is_selected,
                key=f"customer_{i}",
                help=f"Phone: {customer.phone}"
            ):
                if not any(
                    selected.phone == customer.phone and 
                    selected.customer_name == customer.customer_name
                    for selected in st.session_state.selected_customers
                ):
                    st.session_state.selected_customers.append(customer)
            else:
                st.session_state.selected_customers = [
                    selected for selected in st.session_state.selected_customers
                    if not (selected.phone == customer.phone and 
                           selected.customer_name == customer.customer_name)
                ]
    
    # Show selected customers
    if st.session_state.selected_customers:
        st.markdown("---")
        col_count, col_clear = st.columns([4, 1])
        
        with col_count:
            st.info(f"**✓ Selected {len(st.session_state.selected_customers)} customer(s)**")
        
        with col_clear:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.selected_customers = []
                st.rerun()
        
        # Batch action buttons
        render_batch_action_buttons(controller)


def render_batch_action_buttons(controller):
    """Render batch operation buttons."""
    st.markdown("#### Batch Actions")
    
    col_print, col_pdf = st.columns(2)
    
    with col_print:
        if st.button("🖨️ Print Table View", type="primary", use_container_width=True):
            st.write("### 📄 Selected Customers Report")
            selected_data = [
                {
                    'PHONE': customer.phone,
                    'CUSTOMER NAME': customer.customer_name,
                    'APT NO': customer.apartment_no,
                    'ADDRESS': customer.address,
                    'SUBURB': customer.suburb,
                    'PC': customer.postal_code
                }
                for customer in st.session_state.selected_customers
            ]
            st.table(pd.DataFrame(selected_data))
    
    with col_pdf:
        if st.button("📄 Export as PDF", type="secondary", use_container_width=True):
            try:
                pdf_data = controller.create_batch_delivery_slip_pdf(
                    st.session_state.selected_customers
                )
                if pdf_data:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to create PDF")
            except Exception as e:
                st.error(f"❌ Error creating PDF: {str(e)}")
    
    # Export options
    render_batch_export_buttons(controller)


def render_batch_export_buttons(controller):
    """Render batch export buttons."""
    st.markdown("#### Export Selected")
    col_csv, col_excel = st.columns(2)
    
    with col_csv:
        csv_data = controller.export_to_csv(st.session_state.selected_customers)
        if csv_data:
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col_excel:
        excel_data = controller.export_to_excel(st.session_state.selected_customers)
        if excel_data:
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"selected_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


def render_single_customer_actions(controller, customers):
    """Render single customer action buttons."""
    st.markdown("### 👤 Single Customer Actions")
    
    # Customer selection dropdown
    customer_options = [
        f"{i+1}. {customer.customer_name} - {customer.phone}"
        for i, customer in enumerate(customers)
    ]
    selected_index = st.selectbox(
        "Select a customer:",
        range(len(customer_options)),
        format_func=lambda x: customer_options[x]
    )
    
    # Action buttons
    col_edit, col_delete, col_print = st.columns(3)
    
    with col_edit:
        if st.button("✏️ Edit", type="primary", use_container_width=True):
            if selected_index is not None:
                st.session_state.selected_customer = customers[selected_index]
                st.session_state.show_edit_form = True
                st.rerun()
    
    with col_delete:
        if st.button("🗑️ Delete", use_container_width=True):
            if selected_index is not None:
                customer = customers[selected_index]
                if controller.delete_customer(customer):
                    controller.load_customers()
                    st.success(f"✅ Customer '{customer.customer_name}' deleted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete customer")
    
    with col_print:
        if st.button("🖨️ Print Label", use_container_width=True):
            if selected_index is not None:
                customer = customers[selected_index]
                pdf_data = controller.create_delivery_slip_pdf(customer)
                if pdf_data:
                    st.download_button(
                        label="📄 Download Label",
                        data=pdf_data,
                        file_name=controller.printer.get_delivery_slip_filename(customer),
                        mime="application/pdf",
                        use_container_width=True
                    )


def render_edit_customer_form(controller):
    """Render the edit customer form."""
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
                            scheduled_delivery_time=customer.scheduled_delivery_time,
                            apartment_no=apartment_no.strip(),
                            address=address.strip(),
                            suburb=suburb.strip(),
                            postal_code=postal_code.strip()
                        )
                        
                        if controller.update_customer(customer, updated_customer):
                            controller.load_customers()
                            st.success(f"✅ Customer '{updated_customer.customer_name}' updated successfully!")
                            st.session_state.show_edit_form = False
                            st.session_state.selected_customer = None
                            st.rerun()
                        else:
                            st.error("❌ Failed to update customer")
                    except ValueError as e:
                        st.error(f"❌ Validation error: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_edit_form = False
                st.session_state.selected_customer = None
                st.rerun()


def render_export_section(controller):
    """Render the export data section."""
    st.markdown("---")
    st.header("📤 Export All Data")
    
    col_csv, col_excel = st.columns(2)
    
    with col_csv:
        if st.button("📊 Export All to CSV", use_container_width=True):
            csv_data = controller.export_to_csv(controller.customers)
            if csv_data:
                st.download_button(
                    label="📥 Download CSV File",
                    data=csv_data,
                    file_name=f"all_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col_excel:
        if st.button("📈 Export All to Excel", use_container_width=True):
            excel_data = controller.export_to_excel(controller.customers)
            if excel_data:
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data,
                    file_name=f"all_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )


def render_data_management_section(controller):
    """Render the data management section."""
    st.markdown("---")
    st.header("🔧 Data Management")
    
    col_refresh, col_backup, col_stats = st.columns(3)
    
    with col_refresh:
        if st.button("🔄 Refresh Data", use_container_width=True):
            controller.load_customers()
            # Clear search
            if 'search_box' in st.session_state:
                del st.session_state['search_box']
            st.success("✅ Data refreshed!")
            st.rerun()
    
    with col_backup:
        if st.button("💾 Backup Data", use_container_width=True):
            if controller.backup_data():
                st.success("✅ Backup created!")
            else:
                st.error("❌ Backup failed")
    
    with col_stats:
        if st.button("📊 Show Stats", use_container_width=True):
            stats = controller.get_statistics()
            st.info(f"**Total Customers:** {stats.get('total_customers', 0)}")


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    controller = st.session_state.controller
    
    # App title
    st.title("🚚 Delivery Manager")
    
    # Render search section
    render_search_section(controller)
    
    # Add Customer Button
    if st.button("➕ Add New Customer", type="primary"):
        st.session_state.show_add_form = True
        st.rerun()
    
    # Render add customer form if needed
    if st.session_state.show_add_form:
        render_add_customer_form(controller)
        return  # Don't show rest of UI when adding
    
    # Display customer list
    st.markdown("---")
    st.header("📋 Customer List")
    
    customers = controller.filtered_customers
    
    # Show customer count with search info
    search_active = st.session_state.get('search_box', '').strip()
    if search_active:
        st.write(f"**Found {len(customers)} customer(s) matching your search**")
    else:
        st.write(f"**Showing all {len(customers)} customers**")
    
    if customers:
        # Render customer table
        render_customer_table(customers)
        
        # Actions section
        st.markdown("---")
        st.header("📊 Actions")
        
        # Render batch actions
        render_batch_actions(controller, customers)
        
        st.markdown("---")
        
        # Render single customer actions
        render_single_customer_actions(controller, customers)
    else:
        if search_active:
            st.warning(f"⚠️ No customers found matching '{search_active}'. Try a different search term.")
        else:
            st.info("ℹ️ No customers in database. Click 'Add New Customer' to get started!")
    
    # Render edit form if needed
    if st.session_state.show_edit_form and st.session_state.selected_customer:
        render_edit_customer_form(controller)
    
    # Only show export and management if not in edit mode
    if not st.session_state.show_edit_form and not st.session_state.show_add_form:
        # Render export section
        render_export_section(controller)
        
        # Render data management section
        render_data_management_section(controller)
    
    # Footer
    st.markdown("---")
    st.caption("💡 **Tip:** Press Enter or Tab after typing in search to apply filter")


if __name__ == "__main__":
    main()
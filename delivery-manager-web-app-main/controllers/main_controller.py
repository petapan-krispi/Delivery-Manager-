"""
Web-compatible Main Controller for the Delivery Manager application.
Handles business logic and connects web UI with Excel operations.
"""

from typing import List, Optional
from models.customer import Customer
from models.excel_manager import ExcelManager
from utils.printer import DeliverySlipPrinter
from utils.exporter import DataExporter


class MainController:
    """Main controller for the Delivery Manager web application."""
    
    def __init__(self):
        """Initialize the main controller."""
        self.excel_manager = ExcelManager()
        self.printer = DeliverySlipPrinter()
        self.exporter = DataExporter()
        
        # Load initial data
        self.customers = []
        self.filtered_customers = []
        self.load_customers()
        
        # Ensure filtered_customers is properly initialized
        if not self.filtered_customers:
            self.filtered_customers = self.customers.copy()
    
    def _sort_customers_alphabetically(self, customers: List[Customer]) -> List[Customer]:
        """Sort customers alphabetically by customer name (case-insensitive)."""
        return sorted(customers, key=lambda c: c.customer_name.lower())
    
    def load_customers(self) -> List[Customer]:
        """Load customers from Excel file and sort alphabetically."""
        try:
            self.customers = self.excel_manager.load_customers()
            # Sort alphabetically for display
            self.filtered_customers = self._sort_customers_alphabetically(self.customers.copy())
            print(f"DEBUG: Loaded {len(self.customers)} customers, sorted: {len(self.filtered_customers)}")
            return self.customers
        except Exception as e:
            print(f"Error loading customers: {str(e)}")
            return []
    
    def search_customers(self, query: str) -> List[Customer]:
        """Search customers by name, phone, suburb, or postal code with exact matches first."""
        try:
            if not query.strip():
                self.filtered_customers = self._sort_customers_alphabetically(self.customers.copy())
            else:
                query_lower = query.lower().strip()
                exact_matches = []
                partial_matches = []
                
                for customer in self.customers:
                    name_lower = customer.customer_name.lower()
                    
                    # Check for exact match at start of name
                    if name_lower.startswith(query_lower):
                        exact_matches.append(customer)
                    # Check for partial match anywhere in name, phone, suburb, or postal code
                    elif (query_lower in name_lower or
                          query_lower in customer.phone.lower() or
                          query_lower in customer.suburb.lower() or
                          query_lower in customer.postal_code.lower()):
                        partial_matches.append(customer)
                
                # Sort both lists alphabetically
                exact_matches = self._sort_customers_alphabetically(exact_matches)
                partial_matches = self._sort_customers_alphabetically(partial_matches)
                
                # Combine: exact matches first, then partial matches
                self.filtered_customers = exact_matches + partial_matches
            
            return self.filtered_customers
        except Exception as e:
            print(f"Error searching customers: {str(e)}")
            return []
    
    def add_customer(self, customer: Customer) -> bool:
        """Add a new customer."""
        try:
            success = self.excel_manager.add_customer(customer)
            if success:
                self.customers.append(customer)
                # Keep filtered list sorted alphabetically
                self.filtered_customers = self._sort_customers_alphabetically(self.customers.copy())
            return success
        except Exception as e:
            print(f"Error adding customer: {str(e)}")
            return False
    
    def update_customer(self, old_customer: Customer, new_customer: Customer) -> bool:
        """Update an existing customer."""
        try:
            success = self.excel_manager.update_customer(old_customer, new_customer)
            if success:
                # Update in local lists
                for i, existing_customer in enumerate(self.customers):
                    if (existing_customer.phone == old_customer.phone and
                        existing_customer.customer_name == old_customer.customer_name and
                        existing_customer.address == old_customer.address):
                        self.customers[i] = new_customer
                        break
                
                for i, existing_customer in enumerate(self.filtered_customers):
                    if (existing_customer.phone == old_customer.phone and
                        existing_customer.customer_name == old_customer.customer_name and
                        existing_customer.address == old_customer.address):
                        self.filtered_customers[i] = new_customer
                        break
                
                # Re-sort after update
                self.filtered_customers = self._sort_customers_alphabetically(self.filtered_customers)
            return success
        except Exception as e:
            print(f"Error updating customer: {str(e)}")
            return False
    
    def delete_customer(self, customer: Customer) -> bool:
        """Delete a customer."""
        try:
            success = self.excel_manager.delete_customer(customer)
            if success:
                # Remove from local lists
                if customer in self.customers:
                    self.customers.remove(customer)
                if customer in self.filtered_customers:
                    self.filtered_customers.remove(customer)
            return success
        except Exception as e:
            print(f"Error deleting customer: {str(e)}")
            return False
    
    def create_delivery_slip_pdf(self, customer: Customer) -> bytes:
        """Create a PDF delivery slip for a customer."""
        try:
            return self.printer.create_delivery_slip_pdf(customer)
        except Exception as e:
            print(f"Error creating delivery slip PDF: {str(e)}")
            return b""
    
    def create_batch_delivery_slip_pdf(self, customers: List[Customer]) -> bytes:
        """Create a PDF with delivery slips for multiple customers."""
        try:
            return self.printer.create_batch_delivery_slip_pdf(customers)
        except Exception as e:
            print(f"Error creating batch delivery slip PDF: {str(e)}")
            return b""
    
    def create_customer_table_pdf(self, customers: List[Customer], search_query: str = "") -> bytes:
        """Create a PDF with customer table."""
        try:
            return self.printer.create_customer_table_pdf(customers, search_query)
        except Exception as e:
            print(f"Error creating customer table PDF: {str(e)}")
            return b""
    
    def export_to_csv(self, customers: List[Customer]) -> bytes:
        """Export customers to CSV format."""
        try:
            return self.exporter.export_to_csv(customers)
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return b""
    
    def export_to_excel(self, customers: List[Customer]) -> bytes:
        """Export customers to Excel format."""
        try:
            return self.exporter.export_to_excel(customers)
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return b""
    
    def export_to_txt(self, customers: List[Customer]) -> bytes:
        """Export customers to TXT format."""
        try:
            return self.exporter.export_to_txt(customers)
        except Exception as e:
            print(f"Error exporting to TXT: {str(e)}")
            return b""
    
    def get_statistics(self) -> dict:
        """Get application statistics."""
        try:
            return self.excel_manager.get_statistics()
        except Exception as e:
            return {'error': str(e)}
    
    def backup_data(self) -> bool:
        """Create a backup of the Excel file."""
        try:
            return self.excel_manager.backup_file()
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return False
    
    def validate_excel_file(self) -> bool:
        """Validate the Excel file structure."""
        try:
            customers = self.excel_manager.load_customers()
            return True
        except Exception as e:
            print(f"Excel file validation failed: {str(e)}")
            return False
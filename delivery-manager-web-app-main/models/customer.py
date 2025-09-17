"""
Customer data model for delivery management system.
Represents a customer with delivery information.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Customer:
    """Customer data model with delivery information."""
    
    phone: str
    customer_name: str
    scheduled_delivery_time: str
    apartment_no: str
    address: str
    suburb: str
    postal_code: str
    
    def __post_init__(self):
        """Validate customer data after initialization."""
        self.validate()
    
    def validate(self) -> bool:
        """Validate customer data and raise ValueError if invalid."""
        # Allow empty phone numbers but ensure they're at least empty strings
        if self.phone is None:
            self.phone = ''
        
        if not self.customer_name or not self.customer_name.strip():
            raise ValueError("Customer name is required")
        
        if not self.address or not self.address.strip():
            raise ValueError("Address is required")
        
        return True
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary for Excel operations."""
        return {
            'PHONE': self.phone,
            'CUSTOMER NAME': self.customer_name,
            'SCH   \nDEL': self.scheduled_delivery_time,
            'APT\nNO': self.apartment_no,
            'ADDRESS': self.address,
            'SUBURB': self.suburb,
            'PC': self.postal_code
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Create customer from dictionary (Excel row)."""
        return cls(
            phone=data.get('PHONE', ''),
            customer_name=data.get('CUSTOMER NAME', ''),
            scheduled_delivery_time=data.get('SCH   \nDEL', ''),
            apartment_no=data.get('APT\nNO', ''),
            address=data.get('ADDRESS', ''),
            suburb=data.get('SUBURB', ''),
            postal_code=data.get('PC', '')
        )
    
    def update(self, **kwargs) -> None:
        """Update customer fields and revalidate."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.validate()
    
    def __str__(self) -> str:
        """String representation of customer."""
        return f"{self.customer_name} - {self.phone} - {self.address}"
    
    def __repr__(self) -> str:
        """Detailed representation of customer."""
        return (f"Customer(phone='{self.phone}', customer_name='{self.customer_name}', "
                f"scheduled_delivery_time='{self.scheduled_delivery_time}', "
                f"apartment_no='{self.apartment_no}', address='{self.address}', "
                f"suburb='{self.suburb}', postal_code='{self.postal_code}')")

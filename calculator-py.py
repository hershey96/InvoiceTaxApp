"""
BusinessTaxCalculator module for InvoiceTaxApp

This module contains the BusinessTaxCalculator class which handles
all tax calculations, invoice management, and data persistence.
"""

import datetime
import json
import os
import calendar
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import csv


@dataclass
class Invoice:
    """Data class for invoice information"""
    date: datetime.date
    amount: float
    description: str
    invoice_id: str


class BusinessTaxCalculator:
    """Business Tax Calculator class for handling invoices and tax calculations"""
    
    def __init__(self, data_dir="data", data_file=None, fed_tax_rate=0.20, state_tax_rate=0.05, state_code=""):
        """
        Initialize the BusinessTaxCalculator
        
        Args:
            data_dir (str): Directory to store data files
            data_file (str): File to store invoice data (if None, uses default in data_dir)
            fed_tax_rate (float): Default federal tax rate
            state_tax_rate (float): Default state tax rate
            state_code (str): State code
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        if data_file is None:
            self.data_file = os.path.join(self.data_dir, "invoices.json")
        else:
            self.data_file = data_file
            
        self.fed_tax_rate = fed_tax_rate
        self.state_tax_rate = state_tax_rate
        self.state_code = state_code
        self.invoices = []
        self.load_invoices()
        
    def load_invoices(self) -> None:
        """Load invoices from the data file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                self.invoices = []
                for inv in data.get('invoices', []):
                    # Convert string date to datetime.date
                    date_parts = [int(x) for x in inv['date'].split('-')]
                    date = datetime.date(date_parts[0], date_parts[1], date_parts[2])
                    
                    self.invoices.append(Invoice(
                        date=date,
                        amount=float(inv['amount']),
                        description=inv['description'],
                        invoice_id=inv['invoice_id']
                    ))
                    
                self.fed_tax_rate = data.get('fed_tax_rate', self.fed_tax_rate)
                self.state_tax_rate = data.get('state_tax_rate', self.state_tax_rate)
                self.state_code = data.get('state_code', self.state_code)
                
            except (json.JSONDecodeError, KeyError, ValueError, IndexError) as e:
                print(f"Error loading invoices: {e}")
                self.invoices = []
    
    def save_invoices(self) -> None:
        """Save invoices to the data file"""
        data = {
            'fed_tax_rate': self.fed_tax_rate,
            'state_tax_rate': self.state_tax_rate,
            'state_code': self.state_code,
            'invoices': [
                {
                    'date': inv.date.isoformat(),
                    'amount': inv.amount,
                    'description': inv.description,
                    'invoice_id': inv.invoice_id
                }
                for inv in self.invoices
            ]
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save invoices: {e}")
    
    def add_invoice(self, date: datetime.date, amount: float, description: str, invoice_id: str = None) -> Tuple[bool, str]:
        """
        Add a new invoice
        
        Args:
            date (datetime.date): Invoice date
            amount (float): Invoice amount
            description (str): Invoice description
            invoice_id (str, optional): Unique invoice ID. Generated if not provided.
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            # Generate invoice ID if not provided
            if invoice_id is None:
                invoice_id = f"INV-{date.strftime('%Y%m%d')}-{len(self.invoices):04d}"
            
            # Create and add invoice
            invoice = Invoice(
                date=date,
                amount=amount,
                description=description,
                invoice_id=invoice_id
            )
            
            self.invoices.append(invoice)
            self.save_invoices()
            return True, f"Invoice {invoice_id} added successfully."
            
        except Exception as e:
            return False, f"Error adding invoice: {e}"
    
    def delete_invoice(self, invoice_id: str) -> Tuple[bool, str]:
        """
        Delete an invoice by ID
        
        Args:
            invoice_id (str): ID of invoice to delete
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        for i, inv in enumerate(self.invoices):
            if inv.invoice_id == invoice_id:
                del self.invoices[i]
                self.save_invoices()
                return True, f"Invoice {invoice_id} deleted."
        
        return False, f"Invoice {invoice_id} not found."
    
    def get_quarter_bounds(self, year: int, quarter: int) -> Tuple[datetime.date, datetime.date]:
        """
        Get start and end dates for a quarter
        
        Args:
            year (int): Year
            quarter (int): Quarter (1-4)
            
        Returns:
            Tuple[datetime.date, datetime.date]: Start date and end date
        """
        if quarter < 1 or quarter > 4:
            raise ValueError("Quarter must be between 1 and 4")
            
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        
        start_date = datetime.date(year, start_month, 1)
        last_day = calendar.monthrange(year, end_month)[1]
        end_date = datetime.date(year, end_month, last_day)
        
        return start_date, end_date
    
    def get_quarterly_earnings(self, year: int, quarter: int) -> float:
        """
        Calculate earnings for a specific quarter
        
        Args:
            year (int): Year
            quarter (int): Quarter (1-4)
            
        Returns:
            float: Total earnings for the quarter
        """
        start_date, end_date = self.get_quarter_bounds(year, quarter)
        
        total = 0.0
        for inv in self.invoices:
            if start_date <= inv.date <= end_date:
                total += inv.amount
                
        return total

    def get_yearly_earnings(self, year: int) -> float:
        """
        Calculate earnings for an entire year
        
        Args:
            year (int): Year
            
        Returns:
            float: Total earnings for the year
        """
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        total = 0.0
        for inv in self.invoices:
            if start_date <= inv.date <= end_date:
                total += inv.amount
                
        return total
    
    def calculate_quarterly_federal_tax(self, year: int, quarter: int) -> float:
        """
        Calculate federal tax for a specific quarter
        
        Args:
            year (int): Year
            quarter (int): Quarter (1-4)
            
        Returns:
            float: Tax amount for the quarter
        """
        earnings = self.get_quarterly_earnings(year, quarter)
        return earnings * self.fed_tax_rate
    
    def calculate_quarterly_state_tax(self, year: int, quarter: int) -> float:
        """
        Calculate state tax for a specific quarter
        
        Args:
            year (int): Year
            quarter (int): Quarter (1-4)
            
        Returns:
            float: State tax amount for the quarter
        """
        earnings = self.get_quarterly_earnings(year, quarter)
        return earnings * self.state_tax_rate
    
    def calculate_sep_401k_limit(self, year: int) -> Dict:
        """
        Calculate SEP 401(k) contribution limits based on yearly income
        
        Args:
            year (int): Year
            
        Returns:
            Dict: Contribution limits information
        """
        yearly_earnings = self.get_yearly_earnings(year)
        
        # SEP IRA contribution limit calculation
        # For self-employed, the limit is approximately 20% of net income due to deduction calculation
        effective_rate = 0.20  # Simplified calculation
        
        # Annual IRS limits (2024 values - would need to be updated each year)
        max_contribution_limit = 69000  # For 2024
        
        # Calculate potential contribution
        potential_contribution = yearly_earnings * effective_rate
        actual_contribution = min(potential_contribution, max_contribution_limit)
        
        return {
            'yearly_earnings': yearly_earnings,
            'potential_contribution': potential_contribution,
            'actual_contribution': actual_contribution,
            'max_contribution_limit': max_contribution_limit,
            'contribution_percent': 0 if yearly_earnings == 0 else (actual_contribution / yearly_earnings * 100)
        }
    
    def get_all_invoices(self) -> List[Invoice]:
        """
        Get all invoices
        
        Returns:
            List[Invoice]: List of all invoices, sorted by date
        """
        return sorted(self.invoices, key=lambda x: x.date)
    
    def set_tax_rates(self, fed_rate: float, state_rate: float, state_code: str) -> Tuple[bool, str]:
        """
        Set new tax rates
        
        Args:
            fed_rate (float): Federal tax rate (0.0 to 1.0)
            state_rate (float): State tax rate (0.0 to 1.0)
            state_code (str): State code
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if 0.0 <= fed_rate <= 1.0 and 0.0 <= state_rate <= 1.0:
            self.fed_tax_rate = fed_rate
            self.state_tax_rate = state_rate
            self.state_code = state_code
            self.save_invoices()
            return True, f"Tax rates updated: Federal {fed_rate:.2%}, State {state_rate:.2%} ({state_code})"
        else:
            return False, "Tax rates must be between 0.0 and 1.0"
    
    def export_to_csv(self, filename: str) -> Tuple[bool, str]:
        """
        Export invoices to CSV file
        
        Args:
            filename (str): Output CSV filename
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Invoice ID', 'Date', 'Amount', 'Description'])
                
                for inv in sorted(self.invoices, key=lambda x: x.date):
                    writer.writerow([inv.invoice_id, inv.date.isoformat(), inv.amount, inv.description])
            
            return True, f"Exported {len(self.invoices)} invoices to {filename}"
        except Exception as e:
            return False, f"Export failed: {e}"
    
    def generate_quarterly_report(self, year: int, quarter: int = None) -> Dict:
        """
        Generate a quarterly report
        
        Args:
            year (int): Year
            quarter (int, optional): Quarter (1-4). If None, generates for all quarters
            
        Returns:
            Dict: Report data
        """
        if quarter is not None:
            quarters = [quarter]
        else:
            quarters = [1, 2, 3, 4]
        
        report = {
            'year': year,
            'quarters': {}
        }
        
        for q in quarters:
            earnings = self.get_quarterly_earnings(year, q)
            fed_tax = self.calculate_quarterly_federal_tax(year, q)
            state_tax = self.calculate_quarterly_state_tax(year, q)
            
            start_date, end_date = self.get_quarter_bounds(year, q)
            invoices = [inv for inv in self.invoices if start_date <= inv.date <= end_date]
            
            report['quarters'][q] = {
                'earnings': earnings,
                'fed_tax': fed_tax,
                'state_tax': state_tax,
                'total_tax': fed_tax + state_tax,
                'invoice_count': len(invoices)
            }
        
        # Add SEP 401(k) contribution information if generating full year report
        if quarter is None:
            report['sep_401k'] = self.calculate_sep_401k_limit(year)
        
        return report

    def change_data_location(self, new_location: str) -> Tuple[bool, str]:
        """
        Change the data file location
        
        Args:
            new_location (str): New data file path
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            # Save current data to new location
            old_data_file = self.data_file
            self.data_file = new_location
            self.save_invoices()
            return True, f"Data location changed to {new_location}"
        except Exception as e:
            # Revert if failed
            self.data_file = old_data_file
            return False, f"Failed to change data location: {e}"

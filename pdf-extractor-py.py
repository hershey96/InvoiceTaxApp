"""
PDF Invoice Extractor module for InvoiceTaxApp

This module contains the PdfInvoiceExtractor class which handles
extraction of invoice data from PDF documents.
"""

import datetime
import re
import pdfplumber
from typing import List, Dict


class PdfInvoiceExtractor:
    """Class for extracting invoice information from PDF files"""
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> List[Dict]:
        """
        Extract invoice information from a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of invoice dictionaries
        """
        invoices = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract text from page
                    text = page.extract_text()
                    
                    # Look for invoice table
                    # Try to find a table with invoice data
                    tables = page.extract_tables()
                    
                    for table in tables:
                        # Look for table with invoice-related headers
                        headers = [str(h).strip() if h else "" for h in table[0]]
                        
                        # Check if this looks like an invoice table
                        if (any("invoice" in h.lower() for h in headers) and 
                            any("date" in h.lower() for h in headers) and
                            any("amount" in h.lower() for h in headers)):
                            
                            # Find column indices
                            try:
                                doc_type_idx = next(i for i, h in enumerate(headers) if "type" in h.lower())
                                doc_num_idx = next(i for i, h in enumerate(headers) if "number" in h.lower())
                                date_idx = next(i for i, h in enumerate(headers) if "date" in h.lower())
                                amount_idx = next(i for i, h in enumerate(headers) if "amount" in h.lower())
                                currency_idx = next(i for i, h in enumerate(headers) if "currency" in h.lower())
                            except StopIteration:
                                continue
                            
                            # Process rows (skip header)
                            for row in table[1:]:
                                if not row or not any(row):
                                    continue
                                
                                # Clean and validate row data
                                if len(row) <= max(doc_type_idx, doc_num_idx, date_idx, amount_idx, currency_idx):
                                    continue
                                
                                doc_type = str(row[doc_type_idx]).strip() if row[doc_type_idx] else ""
                                doc_num = str(row[doc_num_idx]).strip() if row[doc_num_idx] else ""
                                date_str = str(row[date_idx]).strip() if row[date_idx] else ""
                                amount_str = str(row[amount_idx]).strip() if row[amount_idx] else ""
                                currency = str(row[currency_idx]).strip() if row[currency_idx] else ""
                                
                                # Skip empty rows
                                if not doc_type or not doc_num or not date_str or not amount_str:
                                    continue
                                
                                # Parse date (handle different formats)
                                try:
                                    # Try DD/MM/YYYY format
                                    if '/' in date_str:
                                        date_parts = date_str.split('/')
                                        if len(date_parts) == 3:
                                            date = datetime.date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
                                    # Try YYYY-MM-DD format
                                    elif '-' in date_str:
                                        date_parts = date_str.split('-')
                                        if len(date_parts) == 3:
                                            date = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                                    else:
                                        # Skip rows with invalid dates
                                        continue
                                except (ValueError, IndexError):
                                    # Skip rows with invalid dates
                                    continue
                                
                                # Parse amount (handle currency symbols and commas)
                                try:
                                    # Remove currency symbols, commas, and spaces
                                    amount_clean = re.sub(r'[^\d.]', '', amount_str)
                                    amount = float(amount_clean)
                                except ValueError:
                                    # Skip rows with invalid amounts
                                    continue
                                
                                # Add invoice to list
                                invoice = {
                                    'date': date,
                                    'amount': amount,
                                    'description': f"{doc_type}: {doc_num}",
                                    'currency': currency,
                                    'doc_number': doc_num
                                }
                                
                                invoices.append(invoice)
                    
                    # If no tables were found or extracted, try text-based extraction
                    if not invoices:
                        # Look for patterns like "Invoice XXX-XXX-XXX Date: MM/DD/YYYY Amount: $X,XXX.XX"
                        invoice_patterns = [
                            # Pattern for "Invoice: XXX Date: MM/DD/YYYY Amount: $X,XXX.XX"
                            r'Invoice[:\s]+([^\s]+).*?Date[:\s]+(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}-\d{1,2}).*?Amount[:\s]+[$£€]?([0-9,.]+)',
                            # Pattern for table-like structure in text
                            r'Invoice\s+([^\s]+)\s+(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}-\d{1,2})\s+[$£€]?([0-9,.]+)'
                        ]
                        
                        for pattern in invoice_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                doc_num, date_str, amount_str = match
                                
                                # Parse date
                                try:
                                    if '/' in date_str:
                                        date_parts = date_str.split('/')
                                        date = datetime.date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
                                    else:
                                        date_parts = date_str.split('-')
                                        date = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                                except (ValueError, IndexError):
                                    continue
                                
                                # Parse amount
                                try:
                                    amount_clean = re.sub(r'[^\d.]', '', amount_str)
                                    amount = float(amount_clean)
                                except ValueError:
                                    continue
                                
                                # Add invoice to list
                                invoice = {
                                    'date': date,
                                    'amount': amount,
                                    'description': f"Invoice: {doc_num}",
                                    'currency': 'USD',  # Default currency if not specified
                                    'doc_number': doc_num
                                }
                                
                                invoices.append(invoice)
            
            return invoices
            
        except Exception as e:
            print(f"Error extracting from PDF: {e}")
            return []
    
    @staticmethod
    def extract_from_remittance_advice(pdf_path: str) -> List[Dict]:
        """
        Extract invoice information specifically from remittance advice PDFs
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of invoice dictionaries
        """
        invoices = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract text and tables
                    text = page.extract_text()
                    tables = page.extract_tables()
                    
                    # Check if this is a remittance advice
                    if "remittance advice" in text.lower():
                        # Look for tables with invoice data
                        for table in tables:
                            if len(table) < 2:  # Need at least header and one data row
                                continue
                                
                            # Check if this table has invoice-like headers
                            headers = [str(col).strip().lower() if col else "" for col in table[0]]
                            
                            # Common header patterns in remittance advice
                            if (("document" in " ".join(headers) or "invoice" in " ".join(headers)) and
                                ("date" in " ".join(headers)) and
                                ("amount" in " ".join(headers))):
                                
                                # Find the relevant column indices
                                doc_type_idx = None
                                doc_num_idx = None
                                date_idx = None
                                amount_idx = None
                                currency_idx = None
                                
                                for i, header in enumerate(headers):
                                    if "type" in header and "document" in header:
                                        doc_type_idx = i
                                    elif "number" in header and ("document" in header or "invoice" in header):
                                        doc_num_idx = i
                                    elif "date" in header:
                                        date_idx = i
                                    elif "amount" in header and "payment" in header:
                                        amount_idx = i
                                    elif "currency" in header:
                                        currency_idx = i
                                
                                # Skip if we can't identify the necessary columns
                                if None in (doc_type_idx, doc_num_idx, date_idx, amount_idx):
                                    continue
                                
                                # Process data rows (skip header)
                                for row in table[1:]:
                                    if not row or len(row) <= max(doc_type_idx, doc_num_idx, date_idx, amount_idx):
                                        continue
                                    
                                    try:
                                        # Extract data from row
                                        doc_type = str(row[doc_type_idx]).strip() if row[doc_type_idx] else ""
                                        doc_num = str(row[doc_num_idx]).strip() if row[doc_num_idx] else ""
                                        date_str = str(row[date_idx]).strip() if row[date_idx] else ""
                                        amount_str = str(row[amount_idx]).strip() if row[amount_idx] else ""
                                        
                                        # Currency might be in a separate column or part of amount
                                        currency = "USD"  # Default
                                        if currency_idx is not None and row[currency_idx]:
                                            currency = str(row[currency_idx]).strip()
                                        elif "USD" in amount_str or "$" in amount_str:
                                            currency = "USD"
                                        elif "EUR" in amount_str or "€" in amount_str:
                                            currency = "EUR"
                                        elif "GBP" in amount_str or "£" in amount_str:
                                            currency = "GBP"
                                        
                                        # Skip if missing essential data
                                        if not doc_num or not date_str or not amount_str:
                                            continue
                                        
                                        # Parse date
                                        date = None
                                        date_formats = [
                                            # Try various date formats
                                            ('%d/%m/%Y', r'\d{1,2}/\d{1,2}/\d{4}'),
                                            ('%m/%d/%Y', r'\d{1,2}/\d{1,2}/\d{4}'),
                                            ('%Y-%m-%d', r'\d{4}-\d{1,2}-\d{1,2}'),
                                            ('%d-%m-%Y', r'\d{1,2}-\d{1,2}-\d{4}'),
                                            ('%d.%m.%Y', r'\d{1,2}\.\d{1,2}\.\d{4}')
                                        ]
                                        
                                        for date_format, pattern in date_formats:
                                            if re.match(pattern, date_str):
                                                try:
                                                    date = datetime.datetime.strptime(date_str, date_format).date()
                                                    break
                                                except ValueError:
                                                    continue
                                        
                                        if date is None:
                                            continue
                                        
                                        # Parse amount
                                        # Remove currency symbols and non-numeric chars except decimal points
                                        amount_clean = re.sub(r'[^\d.]', '', amount_str)
                                        amount = float(amount_clean)
                                        
                                        # Create invoice dictionary
                                        invoice = {
                                            'date': date,
                                            'amount': amount,
                                            'description': f"{doc_type}: {doc_num}" if doc_type else f"Invoice: {doc_num}",
                                            'currency': currency,
                                            'doc_number': doc_num
                                        }
                                        
                                        invoices.append(invoice)
                                        
                                    except (ValueError, IndexError) as e:
                                        print(f"Error processing row: {e}")
                                        continue
            
            return invoices
            
        except Exception as e:
            print(f"Error extracting from remittance advice PDF: {e}")
            return []

"""
Main application module for InvoiceTaxApp

This module contains the InvoiceTaxApp class which handles the UI components
and orchestrates the application's functionality.
"""

import datetime
import os
import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkcalendar import DateEntry

# Import other modules
from .calculator import BusinessTaxCalculator
from .pdf_extractor import PdfInvoiceExtractor

class InvoiceTaxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Business Invoice & Tax Calculator")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Initialize calculator with default locations
        self.calculator = BusinessTaxCalculator()
        
        # Create the notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.invoices_tab = ttk.Frame(self.notebook)
        self.import_tab = ttk.Frame(self.notebook)
        self.tax_calc_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.sep_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.invoices_tab, text="Invoices")
        self.notebook.add(self.import_tab, text="Import PDF")
        self.notebook.add(self.tax_calc_tab, text="Tax Calculator")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.sep_tab, text="SEP 401(k)")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Setup each tab
        self.setup_invoices_tab()
        self.setup_import_tab()
        self.setup_tax_calc_tab()
        self.setup_reports_tab()
        self.setup_sep_tab()
        self.setup_settings_tab()
        
        # Create status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set app icon and styling
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', padding=3)
        self.style.configure('TEntry', padding=3)
        
        # Store extracted invoices temporarily
        self.extracted_invoices = []
        
        # Refresh data
        self.refresh_invoice_list()
    
    def setup_invoices_tab(self):
        """Setup the invoices management tab"""
        frame = ttk.Frame(self.invoices_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Invoice form
        form_frame = ttk.LabelFrame(frame, text="Add Invoice", padding="10")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Date field
        ttk.Label(form_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Amount field
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(form_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Description field
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var, width=25)
        self.desc_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Invoice", command=self.add_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Right side - Invoice list
        list_frame = ttk.LabelFrame(frame, text="Invoices", padding="10")
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Treeview for invoices
        columns = ('id', 'date', 'amount', 'description')
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.invoice_tree.heading('id', text='Invoice ID')
        self.invoice_tree.heading('date', text='Date')
        self.invoice_tree.heading('amount', text='Amount')
        self.invoice_tree.heading('description', text='Description')
        
        # Define columns
        self.invoice_tree.column('id', width=120)
        self.invoice_tree.column('date', width=100)
        self.invoice_tree.column('amount', width=100)
        self.invoice_tree.column('description', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscroll=scrollbar.set)
        
        # Pack everything
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame for invoice actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh List", command=self.refresh_invoice_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
    
    def setup_import_tab(self):
        """Setup the PDF import tab"""
        frame = ttk.Frame(self.import_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - PDF selection and extraction
        top_frame = ttk.LabelFrame(frame, text="Import PDF Invoices", padding="10")
        top_frame.pack(fill=tk.X, pady=10)
        
        # PDF file selection
        file_frame = ttk.Frame(top_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.pdf_path_var = tk.StringVar()
        ttk.Label(file_frame, text="PDF File:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Extract Invoices", command=self.extract_pdf_invoices).pack(side=tk.LEFT, padx=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(frame, text="Extracted Invoices Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for extracted invoices
        columns = ('select', 'date', 'doc_number', 'amount', 'currency', 'description')
        self.extracted_tree = ttk.Treeview(preview_frame, columns=columns, show='headings')
        
        # Define headings
        self.extracted_tree.heading('select', text='Import')
        self.extracted_tree.heading('date', text='Date')
        self.extracted_tree.heading('doc_number', text='Document Number')
        self.extracted_tree.heading('amount', text='Amount')
        self.extracted_tree.heading('currency', text='Currency')
        self.extracted_tree.heading('description', text='Description')
        
        # Define columns
        self.extracted_tree.column('select', width=50, anchor=tk.CENTER)
        self.extracted_tree.column('date', width=100)
        self.extracted_tree.column('doc_number', width=150)
        self.extracted_tree.column('amount', width=100)
        self.extracted_tree.column('currency', width=80)
        self.extracted_tree.column('description', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.extracted_tree.yview)
        self.extracted_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.extracted_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame for import actions
        action_frame = ttk.Frame(preview_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Toggle Selected", command=self.toggle_selected_import).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Select All", command=self.select_all_imports).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Selection", command=self.clear_all_imports).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Import Selected", command=self.import_selected_invoices).pack(side=tk.RIGHT, padx=5)
        
        # Log section for import process
        log_frame = ttk.LabelFrame(frame, text="Import Log", padding="10")
        log_frame.pack(fill=tk.X, pady=10)
        
        self.import_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=5)
        self.import_log.pack(fill=tk.BOTH, expand=True)
        self.import_log.insert(tk.END, "Select a PDF file and click 'Extract Invoices' to begin.\n")
        self.import_log.config(state=tk.DISABLED)
    
    def setup_tax_calc_tab(self):
        """Setup the tax calculation tab"""
        frame = ttk.Frame(self.tax_calc_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Year and quarter selection
        select_frame = ttk.LabelFrame(frame, text="Select Period", padding="10")
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(select_frame, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        current_year = datetime.date.today().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(select_frame, textvariable=self.year_var, width=6)
        year_combo['values'] = tuple(range(current_year-5, current_year+2))
        year_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Quarter:").grid(row=0, column=2, padx=5, pady=5)
        self.quarter_var = tk.StringVar(value="1")
        quarter_combo = ttk.Combobox(select_frame, textvariable=self.quarter_var, width=2)
        quarter_combo['values'] = ("1", "2", "3", "4")
        quarter_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(select_frame, text="Calculate", command=self.calculate_tax).grid(row=0, column=4, padx=20, pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(frame, text="Quarterly Tax Calculation", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results display
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(results_text_frame, wrap=tk.WORD, height=20, width=80)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text.insert(tk.END, "Select a year and quarter, then click Calculate.")
        self.results_text.config(state=tk.DISABLED)
    
    def setup_reports_tab(self):
        """Setup the reports tab"""
        frame = ttk.Frame(self.reports_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Year selection
        select_frame = ttk.LabelFrame(frame, text="Generate Report", padding="10")
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(select_frame, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        current_year = datetime.date.today().year
        self.report_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(select_frame, textvariable=self.report_year_var, width=6)
        year_combo['values'] = tuple(range(current_year-5, current_year+2))
        year_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Quarter:").grid(row=0, column=2, padx=5, pady=5)
        self.report_quarter_var = tk.StringVar(value="All")
        quarter_combo = ttk.Combobox(select_frame, textvariable=self.report_quarter_var, width=5)
        quarter_combo['values'] = ("All", "1", "2", "3", "4")
        quarter_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(select_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=4, padx=20, pady=5)
        ttk.Button(select_frame, text="Export Report", command=self.export_report).grid(row=0, column=5, padx=5, pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(frame, text="Quarterly Report", padding="10")
        report_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Report text display
        report_text_frame = ttk.Frame(report_frame)
        report_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.report_text = tk.Text(report_text_frame, wrap=tk.WORD, height=20, width=80)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(report_text_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.report_text.insert(tk.END, "Select a year and optional quarter, then click Generate Report.")
        self.report_text.config(state=tk.DISABLED)

    def setup_sep_tab(self):
        """Setup the SEP 401(k) calculation tab"""
        frame = ttk.Frame(self.sep_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Year selection
        select_frame = ttk.LabelFrame(frame, text="Calculate SEP 401(k) Contribution Limits", padding="10")
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(select_frame, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        current_year = datetime.date.today().year
        self.sep_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(select_frame, textvariable=self.sep_year_var, width=6)
        year_combo['values'] = tuple(range(current_year-5, current_year+2))
        year_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(select_frame, text="Calculate", command=self.calculate_sep).grid(row=0, column=2, padx=20, pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(frame, text="SEP 401(k) Calculation Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results display
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sep_results_text = tk.Text(results_text_frame, wrap=tk.WORD, height=20, width=80)
        self.sep_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, command=self.sep_results_text.yview)
        self.sep_results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sep_results_text.insert(tk.END, "Select a year, then click Calculate to determine SEP 401(k) contribution limits.")
        self.sep_results_text.config(state=tk.DISABLED)
        
    def setup_settings_tab(self):
        """Setup the settings tab"""
        frame = ttk.Frame(self.settings_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Tax rate setting
        tax_frame = ttk.LabelFrame(frame, text="Tax Settings", padding="10")
        tax_frame.pack(fill=tk.X, pady=10)
        
        # Federal tax rate
        ttk.Label(tax_frame, text="Federal Tax Rate (%):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fed_tax_rate_var = tk.StringVar(value=str(self.calculator.fed_tax_rate * 100))
        fed_tax_entry = ttk.Entry(tax_frame, textvariable=self.fed_tax_rate_var, width=6)
        fed_tax_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # State tax rate
        ttk.Label(tax_frame, text="State Tax Rate (%):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.state_tax_rate_var = tk.StringVar(value=str(self.calculator.state_tax_rate * 100))
        state_tax_entry = ttk.Entry(tax_frame, textvariable=self.state_tax_rate_var, width=6)
        state_tax_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # State code
        ttk.Label(tax_frame, text="State Code:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.state_code_var = tk.StringVar(value=self.calculator.state_code)
        state_code_entry = ttk.Entry(tax_frame, textvariable=self.state_code_var, width=6)
        state_code_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(tax_frame, text="Update Tax Rates", command=self.update_tax_rates).grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        
        # File locations
        file_frame = ttk.LabelFrame(frame, text="File Locations", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Data File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_file_var = tk.StringVar(value=self.calculator.data_file)
        ttk.Entry(file_frame, textvariable=self.data_file_var, width=50, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Change...", command=self.change_data_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Default Export Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "exports"))
        ttk.Entry(file_frame, textvariable=self.export_dir_var, width=50, state="readonly").grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Change...", command=self.change_export_dir).grid(row=1, column=2, padx=5, pady=5)
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir_var.get(), exist_ok=True)
        
        # About section
        about_frame = ttk.LabelFrame(frame, text="About", padding="10")
        about_frame.pack(fill=tk.X, pady=10)
        
        about_text = "Business Invoice & Tax Calculator\n\n"
        about_text += "A tool to manage invoices and calculate quarterly taxes for your business.\n"
        about_text += "Includes federal and state tax calculations and SEP 401(k) contribution limits."
        
        ttk.Label(about_frame, text=about_text, justify=tk.LEFT).pack(padx=5, pady=5)
    
    # The rest of your methods would go here...
    # I'll include a few key methods as examples
    
    def add_invoice(self):
        """Add a new invoice from the form"""
        try:
            # Get form values
            date = self.date_entry.get_date()
            amount = float(self.amount_var.get())
            description = self.desc_var.get()
            
            # Validate
            if amount <= 0:
                messagebox.showerror("Invalid Input", "Amount must be greater than zero")
                return
                
            if not description:
                messagebox.showerror("Invalid Input", "Description cannot be empty")
                return
            
            # Add invoice
            success, message = self.calculator.add_invoice(date, amount, description)
            
            if success:
                self.status_var.set(message)
                self.clear_form()
                self.refresh_invoice_list()
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric amount")
    
    def browse_pdf(self):
        """Browse for a PDF file"""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.pdf_path_var.set(filename)
    
    def extract_pdf_invoices(self):
        """Extract invoices from the selected PDF file"""
        pdf_path = self.pdf_path_var.get()
        
        if not pdf_path:
            messagebox.showinfo("Selection Required", "Please select a PDF file first")
            return
            
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"The file '{pdf_path}' does not exist")
            return
            
        # Clear previous data
        for item in self.extracted_tree.get_children():
            self.extracted_tree.delete(item)
            
        self.update_import_log("Extracting invoices from PDF...", clear=True)
        
        # Extract invoices from PDF
        invoices = PdfInvoiceExtractor.extract_from_pdf(pdf_path)
        
        if not invoices:
            self.update_import_log("No invoices found in the PDF.")
            return
            
        # Store extracted invoices and update the tree
        self.extracted_invoices = invoices
        self.update_import_log(f"Found {len(invoices)} invoices in the PDF.")
        
        for i, inv in enumerate(invoices):
            item_id = self.extracted_tree.insert('', 'end', values=(
                "✓",  # Default to selected
                inv['date'].isoformat(),
                inv['doc_number'],
                f"{inv['amount']:.2f}",
                inv['currency'],
                inv['description']
            ))
            
            # Bind toggle event to the first column
            self.extracted_tree.tag_bind(item_id, '<ButtonRelease-1>', self.toggle_import_selection)
            
        self.update_import_log("Review the extracted invoices and click 'Import Selected' to add them to your system.")
    
    # Add all your other methods here...
    
    def clear_form(self):
        """Clear the invoice form"""
        self.date_entry.set_date(datetime.date.today())
        self.amount_var.set("")
        self.desc_var.set("")
    
    def refresh_invoice_list(self):
        """Refresh the invoice list display"""
        # Clear the treeview
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Add all invoices
        invoices = self.calculator.get_all_invoices()
        for inv in invoices:
            self.invoice_tree.insert('', 'end', values=(
                inv.invoice_id,
                inv.date.isoformat(),
                f"${inv.amount:.2f}",
                inv.description
            ))
    
    def update_import_log(self, message, clear=False):
        """Update the import log with a message"""
        self.import_log.config(state=tk.NORMAL)
        if clear:
            self.import_log.delete(1.0, tk.END)
        self.import_log.insert(tk.END, message + "\n")
        self.import_log.see(tk.END)
        self.import_log.config(state=tk.DISABLED)

def main():
    """Main entry point for the application"""
    app = InvoiceTaxApp()
    app.mainloop()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ... import (ProResource, RelatedResourceMixin)


class Company(RelatedResourceMixin, ProResource):

    path = 'companies'

    attribute_names = [
        # this is filled by __init__ and must match this value 'id',
        # integer The registered company number (ID) of the company
        'last_update',
        # dateTime Date last updated
        'name',
        # string The registered company name
        'description',
        # string A description of the company filed with the registrar
        'status',
        # string The status of the company
        'incorporation_date',
        # dateTime The date the company was incorporated
        'latest_annual_return_date',
        # dateTime Date of most recent annual return
        'latest_accounts_date',
        # dateTime Date of most recent filed accounts
        'company_type',
        # string The company type
        'accounts_type',
        # string Type of accounts
        'sic_code',
        # integer Standard Industry Classification (SIC) code
        'previous_company_names_url',
        # string Link to previous company names
        'shareholdings_url',
        # string Link to shareholders information
        'accounts_account_status',
        # integer Accounts status
        'accounts_accounts_format',
        # integer Accounts format
        'accounts_assets_current',
        # integer Current assets
        'accounts_assets_intangible',
        # integer Intangible assets
        'accounts_assets_net',
        # integer Net assets
        'accounts_assets_other_current',
        # integer Other current assets
        'accounts_assets_tangible',
        # integer Tangible assets
        'accounts_url',
        # string Link to company accounts
        'accounts_assets_total_current',
        # integer Total current assets
        'accounts_assets_total_fix',
        # integer Total fixed assets
        'accounts_audit_fees',
        # integer Audit fees
        'accounts_bank_overdraft',
        # integer Bank overdraft
        'accounts_bank_overdraft_lt_loans',
        # integer Bank overdraft & long term loans
        'accounts_capital_employed',
        # integer Capital employed
        'accounts_cash',
        # integer Cash
        'accounts_consolidated',
        # boolean Accounts consolidated (Y/N)
        'accounts_cost_of_sales',
        # integer Cost of sales
        'accounts_currency',
        # string Accounts currency
        'accounts_date',
        # dateTime Accounts date
        'accounts_depreciation',
        # integer Depreciation
        'accounts_directors_emoluments',
        # integer Directors' emoluments
        'accounts_dividends_payable',
        # integer Dividends payable
        'accounts_gross_profit',
        # integer Gross profit
        'accounts_increase_in_cash',
        # integer Increase in cash
        'accounts_interest_payments',
        # integer Interest payments
        'accounts_liabilities_current',
        # integer Current liabilities
        'accounts_liabilities_lt',
        # integer Long term liabilities
        'accounts_liabilities_misc_current',
        # integer Miscellaneous current liabilities
        'accounts_liabilities_total',
        # integer Total liabilities
        'accounts_lt_loans',
        # integer Long term loans
        'accounts_months',
        # integer Months included in accounts
        'accounts_net_cashflow_before_financing',
        # integer Net cashflow before financing
        'accounts_net_cashflow_from_financing',
        # integer Net cashflow from financing
        'accounts_net_worth',
        # integer Net worth
        'accounts_no_of_employees',
        # integer Number of employees
        'accounts_operating_profits',
        # integer Operating profits
        'accounts_operations_net_cashflow',
        # integer Net cashflow
        'accounts_paid_up_equity',
        # integer Paid-up equity
        'accounts_pandl_account_reserve',
        # integer Account reserve
        'accounts_pre_tax_profit',
        # integer Pre-tax profit
        'accounts_profit_after_tax',
        # integer Profit after tax
        'accounts_retained_profit',
        # integer Retained profit
        'accounts_shareholder_funds',
        # integer Shareholder funds
        'accounts_short_term_loans',
        # integer Short term loans
        'accounts_stock',
        # integer Stock
        'accounts_sundry_reserves',
        # integer Sundry reserves
        'accounts_taxation',
        # integer Taxation
        'accounts_trade_creditors',
        # integer Trade creditors
        'accounts_turnover',
        # integer Turnover
        'accounts_wages',
        # integer Wages
        'accounts_working_capital',
        # integer Working capital
        'directors_url',
        # string Link to company directors
        'directorships_url',
        # string Link to directorships
        'directorships_open',
        # integer Number of open directorships
        'directorships_open_secretary',
        # integer Number of current directorships with Company Secretary status
        'directorships_open_director',
        # integer Number of current directorships with Director status
        'directorships_retired',
        # integer Number of retired directorships
        'directorships_retired_secretary',
        # integer Of which secretaries
        'directorships_retired_director',
        # integer Of which directors
        'subsidiaries_url',
        # string Link to company subsidiaries
        'documents_url',
        # string Link to original company documents
        'accounts_filing_date',
        # dateTime Accounts filing date
        'ftse_a',
        # integer FTSE listing category
        'mortgage_partial_outstanding_count',
        # integer Number of partially outstanding mortgages
        'mortgage_partial_property_satisfied_count',
        # integer Number of partially satified mortgages
        'mortgage_partial_property_count',
        # integer Number of partial mortgages
        'mortgages_url',
        # string Link to mortgages
        'mortgages_outstanding_count',
        # integer Number of outstanding mortgages
        'mortgages_satisfied_count',
        # integer Number of satisfied mortgages
        'reg_address1',
        # string Registered address street
        'reg_address2',
        # string Registered address town
        'reg_address3',
        # string Registered address county
        'reg_address4',
        # string Registered address country
        'reg_address_postcode',
        # string Registered address postcode
        'reg_area_code',
        # string Registered address area code
        'reg_phone',
        # string Registered phone number
        'reg_tps',
        # boolean Telephone Preference Service (TPS) notification (Y/N)
        'reg_web',
        # string Registered web address
        'sic2007code',
        'sic2007description',
        # integer 2007 Standard Industry Classification (SIC) code
        'trading_address1',
        # string Trading address street
        'trading_address2',
        # string Trading address town
        'trading_address3',
        # string Trading address county
        'trading_address_postcode',
        # string Trading address postcode

        'charity_number',
        'liquidation_status',
        'directorships_closed_director',
        'sic_description',
        'sic_codes_count',
        'trading_address4',
        'directorships_closed',
        'credit_rating_latest_description',
        'accounts_trade_debtors',
        'directorships_closed_secretary',
        'accounts_accountants',
        'accounts_auditors',
        'accounts_contingent_liability',
        'accounts_exports',
        'accounts_qualification_code',
        'accounts_revaluation_reserve',
        'accounts_solicitors',
        'bank_accounts_url',
        'next_annual_return_date',
        'preference_shareholdings_count',
        'preference_shares_issued',
        'reg_address_town',
        'reg_address_towncode',
        'reg_care_of',
        'reg_email',
        'trading_phone',
        'trading_phone_std',
        'company_url',
        # 'turnover',
        # 'turnover_delta_percentage',
    ]

    related_resources = {
        'service-addresses': 'pro.company.ServiceAddress',
        'registered-address': 'pro.company.RegisteredAddress',
        'parent': 'pro.company.Company',
        'directors': 'pro.company.Director',
        'directorships': 'pro.company.DirectorShip',
        'accounts': 'pro.company.Account',
        'previous-company-names': 'pro.company.PreviousCompanyName',
        'industries': 'pro.company.Industry',
        'shareholders': 'pro.company.Shareholder',
        'bank-accounts': 'pro.company.BankAccount',
        'mortgages': 'pro.company.Mortgage',
        'subsidiaries': 'pro.company.Company',
        'keywords': 'pro.company.Keywords',
    }

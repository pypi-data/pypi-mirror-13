

# from ...resources import Resource
from .. import SearchResource


class CompanySearchResult(SearchResource):
    attribute_names = [
        'locale',
        'name',
        'company_url'
    ]
    result_obj = {
        'company': 'duedil.resources.pro.company.Company'
    }
    term_filters = [
        "locale",
        "location",
        "postcode",
        "sic_code",
        "sic_2007_code",
        "status",
        "currency",
        "keywords",
        "name",
    ]
    range_filters = [
        "employee_count",
        "turnover",
        "turnover_delta_percentage",
        "gross_profit",
        "gross_profit_delta_percentage",
        "cost_of_sales",
        "cost_of_sales_delta_percentage",
        "net_assets",
        "net_assets_delta_percentage",
        "current_assets",
        "current_assets_delta_percentage",
        "total_assets",
        "total_assets_delta_percentage",
        "cash",
        "cash_delta_percentage",
        "total_liabilities",
        "total_liabilities_delta_percentage",
        "net_worth",
        "net_worth_delta_percentage",
        "depreciation",
        "depreciation_delta_percentage",
        "taxation",
        "retained_profits",
        "profit_ratio",
        "inventory_turnover_ratio",
        "net_profitability",
        "return_on_capital_employed",
        "cash_to_total_assets_ratio",
        "gearing",
        "gross_margin_ratio",
        "return_on_assets_ratio",
        "current_ratio",
        "debt_to_capital_ratio",
        "cash_to_current_liabilities_ratio",
        "liquidity_ratio",
    ]

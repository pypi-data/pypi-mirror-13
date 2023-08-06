
from .. import SearchResource


class DirectorSearchResult(SearchResource):
    attribute_names = [
        'name',
        'locale',
        'date_of_birth',
        'director_url',
        'directorships_url',
        'companies_url',
    ]

    result_obj = {
        # this import path is incorrect.
        'director': 'duedil.resources.pro.director.Director'
    }
    term_filters = [
        "name",
        "gender",
        "title",
        "nationality",
        "secretarial",
        "corporate",
        "disqualified",
    ]
    range_filters = [
        "age",
        "data_of_birth",
        "gross_profit",
        "gross_profit_delta_percentage",
        "turnover",
        "turnover_delta_percentage",
        "cost_of_sales",
        "cost_of_sales_delta_percentage",
        "depreciation",
        "depreciation_delta_percentage",
        "taxation",
        "cash",
        "cash_delta_percentage",
        "net_worth",
        "net_worth_delta_percentage",
        "total_assets",
        "total_assets_delta_percentage",
        "current_assets",
        "current_assets_delta_percentage",
        "net_assets",
        "net_assets_delta_percentage",
        "total_liabilities",
        "total_liabilities_delta_percentage",
    ]

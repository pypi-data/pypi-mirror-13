from __future__ import unicode_literals


from ... import ProResource, RelatedResourceMixin


class Director(RelatedResourceMixin, ProResource):

    path = 'directors'

    attribute_names = [
        # 'id',
        # string Director ID
        'last_update',
        # dateTime Date last updated
        'open_directorships_count',
        # integer Number of open directorships
        'open_trading_directorships_count',
        # integer Number of open trading directorships
        'open_trading_director_directorships_count',
        # integer Of which a director
        'open_trading_secretary_directorships_count',
        # integer Of which a secretary
        'closed_directorships_count',
        # integer Number of closed directorships
        'retired_directorships_count',
        # integer Number of retired directorships
        'director_directorships_count',
        # integer Number of directorships (director)
        'open_director_directorships_count',
        # integer Number of open directorships (director)
        'closed_director_directorships_count',
        # integer Number of closed directorships (director)
        'secretary_directorships_count',
        # integer Number of secretary directorships
        'open_secretary_directorships_count',
        # integer Number of open secretary directorships
        'closed_secretary_directorships_count',
        # integer Number of closed secretary directorships
        'retired_secretary_directorships_count',
        # integer Number of retired decretary directorships
        'forename',
        # string Forename
        'surname',
        # string Surname
        'date_of_birth',
        # dateTime Date of Birth
        'directorships_url',
        # string Link to directorships
        'companies_url',
        # string Link to companies
        'director_url',
        # string Link to director profile
        # undocumented:
        'middle_name',
        'title',
        'postal_title',
        'nationality',
        'nation_code',
    ]

    related_resources = {
        'companies': 'pro.company.Company',
        'directorships': 'pro.company.DirectorShip',
    }

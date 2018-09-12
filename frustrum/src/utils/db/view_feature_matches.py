from utils.db.base import Base

class ViewFeatureMatches(Base):

    table_name = 'ViewFeatureMatches'

    cols = [
        ('Asset', str),
        ('Category', str),
        ('Session', str),
        ('Site', str),
        ('Version', int),
        ('View', str),        
        ('ToView', str),
        ('FromFeatures', list, int),
        ('GoodMatch', bool),
	('MatchCount', int),
        ('ToFeatures', list, int),
    ]

    def __init__(self, project, instance_id, database_id, defaults):
        super(ViewFeatureMatches, self).__init__(project, instance_id, database_id, ViewFeatureMatches.table_name, defaults)

def get_view_matches(project, instance, client, site, session):        
    defaults = {
        'Site': site,
        'Session': session
    }
    view_matches = ViewFeatureMatches(project, instance, client, defaults)
    result = view_matches.get_select_rows(['View', 'ToView', 'GoodMatch', 'MatchCount'])
    result = [ [r[0].split(':')[-1]] + [r[1].split(':')[-1]] +  r[2:] for r in result]
    return result
    

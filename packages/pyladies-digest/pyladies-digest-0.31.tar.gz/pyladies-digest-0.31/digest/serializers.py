__author__ = 'lorenamesa'

class Conference(object):

    def __init__(self, **kwargs):
        self.date = kwargs.get('date')
        self.name = kwargs.get('name')
        self.location = kwargs.get('location')
        self.url = kwargs.get('url')
        self.cfp = kwargs.get('cfp', False)
        self.cfp_url = kwargs.get('cfp_url')
        self.cfp_deadline = kwargs.get('cfp_deadline')
        self.fa = kwargs.get('fa', False)
        self.fa_url = kwargs.get('fa_url')
        self.fa_deadline = kwargs.get('fa_deadline')
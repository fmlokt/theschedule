##\brief Howto

from environment import JINJA_ENVIRONMENT
from handlers.basehandler import *

class ShowHowto(BaseLocalAdminHandler):
    def get(self, *args, **kwargs):
        super(ShowHowto, self).get(*args, **kwargs)
        template = JINJA_ENVIRONMENT.\
            get_template('templates/howto.html')
        self.response.write(template.render(self.render_data))


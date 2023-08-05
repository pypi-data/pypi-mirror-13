from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.core import handler

from .. import utils

class BoknowsBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Get NCAA statistics and figures"
        arguments = [
            ( ['-s', '--sport'],
              dict(action='store', help='NCAA sport id') ),
            ( ['-y', '--year'],
              dict(action='store', help='Academic year') ),
            ( ['-w', '--weeks'],
              dict(action='store', help='NCAA week id') ),
            ( ['-d', '--div'],
              dict(action='store', help='NCAA division') ),
            ( ['-a', '--stat'],
              dict(action='store', help='NCAA stats id') )
              ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('default csv dump')
        args = {}
        if self.app.pargs.sport:
            self.app.log.info('sport_code: ' + self.app.pargs.sport)
            args['sport_code'] = self.app.pargs.sport
        if self.app.pargs.year:
            self.app.log.info('academic_year: ' + self.app.pargs.year)
            args['academic_year'] = self.app.pargs.year
        if self.app.pargs.weeks:
            self.app.log.info('rpt_weeks: ' + self.app.pargs.weeks)
            args['rpt_weeks'] = self.app.pargs.weeks
        if self.app.pargs.div:
            self.app.log.info('div: ' + self.app.pargs.div)
            args['div'] = self.app.pargs.div
        if self.app.pargs.stat:
            self.app.log.info('stat_seq: ' + self.app.pargs.stat)
            args['stat_seq'] = self.app.pargs.stat
        
        utils.csv_dump(**args)
        

class BoknowsApp(CementApp):
    class Meta:
        label = 'boknows'
        base_controller = 'base'
        handlers = [BoknowsBaseController]

def main():
    with BoknowsApp() as app:
        app.run()

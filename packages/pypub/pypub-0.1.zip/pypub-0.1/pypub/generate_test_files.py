import os.path

from website_pull.website_pull import pullHtml
from constants import *

output_directory = os.path.join(TEST_DIR, 'test_chapters')

test_sites = ['http://www.bothsidesofthetable.com/2011/05/15/quick-practical-tactical-tips-for-presentations',
        'https://en.wikipedia.org/wiki/Venture_capital',
        'http://www.bhorowitz.com/',
        'http://www.economist.com/news/leaders/21604160-iraqs-second-city-has-fallen-group-wants-create-state-which-wage-jihad',
        ]

for index, site in enumerate(test_sites):
    output_name = os.path.join(output_directory, str(index) + '.html')
    pullHtml(site, output_name)


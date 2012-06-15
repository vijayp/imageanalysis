from harvestman.apps.spider import HarvestMan
from harvestman.lib.common.macros import *
import re

class MyCustomCrawler(HarvestMan):
    """ A custom crawler """

    def save_this_url(self, event, *args, **kwargs):
        """ Custom callback function which modifies behaviour
            of saving URLs to disk """

        # Get the url object
        url = event.url
        ustr = str(url)
        # If not image, save always
        if ('/poster' not in ustr):
            return False

        if url.is_document() or (url.is_image() and re.search('[/]t_[^_]+_[^_.]*.jpg',ustr)):
            
            return True
        return False


# Set up the custom crawler
if __name__ == "__main__":
    crawler = MyCustomCrawler()
    crawler.initialize()
    # Get the configuration object
    config = crawler.get_config()
    # Register for 'save_url_data' event which will be called
    # back just before a URL is saved to disk
    crawler.register('save_url_data', crawler.save_this_url)
    # Run
    crawler.main()

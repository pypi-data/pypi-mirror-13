import logging
import json

from netuitive import __version__

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


class Client(object):

    """
        Netuitive Rest Api Client for agent data ingest.
        Posts Element data to Netuitive Cloud

        :param url: Base data source URL
        :type url: string
        :param api_key: API Key for data source
        :type api_key: string


    """

    def __init__(self, url='https://api.app.netuitive.com/ingest',
                 api_key='apikey', agent='Netuitive-Python/' + __version__):

        if url.endswith('/'):
            url = url[:-1]

        self.url = url
        self.api_key = api_key
        self.dataurl = self.url + '/' + self.api_key
        self.eventurl = self.dataurl.replace('/ingest/', '/ingest/events/', 1)
        self.agent = agent

    # these should probably return true on success

    def post(self, element):
        """
            :param element: Element to post to Netuitive
            :type element: object
        """

        payload = json.dumps(
            [element], default=lambda o: o.__dict__, sort_keys=True)
        logging.debug(payload)
        try:

            headers = {'Content-Type': 'application/json',
                       'User-Agent': self.agent}
            request = urllib2.Request(
                self.dataurl, data=payload, headers=headers)
            resp = urllib2.urlopen(request)
            logging.debug("Response code: %d", resp.getcode())

            resp.close()

            return(True)

        except Exception as e:
            logging.exception(
                'error posting payload to api ingest endpoint (%s): %s',
                self.dataurl, e)

    def post_event(self, event):
        """
            :param event: Event to post to Netuitive
            :type event: object
        """

        payload = json.dumps(
            [event], default=lambda o: o.__dict__, sort_keys=True)
        logging.debug(payload)
        try:
            headers = {'Content-Type': 'application/json',
                       'User-Agent': self.agent}
            request = urllib2.Request(
                self.eventurl, data=payload, headers=headers)
            resp = urllib2.urlopen(request)
            logging.debug("Response code: %d", resp.getcode())
            resp.close()

            # if resp.getcode() != 202:
            #     raise Exception("Response code: %d", resp.getcode())

            return(True)

        except Exception as e:
            logging.exception(
                'error posting payload to api ingest endpoint (%s): %s',
                self.eventurl, e)

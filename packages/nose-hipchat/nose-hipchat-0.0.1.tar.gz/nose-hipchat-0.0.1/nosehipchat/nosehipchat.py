import logging
import os
import urllib2
import json

from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.nose-hipchat')


def publish_to_hipchat(url, color, message, notify=False):
    """
    Publishes a message to HipChat using HTTP GET.
    Raises exceptions (from urllib2) for HTTP failure conditions.

    :param url: Complete URL of the form https://yourcompany.hipchat.com/v2/room/12345/notification?auth_token=ABC123
    :param color: String representing a color understood by HipChat (e.g. "green", "red", "yellow")
    :param message: Text to publish in HipChat
    :param notify: Boolean indicating whether HipChat should raise a notification
    :return: String with response from server.
    """
    headers = {"content-type": "application/json"} #, "authorization": "Bearer %s" % V2TOKEN}
    datastr = json.dumps({"color": color, "message": message, "notify": notify, "message_format":"text"})
    request = urllib2.Request(url, headers=headers, data=datastr)
    uo = urllib2.urlopen(request)
    rawresponse = ''.join(uo)
    uo.close()
    return rawresponse


class NoseHipChat(Plugin):
    name = 'nose-hipchat'

    def __init__(self):
        super(NoseHipChat, self).__init__()
        self.epilogue = None
        self.hipchat_url = None

    def options(self, parser, env=os.environ):
        super(NoseHipChat, self).options(parser, env=env)
        parser.add_option("--hipchat-url", action="store",
            dest="hipchat_url",
            metavar="URL",
            help="URL for posting to HipChat. " +
                 "Example: https://yourcompany.hipchat.com/v2/room/12345/notification?auth_token=ABC123")
        parser.add_option("--hipchat-epilogue", action="store",
            dest="hipchat_epilogue",
            metavar="TEXT",
            help='Text to append to HipChat messages' +
                 'Example: nosetests --with-nose-hipchat --hipchat-url=${URL} ' +
                 '--hipchat-epilogue="See log file in /tmp/loggy.log" >> /tmp/loggy.log 2>&1')


    def configure(self, options, conf):
        super(NoseHipChat, self).configure(options, conf)
        if not self.enabled:
            return

        if options.hipchat_url:
            self.hipchat_url = options.hipchat_url
        else:
            # Nose plugins (at least in nose.plugins.0.10) use optparse instead of argparse, and the only way
            # to specify that an option is required is to check for it after the parsing.
            raise ValueError("Missing required --hipchat-url argument. Example: " +
                             "--hipchat-url=https://yourcompany.hipchat.com/v2/room/12345/notification?auth_token=ABC123")

        if options.hipchat_epilogue:
            self.epilogue = options.hipchat_epilogue

    def finalize(self, result):
        color = "red"
        message = ""

        source = ""
        if len(result.config.testNames) == 0:
            source = result.config.workingDir
        elif len(result.config.testNames) == 1:
            source = os.path.join(result.config.workingDir, result.config.testNames[0])
        else:
            source = result.config.workingDir + str(result.config.testNames)

        message += "\nRan %d test%s from %s" % (result.testsRun, result.testsRun != 1 and "s" or "", source)

        if not result.wasSuccessful():
            message += '\nFAILED (failures=%d ' % len(result.failures) + ' errors=%d' % len(result.errors) + ')'
            if len(result.failures) > 0:
                message += '\nFailures:'
                for item in result.failures:
                    message += '\n* ' + str(item[0])
            if len(result.errors) > 0:
                message += '\nErrors:'
                for item in result.errors:
                    message += '\n* ' + str(item[0])
        else:
            color = "green"
            message += '\nSUCCEEDED'

        if self.epilogue is not None:
            message += '\n' + self.epilogue

        publishing_result = publish_to_hipchat(self.hipchat_url, color, message)
        print publishing_result

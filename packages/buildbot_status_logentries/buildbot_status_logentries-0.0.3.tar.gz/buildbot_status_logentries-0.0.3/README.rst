Logentries Buildbot status plugin
=================================

This plugin sends a subset of status updates to the Logentries service.

First install the plugin::

    pip install buildbot_status_logentries


Then in your master.cfg file you can do::

    from buildbot.plugins import *
    c['status'].append(status.LogentriesStatusPush(api_token="c1481e42-75b3-4772-bb7a-db92691d74e9", endpoint="data.logentries.com", port=10000))

To use SSL::

    from buildbot.plugins import *
    c['status'].append(status.LogentriesStatusPush(api_token="c1481e42-75b3-4772-bb7a-db92691d74e9", endpoint="data.logentries.com", port=20000, tls=True))

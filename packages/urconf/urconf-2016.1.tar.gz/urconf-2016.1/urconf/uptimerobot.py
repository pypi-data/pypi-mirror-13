import json
import logging
import types

import requests
import typedecorator

from urconf.uptimerobot_syncable import Contact, Monitor

logger = logging.getLogger("urconf")
typedecorator.setup_typecheck()

DEFAULT_INTERVAL = 5  # minutes

# There are some error codes that mean that mean there is no objects of a given
# type (alert contacts or monitors) defined in the account yet. They are:
# 212: The account has no monitors
# 221: The account has no alert contacts
NO_OBJECTS_ERROR_CODES = ["212", "221"]


class UptimeRobotAPIError(Exception):
    """An exception which is raised when Uptime Robot API returns an error."""
    pass


class UptimeRobot(object):
    """UptimeRobot is the main object used to sync configuration.

    It keeps alert contacts and monitors defined by the user in
    `self._contacts` and `self_monitors` lists.
    """
    @typedecorator.params(self=object, api_key=str, url=str, dry_run=bool)
    def __init__(self, api_key, url="https://api.uptimerobot.com/",
                 dry_run=False):
        """Initializes the configuration.

        Args:
            api_key: (string) Uptime Robot API key. This should be the
                "Main API Key", not one of the monitor-specific API keys.
            url: (string) Base URL for Uptime Robot API.
            dry_run: (bool) Flag that can be set to True to prevent urconf
                from changing Uptime Robot configuration.
        """
        self._url = url.rstrip("/") + "/"
        self._dry_run = dry_run
        # These are HTTP query parameters that will be passed to the API with
        # all requests.
        self.params = {
            "apiKey": api_key,
            "format": "json",
            "noJsonCallback": 1,
        }
        self._contacts = {}
        self._monitors = {}
        # `requests` logs at INFO by default, which is annoying.
        logging.getLogger("requests").setLevel(logging.WARNING)

    @typedecorator.params(self=object, method=str,
                          params={str: typedecorator.Union(str, int)})
    def _api_get(self, method, params):
        """Issues a GET request to the API and returns the result.

        Args:
            method: (string) API method to call.
            params: ({string: string}) A dictionary containing key/value
                pairs that will be used in the URL query string.

        Returns:
            Unmarshalled API response as a Python object.

        Raises:
            UptimeRobotAPIError: when API returns an unexpected error.
        """
        url = self._url + method
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            raise UptimeRobotAPIError("Got HTTP error {} fetching {}".format(
                resp.status_code, url))
        logger.debug("GET {} {}: {}".format(url, params, resp.text))
        try:
            data = json.loads(resp.text)
        except ValueError as e:
            raise UptimeRobotAPIError(
                "Error decoding JSON of {}: {}. Got: {}".format(
                    method, e, resp.text))
        if data["stat"] != "ok" and data["id"] not in NO_OBJECTS_ERROR_CODES:
            raise UptimeRobotAPIError("{} returned error: {} (code {})".format(
                method, data["message"], data["id"]))
        return data

    @typedecorator.params(
        self=object, method=str, params={str: typedecorator.Union(str, int)},
        element_func=types.FunctionType)
    def _api_get_paginated(self, method, params, element_func):
        """Fetches all elements from a given API method.

        This function gets all elements that a given API method returns,
        issuing multiple GET calls if results do not fit in a single page.

        Args:
            method: (string) API method to call.
            params: ({string: string}) A dictionary containing key/value
                pairs that will be used in the URL query string.
            element_func: function that extracts a list of results from the
                object returned by the API call in question. For example, if
                returned JSON is `{"result": [...]}`, the function can be
                `lambda x: x["result"]`.

        Returns:
            A list of Python objects corresponding to API response.
        """
        params = params.copy()
        result = []
        while True:
            response = self._api_get(method, params)
            if "id" in response and response["id"] in NO_OBJECTS_ERROR_CODES:
                # No objects of given type exist yet, return empty list.
                return []
            result.extend(element_func(response))
            for field in ("total", "offset", "limit"):
                response[field] = int(response[field])
            if response["total"] > response["offset"] + response["limit"]:
                params["offset"] = response["offset"] + response["limit"]
            else:
                break
        return result

    def _sync_monitors(self):
        """Synchronizes locally defined list of monitors with the server.

        This method compares locally defined monitors with the result of the
        `getMonitors` API method and synchronizes them by creating missing
        monitors, deleting obsolete ones, and updating the ones that changed.

        Note: creating and updating monitors requires server-side contact IDs,
        so `_sync_monitors` should only be executed after `_sync_contacts`.
        """
        existing = {}
        params = self.params.copy()
        params.update({"showMonitorAlertContacts": 1})
        fetched = self._api_get_paginated(
            "getMonitors", params, lambda x: x["monitors"]["monitor"])
        for monitor_dict in fetched:
            # getMonitors returns interval in seconds, while editMonitor
            # expects minutes. Exciting, I know.
            monitor_dict["interval"] = int(monitor_dict["interval"]) / 60
            m = Monitor(**monitor_dict)
            if m.name in self._monitors:
                existing[m.name] = True
                if not m == self._monitors[m.name]:
                    self._api_update_monitor(m, self._monitors[m.name])
            else:
                self._api_delete_monitor(m)
        for name in self._monitors:
            if name not in existing:
                self._api_create_monitor(self._monitors[name])

    @typedecorator.params(self=object, old="Monitor", new="Monitor")
    def _api_update_monitor(self, old, new):
        logger.info("Updating monitor {}".format(new.name))
        if old["type"] != new["type"]:
            logger.info("Monitor type updates are not possible, "
                        "will remove and re-add {}".format(new.name))
            self._api_delete_monitor(old)
            self._api_create_monitor(new)
            return
        if self._dry_run:
            return
        params = self.params.copy()
        params.update(new._params_update)
        params["monitorID"] = old["id"]
        self._api_get("editMonitor", params)

    @typedecorator.params(self=object, monitor="Monitor")
    def _api_delete_monitor(self, monitor):
        logger.info("Deleting monitor {}".format(monitor.name))
        if self._dry_run:
            return
        params = self.params.copy()
        params.update(monitor._params_delete)
        self._api_get("deleteMonitor", params)

    @typedecorator.params(self=object, monitor="Monitor")
    def _api_create_monitor(self, monitor):
        logger.info("Creating monitor {}".format(monitor.name))
        if self._dry_run:
            return
        params = self.params.copy()
        params.update(monitor._params_create)
        self._api_get("newMonitor", params)

    def _sync_contacts(self):
        """Synchronizes locally defined list of contacts with the server.

        This method compares locally defined contacts with the result of the
        `getAlertContacts` API method and synchronizes them by creating missing
        contacts and deleting obsolete ones.

        This also populates server-side contact IDs that are required to create
        and update monitors, so `_sync_contacts` should be executed before
        `_sync_monitors`.
        """
        existing = {}
        fetched = self._api_get_paginated(
            "getAlertContacts", self.params,
            lambda x: x["alertcontacts"]["alertcontact"])
        for contact_dict in fetched:
            c = Contact(**contact_dict)
            if c.name in self._contacts:
                if c != self._contacts[c.name]:
                    # There is no editContact call, we have to delete the old
                    # contact (and let it be added again by the code below).
                    self._api_delete_contact(c)
                else:
                    existing[c.name] = True
                    # Populate the `id` field based on the contact information
                    # we got from the server. This id will be required for the
                    # newMonitor / editMonitor calls we make later.
                    self._contacts[c.name]["id"] = c["id"]
            else:
                self._api_delete_contact(c)
        for name in self._contacts:
            if name not in existing:
                contact_id = self._api_create_contact(self._contacts[name])
                self._contacts[name]["id"] = contact_id

    @typedecorator.params(self=object, contact="Contact")
    def _api_delete_contact(self, contact):
        logger.info("Deleting contact {}".format(contact.name))
        if self._dry_run:
            return
        params = self.params.copy()
        params.update(contact._params_delete)
        self._api_get("deleteAlertContact", params)

    @typedecorator.params(self=object, contact="Contact")
    def _api_create_contact(self, contact):
        logger.info("Creating contact {}".format(contact.name))
        if self._dry_run:
            return
        params = self.params.copy()
        params.update(contact._params_create)
        result = self._api_get("newAlertContact", params)
        return result["alertcontact"]["id"]

    @typedecorator.returns("Contact")
    @typedecorator.params(self=object, name=str, email=str)
    def email_contact(self, name, email=None):
        """Defines an email contact.

        Args:
            name: (string) name used for this contact in the Uptime Robot web
                interface.
            email: (string) e-mail address (defaults to `name` if not
                specified)

        Returns:
            Contact object which can later be used in add_contacts method
                of a monitor.
        """
        assert name not in self._contacts, "Duplicate name: {}".format(name)
        c = Contact(
            friendlyname=name, type=Contact.TYPE_EMAIL, value=email or name)
        self._contacts[c.name] = c
        return c

    @typedecorator.returns("Contact")
    @typedecorator.params(self=object, name=str, key=str)
    def boxcar_contact(self, name, key=None):
        """Defines a Boxcar contact.

        Args:
            name: (string) name used for this contact in the Uptime Robot web
                interface.
            key: (string) boxcar API key (defaults to `name` if not specified).

        Returns:
            Contact object which can later be used in add_contacts method
                of a monitor.
        """
        assert name not in self._contacts, "Duplicate name: {}".format(name)
        c = Contact(
            friendlyname=name, type=Contact.TYPE_BOXCAR, value=key or name)
        self._contacts[c.name] = c
        return c

    @typedecorator.returns("Monitor")
    @typedecorator.params(
        self=object, name=str, url=str, keyword=str, should_exist=bool,
        http_username=str, http_password=str, interval=int)
    def keyword_monitor(self, name, url, keyword, should_exist=True,
                        http_username="", http_password="",
                        interval=DEFAULT_INTERVAL):
        """Defines a keyword monitor.

        Args:
            name: (string) name used for this monitor in the Uptime Robot web
                interface.
            url: (string) URL to check.
            keyword: (string) Keyword to check.
            should_exist: (string) Whether the keyword should exist or not
                (defaults to True).
            http_username: (string) Username to use for HTTP authentification.
            http_password: (string) Password to use for HTTP authentification.
            interval: (int) Monitoring interval in minutes.

        Returns:
            Monitor object.
        """
        assert name not in self._monitors, "Duplicate name: {}".format(name)
        keywordtype = 2 if should_exist else 1
        m = Monitor(friendlyname=name, type=Monitor.TYPE_KEYWORD, url=url,
                    keywordvalue=keyword, keywordtype=keywordtype,
                    httpusername=http_username, httppassword=http_password,
                    interval=interval)
        self._monitors[m.name] = m
        return m

    @typedecorator.returns("Monitor")
    @typedecorator.params(self=object, name=str, hostname=str, port=int,
                          interval=int)
    def port_monitor(self, name, hostname, port, interval=DEFAULT_INTERVAL):
        """Defines a port monitor.

        Args:
            name: (string) name used for this monitor in the Uptime Robot web
                interface.
            hostname: (string) Host name to check.
            port: (int) TCP port.
            interval: (int) Monitoring interval in minutes.

        Returns:
            Monitor object.
        """
        assert name not in self._monitors, "Duplicate name: {}".format(name)
        # Port to subtype map from https://uptimerobot.com/api
        port_to_subtype = {80: 1, 443: 2, 21: 3, 25: 4, 110: 5, 143: 6}
        subtype = port_to_subtype.setdefault(port, 99)
        m = Monitor(friendlyname=name, type=Monitor.TYPE_PORT, url=hostname,
                    subtype=subtype, port=port, interval=interval)
        self._monitors[m.name] = m
        return m

    def sync(self):
        """Synchronizes configuration with the Uptime Robot API.

        This method should be called after all contacts and monitors have been
        defined and will sync defined configuration to the Uptime Robot."""
        self._sync_contacts()
        self._sync_monitors()

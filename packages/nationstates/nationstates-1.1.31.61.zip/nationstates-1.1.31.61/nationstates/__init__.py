from time import time as timestamp
from time import sleep

import copy


if __name__ != "__main__":
    from . import NScore
    from .arguments_obj import NSArgs
    from .NScore import exceptions
    from .mixins import (
        NSUserAgentMixin,
        NSPropertiesMixin,
        NSSettersMixin,
        escape_url

    )
else:
    import NScore
    from NScore import exceptions
    from arguments_obj import NSArgs
    from mixins import (
        NSUserAgentMixin,
        NSPropertiesMixin,
        NSSettersMixin,
        escape_url
    )
# this is used in nationstates get_??? methods
__apiversion__ = "7"


"""PyNationstates

This module wraps around the Nationstates API to create a simple uniform way to access the API.
"""


class RateLimit(object):

    """
    This object wraps around the ratelimiting system

    Classes that use the rate-limiter must inherit this.

    If a function needs to use the rate limiter, it must create
    a RateLimit() obj and use its methods. This protect the
    global state of the Rate Limiter from side effects.

    """

    @property
    def rltime(self):
        """Returns the current tracker"""
        return NScore._rltracker_

    @rltime.setter
    def rltime(self, val):
        """Sets the current tracker"""
        NScore._rltracker_ = val

    def ratelimitcheck(self, amount_allow=48, within_time=30):
        """Checks if PyNationstates needs pause to prevent api banning"""

        if len(self.rltime) >= amount_allow:
            currenttime = timestamp()
            try:
                while (self.rltime[-1]+within_time) < currenttime:
                    del self.rltime[-1]
                if len(self.rltime) >= amount_allow:
                    return False
            except IndexError as err:
                if len(self.rltime) == 0:
                    return True
            else:
                return True
        else:
            return True

    def add_timestamp(self):
        """Adds timestamp to rltime"""
        self.rltime = [timestamp()] + self.rltime


class Shard(NScore.Shard):

    """Inherits from NScore Shard"""

    @property
    def name(self):
        """Returns the Name of the Shard"""
        return self._get_main_value()


class Nationstates(NSPropertiesMixin, NSSettersMixin, RateLimit):

    """
    Api object

    This Wraps around the NScore.Api Object.

    """

    def __init__(self, api, value=None, shard=None,
                 user_agent=None, auto_load=False, version=None,
                 disable_ratelimit=False):
        """
        Passes on the arguments to self.__call__()

        Creates the variable self.collect and self.has_data
        """

        self.has_data = False
        self.api_instance = NScore.Api(api)

        self.__call__(api, value, shard, user_agent, auto_load, version)

    def __call__(self, api, value=None, shard=None,
                 user_agent=None, auto_load=False, version=None):
        """
        Handles the arguments and sends the args to be parsed

        Then sets up a NScore.Api instance (api_instance) that this object
             will interact with

        :param api: The type of API being accesses
            ("nation", "region", "world", "wa")

        :param value: The value of the API type (For the example,
            the nation to search when using "nation")

        :param shard: A list of nationstates shard(s)

        :param user_agent: A custom useragent.
            if not set, it will use a default message.

        :param auto_load: If True, This object will load on creation

        :param version: The Api version to request.

        """

        args = NSArgs(api, value, shard, user_agent, auto_load, version)
        if not args.api in ("nation", "region", "world", "wa", "verify"):
            raise exceptions.APIError("Invalid api type: {}".format(api))

        # NScore
        # This needs to be created at the start of the run
        self.api = args.api

        self.value = args.value
        self.shard = args.shard
        self.user_agent = args.user_agent
        self.has_data = False
        self.auto_load_bool = args.auto_load
        self.version = args.version

        if args.auto_load is True:
            return self.load()

    def __repr__(self):

        if self.api != "world":
            return "<ns:{type}:{value}>".format(
                type=self.api, value=self.value)
        else:
            return "<ns:world:shard({shardlen})>".format(
                shardlen=len(self.shard) if self.shard else "0")

    def __getitem__(self, key):
        """getitem implentation"""
        if self.has_data is False:
            raise exceptions.CollectError(
                "Request Required to access getitem")
        if key is self.api:
            return self.collect()
        return self.collect()[key]

    def __getattr__(self, attr):
        """Allows dynamic access to Nationstates shards"""
        if self.has_data:
            if attr in self.collect().keys():
                return self.collect()[attr]
        raise AttributeError('\'%s\' has no attribute \'%s\'' % (type(self),
                                                                 attr))

    def __copy__(self):
        """Copies the Nationstates Object"""
        proto_copy = Nationstates(
            self.api, self.value, self.shard, self.user_agent,
            False, self.version)
        proto_copy.has_data = self.has_data
        proto_copy.api_instance = copy.copy(self.api_instance)
        return proto_copy

    def shard_handeler(self, shard):
        """Used Interally to handle shards"""
        if not isinstance(shard, list):
            return list(shard)
        else:
            return shard

    def load(self, user_agent=None, no_ratelimit=False, safe="safe",
             retry_after=2, numattempt=3):
        self.__safe__ = safe

        if safe == "safe":
            return self._load(user_agent=user_agent, no_ratelimit=no_ratelimit,
                              within_time=30, amount_allow=30)

        if safe == "notsafe":
            return self._load(user_agent=user_agent, no_ratelimit=no_ratelimit,
                              within_time=30, amount_allow=48)

        if safe == "verysafe":
            return self._load(user_agent=user_agent, no_ratelimit=no_ratelimit,
                              within_time=30, amount_allow=25)

    def _load(self, user_agent=None, no_ratelimit=False,
              retry_after=2, numattempt=3, amount_allow=48, within_time=30,
              no_loop=False):
        """Requests/Refreshs the data

        :param user_agent: parameter

        """
        # These next three if statements handle user_agents
        if not (user_agent or self.user_agent):
            print("Warning: No user-agent set, default will be used.")
        if user_agent and not self.user_agent:
            self.user_agent = user_agent
        if not user_agent and self.user_agent:
            user_agent = self.user_agent
        if self.ratelimitcheck(amount_allow, within_time) or no_ratelimit:
            try:
                self.add_timestamp()
                self.has_data = bool(self.api_instance.load(
                    user_agent=user_agent))
                if self.has_data:
                    return self
            except exceptions.NSError as err:
                raise err
        elif not no_ratelimit and not no_loop:
            attemptsleft = numattempt
            while not self.ratelimitcheck(amount_allow, within_time):
                if numattempt == 0:
                    raise NScore.RateLimitCatch(
                        "Rate Limit Protection Blocked this Request")
                sleep(retry_after)
                self._load(
                    user_agent=user_agent,
                    numattempt=(
                        attemptsleft-1) if (
                        not attemptsleft is None) else None,
                    no_loop=True,
                    amount_allow=amount_allow,
                    within_time=within_time)
                if self.has_data:
                    return self
            # In the rare case where the ratelimiter
            if self.has_data and self.ratelimitcheck(
                    amount_allow, within_time):
                return self   # is within a narrow error prone zone
            if not self.has_data and self.ratelimitcheck(
                    amount_allow, within_time):
                return self._load(user_agent=user_agent, no_ratelimit=True,
                                  amount_allow=amount_allow,
                                  within_time=within_time)
            raise NScore.RateLimitCatch(
                "Rate Limit Protection Blocked this Request")

    def __dir__(self):
        if self.has_data:
            return super(
                object, Nationstates).__dir__() + list(self.collect().keys())
        return super(object, Nationstates).__dir__()

    def collect(self):
        """Returns a Dictionary of the collected shards"""
        if not self.has_data:
            raise NScore.CollectError(
                "collect requires request to collect data")
        return self.full_collect()[self.api]

    def full_collect(self):
        """Returns NScore's collect"""
        return self.api_instance.collect()

    @property
    def data(self):
        """Property for the date generated by the last request"""
        return self.api_instance.all_data()

    @property
    def url(self):
        """Generates a URL according to the current NS object"""
        if not self.data:
            return self.api_instance.get_url()
        else:
            return self.data["url"]


class Api(object):

    def __init__(self, user_agent=None, v=__apiversion__):
        """Creates Api Instance"""
        self.instance_version = (v, (v != __apiversion__))
        self.nsobj = Nationstates("world", shard=None, auto_load=False)
        self.user_agent = user_agent if user_agent else None

    @property
    def user_agent(self):
        """Returns current instance's user_agent"""
        return self._user_agent_store

    @user_agent.setter
    def user_agent(self, val):
        """Sets the user_agent"""
        self._user_agent_store = val
        self.nsobj.set_useragent(val)

    def _call(self, api, value, shard, user_agent, auto_load, version):
        """Used internally to request the api"""
        self.nsobj(api, value=value, shard=shard,
                   user_agent=user_agent, auto_load=auto_load, version=version)
        return self.nsobj

    def request(self, api, value=None, shard=None,
                user_agent=None, auto_load=True,
                version=__apiversion__):
        """Requests the api with the specific parameters

        :param api: The api being requested
        :param value: The value of the api
        :param shard: Shards to be requested
        :param user_agent: user_agent to be used for this request
        :param auto_load: If true the Nationstates instance will request the api on creation
        :param version: version to use.

        """
        version = version if (version and version != __apiversion__) else (
            self.instance_version[0]
            if self.instance_version[1] else __apiversion__)
        useragent = self.user_agent if not user_agent else user_agent
        req = copy.copy(
            self._call(api, value, shard, useragent, auto_load, version))
        req.api_instance.session = self.nsobj.api_instance.session
        return req

    def get_nation(self, value=None, shard=None,
                   user_agent=None, auto_load=True,
                   version=__apiversion__):
        """
        Handle Nation requests

        :param api: The api being requested
        :param value: The value of the api
        :param shard: Shards to be requested
        :param user_agent: user_agent to be used for this request
        :param auto_load: If true the Nationstates instance will request the api on creation
        :param version: version to use.
        """
        return self.request("nation", value, shard, user_agent,
                            auto_load, version)

    def get_region(self, value=None, shard=None,
                   user_agent=None, auto_load=True,
                   version=__apiversion__):
        """
        Handles Region requests

        :param api: The api being requested
        :param value: The value of the api
        :param shard: Shards to be requested
        :param user_agent: user_agent to be used for this request
        :param auto_load: If true the Nationstates instance will request the api on creation
        :param version: version to use.
        """
        return self.request("region", value, shard, user_agent,
                            auto_load, version)

    def get_world(self, shard=None, user_agent=None, auto_load=True,
                  version=__apiversion__):
        """
        Handles world requests

        :param api: The api being requested
        :param shard: Shards to be requested
        :param user_agent: user_agent to be used for this request
        :param auto_load: If true the Nationstates instance will request the api on creation
        :param version: version to use.
        """
        return self.request("world", None, shard, user_agent,
                            auto_load, version)

    def get_wa(self, council=None, shard=None,
               user_agent=None, auto_load=True,
               version=__apiversion__):
        """
        Handles WA requests

        :param api: The api being requested
        :param council: The council being requested
        :param shard: Shards to be requested
        :param user_agent: user_agent to be used for this request
        :param auto_load: If true the Nationstates instance will request the api on creation
        :param version: version to use.
        """
        return self.request("wa", council, shard, user_agent,
                            auto_load, version)


def get_ratelimit():
    # To prevent dependencies
    RatelimitObj = RateLimit()
    return RatelimitObj.rltime


def clear_ratelimit():
    RatelimitObj = RateLimit()
    RatelimitObj.rltime = list()


def gen_url(api, value=None, shard=None, version=None):
    """Generates a url based on the parameters"""

    if value is None and not api == "world":
        raise exceptions.NSError(
            "{} requires parameters to generate url.".format(api))

    instance = Nationstates(api, value=value, shard=shard,
                            version=version, user_agent="", auto_load=False)
    instance.api_instance.session.close()
    return instance.url

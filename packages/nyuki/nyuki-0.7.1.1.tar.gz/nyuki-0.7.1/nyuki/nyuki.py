import asyncio
import codecs
import json
from jsonschema import validate, ValidationError
import logging
import logging.config
import signal
import sys

from nyuki.bus import Bus
from nyuki.capabilities import Exposer, Response, resource
from nyuki.commands import get_command_kwargs
from nyuki.config import (
    get_full_config, write_conf_json, merge_configs, DEFAULT_CONF_FILE
)
from nyuki.events import EventManager
from nyuki.handlers import MetaHandler


log = logging.getLogger(__name__)


class Nyuki(metaclass=MetaHandler):

    """
    A lightweigh base class to build nyukis. A nyuki provides tools that shall
    help the developer with managing the following topics:
      - Bus of communication between nyukis.
      - Asynchronous events.
      - Capabilities exposure through a REST API.
    This class has been written to perform the features above in a reliable,
    single-threaded, asynchronous and concurrent-safe environment.
    The core engine of a nyuki implementation is the asyncio event loop
    (a single loop is used for all features).
    A wrapper is also provide to ease the use of asynchronous calls
    over the actions nyukis are inteded to do.
    """

    # Configuration schema must follow jsonschema rules.
    BASE_CONF_SCHEMA = {
        "type": "object",
        "required": ["bus", "api", "log"],
        "properties": {
            "bus": {
                "type": "object",
                "required": ["jid", "password"],
                "properties": {
                    "jid": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    }

    def __init__(self, **kwargs):
        # Set stdout as utf-8 codec
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        except Exception as exc:
            # Nosetests seems to alter stdout, breaking detach()
            log.warning('Could not change stdout codec')
            log.exception(exc)

        # List of configuration schemas
        self._schemas = []

        # Get configuration from multiple sources and register base schema
        kwargs = kwargs or get_command_kwargs()
        self.config_filename = kwargs.get('config', DEFAULT_CONF_FILE)
        self._config = get_full_config(**kwargs)
        self.register_schema(self.BASE_CONF_SCHEMA)

        # Initialize logging
        logging.config.dictConfig(self._config['log'])

        self.loop = asyncio.get_event_loop()
        self.event_manager = EventManager(self.loop)
        self._bus = self._make_bus()
        self._exposer = Exposer(
            self.loop,
            debug=(self._config['log']['root']['level'] == "DEBUG")
        )

        self.is_stopping = False

    @property
    def config(self):
        return self._config

    @property
    def capabilities(self):
        return self._exposer.capabilities

    @property
    def capability_exposer(self):
        return self._exposer

    @property
    def request(self):
        return self._bus.request

    @property
    def publish(self):
        return self._bus.publish

    @property
    def subscribe(self):
        return self._bus.subscribe

    def _make_bus(self):
        """
        Returns a new set up Bus object.
        """
        bus = Bus(
            loop=self.loop,
            event_manager=self.event_manager,
            **self._config['bus']
        )
        bus.client.disconnected.add_done_callback(self._bus_disconnected)
        return bus

    def start(self):
        """
        Start the nyuki: launch the bus client and expose capabilities.
        Basically, it starts the event loop.
        """
        signal.signal(signal.SIGTERM, self.abort)
        signal.signal(signal.SIGINT, self.abort)
        self._bus.connect()
        self._exposer.expose(**self._config['api'])

        if asyncio.iscoroutinefunction(self.setup):
            asyncio.async(self.setup())
        else:
            self.loop.call_soon(self.setup)

        self.loop.run_forever()
        self.loop.close()

    def _bus_disconnected(self, future):
        """
        Handle bus disconnection.
        If it was manual stop the nyuki, else try to reconnect.
        """
        log.info('Bus disconnected')
        if self.is_stopping:
            log.info('Tearing down nyuki')
            self.teardown()
            self._stop_loop()
        else:
            log.info('Reconnecting...')
            self._bus = self._make_bus()
            self._bus.connect()

    def _stop_loop(self):
        """
        Call the loop to stop itself.
        """
        self.loop.call_soon_threadsafe(self.loop.stop)

    def abort(self, signum, frame):
        """
        Signal handler: gracefully stop the nyuki.
        """
        log.warning("Caught signal {}".format(signum))
        self.stop()

    def stop(self, timeout=5):
        """
        Stop the nyuki. Basically, disconnect to the bus. That will eventually
        trigger a `Disconnected` event.
        """
        if self.is_stopping:
            log.warning('Forcing the nyuki stopping')
            self._stop_loop()
            return

        self.is_stopping = True

        def timed_out():
            log.warning('Could not stop nyuki after '
                        '{} seconds, killing'.format(timeout))
            self._stop_loop()

        self.loop.call_later(timeout, timed_out)
        self._exposer.shutdown()
        self._bus.disconnect()

    def register_schema(self, schema, format_checker=None):
        """
        Add a jsonschema to validate on configuration update.
        """
        self._schemas.append((schema, format_checker))
        self._validate_config()

    def _validate_config(self, config=None):
        """
        Validate on all registered configuration schemas.
        """
        log.debug('Validating configuration')
        config = config or self._config
        for schema, checker in self._schemas:
            validate(config, schema, format_checker=checker)

    @asyncio.coroutine
    def setup(self):
        """
        First thing called when starting the event loop, coroutine or not.
        """
        pass

    def teardown(self):
        """
        Called right before closing the event loop, stopping the Nyuki.
        """
        pass

    def update_config(self, *new_confs):
        """
        Update the current configuration with the given list of dicts.
        """
        config = merge_configs(self._config, *new_confs)
        self._validate_config(config)
        self._config = config

    def save_config(self):
        """
        Save the current configuration dict to its JSON file.
        """
        write_conf_json(self.config, self.config_filename)

    def reload(self, services=False):
        """
        Override this to implement a reloading to your Nyuki.
        (called on PATCH /config)
        """
        self.save_config()
        logging.config.dictConfig(self._config['log'])
        if services:
            self._bus.disconnect()
            self._exposer.restart(**self._config['api'])

    @resource(endpoint='/config', version='v1')
    class Configuration:

        def get(self, request):
            return Response(self._config)

        def patch(self, request):
            try:
                self.update_config(request)
            except ValidationError as error:
                error = {'error': error.message}
                log.error('Bad configuration received : {}'.format(request))
                log.debug(error)
                return Response(body=error, status=400)
            else:
                self.reload('api' in request or 'bus' in request)
            return Response(self._config)

    @resource(endpoint='/swagger', version='v1')
    class Swagger:
        def get(self, request):
            try:
                with open('swagger.json', 'r') as f:
                    body = json.loads(f.read())
            except OSError:
                return Response(status=404, body={
                    'error': 'Missing swagger documentation'
                })

            return Response(body=body)

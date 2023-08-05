# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import logging
import os
import yaml

from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider
from libcloud.loadbalancer.providers import get_driver as get_balancer_driver
from libcloud.loadbalancer.types import Provider as BalancerProvider

from exception import PlumberyException
from facility import PlumberyFacility
from polisher import PlumberyPolisher

__all__ = ['PlumberyEngine', 'PlumberyFittings']


class PlumberyEngine:
    """
    Infrastructure as code at Dimension Data with Apache Libcloud

    :param fileName: the location of the plan for the fittings
    :type fileName: ``str``

    Plumbery is a convenient tool for infrastructure managers at cloud times.
    It allows for easy and repeatable deployments of various
    fittings, including compute nodes and related storage. It allows also for
    quick dismandling of the fittings when required.
    The idea here is not to compete with respected solutions such as chef or
    puppet. At its name implies, plumbery is targeting pipes and fittings, the
    very basic utility stuff that sophisticated tools can leverage.

    Example::

        from plumbery.engine import PlumberyEngine
        engine = PlumberyEngine('fittings.yaml')
        engine.build_all_blueprints()

    In this example the overall plan, in textual format, is given to the engine
    in preparation of subsequent processing. The software is not trying to
    guess a name by default, so if you do not provide a name, no configuration
    file is loaded. You can load the plan at any stage, or restart the engine
    with an updated plan, by invoking the member function ``parse_layout()``

    Note:
        While plumbery is not making assumptions for your configuration files,
        if your infrastructure is simple enough to fit in one single file then
        you are highly encouraged to name it ``fittings.yaml``

    Beyond the plan for your fittings, plumbery is also requiring some specific
    credentials to connect to cloud providers. To preserve the confidentiality
    of such information, it is read from the environment, and not from any
    configuration file. Therefore the need for local setup before running
    plumbery. This is part of the installation process.

    Last but not least, plumbery sets the root password of any new server that
    it creates. For obvious security reasons this is not taken from the
    fittings plan but from the environment, or it can be set in code.

    Under Linux, you may want to edit ``~/.bash_profile`` like this::

        # credentials to access cloud resources from Dimension Data
        export MCP_USERNAME='foo.bar'
        export MCP_PASSWORD='WhatsUpDoc'

        # password to access nodes remotely
        export SHARED_SECRET='*you really want to put a tricky password here*'

    These simple precautions are aiming to protect your infrastructure as much
    as possible. The general goal is to minimize risks induced by exposure to
    your fittings plan. You may lead transformation towards so-called
    infrastructure as code, and for this you will add version control to your
    fittings plan. As a result, plans will be stored in git or equivalent, and
    shared across some people.

    Attributes:

        safeMode (boolean):
            If True, which is the default, then no actual change
            will be made against the infrastructure. This global attribute
            is coming from the fittings plan.

    """

    safeMode = True

    def __init__(self, plan=None):
        """
        Ignites the plumbing engine

        :param plan: the file that contains fittings plan
        :type plan: ``str`` or ``file``

        """

        self.facilities = []

        self.polishers = []

        self._buildPolisher = None

        self._sharedSecret = None

        self._userName = None

        self._userPassword = None

        if plan is not None:
            self.from_file(plan)

    def from_file(self, plan=None):
        """
        Reads the fittings plan from a file

        :param plan: the file that contains fittings plan
        :type plan: ``str`` or ``file``

        The fittings plan is expected to follow YAML specifications, and it
        must have multiple documents in it. The first document provides
        general configuration parameters for the engine. Subsequent documents
        describe the various locations for the fittings.

        An example of a minimum fittings plan::

            ---
            safeMode: False
            ---
            # Frankfurt in Europe
            locationId: EU6
            regionId: dd-eu

            blueprints:

              - myBluePrint:
                  domain:
                    name: myDC
                  ethernet:
                    name: myVLAN
                    subnet: 10.1.10.0
                  nodes:
                    - myServer

        In this example, the plan is to deploy a single node in the data centre
        at Frankfurt, in Europe. The node `myServer` will be placed in a
        network named `myVLAN`, and the network will be part of a network
        domain acting as a virtual data centre, `myDC`. The blueprint has a
        name, `myBluePrint`, so that it can be handled independently from
        other blueprints.

        """

        if plan is None:
            plan = os.getenv('PLUMBERY')

        if isinstance(plan, str):
            plan = open(plan, 'r')

        documents = yaml.load_all(plan)

        # first document contains engine settings
        self.set(documents.next())

        # then one document per facility
        for document in documents:
            self.add_facility(document)

        if self.safeMode:
            logging.info(
                "Running in safe mode"
                " - no actual change will be made to the fittings")

    def from_text(self, plan):
        """
        Reads the fittings plan

        :param plan: the fittings plan
        :type plan: ``str``

        The fittings plan is expected to follow YAML specifications, and it
        must have multiple documents in it. The first document provides
        general configuration parameters for the engine. Subsequent documents
        describe the various locations for the fittings.

        Example of use::

            myPlan = \"\"\"
            ---
            safeMode: True
            ---
            # Frankfurt in Europe
            locationId: EU6
            regionId: dd-eu

            blueprints:

              - myBlueprint:
                  domain:
                    name: myDC
                  ethernet:
                    name: myVLAN
                    subnet: 10.1.10.0
                  nodes:
                    - myServer
            \"\"\"

            engine = PlumberyEngine()
            engine.from_text(myPlan)

        In this example, the plan is to deploy a single node in the data centre
        at Frankfurt, in Europe. The node `myServer` will be placed in a
        network named `myVLAN`, and the network will be part of a network
        domain acting as a virtual data centre, `myDC`. The blueprint has a
        name, `myBluePrint`, so that it can be handled independently from
        other blueprints.

        """

        self.from_file(io.TextIOWrapper(io.BytesIO(plan)))

    def set(self, settings):
        """
        Changes the settings of the engine

        :param settings: the new settings
        :type settings: ``dict``

        """

        if not isinstance(settings, dict):
            raise TypeError('settings should be a dictionary')

        if 'safeMode' not in settings:
            raise LookupError('safeMode is not defined')

        self.safeMode = settings['safeMode']
        if self.safeMode not in [True, False]:
            raise ValueError('safeMode should be either True or False')

        if 'polishers' in settings:
            for item in settings['polishers']:
                key = item.keys()[0]
                value = item[key]
                self.polishers.append(
                    PlumberyPolisher.from_shelf(key, value))

        if 'buildPolisher' in settings:
            self._buildPolisher = settings['buildPolisher']
        else:
            self._buildPolisher = 'spit'

    def set_shared_secret(self, secret):
        """
        Changes the shared secret to be used with new nodes

        :param secret: the user name to be used with the driver
        :type secret: ``str``

        This function can be used to supplement the normal provision of
        the shared secret via the environment variable ``SHARED_SECRET``.

        """

        self._sharedSecret = secret

    def get_shared_secret(self):
        """
        Retrieves the secret that is communicated to new nodes during setup

        :return: the shared secret to be given to the driver
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no shared secret can be found

        The shared secret is not put in the fittings plan, but is normally
        taken from the environment variable ``SHARED_SECRET``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # password to access nodes remotely
            export SHARED_SECRET='*you really want to use a tricky password*'

        Alternatively, you can use the member function ``set_shared_secret()``
        to set this important attribute via code.

        """

        if self._sharedSecret is None:
            self._sharedSecret = os.getenv('SHARED_SECRET')
            if self._sharedSecret is None or len(self._sharedSecret) < 3:
                raise PlumberyException(
                    "Error: missing node password "
                    "in environment SHARED_SECRET")

        return self._sharedSecret

    def set_user_name(self, name):
        """
        Changes the name used to authenticate to the API

        :param name: the user name to be used with the driver
        :type name: ``str``

        This function can be used to supplement the normal provision of
        a user name via the environment variable ``MCP_USERNAME``.

        """

        self._userName = name

    def get_user_name(self):
        """
        Retrieves user name to authenticate to the API

        :return: the user name to be used with the driver
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no user name can be found

        The user name is not put in the fittings plan, but is normally taken
        from the environment variable ``MCP_USERNAME``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userName is None:
            self._userName = os.getenv('MCP_USERNAME')
            if self._userName is None or len(self._userName) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_USERNAME")

        return self._userName

    def set_user_password(self, password):
        """
        Changes the password used to authenticate to the API

        :param password: the user password to be used with the driver
        :type password: ``str``

        This function can be used to supplement the normal provision of
        a user password via the environment variable ``MCP_PASSWORD``.

        """

        self._userPassword = password

    def get_user_password(self):
        """
        Retrieves user password to authenticate to the API

        :return: the user password to be used with the driver
        :rtype: ``str``

        :raises: :class:`plumbery.PlumberyException`
            - if no user password can be found

        The user password is not put in the fittings plan, but is normally
        taken from the environment variable ``MCP_PASSWORD``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userPassword is None:
            self._userPassword = os.getenv('MCP_PASSWORD')
            if self._userPassword is None or len(self._userPassword) < 3:
                raise PlumberyException(
                    "Error: missing credentials in environment MCP_PASSWORD")

        return self._userPassword

    def add_facility(self, facility):
        """
        Extends the scope of this plumbing engine

        :param facility: description of an additional facility
        :type facility: ``dict`` or :class:`plumbery.PlumberyFacility`

        """

        if isinstance(facility, dict):
            facility = PlumberyFacility(self, PlumberyFittings(**facility))

        self.facilities.append(facility)

    def list_facility(self, location):
        """
        Retrieves facilities by their location

        :param location: the target location, e.g., 'EU6'
        :type location: ``str`` or ``list`` of ``str``

        :return: the list of matching facilities
        :rtype: ``list`` of :class:`plumbery.PlumberyFacility` or ``[]``

        Examples::

            >>>engine.list_facility(location='EU6')
            ...

            >>>engine.list_facility(location='EU6 NA9')
            ...

            >>>engine.list_facility(location=['EU6', 'NA9'])
            ...

        """

        if isinstance(location, str):
            location = location.split(' ')

        matches = []

        for item in location:
            if isinstance(item, PlumberyFacility):
                matches.append(item)

        for facility in self.facilities:
            if facility.fittings.locationId in location:
                matches.append(facility)

        return matches

    def do(self, action, blueprints=None, facilities=None):

        if action == 'build':
            if blueprints is None:
                self.build_all_blueprints(facilities)
            else:
                self.build_blueprint(blueprints, facilities)

        elif action == 'start':
            if blueprints is None:
                self.start_all_nodes(facilities)
            else:
                self.start_nodes(blueprints, facilities)

        elif action == 'polish':
            if blueprints is None:
                self.polish_all_blueprints(filter=None,
                                           facilities=facilities)
            else:
                self.polish_blueprint(blueprints, facilities)

        elif action == 'stop':
            if blueprints is None:
                self.stop_all_nodes(facilities)
            else:
                self.stop_nodes(blueprints, facilities)

        elif action == 'destroy':
            if blueprints is None:
                self.destroy_all_blueprints(facilities)
            else:
                self.destroy_blueprint(blueprints, facilities)

        else:
            if blueprints is None:
                self.polish_all_blueprints(filter=action,
                                           facilities=facilities)
            else:
                self.polish_blueprint(blueprints,
                                      filter=action,
                                      facilities=facilities)

    def build_all_blueprints(self, facilities=None):
        """
        Builds all blueprints described in fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to build all blueprints there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Examples::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints()

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_all_blueprints('EU6 NA9')

        """

        logging.info("Building all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.build_all_blueprints()

        self.polish_all_blueprints(filter=self._buildPolisher,
                                   facilities=facilities)

    def build_blueprint(self, names, facilities=None):
        """
        Builds named blueprint from fittings plan

        :param names: the name(s) of the blueprint(s) to deploy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to build one single blueprint there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').build_blueprints('sql')

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Building blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.build_blueprint(names)

        self.polish_blueprint(names=names,
                              filter=self._buildPolisher,
                              facilities=facilities)

    def destroy_all_blueprints(self, facilities=None):
        """
        Destroys all blueprints from fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy all blueprints there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_all_blueprints()

    def destroy_all_nodes(self, facilities=None):
        """
        Destroys all nodes from fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        logging.info("Destroying nodes from all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_all_nodes()

    def destroy_blueprint(self, names, facilities=None):
        """
        Destroys one or several blueprint(s) from fittings plan

        :param names: the name(s) of the blueprint(s) to destroy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy one single blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Destroying blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_blueprint(names)

    def destroy_nodes(self, names, facilities=None):
        """
        Destroys nodes for one or several blueprint(s) of the fittings plan

        :param names: the name(s) of the blueprint(s) to destroy
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to destroy nodes from one blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Note:
            Running nodes are always preserved from destruction.
            Therefore the need to stop nodes, in a separate command, before
            they can be actually destroyed.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Destroying nodes from blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.destroy_nodes(names)

    def polish_all_blueprints(self, filter=None, facilities=None):
        """
        Walks all resources and polishes them

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to apply polishers there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_all_blueprints()

        """

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        if len(polishers) < 1:
            return False

        logging.info("Polishing all blueprints")

        for polisher in polishers:
            polisher.go(self)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            for polisher in polishers:
                polisher.move_to(facility)
            facility.polish_all_blueprints(polishers)

        for polisher in polishers:
            polisher.reap()

    def polish_blueprint(self, names, filter=None, facilities=None):
        """
        Walks resources from the target blueprint and polishes them

        :param names: the name(s) of the blueprint(s) to polish
        :type names: ``str`` or ``list`` of ``str``

        :param filter: the name of a single polisher to apply. If this
            parameter is missing, all polishers declared in the fittings plan
            will be applied
        :type filter: ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to apply one polisher to one blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        Example::

            from plumbery.engine import PlumberyEngine
            PlumberyEngine('fittings.yaml').polish_blueprint('sql')

        """

        polishers = PlumberyPolisher.filter(self.polishers, filter)

        if len(polishers) < 1:
            return False

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Polishing blueprint '{}'".format(label))

        for polisher in polishers:
            polisher.go(self)

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            for polisher in polishers:
                polisher.move_to(facility)
            facility.polish_blueprint(names, polishers)

        for polisher in polishers:
            polisher.reap()

    def start_all_nodes(self, facilities=None):
        """
        Starts all nodes described in the fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to start all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already up and running.

        """

        logging.info("Starting nodes from all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.start_all_nodes()

    def start_nodes(self, names, facilities=None):
        """
        Starts nodes of one blueprint of the fittings plan

        :param names: the name(s) of the blueprint(s) to start
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to start nodes from some blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already up and running.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Starting nodes from blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.start_nodes(names)

    def stop_all_nodes(self, facilities=None):
        """
        Stops all nodes of the fittings plan

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to stop all nodes there.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already stopped.

        """

        logging.info("Stopping nodes from all blueprints")

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.stop_all_nodes()

    def stop_nodes(self, names, facilities=None):
        """
        Stops nodes of one blueprint of the fittings plan

        :param names: the name(s) of the blueprint(s) to stop
        :type names: ``str`` or ``list`` of ``str``

        :param facilities: explicit list of target facilities
        :type facilities: ``str`` or ``list`` of ``str``

        This function checks facilities to stop nodes from some blueprint.
        The default behaviour is to consider all facilities mentioned in the
        fittings plan. If a list of facilities is provided, than the action is
        limited to this subset only.

        This function has no effect on nodes that are already stopped.

        """

        if isinstance(names, list):
            label = ' '.join(names)
        else:
            label = names

        logging.info("Stopping nodes from blueprint '{}'".format(label))

        if facilities is not None:
            facilities = self.list_facility(facilities)
        else:
            facilities = self.facilities

        for facility in facilities:
            facility.focus()
            facility.stop_nodes(names)

    def get_compute_driver(self, region):
        """
        Loads a compute driver from Apache Libcloud

        """

        driver = get_compute_driver(ComputeProvider.DIMENSIONDATA)

        return driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region)

    def get_balancer_driver(self, region):
        """
        Loads a load balancer driver from Apache Libcloud

        """

        driver = get_balancer_driver(BalancerProvider.DIMENSIONDATA)

        return driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region)


class PlumberyFittings:
    """
    Describe fittings plan for one facility

    :param entries: plan of the fittings
    :type entries: ``dict``

    """

    def __init__(self, **entries):

        self.basement = None
        self.blueprints = []
        self.locationID = None
        self.regionID = None
        self.rub = []

        self.__dict__.update(entries)

    def __repr__(self):

        return "<PlumberyFittings locationId: {}, regionId: {}, "   \
               "rub: {}, blueprints: {}, basement: {}>"    \
               .format(self.locationId, self.regionId, self.rub,
                       self.blueprints, self.basement)

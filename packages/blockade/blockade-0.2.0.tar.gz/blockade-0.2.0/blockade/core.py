#
#  Copyright (C) 2014 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

import errno
import random
import re
import sys
import time

import docker

from .errors import BlockadeError,\
                    AlreadyInitializedError,\
                    BlockadeContainerConflictError,\
                    InsufficientPermissionsError

from .net import NetworkState, BlockadeNetwork
from .state import BlockadeState, BlockadeStateFactory


# TODO: configurable timeout
DEFAULT_KILL_TIMEOUT = 3


class Blockade(object):
    def __init__(self, config, state_factory=None, network=None,
                 docker_client=None):
        self.config = config
        self.state_factory = state_factory or BlockadeStateFactory()
        self.network = network or BlockadeNetwork(config)
        self.docker_client = docker_client or docker.Client()

    def create(self, blockade_id=None, verbose=False, force=False):
        container_state = {}

        if blockade_id:
            if re.match(r"^[a-zA-Z0-9-.]+$", blockade_id) is None:
                raise BlockadeError("'%s' is an invalid blockade ID. "
                                    "You may use only [a-zA-Z0-9-.]")
        else:
            blockade_id = self.state_factory.get_blockade_id()

        num_containers = len(self.config.sorted_containers)

        # we can check if a state file already exists beforehand
        if self.state_factory.exists():
            raise AlreadyInitializedError('a blockade already exists in here - '
                                          'you may want to destroy it first')

        def vprint(msg):
            if verbose:
                sys.stdout.write(msg)
                sys.stdout.flush()

        for idx, container in enumerate(self.config.sorted_containers):
            name = container.name

            vprint("\r[%d/%d] Starting '%s' " % (idx+1, num_containers, name))

            # in case a startup delay is configured
            # we have to wait in here
            if container.start_delay > 0:
                vprint('(delaying for %s seconds)' % (container.start_delay))
                time.sleep(container.start_delay)

            container_id = self._start_container(blockade_id, container, force)
            device = self._init_container(container_id, name)

            # store device in state file
            container_state[name] = {'device': device, 'id': container_id}

        # clear progress line
        vprint('\r')

        # try to persist container states
        state = self.state_factory.initialize(container_state, blockade_id)

        container_descriptions = []
        for container in self.config.sorted_containers:
            description = self._get_container_description(state, container.name)

            container_descriptions.append(description)

        return container_descriptions

    def _init_container(self, container_id, container_name):
        # next we have to determine the veth pair of host/container
        # that we formerly could pass in via 'lxc_conf' which is
        # deprecated since docker > 1.6
        device = None
        try:
            device = self.network.get_container_device(self.docker_client, container_id)
        except OSError as err:
            if err.errno in (errno.EACCES, errno.EPERM):
                msg = "Failed to determine network device of container '%s' [%s]" % (container_name, container_id)
                raise InsufficientPermissionsError(msg)
            raise

        return device

    def _start_container(self, blockade_id, container, force=False):
        container_name = container.container_name or docker_container_name(blockade_id, container.name)
        volumes = list(container.volumes.values()) or None
        links = dict((docker_container_name(blockade_id, link), alias)
                     for link, alias in container.links.items())

        # the docker api for port bindings is `internal:external`
        port_bindings = dict((v, k) for k, v in container.publish_ports.items())

        host_config = self.docker_client.create_host_config(
            binds=container.volumes,
            port_bindings=port_bindings, links=links)

        def create_container():
            # try to create container
            response = self.docker_client.create_container(
                container.image,
                command=container.command,
                name=container_name,
                ports=container.expose_ports,
                volumes=volumes,
                hostname=container.hostname,
                environment=container.environment,
                host_config=host_config,
                labels={"blockade.id": blockade_id})

            return response['Id']

        try:
            container_id = create_container()
        except docker.errors.APIError as err:
            if err.response.status_code == 409 and err.is_client_error():
                # if force is set we are retrying after removing the
                # container with that name first
                if force and self.__try_remove_container(container_name):
                    container_id = create_container()
                else:
                    raise BlockadeContainerConflictError(err)
            else:
                raise

        # start container
        self.docker_client.start(container_id)
        return container_id

    def __try_remove_container(self, name):
        try:
            self.docker_client.remove_container(name, force=True)
            return True
        except Exception:
            # TODO: log error?
            return False

    def _get_container_description(self, state, name, network_state=True,
                                   ip_partitions=None):
        state_container = state.containers[name]
        container_id = state_container['id']

        try:
            container = self.docker_client.inspect_container(container_id)
        except docker.errors.APIError as err:
            if err.response.status_code == 404:
                return Container(name, container_id, ContainerState.MISSING)
            else:
                raise

        state_dict = container.get('State')
        if state_dict and state_dict.get('Running'):
            container_state = ContainerState.UP
        else:
            container_state = ContainerState.DOWN

        extras = {}
        network = container.get('NetworkSettings')
        ip = None
        if network:
            ip = network.get('IPAddress')
            if ip:
                extras['ip_address'] = ip

        if (network_state and name in state.containers
                and container_state == ContainerState.UP):
            device = state_container['device']
            extras['device'] = device
            extras['network_state'] = self.network.network_state(device)

            # include partition ID if we were provided a map of them
            if ip_partitions and ip:
                extras['partition'] = ip_partitions.get(ip)
        else:
            extras['network_state'] = NetworkState.UNKNOWN
            extras['device'] = None

        # lookup 'holy' and 'neutral' containers
        # TODO: this might go into the state as well..?
        cfg_container = self.config.containers.get(name)
        extras['neutral'] = cfg_container.neutral if cfg_container else False
        extras['holy'] = cfg_container.holy if cfg_container else False

        return Container(name, container_id, container_state, **extras)

    def destroy(self, force=False):
        state = self.state_factory.load()

        containers = self._get_docker_containers(state)
        for container in list(containers.values()):
            container_id = container['Id']
            self.docker_client.stop(container_id, timeout=DEFAULT_KILL_TIMEOUT)
            self.docker_client.remove_container(container_id)

        self.network.restore(state.blockade_id)
        self.state_factory.destroy()

    def _get_docker_containers(self, state):
        containers = {}
        filters = {"label": ["blockade.id=" + state.blockade_id]}
        prefix = state.blockade_id + "_"
        for container in self.docker_client.containers(all=True, filters=filters):
            for name in container['Names']:
                # strip leading '/'
                name = name[1:] if name[0] == '/' else name

                # strip prefix. containers will have these UNLESS `container_name`
                # was specified in the config
                name = name[len(prefix):] if name.startswith(prefix) else name
                if name in state.containers:
                    containers[name] = container
                    break
        return containers

    def _get_all_containers(self, state):
        containers = []
        ip_partitions = self.network.get_ip_partitions(state.blockade_id)
        docker_containers = self._get_docker_containers(state)

        for name in docker_containers.keys():
            container = self._get_container_description(state, name, ip_partitions=ip_partitions)
            containers.append(container)
        return containers

    def status(self):
        state = self.state_factory.load()
        return self._get_all_containers(state)

    def _get_running_containers(self, container_names=None, state=None):
        state = state or self.state_factory.load()
        containers = self._get_all_containers(state)

        running = dict((c.name, c) for c in containers
                       if c.state == ContainerState.UP)
        if container_names is None:
            return list(running.values())

        found = []
        for name in container_names:
            container = running.get(name)
            if not container:
                raise BlockadeError("Container %s is not found or not running"
                                    % (name,))
            found.append(container)
        return found

    def _get_running_container(self, container_name, state=None):
        return self._get_running_containers((container_name,), state)[0]

    def __with_running_container_device(self, container_names, state, func):
        containers = self._get_running_containers(container_names, state)
        for container in containers:
            device = container.device
            func(device)

    def flaky(self, container_names, state):
        self.__with_running_container_device(container_names, state, self.network.flaky)

    def slow(self, container_names, state):
        self.__with_running_container_device(container_names, state, self.network.slow)

    def duplicate(self, container_names, state):
        self.__with_running_container_device(container_names, state, self.network.duplicate)

    def fast(self, container_names, state):
        self.__with_running_container_device(container_names, state, self.network.fast)

    def restart(self, container_names, state):
        containers = self._get_running_containers(container_names, state)
        for container in containers:
            self._stop(container)
            state = self._start(container.name, state)

    def stop(self, container_names, state):
        containers = self._get_running_containers(container_names, state)
        for container in containers:
            self._stop(container)

    def _stop(self, container):
        self.docker_client.stop(container.container_id, timeout=DEFAULT_KILL_TIMEOUT)

    def start(self, container_names, state):
        for container in container_names:
            state = self._start(container, state)

    def _start(self, container, state):
        container_id = state.container_id(container)
        if container_id is None:
            return

        # TODO: determine between create and/or start?
        self.docker_client.start(container_id)
        device = self._init_container(container_id, container)

        # update state
        updated_containers = state.containers
        updated_containers[container] = {'id': container_id, 'device': device}
        self.state_factory.update(state.blockade_id, updated_containers)

        # make sure further calls are operating on the updated state
        return BlockadeState(state.blockade_id, updated_containers)

    def random_partition(self):
        state = self.state_factory.load()
        containers = [c.name for c in self._get_running_containers(state=state)
                      if not c.holy]

        # no containers to partition
        if not containers:
            return []

        num_containers = len(containers)
        num_partitions = random.randint(1, num_containers)

        # no partition at all -> join
        if num_partitions <= 1:
            self.join()
            return []
        else:
            pick = lambda: containers.pop(random.randint(0, len(containers)-1))

            # pick at least one container for each partition
            partitions = [[pick()] for _ in xrange(num_partitions)]

            # distribute the rest of the containers among the partitions
            for _ in xrange(len(containers)):
                random_partition = random.randint(0, num_partitions-1)
                partitions[random_partition].append(pick())

            self.partition(partitions, state)
            return partitions

    def partition(self, partitions, state=None):
        state = state or self.state_factory.load()
        containers = self._get_running_containers(state=state)
        container_dict = dict((c.name, c) for c in containers)
        partitions = expand_partitions(containers, partitions)

        container_partitions = []
        for partition in partitions:
            container_partitions.append([container_dict[c] for c in partition])

        self.network.partition_containers(state.blockade_id,
                                          container_partitions)

    def join(self):
        state = self.state_factory.load()
        self.network.restore(state.blockade_id)

    def logs(self, container_name):
        container = self._get_running_container(container_name)
        return self.docker_client.logs(container.container_id)


class Container(object):
    ip_address = None
    device = None
    network_state = NetworkState.NORMAL
    partition = None

    def __init__(self, name, container_id, state, **kwargs):
        self.name = name
        self.container_id = container_id
        self.state = state
        self.holy = False
        self.neutral = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return dict(name=self.name,
                    container_id=self.container_id,
                    state=self.state,
                    ip_address=self.ip_address,
                    device=self.device,
                    network_state=self.network_state,
                    partition=self.partition)


class ContainerState(object):
    '''Different possible container states
    '''
    UP = "UP"
    DOWN = "DOWN"
    MISSING = "MISSING"


def docker_container_name(blockade_id, name):
    return '_'.join((blockade_id, name))


def expand_partitions(containers, partitions):
    '''
    Validate the partitions of containers. If there are any containers
    not in any partition, place them in an new partition.
    '''

    # filter out holy containers that don't belong
    # to any partition at all
    all_names = frozenset(c.name for c in containers if not c.holy)
    holy_names = frozenset(c.name for c in containers if c.holy)
    neutral_names = frozenset(c.name for c in containers if c.neutral)
    partitions = [frozenset(p) for p in partitions]

    unknown = set()
    holy = set()
    union = set()

    for partition in partitions:
        unknown.update(partition - all_names - holy_names)
        holy.update(partition - all_names)
        union.update(partition)

    if unknown:
        raise BlockadeError('Partitions contain unknown containers: %s' %
                            list(unknown))

    if holy:
        raise BlockadeError('Partitions contain holy containers: %s' %
                            list(holy))

    # put any leftover containers in an implicit partition
    leftover = all_names.difference(union)
    if leftover:
        partitions.append(leftover)

    # we create an 'implicit' partition for the neutral containers
    # in case they are not part of the leftover anyways
    if not neutral_names.issubset(leftover):
        partitions.append(neutral_names)

    return partitions

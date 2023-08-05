# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# (c) Copyright 2012-2015 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
HPELeftHand REST Client

.. module: HPELeftHandClient
.. moduleauthor: Kurt Martin

:Author: Kurt Martin
:Description: This is the LeftHand/StoreVirtual Client that talks to the
LeftHand OS REST Service. This version also supports running actions on the
LeftHand that use SSH.

This client requires and works with version 11.5 of the LeftHand firmware

"""

try:
    # For Python 3.0 and later
    from urllib.parse import quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import quote

from hpelefthandclient import exceptions, http, ssh


class HPELeftHandClient(object):

    # Minimum API version needed for consistency group support
    MIN_CG_API_VERSION = '1.2'

    def __init__(self, api_url, debug=False, secure=False,
                 suppress_ssl_warnings=False, timeout=None):
        self.api_url = api_url
        self.http = http.HTTPJSONRESTClient(
            self.api_url, secure=secure,
            suppress_ssl_warnings=suppress_ssl_warnings, timeout=timeout)
        self.api_version = None
        self.ssh = None

        self.debug_rest(debug)

    def setSSHOptions(self, ip, login, password, port=16022,
                      conn_timeout=None, privatekey=None,
                      **kwargs):
        """Set SSH Options for ssh calls.

        This is used to set the SSH credentials for calls
        that use SSH instead of REST HTTP.

        :param ip: The IP address of the LeftHand array
        :type ip: str
        :param login: Username to log into SSH
        :type login: str
        :param password: Password to log into SSH
        :type password: str
        :param port: Port the SSH service is running on. The default port
                     is 16022
        :type port: int
        :param conn_timeout: The connection timeout in seconds. Default is no
                             connection timeout.
        :type conn_timeout: int
        :param privatekey: File location of SSH private key. Default does not
                           use a private key.
        :type privatekey: int

        """
        self.ssh = ssh.HPELeftHandSSHClient(ip, login, password, port,
                                            conn_timeout, privatekey,
                                            **kwargs)

    def _run(self, cmd):
        if self.ssh is None:
            raise exceptions.SSHException('SSH is not initialized. Initialize'
                                          ' it by calling "setSSHOptions".')
        else:
            self.ssh.open()
            return self.ssh.run(cmd)

    def debug_rest(self, flag):
        """
        This is useful for debugging requests to LeftHand

        :param flag: set to True to enable debugging
        :type flag: bool

        """
        self.http.set_debug_flag(flag)
        if self.ssh:
            self.ssh.set_debug_flag(flag)

    def login(self, username, password):
        """
        This authenticates against the LH OS REST server and creates a session.

        :param username: The username
        :type username: str
        :param password: The password
        :type password: str

        :returns: None

        """
        try:
            resp = self.http.authenticate(username, password)
            self.api_version = resp['x-api-version']
        except Exception as ex:
            ex_desc = ex.get_description()

            if (ex_desc and ("Unable to find the server at" in ex_desc or
                             "Only absolute URIs are allowed" in ex_desc)):
                raise exceptions.HTTPBadRequest(ex_desc)
            if (ex_desc and "SSL Certificate Verification Failed" in ex_desc):
                raise exceptions.SSLCertFailed()
            else:
                msg = ('Error: \'%s\' - Error communicating with the LeftHand '
                       'API. Check proxy settings. If error persists, either '
                       'the LeftHand API is not running or the version of the '
                       'API is not supported.') % ex_desc
                raise exceptions.UnsupportedVersion(msg)

    def logout(self):
        """
        This destroys the session and logs out from the LH OS server

        :returns: None

        """
        self.http.unauthenticate()
        if self.ssh:
            self.ssh.close()

    def getApiVersion(self):
        """
        This retrieves the API version of the backend.

        :returns:  REST API Version
        """
        return self.api_version

    def getClusters(self):
        """
        Get the list of Clusters

        :returns: list of Clusters
        """
        response, body = self.http.get('/clusters')
        return body

    def getCluster(self, cluster_id):
        """
        Get information about a Cluster

        :param cluster_id: The id of the cluster to find
        :type cluster_id: str

        :returns: cluster
        """
        response, body = self.http.get('/clusters/%s' % cluster_id)
        return body

    def getClusterByName(self, name):
        """
        Get information about a cluster by name

        :param name: The name of the cluster to find
        :type name: str

        :returns: cluster
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CLUSTER - cluster doesn't exist
        """
        response, body = self.http.get('/clusters?name=%s' % name)
        return body

    def getServers(self):
        """
        Get the list of Servers

        :returns: list of Servers
        """
        response, body = self.http.get('/servers')
        return body

    def getServer(self, server_id):
        """
        Get information about a server

        :param server_id: The id of the server to find
        :type server_id: str

        :returns: server
        :raises: :class:`~hpelefthandclient.exceptions.HTTPServerError`
        """
        response, body = self.http.get('/servers/%s' % server_id)
        return body

    def getServerByName(self, name):
        """
        Get information about a server by name

        :param name: The name of the server to find
        :type name: str

        :returns: server
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SERVER - server doesn't exist
        """
        response, body = self.http.get('/servers?name=%s' % name)
        return body

    def createServer(self, name, iqn, optional=None):
        """
        Create a server by name

        :param name: The name of the server to create
        :type name: str
        :param iqn: The iSCSI qualified name
        :type name: str
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'description' : "some comment",
                'iscsiEnabled' : True,
                'chapName': "some chap name",
                'chapAuthenticationRequired': False,
                'chapInitiatorSecret': "initiator secret",
                'chapTargetSecret': "target secret",
                'iscsiLoadBalancingEnabled': True,
                'controllingServerName': "server name",
                'fibreChannelEnabled': False,
                'inServerCluster": True
            }

        :returns: server
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SERVER - server doesn't exist
        """
        info = {'name': name, 'iscsiIQN': iqn}
        if optional:
            info = self._mergeDict(info, optional)

        response, body = self.http.post('/servers', body=info)
        return body

    def deleteServer(self, server_id):
        """
        Delete a Server

        :param server_id: the server ID to delete

        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SERVER - The server does not exist
        """
        response, body = self.http.delete('/servers/%s' % server_id)
        return body

    def getSnapshots(self):
        """
        Get the list of Snapshots

        :returns: list of Snapshots
        """
        response, body = self.http.get('/snapshots')
        return body

    def getSnapshot(self, snapshot_id):
        """
        Get information about a Snapshot

        :returns: snapshot
        :raises: :class:`~hpelefthandclient.exceptions.HTTPServerError`
        """
        response, body = self.http.get('/snapshots/%s' % snapshot_id)
        return body

    def getSnapshotByName(self, name):
        """
        Get information about a snapshot by name

        :param name: The name of the snapshot to find

        :returns: volume
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SNAP - shapshot doesn't exist
        """
        response, body = self.http.get('/snapshots?name=%s' % name)
        return body

    def createSnapshot(self, name, source_volume_id, optional=None):
        """
        Create a snapshot of an existing Volume

        :param name: Name of the Snapshot
        :type name: str
        :param source_volume_id: The volume you want to snapshot
        :type source_volume_id: int
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'description' : "some comment",
                'inheritAccess' : false
            }

        """
        parameters = {'name': name}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action': 'createSnapshot',
                'parameters': parameters}

        response, body = self.http.post('/volumes/%s' % source_volume_id,
                                        body=info)
        return body

    def createSnapshotSet(self, source_volume_id, snapshot_set,
                          optional=None):
        """
        Create a snapshot of multiple existing volumes

        :param source_volume_id: The base volume you want to snapshot. NOTE:
                                 Must be the ID of the first volume listed in
                                 snapshot_set.
        :type source_volume_id: int
        :param snapshot_set: Array of SnapshotSet entities. The 1st entry
                             of the array will always be the current volume.
        :type snapshot_set: Array
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python
            snapshotSet = [
                {
                    "volumeName": "myVol1",
                    "volumeId": 48,
                    "snapshotName": "myVolSnapshot-0"
                },
                {
                    "volumeName": "myVol2",
                    "volumeId": 58,
                    "snapshotName": "myVolSnapshot-1"
                }
            ]

            optional = {
                'description' : "some comment",
                'inheritAccess' : false
            }

        """
        # we need to be on LeftHand API version 1.2 to create a snapshot set
        if self.api_version < self.MIN_CG_API_VERSION:
            ex_msg = ('Invalid LeftHand API version found (%(found)s).'
                      'Version %(minimum)s or greater required.') % {
                'found': self.api_version,
                'minimum': self.MIN_CG_API_VERSION}
            raise exceptions.UnsupportedVersion(ex_msg)

        parameters = {'snapshotSet': snapshot_set}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action': 'createSnapshotSet',
                'parameters': parameters}

        response, body = self.http.post('/volumes/%s' % source_volume_id,
                                        body=info)
        return body

    def deleteSnapshot(self, snapshot_id):
        """
        Delete a Snapshot

        :param snapshot_id: the snapshot ID to delete

        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SNAPSHOT - The snapshot does not exist
        """
        response, body = self.http.delete('/snapshots/%s' % snapshot_id)
        return body

    def cloneSnapshot(self, name, source_snapshot_id, optional=None):
        """
        Create a clone of an existing Shapshot

        :param name: Name of the Snapshot clone
        :type name: str
        :param source_snapshot_id: The snapshot you want to clone
        :type source_snapshot_id: int
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'description' : "some comment"
            }

        """
        parameters = {'name': name}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action': 'createSmartClone',
                'parameters': parameters}

        response, body = self.http.post('/snapshots/%s' % source_snapshot_id,
                                        body=info)
        return body

    def modifySnapshot(self, snapshot_id, options):
        """Modify an existing snapshot.

        :param snapshot_id: The id of the snapshot to find
        :type snapshot_id: str
        :param options: Dictionary of snapshot options to be modified
        :type options: dict

        :returns: snapshot
        :raises: :class:`~hpelefthandclient.exceptions.HTTPServerError`
            - SNAPSHOT_ID_NOT_FOUND - snapshot doesn't exist
        """
        response, body = self.http.put('/snapshots/%s' % snapshot_id,
                                       body=options)
        return body

    def getVolumes(self, cluster=None, fields=None):
        """
        Get the list of Volumes

        :param cluster: a cluster name
        :type cluster: str
        :param fields: specific fields of the returning data
        :type fields: list

        :returns: list of Volumes
        """
        fieldsQuery = []
        query = None
        if fields:
            tmpFields = []
            for field in fields:
                tmpFields.append(field)
            fieldsQuery = ('%s' % ','.join(tmpFields))

        if cluster and fieldsQuery:
            query = ('clusterName=%(cluster)s&fields=%(fieldsQuery)s' %
                     ({'cluster': quote(cluster.encode('utf8')),
                       'fieldsQuery': fieldsQuery}))
        elif cluster:
            # clusterName is documented, but not working, at this
            # point will get everything
            query = 'clusterName=%s' % quote(cluster.encode('utf8'))
        elif fieldsQuery:
            query = 'fields=%s' % fieldsQuery

        url = '/volumes'
        if query:
            url = '/volumes?%s' % query

        response, body = self.http.get(url)

        # Workaround for clusterName doesn't work in current API
        if cluster and fields and 'members[clusterName]' in fields:
            all_members = body['members']
            cluster_members = [member for member in all_members
                               if member['clusterName'] == cluster]
            body['members'] = cluster_members
            body['total'] = len(cluster_members)

        return body

    def getVolume(self, volume_id, query=None):
        """
        Get information about a volume

        :param volume_id: The id of the volume to find
        :param query: Optional query parameter, e.g. fields, expand-links
        :type volume_id: str

        :returns: volume
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist
        """
        uri = '/volumes/%s' % volume_id
        if query:
            uri = uri + '?' + query
        response, body = self.http.get(uri)
        return body

    def getVolumeByName(self, name):
        """
        Get information about a volume by name

        :param name: The name of the volume to find
        :type name: str

        :returns: volume
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist
        """
        response, body = self.http.get('/volumes?name=%s' % name)
        return body

    def findServerVolumes(self, server_name):
        """Find volumes that are exported to a server.

        :param server_name: The name of the server to search.
        :type server_name: str

        :returns: A list of volumes that are on the specified server.
        """

        # The only mechanism we have in 1.0 of the REST API
        # is to fetch all volumes and filter through them.
        # So we limit the return fields to cut down on the
        # n/w usage.
        # TODO(walter-boring)
        response, body = self.http.get(
            '/volumes?fields=members[name],members[volumeACL]')

        # Creates a list of volumes that have read/write access to the
        # specified server.
        volumes = [
            self.getVolumeByName(volume['name'])
            # Filter out volumes that do not have the volumeACL property set.
            for volume in body['members']
            if ('volumeACL' in volume and
                volume['volumeACL'] is not None)
            # Filter out volumes that do not have access to the target server.
            for entry in volume['volumeACL']
            if ('server' in entry and
                entry['server']['name'] == server_name)
        ]

        return volumes

    def createVolume(self, name, cluster_id, size, optional=None):
        """ Create a new volume

        :param name: the name of the volume
        :type name: str
        :param cluster_id: the cluster Id
        :type cluster_id: int
        :param sizeKB: size in KB for the volume
        :type sizeKB: int
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
             'description': 'some comment',
             'isThinProvisioned': 'true',
             'autogrowSeconds': 200,
             'clusterName': 'somename',
             'isAdaptiveOptimizationEnabled': 'true',
             'dataProtectionLevel': 2,
            }

        :returns: List of Volumes

        :raises: :class:`~hpelefthandclient.exceptions.HTTPConflict`
            - EXISTENT_SV - Volume Exists already
        """
        info = {'name': name, 'clusterId': cluster_id, 'size': size}
        if optional:
            info = self._mergeDict(info, optional)

        response, body = self.http.post('/volumes', body=info)
        return body

    def deleteVolume(self, volume_id):
        """
        Delete a volume

        :param name: the name of the volume
        :type name: str

        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        """
        response, body = self.http.delete('/volumes/%s' % volume_id)
        return body

    def modifyVolume(self, volume_id, optional):
        """Modify an existing volume.

        :param volume_id: The id of the volume to find
        :type volume_id: str

        :returns: volume
        :raises: :class:`~hpelefthandclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist
        """
        info = {'volume_id': volume_id}
        info = self._mergeDict(info, optional)
        response, body = self.http.put('/volumes/%s' % volume_id, body=info)
        return body

    def cloneVolume(self, name, source_volume_id, optional=None):
        """
        Create a clone of an existing Volume

        :param name: Name of the Volume clone
        :type name: str
        :param source_volume_id: The Volume you want to clone
        :type source_volume_id: int
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'description' : "some comment"
            }

        """
        parameters = {'name': name}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action': 'createSmartClone',
                'parameters': parameters}

        response, body = self.http.post('/volumes/%s' % source_volume_id,
                                        body=info)
        return body

    def addServerAccess(self, volume_id, server_id, optional=None):
        """
        Assign a Volume to a Server

        :param volume_id: Volume ID of the volume
        :type name: int
        :param server_id: Server ID of the server to add the volume to
        :type source_volume_id: int
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'Transport' : 0,
                'Lun' : 1,
            }

        """
        parameters = {'serverID': server_id,
                      'exclusiveAccess': True,
                      'readAccess': True,
                      'writeAccess': True}
        if optional:
            parameters = self._mergeDict(parameters, optional)

        info = {'action': 'addServerAccess',
                'parameters': parameters}

        response, body = self.http.post('/volumes/%s' % volume_id,
                                        body=info)
        return body

    def removeServerAccess(self, volume_id, server_id):
        """
        Unassign a Volume from a Server

        :param volume_id: Volume ID of the volume
        :type name: int
        :param server_id: Server ID of the server to remove the volume fom
        :type source_volume_id: int

        """
        parameters = {'serverID': server_id}

        info = {'action': 'removeServerAccess',
                'parameters': parameters}

        response, body = self.http.post('/volumes/%s' % volume_id,
                                        body=info)
        return body

    # Remote Copy related SSH commands
    def makeVolumeRemote(self, name, snapshot_name):
        """
        Make a volume remote. This command is issued against a secondary
        cluster and tells a volume it is associated to a primary volume
        on another system,

        :param name: Name of the volume
        :type name: str
        :param snapshot_name: Name of the remote snapshot that will be auto
                              created.
        :type snapshot_name: str

        """
        cmd = ['makeRemote',
               'volumeName=' + name,
               'snapshotName=' + snapshot_name]
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def makeVolumePrimary(self, name):
        """
        Make a remote volume a priamry volume. This command is issued against
        a secondary array to make a volume primary again. After a failover,
        this is needed to attach the volume.

        :param name: Name of the volume
        :type name: str
        """
        cmd = ['makePrimary',
               'volumeName=' + name]
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def createRemoteSnapshotSchedule(self, name, schedule_name, recur_period,
                                     start_time, retention_count,
                                     remote_cluster, remote_retention_count,
                                     remote_volume_name, remote_ip,
                                     remote_user_name, remote_password):
        """
        Creates a remote snapshot schedule. This command is run on the primary
        system and effectively creates asynchronous periodic replication
        between two arrays.

        :param name: Name of primary volume
        :type name: str
        :param schedule_name: Name of the schedule
        :type schedule_name: str
        :param recur_period: How often the remote snapshot will take place.
                             Minimum of 1800 seconds (30 mins).
        :type recur_period: int
        :param start_time: ISO 8601, UTC formatted date string like:
                           YYYY-MM-DDTHH:MM:SSZ
        :type start_time: str
        :param retention_count: The number of snapshots to maintain.
                                Must be between 1 and 50.
        :type retention_count: int
        :param remote_cluster: The name of the remote cluster to host the
                               remote volume.
        :type remote_cluster: str
        :param remote_retention_count: The number of remote snapshots to
                                       maintain. Must be between 1 and 50.
        :type remote_retention_count: int
        :param remote_volume_name: The name of the remote volume to host
                                   the snapshot.
        :type remote_volume_name: str
        :param remote_ip: The IP address of the remote group. NOTE: This
                          CANNOT be the VIP. It must be an IP of a node
                          within the cluster.
        :type remote_ip: str
        :param remote_user_name: The authentication user name for the remote
                                 group.
        :type remote_user_name: str
        :param remote_password: The password for the remote group.
        :type remote_password: str

        """
        cmd = ['createSnapshotSchedule',
               'volumename=' + name,
               'schedulename=' + schedule_name,
               'recurperiod=' + str(recur_period),
               'starttime=' + start_time,
               'retentioncount=' + str(retention_count),
               'remotecluster=' + remote_cluster,
               'remoteretentioncount=' + str(remote_retention_count),
               'remotevolume=' + remote_volume_name,
               'remoteip=' + remote_ip,
               'remoteusername=' + remote_user_name,
               'remotepassword=' + remote_password]
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def deleteRemoteSnapshotSchedule(self, name):
        """
        Deletes and existing remote snapshot schedule.

        :param name: Name of the remote snapshot schedule.
        :type name: str

        """
        cmd = ['deleteSnapshotSchedule',
               'scheduleName=' + name]
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def getRemoteSnapshotSchedule(self, name):
        """
        Retrieves remote snapshot schedule information

        :param name: Name of the remote snapshot schedule.
        :type name: str

        :returns: Command output with the remote snapshot schedule
                  information.
        """
        cmd = ['getSnapshotScheduleInfo',
               'scheduleName=' + name]
        schedule = self._run(cmd)
        return schedule

    def stopRemoteSnapshotSchedule(self, name):
        """
        Stops a remote snapshot schedule

        :param name: Name of the remote snapshot schedule.
        :type name: str
        """
        cmd = ['modifySnapshotSchedule',
               'scheduleName=' + name,
               'paused=1']
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def startRemoteSnapshotSchedule(self, name):
        """
        Starts a remote snapshot schedule

        :param name: Name of the remote snapshot schedule.
        :type name: str
        """
        cmd = ['modifySnapshotSchedule',
               'scheduleName=' + name,
               'paused=0']
        output = self._run(cmd)
        return self.ssh.was_command_successful(output)

    def doesRemoteSnapshotScheduleExist(self, name):
        """
        Determines if a remote snapshot schedule exists.

        :param name: Name of the remote snapshot schedule.
        :type name: str

        :returns: Whether or not a remote snapshot schedule exists.
        """
        output = self.getRemoteSnapshotSchedule(name)
        return self.ssh.was_command_successful(output)

    def getIPFromCluster(self, cluster_name):
        """
        Given a cluster name, this will return the first IP address in the
        cluster. The main use case for this is to create remote snapshot
        schedules, considering the VIP cannot be provided; an individual
        node IP is required.

        :param cluster_name: The cluster name
        :type cluster_name: str

        :returns: IP address of a node in the cluster

        """
        target_ip = None
        cluster = self.getClusterByName(cluster_name)
        if cluster:
            target_ip = cluster['storageModuleIPAddresses'][0]

        return target_ip

    def _mergeDict(self, dict1, dict2):
        """
        Safely merge 2 dictionaries together

        :param dict1: The first dictionary
        :type dict1: dict
        :param dict2: The second dictionary
        :type dict2: dict

        :returns: dict

        :raises Exception: dict1, dict2 is not a dictionary
        """
        if type(dict1) is not dict:
            raise Exception("dict1 is not a dictionary")
        if type(dict2) is not dict:
            raise Exception("dict2 is not a dictionary")

        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3

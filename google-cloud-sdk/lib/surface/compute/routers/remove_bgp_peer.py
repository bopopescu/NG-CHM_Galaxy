# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command for removing a BGP peer from a router."""
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.core import exceptions
from googlecloudsdk.third_party.py27 import py27_copy as copy


class PeerNotFoundError(exceptions.Error):
  """Raised when a peer is not found."""

  def __init__(self, name):
    self.name = name
    msg = 'peer `{0}` not found'.format(name)
    super(PeerNotFoundError, self
         ).__init__(msg)


class RemoveBgpPeer(base_classes.ReadWriteCommand):
  """Remove a BGP peer from a router."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--peer-name',
        required=True,
        help='The name of the peer being removed.')

    utils.AddRegionFlag(
        parser,
        resource_type='router',
        operation_type='update')

    parser.add_argument(
        'name',
        help='The name of the router.')

  @property
  def service(self):
    return self.compute.routers

  @property
  def resource_type(self):
    return 'routers'

  def CreateReference(self, args):
    return self.CreateRegionalReference(args.name, args.region)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeRoutersGetRequest(
                router=self.ref.Name(),
                region=self.ref.region,
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'Update',
            self.messages.ComputeRoutersUpdateRequest(
                router=self.ref.Name(),
                routerResource=replacement,
                region=self.ref.region,
                project=self.project))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    # remove peer if exists
    peer = None
    for p in replacement.bgpPeers:
      if p.name == args.peer_name:
        peer = p
        replacement.bgpPeers.remove(peer)
        break

    if peer is None:
      raise PeerNotFoundError(args.peer_name)

    return replacement


RemoveBgpPeer.detailed_help = {
    'DESCRIPTION': """
        *{command}* removes a BGP peer from a router.
        """,
}

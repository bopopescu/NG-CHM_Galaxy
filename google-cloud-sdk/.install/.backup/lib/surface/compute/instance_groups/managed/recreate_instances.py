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
"""Command for recreating instances managed by a managed instance group."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import constants
from googlecloudsdk.api_lib.compute import instance_groups_utils
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base


def _AddArgs(parser, multizonal):
  """Adds args."""
  parser.add_argument('name',
                      help='Managed instance group name.')
  parser.add_argument(
      '--instances',
      type=arg_parsers.ArgList(min_length=1),
      action=arg_parsers.FloatingListValuesCatcher(),
      metavar='INSTANCE',
      required=True,
      help='Names of instances to recreate.')
  if multizonal:
    scope_parser = parser.add_mutually_exclusive_group()
    utils.AddRegionFlag(
        scope_parser,
        resource_type='instance group',
        operation_type='recreate instances',
        explanation=constants.REGION_PROPERTY_EXPLANATION_NO_DEFAULT)
    utils.AddZoneFlag(
        scope_parser,
        resource_type='instance group manager',
        operation_type='recreate instances',
        explanation=constants.ZONE_PROPERTY_EXPLANATION_NO_DEFAULT)
  else:
    utils.AddZoneFlag(
        parser,
        resource_type='instance group manager',
        operation_type='recreate instances')


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class RecreateInstances(base_classes.BaseAsyncMutator):
  """Recreate instances managed by a managed instance group."""

  @staticmethod
  def Args(parser):
    _AddArgs(parser=parser, multizonal=False)

  @property
  def method(self):
    return 'RecreateInstances'

  @property
  def service(self):
    return self.compute.instanceGroupManagers

  @property
  def resource_type(self):
    return 'instanceGroupManagers'

  def CreateRequests(self, args):
    zone_ref = self.CreateZonalReference(args.name, args.zone)
    instances_ref = self.CreateZonalReferences(args.instances,
                                               zone_ref.zone,
                                               resource_type='instances')
    instances = [instance_ref.SelfLink() for instance_ref in instances_ref]
    return [(self.method,
             self.messages.ComputeInstanceGroupManagersRecreateInstancesRequest(
                 instanceGroupManager=zone_ref.Name(),
                 instanceGroupManagersRecreateInstancesRequest=(
                     self.messages.
                     InstanceGroupManagersRecreateInstancesRequest(
                         instances=instances,
                     )
                 ),
                 project=self.project,
                 zone=zone_ref.zone,
             ),),]


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class RecreateInstancesAlpha(RecreateInstances,
                             instance_groups_utils.InstancesReferenceMixin,
                             instance_groups_utils.InstanceGroupReferenceMixin):
  """Recreate instances managed by a managed instance group."""

  @staticmethod
  def Args(parser):
    _AddArgs(parser=parser, multizonal=True)

  def CreateRequests(self, args):
    errors = []
    group_ref = self.CreateInstanceGroupReference(
        name=args.name, region=args.region, zone=args.zone)
    instances = self.CreateInstanceReferences(group_ref, args.instances, errors)

    if group_ref.Collection() == 'compute.instanceGroupManagers':
      service = self.compute.instanceGroupManagers
      request = (
          self.messages.ComputeInstanceGroupManagersRecreateInstancesRequest(
              instanceGroupManager=group_ref.Name(),
              instanceGroupManagersRecreateInstancesRequest=(
                  self.messages.InstanceGroupManagersRecreateInstancesRequest(
                      instances=instances,
                  )
              ),
              project=self.project,
              zone=group_ref.zone,
          ))
    else:
      service = self.compute.regionInstanceGroupManagers
      request = (
          self.messages.
          ComputeRegionInstanceGroupManagersRecreateInstancesRequest(
              instanceGroupManager=group_ref.Name(),
              regionInstanceGroupManagersRecreateRequest=(
                  self.messages.RegionInstanceGroupManagersRecreateRequest(
                      instances=instances,)
              ),
              project=self.project,
              region=group_ref.region,
          ))

    return [(service, self.method, request)]


RecreateInstances.detailed_help = {
    'brief': 'Recreate instances managed by a managed instance group.',
    'DESCRIPTION': """
        *{command}* is used to recreate one or more instances in a managed
instance group. The underlying virtual machine instances are deleted and
recreated based on the latest instance template configured for the managed
instance group.
""",
}
RecreateInstancesAlpha.detailed_help = RecreateInstances.detailed_help
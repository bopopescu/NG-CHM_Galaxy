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

"""Implementation of gcloud dataflow jobs show command.
"""
from googlecloudsdk.api_lib.dataflow import job_display
from googlecloudsdk.api_lib.dataflow import job_utils
from googlecloudsdk.api_lib.dataflow import step_json
from googlecloudsdk.calliope import base
from surface import dataflow as commands


class Show(base.Command):
  """Shows a short description of the given job.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: argparse.ArgumentParser to register arguments with.
    """
    job_utils.ArgsForJobRef(parser)

    parser.add_argument(
        '--environment', action='store_true',
        help='If present, the environment will be listed.')
    parser.add_argument(
        '--steps', action='store_true',
        help='If present, the steps will be listed.')

  def Run(self, args):
    """Runs the command.

    Args:
      args: The arguments that were provided to this command invocation.

    Returns:
      A Job message.
    """
    job = job_utils.GetJobForArgs(self.context, args)

    # Extract the basic display information for the job
    dataflow_messages = self.context[commands.DATAFLOW_MESSAGES_MODULE_KEY]
    shown_job = job_display.DisplayInfo(job, dataflow_messages)

    # TODO(user): "Prettify" the environment, etc, since it includes
    # JSON as a string in  some of the fields.
    if args.environment:
      shown_job.environment = job.environment

    if args.steps:
      shown_job.steps = [
          self._PrettyStep(step) for step in step_json.ExtractSteps(job)]

    return shown_job

  def _PrettyStep(self, step):
    """Prettify a given step, by only extracting certain pieces of info.

    Args:
      step: The step to prettify.
    Returns:
      A dictionary describing the step.
    """
    return {
        'id': step['name'],
        'user_name': step['properties']['user_name']
    }

  def Display(self, args, job):
    """This method is called to print the result of the Run() method.

    Args:
      args: all the arguments that were provided to this command invocation.
      job: The Job message returned from the Run() method.
    """
    self.format(job)

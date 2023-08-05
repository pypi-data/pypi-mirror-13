# -*- coding: utf-8 -*-
"""
Command line client for deploying CFN stacks via crassus
Usage:
    gaius --stack STACK --parameters PARAMETERS --trigger-channel TOPIC_ARN
         [--region REGION] --back-channel QUEUE_URL [--timeout TIMEOUT]

Options:
  -h --help                     Show this
  --stack STACK                 Stack Name
  --parameters PARAMETERS       Parameters in format key=value[,key=value]
  --trigger-channel TOPIC_ARN   The ARN of the notify topic
  --region REGION               The region to deploy in [default: eu-west-1]
  --back-channel QUEUE_URL      The URL of the back-channel AWS::SQS
                                from Crassus
  --timeout TIMEOUT             Timeout in seconds after that gaius stops
                                polling on back channel and returns
                                [default: 600]
"""
import sys
import logging
from docopt import docopt

from . import service


logger = logging.getLogger('gaius')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def communicate():
    arguments = docopt(__doc__)
    stack_name = arguments['--stack']
    parameters = arguments['--parameters']
    topic_arn = arguments['--trigger-channel']
    region = arguments['--region']
    back_channel_url = arguments['--back-channel']
    timeout = int(arguments['--timeout'])

    service.cleanup(back_channel_url, timeout, stack_name, region)

    service.notify(stack_name, parameters, topic_arn, region)
    try:
        service.receive(back_channel_url, timeout, stack_name, region)
    except service.DeploymentErrorException as ex:
        logger.warn("Error occured during deployment: %s", ex)
        sys.exit(1)

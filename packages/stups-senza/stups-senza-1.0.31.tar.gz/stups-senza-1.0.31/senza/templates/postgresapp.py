'''
HA Postgres app, which needs an S3 bucket to store WAL files
'''

import click
from clickclick import warning, error, choice
from senza.aws import get_security_group, encrypt, list_kms_keys
from senza.utils import pystache_render
import requests
import random
import string

from ._helper import prompt, check_security_group, check_s3_bucket, get_account_alias

POSTGRES_PORT = 5432
HEALTHCHECK_PORT = 8008
SPILO_IMAGE_ADDRESS = "registry.opensource.zalan.do/acid/spilo-9.4"

TEMPLATE = '''
# basic information for generating and executing this definition
SenzaInfo:
  StackName: spilo
  {{^docker_image}}
  Parameters:
    - ImageVersion:
        Description: "Docker image version of spilo."
  {{/docker_image}}
  Tags:
    - SpiloCluster: "{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>"

# a list of senza components to apply to the definition
SenzaComponents:

  # this basic configuration is required for the other components
  - Configuration:
      Type: Senza::StupsAutoConfiguration # auto-detect network setup

  # will create a launch configuration and auto scaling group with scaling triggers
  - AppServer:
      Type: Senza::TaupageAutoScalingGroup
      AutoScaling:
        Minimum: 3
        Maximum: 3
        MetricType: CPU
      InstanceType: {{instance_type}}
      {{#ebs_optimized}}
      EbsOptimized: True
      {{/ebs_optimized}}
      BlockDeviceMappings:
        - DeviceName: /dev/xvdk
          {{#use_ebs}}
          Ebs:
            VolumeSize: {{volume_size}}
            VolumeType: {{volume_type}}
            {{#snapshot_id}}
            SnapshotId: {{snapshot_id}}
            {{/snapshot_id}}
            {{#volume_iops}}
            Iops: {{volume_iops}}
            {{/volume_iops}}
          {{/use_ebs}}
          {{^use_ebs}}
          VirtualName: ephemeral0
          {{/use_ebs}}
      ElasticLoadBalancer:
        - PostgresLoadBalancer
        - PostgresReplicaLoadBalancer
      HealthCheckType: EC2
      SecurityGroups:
        - app-spilo
      IamRoles:
        - Ref: PostgresAccessRole
      AssociatePublicIpAddress: false # change for standalone deployment in default VPC
      TaupageConfig:
        runtime: Docker
        {{#docker_image}}
        source: {{docker_image}}
        {{/docker_image}}
        {{^docker_image}}
        source: "{{=<% %>=}}{{Arguments.ImageVersion}}<%={{ }}=%>"
        {{/docker_image}}
        ports:
          {{postgres_port}}: {{postgres_port}}
          {{healthcheck_port}}: {{healthcheck_port}}
        etcd_discovery_domain: "{{discovery_domain}}"
        environment:
          SCOPE: "{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>"
          ETCD_DISCOVERY_DOMAIN: "{{discovery_domain}}"
          WAL_S3_BUCKET: "{{wal_s3_bucket}}"
          PGPASSWORD_SUPERUSER: "{{pgpassword_superuser}}"
          PGPASSWORD_ADMIN: "{{pgpassword_admin}}"
          PGPASSWORD_STANDBY: "{{pgpassword_standby}}"
        root: True
        mounts:
          /home/postgres/pgdata:
            partition: /dev/xvdk
            filesystem: {{fstype}}
            erase_on_boot: true
            options: {{fsoptions}}
        {{#scalyr_account_key}}
        scalyr_account_key: {{scalyr_account_key}}
        {{/scalyr_account_key}}
Resources:
  PostgresReplicaRoute53Record:
    Type: AWS::Route53::RecordSet
    Properties:
      Type: CNAME
      TTL: 20
      HostedZoneName: {{hosted_zone}}
      Name: "{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>-replica.{{hosted_zone}}"
      ResourceRecords:
        - Fn::GetAtt:
           - PostgresReplicaLoadBalancer
           - DNSName
  PostgresRoute53Record:
    Type: AWS::Route53::RecordSet
    Properties:
      Type: CNAME
      TTL: 20
      HostedZoneName: {{hosted_zone}}
      Name: "{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>.{{hosted_zone}}"
      ResourceRecords:
        - Fn::GetAtt:
           - PostgresLoadBalancer
           - DNSName
  PostgresReplicaLoadBalancer:
    Type: AWS::ElasticLoadBalancing::LoadBalancer
    Properties:
      CrossZone: true
      HealthCheck:
        HealthyThreshold: 2
        Interval: 5
        Target: HTTP:{{healthcheck_port}}/replica
        Timeout: 3
        UnhealthyThreshold: 2
      Listeners:
        - InstancePort: 5432
          LoadBalancerPort: 5432
          Protocol: TCP
      LoadBalancerName: "spilo-{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>-replica"
      ConnectionSettings:
        IdleTimeout: 3600
      SecurityGroups:
        - {{spilo_sg_id}}
      Scheme: internal
      Subnets:
        Fn::FindInMap:
          - LoadBalancerSubnets
          - Ref: AWS::Region
          - Subnets
  PostgresLoadBalancer:
    Type: AWS::ElasticLoadBalancing::LoadBalancer
    Properties:
      CrossZone: true
      HealthCheck:
        HealthyThreshold: 2
        Interval: 5
        Target: HTTP:{{healthcheck_port}}/master
        Timeout: 3
        UnhealthyThreshold: 2
      Listeners:
        - InstancePort: 5432
          LoadBalancerPort: 5432
          Protocol: TCP
      LoadBalancerName: "spilo-{{=<% %>=}}{{Arguments.version}}<%={{ }}=%>"
      ConnectionSettings:
        IdleTimeout: 3600
      SecurityGroups:
        - {{spilo_sg_id}}
      Scheme: internal
      Subnets:
        Fn::FindInMap:
          - LoadBalancerSubnets
          - Ref: AWS::Region
          - Subnets
  PostgresAccessRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
        - Effect: Allow
          Principal:
            Service: ec2.amazonaws.com
          Action: sts:AssumeRole
      Path: /
      Policies:
      - PolicyName: SpiloEC2S3KMSAccess
        PolicyDocument:
          Version: "2012-10-17"
          Statement:
          - Effect: Allow
            Action: s3:*
            Resource:
              - arn:aws:s3:::{{wal_s3_bucket}}/spilo/*
              - arn:aws:s3:::{{wal_s3_bucket}}
          - Effect: Allow
            Action: ec2:CreateTags
            Resource: "*"
          - Effect: Allow
            Action: ec2:Describe*
            Resource: "*"
          {{#kms_arn}}
          - Effect: Allow
            Action:
              - "kms:Decrypt"
              - "kms:Encrypt"
            Resource:
              - {{kms_arn}}
          {{/kms_arn}}
'''


def ebs_optimized_supported(instance_type):
    # per http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html
    """
    >>> ebs_optimized_supported('c3.xlarge')
    True
    >>> ebs_optimized_supported('t2.micro')
    False
    """
    return instance_type in ('c1.large', 'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge',
                             'c4.large', 'c4.xlarge', 'c4.2xlarge', 'c4.4xlarge', 'c4.8xlarge',
                             'd2.xlarge', 'd2.2xlarge', 'd2.4xlarge', 'd2.8xlarge',
                             'g2.2xlarge', 'i2.xlarge', 'i2.2xlarge', 'i2.4xlarge',
                             'm1.large', 'm1.xlarge', 'm2.2xlarge', 'm2.4xlarge',
                             'm3.xlarge', 'm3.2xlarge', 'r3.xlarge', 'r3.2xlarge',
                             'r3.4xlarge')


def set_default_variables(variables):
    variables.setdefault('discovery_domain', 'postgres.example.com')
    variables.setdefault('docker_image', None)
    variables.setdefault('ebs_optimized', None)
    variables.setdefault('fsoptions', 'noatime,nodiratime,nobarrier')
    variables.setdefault('fstype', 'ext4')
    variables.setdefault('healthcheck_port', HEALTHCHECK_PORT)
    variables.setdefault('hosted_zone', 'example.com')
    variables.setdefault('instance_type', 't2.micro')
    variables.setdefault('kms_arn', None)
    variables.setdefault('pgpassword_admin', 'admin')
    variables.setdefault('pgpassword_standby', 'standby')
    variables.setdefault('pgpassword_superuser', 'zalando')
    variables.setdefault('postgres_port', POSTGRES_PORT)
    variables.setdefault('scalyr_account_key', None)
    variables.setdefault('snapshot_id', None)
    variables.setdefault('spilo_sg_id', None)
    variables.setdefault('use_ebs', True)
    variables.setdefault('volume_iops', 300)
    variables.setdefault('volume_size', 10)
    variables.setdefault('volume_type', 'gp2')
    variables.setdefault('wal_s3_bucket', None)

    return variables


def gather_user_variables(variables, region, account_info):
    defaults = set_default_variables(dict())

    if click.confirm('Do you want to set the docker image now? [No]'):
        prompt(variables, "docker_image", "Docker Image Version", default=get_latest_spilo_image())

    prompt(variables, 'wal_s3_bucket', 'Postgres WAL S3 bucket to use',
           default='{}-{}-spilo-app'.format(get_account_alias(), region))

    prompt(variables, 'instance_type', 'EC2 instance type', default='t2.micro')

    variables['hosted_zone'] = account_info.Domain or defaults['hosted_zone']
    if (variables['hosted_zone'][-1:] != '.'):
        variables['hosted_zone'] += '.'
    prompt(variables, 'discovery_domain', 'ETCD Discovery Domain',
           default='postgres.' + variables['hosted_zone'][:-1])

    if variables['instance_type'].lower().split('.')[0] in ('c3', 'g2', 'hi1', 'i2', 'm3', 'r3'):
        variables['use_ebs'] = click.confirm('Do you want database data directory on external (EBS) storage? [Yes]',
                                             default=defaults['use_ebs'])
    else:
        variables['use_ebs'] = True

    if variables['use_ebs']:
        prompt(variables, 'volume_size', 'Database volume size (GB, 10 or more)', default=defaults['volume_size'])
        prompt(variables, 'volume_type', 'Database volume type (gp2, io1 or standard)',
               default=defaults['volume_type'])
        if variables['volume_type'] == 'io1':
            pio_max = variables['volume_size'] * 30
            prompt(variables, "volume_iops", 'Provisioned I/O operations per second (100 - {0})'.
                   format(pio_max), default=str(pio_max))
        prompt(variables, "snapshot_id", "ID of the snapshot to populate EBS volume from", default="")
        if ebs_optimized_supported(variables['instance_type']):
            variables['ebs_optimized'] = True
    prompt(variables, "fstype", "Filesystem for the data partition", default=defaults['fstype'])
    prompt(variables, "fsoptions", "Filesystem mount options (comma-separated)",
           default=defaults['fsoptions'])
    prompt(variables, "scalyr_account_key", "Account key for your scalyr account", "")

    prompt(variables, 'pgpassword_superuser', "Password for PostgreSQL superuser [random]", show_default=False,
           default=generate_random_password, hide_input=True, confirmation_prompt=True)
    prompt(variables, 'pgpassword_standby', "Password for PostgreSQL user standby [random]", show_default=False,
           default=generate_random_password, hide_input=True, confirmation_prompt=True)
    prompt(variables, 'pgpassword_admin', "Password for PostgreSQL user admin", show_default=True,
           default=defaults['pgpassword_admin'], hide_input=True, confirmation_prompt=True)

    if click.confirm('Do you wish to encrypt these passwords using KMS?', default=False):
        kms_keys = [k for k in list_kms_keys(region) if 'alias/aws/ebs' not in k['aliases']]

        if len(kms_keys) == 0:
            raise click.UsageError('No KMS key is available for encrypting and decrypting. '
                                   'Ensure you have at least 1 key available.')

        options = ['{}: {}'.format(k['KeyId'], k['Description']) for k in kms_keys]
        kms_key = choice(prompt='Please select the encryption key', options=options)
        kms_keyid = kms_key.split(':')[0]

        variables['kms_arn'] = [k['Arn'] for k in kms_keys if k['KeyId'] == kms_keyid][0]

        for key in [k for k in variables if k.startswith('pgpassword_')]:
            encrypted = encrypt(region=region, KeyId=kms_keyid, Plaintext=variables[key], b64encode=True)
            variables[key] = 'aws:kms:{}'.format(encrypted)

    set_default_variables(variables)

    sg_name = 'app-spilo'
    rules_missing = check_security_group(sg_name,
                                         [('tcp', 22), ('tcp', POSTGRES_PORT), ('tcp', HEALTHCHECK_PORT)],
                                         region, allow_from_self=True)

    if ('tcp', 22) in rules_missing:
        warning('Security group {} does not allow SSH access, you will not be able to ssh into your servers'.
                format(sg_name))

    if ('tcp', POSTGRES_PORT) in rules_missing:
        error('Security group {} does not allow inbound TCP traffic on the default postgres port ({})'.format(
            sg_name, POSTGRES_PORT
        ))

    if ('tcp', HEALTHCHECK_PORT) in rules_missing:
        error('Security group {} does not allow inbound TCP traffic on the default health check port ({})'.
              format(sg_name, HEALTHCHECK_PORT))
    variables['spilo_sg_id'] = get_security_group(region, sg_name).id

    check_s3_bucket(variables['wal_s3_bucket'], region)

    return variables


def generate_random_password(length=64):
    """
    >>> len(generate_random_password(61))
    61
    """
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def generate_definition(variables):
    """
    >>> variables = set_default_variables(dict())
    >>> len(generate_definition(variables)) > 300
    True
    """
    definition_yaml = pystache_render(TEMPLATE, variables)
    return definition_yaml


def get_latest_spilo_image(registry_url='https://registry.opensource.zalan.do',
                           address='/teams/acid/artifacts/spilo-9.4/tags'):
    try:
        r = requests.get(registry_url + address)
        if r.ok:
            # sort the tags by creation date
            latest = None
            for entry in sorted(r.json(), key=lambda t: t['created'], reverse=True):
                tag = entry['name']
                # try to avoid snapshots if possible
                if 'SNAPSHOT' not in tag:
                    latest = tag
                    break
                latest = latest or tag
            return "{0}:{1}".format(SPILO_IMAGE_ADDRESS, latest)
    except:
        pass
    return ""

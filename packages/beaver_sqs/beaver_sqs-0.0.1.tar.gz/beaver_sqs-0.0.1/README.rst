.. image:: https://travis-ci.org/python-beaver/beaver-sqs?branch=master
    :target: https://travis-ci.org/python-beaver/beaver-sqs

.. image:: https://coveralls.io/repos/python-beaver/beaver-sqs/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/python-beaver/beaver-sqs?branch=master

Beaver-SQS
==========

Transport module for `Python-Beaver <https://github.com/python-beaver/python-beaver>`_ to deliver log entries via AWS SQS.

**Usage**

Beaver can optionally get data from a configfile using the -c flag. This file is in ini format. Global configuration will be under the beaver stanza. The following are global beaver configuration keys with their respective meanings:

- sqs_aws_access_key: Can be left blank to use IAM Roles or AWS_ACCESS_KEY_ID environment variable (see: https://github.com/boto/boto#getting-started-with-boto)
- sqs_aws_secret_key: Can be left blank to use IAM Roles or AWS_SECRET_ACCESS_KEY environment variable (see: https://github.com/boto/boto#getting-started-with-boto)
- sqs_aws_profile_name: Can be left blank to use IAM Roles AWS_SECRET_ACCESS_KEY environment variable, or fixed keypair (above) (see: https://github.com/boto/boto#getting-started-with-boto)
- sqs_aws_region: Default us-east-1. AWS Region
- sqs_aws_queue: SQS queue, or comma delimited list of queues (must exist)
- sqs_aws_queue_owner_acct_id: Optional. Defaults None. Account ID or Principal allowed to write to queue
- sqs_bulk_lines: Optional. Send multiple log entries in a single SQS message (cost saving benefit on larger environments)

**Example**
::

  # /etc/beaver/conf
  [beaver]
  sqs_aws_region: us-east-1
  sqs_aws_queue: logstash-input1,logstash-input2
  sqs_aws_access_key: <access_key>
  sqs_aws_secret_key: <secret_key>

  # logstash indexer config:
  input {
    sqs {
      queue => "logstash-input1"
      access_key_id => "<access_key>"
      secret_access_key => "<secret_key>"
    }
  }
  output { stdout { debug => true } }


**Contributing**

See: `CONTRIBUTING.rst <CONTRIBUTING.rst>`_

**Credits**

- `Jamie Cressey <https://github.com/jamiecressey>`_
- `Jose Gonzalez <https://github.com/josegonzalez>`_

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import configargparse
import bullkit

def main(*arg):
	# Parse command line options.
	commandargs = configargparse.ArgumentParser(description='This script performs various security checks on an Amazon Web Services account.')
	commandargs.add_argument('-v', env_var='VERBOSE', action="store_true", default=False, help='Print additional debugging output to stderr.')
	commandargs.add_argument('--noslack', env_var='NOSLACK', action="store_true", default=False, help='Print output to stdout rather than Slack.')
	commandargs.add_argument('--slacktoken', env_var='SLACKTOKEN', help='Your Slack API token. Required unless you use --noslack.')
	commandargs.add_argument('--mfa', env_var='MFA', action="store_true", default=False, help='Check for IAM users that don\'t have MFA enabled.')
	commandargs.add_argument('--mfachannel', env_var='MFACHANNEL', help='The Slack channel to which we should post the results of the IAM user MFA check.')
	commandargs.add_argument('--mfanagusers', env_var='MFANAGUSERS', action="store_true", default=False, help='Send Slack messages directly to users who need to enable MFA. Relies on a properly populated users.yml file.')
	commandargs.add_argument('--publics3', env_var='PUBLICS3', action="store_true", default=False, help='Check for public S3 buckets.')
	commandargs.add_argument('--publics3channel', env_var='PUBLICS3CHANNEL', help='The Slack channel to which we should post the results of the public S3 bucket check.')

	# If we're supposed to talk to Slack...
	if not commandargs.parse_args().noslack:
		# ...fail if the API token hasn't been provided.
		if not commandargs.parse_args().slacktoken:
			bullkit.abort('--slacktoken must be specified if you\'re not suppressing Slack output with --noslack')

		# ...fail if we've not been told what Slack channel to use for MFA results.
		if commandargs.parse_args().mfa:
			if not commandargs.parse_args().mfachannel:
				bullkit.abort('--mfachannel must be specified if you\'re using --mfa without --noslack')

		# ...fail if we've not been told what Slack channel to use for public S3 results.
		if commandargs.parse_args().publics3:
			if not commandargs.parse_args().publics3channel:
				bullkit.abort('--publics3channel must be specified if you\'re using --publics3 without --noslack')

	if commandargs.parse_args().mfa:
		import mfa
		mfa.mfa(commandargs)

	if commandargs.parse_args().publics3:
		import publics3
		publics3.publics3(commandargs)

# Only execute main() if we're being executed, not if we're being imported.
if __name__ == "__main__":
	main()
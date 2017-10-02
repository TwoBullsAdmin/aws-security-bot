#! /usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import bullkit
import sys
from slackclient import SlackClient

def publics3 (commandargs):
	bad_buckets = {}
	bullkit.debug('Getting the list of S3 buckets...', commandargs)
	client = boto3.client('s3')
	for bucket in client.list_buckets()['Buckets']:
		bullkit.debug('Checking the ACL of: ' + bucket['Name'], commandargs)
		bucketacl = boto3.resource('s3').BucketAcl(bucket['Name'])
		for grant in bucketacl.grants:
			if grant['Grantee']['Type'] == 'Group':
				if grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
					if not bad_buckets.get(bucket['Name']):
						bullkit.debug('Oh no, it\'s public!', commandargs)
						bad_buckets[bucket['Name']] = []
					bad_buckets[bucket['Name']].append(grant['Permission'])

	# If we didn't find any public buckets...
	if not bad_buckets:
		bullkit.debug('No public buckets found, nice!', commandargs)
	
	# If we found public buckets...
	else:
		# Format the list into a string for a Slack message.
		bullkit.debug('Found these public buckets: ' + str(bad_buckets), commandargs)
		bullkit.debug('Formatting the list of bad buckets...', commandargs)
		slackmsg = ''
		bad_buckets_formatted = []
		for bucket, privs in bad_buckets.iteritems():
			bad_buckets_formatted.append(bucket + ': ' + str(privs))
		slackmsg = 'The following S3 buckets are public:\n```' + '\n'.join(bad_buckets_formatted) + '```\nYou should adjust their permissions immediately.'

		# If we've been told to post to Slack...
		if not commandargs.parse_args().noslack:
			bullkit.debug('Sending the list to Slack...', commandargs)
			# Post the list to the relevant Slack channel.
			slack = SlackClient(commandargs.parse_args().slacktoken)
			slackresult = slack.api_call('chat.postMessage', channel=commandargs.parse_args().publics3channel, username='AWS Security Bot', icon_emoji=':robot_face:', text=slackmsg)

			# Make sure the post was successful.
			if slackresult['ok'] is not True:
				bullkit.abort('Posting to Slack was unsuccessful. Slack said:\n' + str(slackresult))
			bullkit.debug('Sent successfully.', commandargs)

		# If we've been told to *not* post to Slack...
		else:
			# Print the list to standard output.
			print slackmsg
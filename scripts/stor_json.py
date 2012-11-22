#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import datetime
import time
import twitter

def stor_json(args):
	api = twitter.Api()
	
	base = datetime.datetime.today()
	from_day = args.start
	range_days = args.days
	dateList = [base - datetime.timedelta(days=x) for x in range(from_day,range_days)]
	sleeptime = 2
	retrysleeptime = 60
	hashtag = ""
	i = 0
	for h in args.hashtags:
		if not i == len(args.hashtags)-1:
			hashtag += "#%s OR " % (args.hashtags[i])
		else:
			hashtag += "#%s" % (args.hashtags[i])
		i += 1

	if args.verbose:
		print("Hashtags: %s" % (hashtag))

	
	all_tweets = []
	for d in dateList:
		tweets_per_day = 0
		nextday = (d + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
		day = d.strftime('%Y-%m-%d')
		if args.verbose:
			print("Fetching from %s until %s" % (day, nextday))
		r = []
	
	
		rf = api.GetSearch(
				term="#%s since:%s until:%s" % (hashtag, day, nextday),
				per_page=1,
				page=1,
				result_type="recent")
		if len(rf):
			max_id = int(rf[-1].id)
			if args.verbose:
				print("Startdate: %s" % (rf[-1].created_at))
			results = True
			while results:
				if args.verbose:
					print("Next round with new max_id: %i" % (max_id))
				try:
					rf = api.GetSearch(
							term="%s since:%s until:%s max_id:%i" % 
							(hashtag, day, nextday, max_id), 
							per_page=100, 
							page=1,
							query_users=False,
							include_entities=False,
							show_user="false",
							result_type="recent")
				except:
					if args.verbose:
						print("Retry with the same parameters in %i seconds" % (retrysleeptime))
					time.sleep(retrysleeptime)
					continue
				if args.verbose:
					print("Results: %s" % (len(rf)))
				if len(rf) == 1 and rf[-1].id == max_id:
					if args.verbose:
						print("No more tweets for this day")
					results = False
				else:
					tweets_per_day += len(rf)
					json = [j.AsJsonString() for j in rf]
					r.extend(json)
					max_id = int(rf[-1].id)
					if args.verbose:
						print("Last date: %s" % (rf[-1].created_at))
						print("Sleeping %i seconds (otherwise Twitter gets angry)" % (sleeptime))
					time.sleep(sleeptime)
			if args.outfile == None:
				outfile = '%s_%s.json' % (hashtag.replace('#', '').replace(' ', '_'), day)
			else:
				outfile = args.outfile
			f = open(outfile, 'w')
			f.write(str(r))
			f.close()
			print("##### %d tweets written to %s" % (tweets_per_day, outfile))
		all_tweets.append((day, tweets_per_day))

	if args.verbose:
		print(all_tweets)
		sum_tweets = 0
		for (d, t) in all_tweets:
			if args.verbose:
				print("Tweets at %s: %i" % (d, t))
			sum_tweets += t
		print("Summary Tweets: %i" % (sum_tweets))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Store Tweets with given Hashtag(s) in a json format.')
	parser.add_argument('-v', '--verbose', action='store_true',
			help='Verbose output')
	parser.add_argument('-d', '--days', 
			metavar='days',
			type=int,
			default=1,
			help='number of days to go back from today [default: %(default)s]; Twitter stores roughly 9 days back in the search API')
	parser.add_argument('-s', '--start', 
			metavar='days',
			type=int,
			default=0,
			help='number of days to start from relative to today [default: %(default)s]')
	parser.add_argument('-o', '--outfile',
			metavar='outfile',
			type=str,
			help='file to write json into; defaults to a filename based on hashtags and date')
	parser.add_argument('hashtags',
			metavar='hashtag',
			type=str,
			nargs='+',
			help='hashtag to search for')

	if len(sys.argv) == 1:
		parser.print_help()
		print("No hashtag given.")
		sys.exit(1)

	args = parser.parse_args(sys.argv[1:])
	
	if args.verbose:
		print("Application arguments:\n%s" % str(vars(args)))
	
	if args.days <= args.start:
		print("Start day must be greater than number of days.")
		sys.exit(1)
	
	stor_json(args)

	

sys.exit(0)

# vim: ts=4, sw=4

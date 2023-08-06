#!/usr/bin/env python2

import argparse
import urllib
import urllib2
import re
import sys

BASE_URL = "http://biit.cs.ut.ee/gprofiler/"
VERSION = "0.1"

def debug(msg):
	sys.stderr.write(msg)
	sys.stderr.write("\n")

def warn(msg, is_error=0):
	if (is_error):
		msg = "ERROR: " + msg
	else:
		msg = "WARNING: " + msg
	debug(msg)

def err(msg):
	warn(msg, is_error=1)
	sys.exit(1)

def parse_command_line():
	parser = argparse.ArgumentParser(description = "Query g:Profiler (" + BASE_URL + ").")
	qgroup = parser.add_mutually_exclusive_group(required=True)
	cbgroup = parser.add_mutually_exclusive_group()
	
	qgroup.add_argument(
		"-q", "--query-file", default=None,
		help="A list of query symbols"
	)
	parser.add_argument(
		"-O", "--output", default=None,
		help="Store output in the specified file instead of standard output"
	)	
	parser.add_argument(
		"-o", "--organism", default="hsapiens",
		help="The organism name in g:Profiler format"
	)
	parser.add_argument(
		"-a", "--all-results", action="store_false",
		help="All results, including those deemed not significant"
	)
	parser.add_argument(
		"--ordered", action="store_true",
		help="Ordered query"
	)
	parser.add_argument(
		"-r", "--region-query", action="store_true",
		help="The query consists of chromosomal regions"
	)
	parser.add_argument(
		"-e", "--exclude-iea", action="store_true",
		help="Exclude electronic GO annotations"
	)
	parser.add_argument(
		"-u", "--underrep", action="store_true",
		help="Measure underrepresentation"
	)
	parser.add_argument(
		"-E", "--evcodes", action="store_true",
		help="Request evidence codes in output as the final column"
	)	
	parser.add_argument(
		"-H", "--hier-sorting", action="store_true",
		help="Sort output into subgraphs"
	)
	parser.add_argument(
		"--hier-filtering", default=None, choices=["moderate", "strong"],
		help="Hierarchical filtering"
	)
	parser.add_argument(
		"-p", "--max-p-value", default=None, type=float,
		help="Custom p-value threshold"
	)
	parser.add_argument(
		"--min-set-size", default=None, type=int,
		help="Minimum size of functional category"
	)
	parser.add_argument(
		"--max-set-size", default=None, type=int,
		help="Maximum size of functional category"
	)
	parser.add_argument(
		"-c", "--correction-method", default="gSCS", choices=["gSCS", "fdr", "bonferroni"],
		help="Algorithm used for determining the significance threshold"
	)
	parser.add_argument(
		"-d", "--domain-size", default="annotated", choices=["annotated", "known"],
		help="Statistical domain size"
	)
	parser.add_argument(
		"--numeric-ns", default=None,
		help="Namespace to use for fully numeric IDs"
	)
	cbgroup.add_argument(
		"-b", "--custom-bg", default=None,
		help="List of symbols to use as a statistical background"
	)
	cbgroup.add_argument(
		"-B", "--custom-bg-file", default=None,
		help="List of symbols to use as a statistical background (file name)"
	)
	parser.add_argument(
		"-f", "--src-filter", default=None,
		help="Data sources to use, space-separated (e.g. \"GO:BP GO:CC KEGG\")"
	)
	qgroup.add_argument(
		"query", nargs="*", default=[],
		help="Query symbols (if --query-file has not been specified)"
	)
	
	# Debug options
	
	parser.add_argument(
		"--columns", default=None,
		help="Output nth columns only, separate multiple columns with commas"
	)	
	
	return parser.parse_args()
	
def transform_params(args):
	
	# Transform command-line parameters into a parameter set
	# expected by g:Profiler API
	
	args = vars(args)
	postdata = {}

	# Helper routines
	
	def transform_list(from_arg, to_arg):
		return [to_arg, " ".join(args[from_arg])]

	def transform_file(from_arg, to_arg):		
		return [to_arg, re.sub(r"\s+", " ", open(args[from_arg], "r").read())]
			
	def transform_boolean(from_arg, to_arg):
		return [to_arg, "1" if args[from_arg] else "0"]
		
	def transform_srcfilter(from_arg):
		r = []
		fstr = args[from_arg].strip()
		
		if (fstr == ""):
			return None
		
		for src in re.split(r"\s+", fstr):
			r.append(["sf_" + src, "1"])
		return r
	
	# Argument mapping. If parameter map value is
	#
	# - a string, then keep argument value, but transform argument name
	# - a function, then it is expected to return either 
	#   ~ a list containing the posted argument name-value pair
	#   ~ a list of lists containing such pairs
	
	pmap = {
		"query"				: lambda from_arg: transform_list(from_arg, "query"),
		"query_file"		: lambda from_arg: transform_file(from_arg, "query"),
		"organism"			: "organism",
		"all_results"		: lambda from_arg: transform_boolean(from_arg, "significant"),
		"ordered"			: lambda from_arg: transform_boolean(from_arg, "ordered_query"),
		"region_query"		: lambda from_arg: transform_boolean(from_arg, "region_query"),
		"exclude_iea"		: lambda from_arg: transform_boolean(from_arg, "no_iea"),
		"underrep"			: lambda from_arg: transform_boolean(from_arg, "underrep"),
		"evcodes"			: lambda from_arg: transform_boolean(from_arg, "txt_evcodes"),
		"hier_sorting"		: lambda from_arg: transform_boolean(from_arg, "sort_by_structure"),
		"hier_filtering"	: lambda from_arg: [\
			"hierfiltering", \
			"compact_rgroups" if args[from_arg] == "moderate" else "compact_ccomp"],
		"max_p_value"		: "user_thr",
		"min_set_size"		: "min_set_size",
		"max_set_size"		: "max_set_size",
		"correction_method"	: lambda from_arg: [\
			"threshold_algo", \
			"analytical" if args[from_arg] == "gSCS" else args[from_arg]],
		"domain_size"		: "domain_size_type",
		"numeric_ns"		: "prefix",
		"custom_bg"			: "custbg",
		"custom_bg_file"	: lambda from_arg: transform_file(from_arg, "custbg"),
		"src_filter"		: transform_srcfilter
	}
		
	for k, v in pmap.iteritems():
		
		# Skip nonexistent parameters
		
		if (args[k] is None or (type(args[k]) is list and len(args[k]) == 0)):
			continue
		
		# Transform parameters

		if (type(v) is str):
			postdata[v] = args[k]
		elif (hasattr(v, "__call__")):
			r = v(k)
			
			if (type(r) is list and type(r[0]) is list):
				for to_arg in r:
					postdata[to_arg[0]] = to_arg[1]
			elif (type(r) is list):
				postdata[r[0]] = r[1]
			
	return postdata
		
def main():
	res = ""
	args = parse_command_line()
	postdata = transform_params(args)
	columns = None
	outf = None
	
	# Initialization
	
	postdata.update({
		"output" : "mini"
	})
	
	if (args.columns):
		columns = [int(cid.strip())-1 for cid in re.sub(r"[^\d,]", "", args.columns).split(",")]
		columns.sort()	
	if (args.output):
		outf = open(args.output, "w")
	
	# g:Profiler query or use dummy output for debugging
	
	if (re.match(r"http", BASE_URL)):
		data = urllib.urlencode(postdata)
		headers = { "User-Agent" : "gprofiler-python-native/" + VERSION }
		rq = urllib2.Request(BASE_URL, data, headers)			
		res = urllib2.urlopen(rq, timeout=60*30)
	else:
		res = open(BASE_URL, "r")
	
	for line in res:
		if (re.match(r"\s*#", line)):
			continue
		if (columns is not None):
			entries = line.split("\t")
			line = "\t".join([entries[i] for i in columns])
			
		line = line.rstrip()
			
		if (outf):
			outf.write(line + "\n")
		else:
			print line
	
	sys.exit(0);

main()

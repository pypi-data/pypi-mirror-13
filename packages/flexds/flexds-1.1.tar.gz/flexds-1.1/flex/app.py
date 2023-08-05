"""
Copyright 2016 Derek Ruths

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os, os.path
import sys
import argparse
import logging
import time

from flex.pipeline import *

logger = logging.getLogger(os.path.basename(__file__))

LOG_LEVELS = ['DEBUG','INFO','WARN','ERROR','CRITICAL']
COMMANDS = ['tasks','unmark','mark','run']

def do_info(args):
	raise NotImplementedError
	pass

def do_wipe(args):
	raise NotImplementedError
	pass

def do_import(args):
	raise NotImplementedError
	pass

def do_export(args):
	raise NotImplementedError
	pass

def do_tasks(args):
	parser = argparse.ArgumentParser('fx tasks',description='print information on tasks in a particular pipeline')
	parser.add_argument('pipeline_file',help='the pipeline of interest')

	args = parser.parse_args(args)

	# load the pipeline
	p = get_pipeline(args.pipeline_file)

	# print out all the tasks in sort order
	make_tname_str = lambda x: '%s/%s' % (x.pipeline.name,x.name)

	visitation_list = p.get_visitation_list()
	tname_width = max([len(make_tname_str(x)) for x,depth in visitation_list]) + 4

	for task,depth in visitation_list:
		info_str = make_tname_str(task).ljust(tname_width)
		if task.is_marked():
			info_str += '%s' % time.ctime(task.mark_timestamp())
		else:
			info_str += '--'

		print info_str

def do_unmark(args):
	parser = argparse.ArgumentParser('fx unmark',description='unmark one or more tasks')
	parser.add_argument('-f','--force',action='store_true',help='set this to actually unmark an entirely pipeline or pipelines')
	parser.add_argument('-r','--recur',action='store_true',default=False,help='unmark all dependent tasks as well')
	parser.add_argument('pipeline_file',help='the pipeline to unmark tasks in')
	parser.add_argument('task_names',nargs='*',help='the specific task to unmark. If omitted, the entire pipeline will be unmarked')

	args = parser.parse_args(args)

	# load the pipeline
	p = get_pipeline(args.pipeline_file)

	if not args.task_names:
		do_it = args.force
		if not do_it:
			# prompt
			x = raw_input('are you sure you want to unmark entire pipelines? (y/n) ')
			do_it = (x == 'y')
				
		if do_it:
			p.unmark_all_tasks(args.recur)
		else:
			print 'unmarking operation aborted'

	else:
		for tname in args.task_names:
			logger.debug('unmarking task: %s' % tname)
			task = p.get_task(tname)

			if task is None:
				logger.error('task %s dos not exist' % tname)
				sys.exit(-1)

			task.unmark()
		
def do_mark(args):
	parser = argparse.ArgumentParser('fx mark',description='mark one or more tasks')
	parser.add_argument('-f','--force',action='store_true',help='set this to actually mark an entire pipeline or pipelines')
	parser.add_argument('-r','--recur',action='store_true',default=False,help='mark all dependent tasks as well')
	parser.add_argument('pipeline_file',help='the pipeline to mark tasks in')
	parser.add_argument('task_names',nargs='*',help='the specific task to mark. If omitted, the entire pipeline will be marked')

	args = parser.parse_args(args)

	# load the pipeline
	p = get_pipeline(args.pipeline_file)

	if not args.task_names:
		do_it = args.force
		if not do_it:
			# prompt
			x = raw_input('are you sure you want to mark entire pipelines? (y/n) ')
			do_it = (x == 'y')
				
		if do_it:
			p.mark_all_tasks(args.recur)
		else:
			print 'marking operation aborted'
	else:
		for tname in args.task_names:
			logger.debug('marking task: %s' % tname)
			task = p.get_task(tname)

			if task is None:
				logger.error('task %s does not exist' % tname)
				sys.exit(-1)

			task.mark()

def do_dry_run(args):
	raise NotImplementedError
	pass

def do_run(args):
	parser = argparse.ArgumentParser('fx run',description='run a flex pipeline')
	parser.add_argument('-f','--force',choices=['NONE','TOP','ALL','SOLO'],default='NONE',
		help='force tasks to run, even if they is already marked. NONE will not force any marked tasks to run; TOP will force the named task or the top-level tasks in the pipeline to run; ALL will force all marked tasks encountered in the dependency tree to run; SOLO will force the specified task to run, but NOT any of its dependencies (regardless of their state).')
	parser.add_argument('pipeline_file',help='the pipeline to run')
	parser.add_argument('task_name',nargs='?',help='the specific task to run. If omitted, the entire pipeline will be run')

	
	args = parser.parse_args(args)

	force_val_lookup = {'NONE':FORCE_NONE, 'TOP':FORCE_TOP, 'ALL':FORCE_ALL, 'SOLO':FORCE_SOLO}
	force_val = force_val_lookup[args.force.upper()]

	if not args.task_name and force_val == FORCE_SOLO:
		logger.error('force status SOLO can only be used when tasks have been explicitly specified')
		sys.exit(-1)

	# load the pipeline
	p = get_pipeline(args.pipeline_file)

	if not args.task_name:
		# run the whole pipeline
		p.run(force=force_val)
	else:
		t = p.get_task(args.task_name)

		if t is None:
			logger.error('task %s does not exist' % args.task_name)
			sys.exit(-1)
		else:
			t.run(force=force_val)

def main():
	parser = argparse.ArgumentParser('fx')
	parser.add_argument('-l','--log_level',choices=LOG_LEVELS,default='ERROR')
	parser.add_argument('command',choices=COMMANDS)
	parser.add_argument('cmd_args',nargs=argparse.REMAINDER)

	args = parser.parse_args()

	# configure the logger
	log_level = eval('logging.%s' % args.log_level)
	logging.basicConfig(level=log_level,format='%(levelname)s: %(message)s')

	# run the command
	logger.debug('running command: %s' % args.command)
	try:
		eval('do_%s(args.cmd_args)' % args.command)
	except ParseException as e:
		if log_level in [logging.DEBUG,logging.INFO]:
			logging.exception('parsing error on line %d: %s' % (e.lineno,e.message))
		else:
			logging.error('parsing error on line %d: %s' % (e.lineno,e.message))

		sys.exit(-1)
	except Exception as e:
		if log_level in [logging.DEBUG,logging.INFO]:
			logging.exception('command %s failed' % args.command)
		else:
			logging.error('command %s failed: %s' % (args.command,e.message))

		sys.exit(-1)

	sys.exit(0)
	return

if __name__ == '__main__':
	main()

import sys
import os
import os.path
import json
import argparse
import hashlib
import time
import multiprocessing
from itertools import groupby
from importlib import import_module
from multiprocessing import Pool

from q.containers.q_exec.launch_sfm_module import modules, load_module, load_class

modules_list = dict([
    ('raw2json', 'raw2json_pipeline'),
    ('raw2exrdistorted', 'raw2exrdistorted_pipeline'),
    ('exrdistorted2undistorted', 'exrdistorted2undistorted_pipeline'),
    ('exrdistorted2thumb', 'exrdistorted2thumb_pipeline'),
    ('undistorted2features', 'undistorted2features_pipeline'),
    ('undistorted2tile', 'undistorted2tile_pipeline'),
    ('matcher', 'matcher_pipeline'),
    ('solver', 'sparse_solver_pipeline'),
])

# processes a single message
class LocalMessageProcessor:

    get_handler = staticmethod(lambda module_key: load_class(load_module(modules[module_key]), modules[module_key])())

    def __init__(self, module):
        self.module = module
        self.handler = LocalMessageProcessor.get_handler(self.module)
        
    def _process_message(self, message):
        print('[start processing message ...][msg=%s]' % message)
        handler = LocalMessageProcessor.get_handler(self.module)
        results = handler.initializeAndExecute(message)
        #self.handler.close()
        print('[finished processing message ...][msg=%s]' % message)
        return results

    # returns dictionary of {destination_type -> [messages]}
    @staticmethod
    def _groupby_destination(results):
        results = list(filter(lambda r: r[0] == 0, results))
        results = sum([r[1] for r in results], [])
        results = sorted(results, key=lambda result: result['destination'])
        return dict([
            (dst, list(messages))
            for dst, messages in groupby(results, lambda result: result['destination'])
        ])    

    @staticmethod
    def process_messages(args):

        def load_messages(message_file):        
            with open(message_file, 'r') as inp:
                return [json.loads(line.rstrip()) for line in inp.readlines()]

        def store_messages(msgs, message_file):        
            with open(message_file, 'w') as out:
                for m in msgs:
                    out.write(json.dumps(m) + '\n')

        # process messages
        message_processor = LocalMessageProcessor(args.module)
        results = list(Pool(args.num_instances).map(
            message_processor._process_message, load_messages(args.input_messages_file)
        ))
        results = LocalMessageProcessor._groupby_destination(results)

        # store messages for each dst in separate file
        for dst, messages in results.items():
            store_messages(list(messages), os.path.join(args.output_messages_dir, '%s_input.json' % dst))
    
if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='launch sfm local')
    parser.add_argument('--module', help='module name', required=True)    
    parser.add_argument('--input_messages_file', help='json input message file', required=True)    
    parser.add_argument('--output_messages_dir', help='json output message dir', required=True)    
    parser.add_argument('--num_instances', help='num instances', type=int, default=10, required=False) 
    args = parser.parse_args()
    
    LocalMessageProcessor.process_messages(args)

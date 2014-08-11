#!/usr/bin/env python
'''
Boss - app printing random stuff and randomly freaks out.

Disclaimer: this application has noting to do with my previous or current bosses. All 
similarities are coincidental.
  

Application purpose is to test ontimer scheduler 
and exhibit random behavior.

Credit due to Corporate BS generator: http://www.atrixnet.com/bs-generator.html
I took arrays of adverbs, verbs, adjectives, nouns from there. I could not find 
any copyright or terms of use on page. I guess it is ok, but if it is not, please  
don't sue me just let me know. 

'''
from __future__ import print_function

import argparse
import sys
from random import randrange
from time import sleep

adverbs =  (
'appropriately', 'assertively', 'authoritatively', 'collaboratively', 'compellingly', 'competently', 'completely',
'continually', 'conveniently', 'credibly', 'distinctively', 'dramatically', 'dynamically', 'efficiently',
'energistically', 'enthusiastically', 'globally', 'holisticly', 'interactively', 'intrinsicly', 'monotonectally',
'objectively', 'phosfluorescently', 'proactively', 'professionally', 'progressively', 'quickly', 'rapidiously',
'seamlessly', 'synergistically', 'uniquely', 'fungibly'
)

verbs = (
'actualize', 'administrate', 'aggregate', 'architect', 'benchmark', 'brand', 'build', 'communicate', 'conceptualize',
'coordinate', 'create', 'cultivate', 'customize', 'deliver', 'deploy', 'develop', 'disintermediate', 'disseminate',
'drive', 'embrace', 'e-enable', 'empower', 'enable', 'engage', 'engineer', 'enhance', 'envisioneer', 'evisculate',
'evolve', 'expedite', 'exploit', 'extend', 'fabricate', 'facilitate', 'fashion', 'formulate', 'foster', 'generate',
'grow', 'harness', 'impact', 'implement', 'incentivize', 'incubate', 'initiate', 'innovate', 'integrate', 'iterate',
'leverage existing', 'leverage other\'s', 'maintain', 'matrix', 'maximize', 'mesh', 'monetize', 'morph', 'myocardinate',
'negotiate', 'network', 'optimize', 'orchestrate', 'parallel task', 'plagiarize', 'pontificate', 'predominate',
'procrastinate', 'productivate', 'productize', 'promote', 'provide access to', 'pursue', 'recaptiualize',
'reconceptualize', 'redefine', 're-engineer', 'reintermediate', 'reinvent', 'repurpose', 'restore', 'revolutionize',
'scale', 'seize', 'simplify', 'strategize', 'streamline', 'supply', 'syndicate', 'synergize', 'synthesize', 'target',
'transform', 'transition', 'underwhelm', 'unleash', 'utilize', 'visualize', 'whiteboard', 'cloudify'
)

adjectives =  (
'24/7', '24/365', 'accurate', 'adaptive', 'alternative', 'an expanded array of', 'B2B', 'B2C', 'backend',
'backward-compatible', 'best-of-breed', 'bleeding-edge', 'bricks-and-clicks', 'business', 'clicks-and-mortar',
'client-based', 'client-centered', 'client-centric', 'client-focused', 'collaborative', 'compelling',  'competitive',
'cooperative', 'corporate', 'cost effective', 'covalent', 'cross functional', 'cross-media', 'cross-platform',
'cross-unit', 'customer directed', 'customized', 'cutting-edge', 'distinctive', 'distributed', 'diverse', 'dynamic',
'e-business', 'economically sound', 'effective', 'efficient', 'emerging', 'empowered', 'enabled', 'end-to-end',
'enterprise', 'enterprise-wide', 'equity invested', 'error-free', 'ethical', 'excellent', 'exceptional', 'extensible',
'extensive', 'flexible', 'focused', 'frictionless', 'front-end', 'fully researched', 'fully tested', 'functional',
'functionalized', 'future-proof', 'global', 'go forward', 'goal-oriented', 'granular', 'high standards in',
'high-payoff', 'high-quality', 'highly efficient', 'holistic', 'impactful', 'inexpensive', 'innovative',
'installed base', 'integrated', 'interactive', 'interdependent', 'intermandated', 'interoperable', 'intuitive',
'just in time', 'leading-edge', 'leveraged', 'long-term high-impact', 'low-risk high-yield', 'magnetic',
'maintainable', 'market positioning', 'market-driven', 'mission-critical', 'multidisciplinary', 'multifunctional',
'multimedia based', 'next-generation', 'one-to-one', 'open-source', 'optimal', 'orthogonal', 'out-of-the-box',
'pandemic', 'parallel', 'performance based', 'plug-and-play', 'premier', 'premium', 'principle-centered', 'proactive',
'process-centric', 'professional', 'progressive', 'prospective', 'quality', 'real-time', 'reliable', 'resource sucking',
'resource maximizing', 'resource-leveling', 'revolutionary', 'robust', 'scalable', 'seamless', 'stand-alone',
'standardized', 'standards compliant', 'state of the art', 'sticky', 'strategic', 'superior', 'sustainable',
'synergistic', 'tactical', 'team building', 'team driven', 'technically sound', 'timely', 'top-line', 'transparent',
'turnkey', 'ubiquitous', 'unique', 'user-centric', 'user friendly', 'value-added', 'vertical', 'viral', 'virtual',
'visionary', 'web-enabled', 'wireless', 'world-class', 'worldwide', 'fungible', 'cloud-ready'
)

nouns =  (
'action items', 'alignments', 'applications', 'architectures', 'bandwidth', 'benefits',
'best practices', 'catalysts for change', 'channels', 'collaboration and idea-sharing', 'communities', 'content',
'convergence', 'core competencies', 'customer service', 'data', 'deliverables', 'e-business', 'e-commerce', 'e-markets',
'e-tailers', 'e-services', 'experiences', 'expertise', 'functionalities', 'growth strategies', 'human capital',
'ideas', 'imperatives', 'infomediaries', 'information', 'infrastructures', 'initiatives', 'innovation',
'intellectual capital', 'interfaces', 'internal or "organic" sources', 'leadership', 'leadership skills',
'manufactured products', 'markets', 'materials', 'meta-services', 'methodologies', 'methods of empowerment', 'metrics',
'mindshare', 'models', 'networks', 'niches', 'niche markets', 'opportunities', '"outside the box" thinking', 'outsourcing',
'paradigms', 'partnerships', 'platforms', 'portals', 'potentialities', 'process improvements', 'processes', 'products',
'quality vectors', 'relationships', 'resources', 'results', 'ROI', 'scenarios', 'schemas', 'services', 'solutions',
'sources', 'strategic theme areas', 'supply chains', 'synergy', 'systems', 'technologies', 'technology',
'testing procedures', 'total linkage', 'users', 'value', 'vortals', 'web-readiness', 'web services', 'fungibility', 'clouds', 'nosql', 'storage'
)

phrase = [adverbs, verbs, adjectives, nouns ]

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)
    
def main():
        
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freakout", type=float, default=.25, help='freak out probability.')
    parser.add_argument("--errvsout", type=float, default=.33, help='probability whether  boss speaks into stderr or in stdout.')
    parser.add_argument("--bs", type=int, default=5, help='how much BS boss will say')
    parser.add_argument("--delay", type=float, default=1., help='what average time delay between phrases .')
    args = parser.parse_args()
    
    for i in range(args.bs):
        sleep(args.delay * float(randrange(100)) / 50. )
        wordlist = [ m[randrange(len(m))] for m in phrase ]
        if args.errvsout >=  float( randrange(100) )/100.0:
            warning( *wordlist)
        else:
            print( *wordlist)
    
    if args.freakout >=  float( randrange(100) )/100.0:
        rc = randrange(254)+1
        warning('freak out with: %d' % rc)
        raise SystemExit(rc)

if __name__ == '__main__':
    main()    

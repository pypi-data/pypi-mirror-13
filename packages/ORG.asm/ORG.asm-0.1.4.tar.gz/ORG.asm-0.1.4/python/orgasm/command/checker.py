from orgasm import getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
     scaffold, path2fasta

__title__="Check the consistency of the assembling"

default_config = { 
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='<index>', 
                        help='index root filename (produced by the orgasmi command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
        
    parser.add_argument('--back',             dest='orgasm:back', 
                                              metavar='<insert size>',
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')

def readPath(filename):
    
    pathin  = open(filename)
    paths = [[int(y) for y in x.split(" ")] for x in pathin]
    
    return paths


def path2idseq(self,assgraph,path,identifier="contig",minlink=10,nlength=20,back=200,logger=None):
    '''
    Convert a path in an compact assembling graph in a fasta formated sequences.
    
    :param assgraph: The compact assembling graph as produced by the
                     :py:meth:`~orgasm.assembler.Assembler.compactAssembling` method
    :type assgraph:  :py:class:`~orgasm.graph.DiGraphMultiEdge`
    :param path:     an ``iterable`` providing an ordered list of ``stemid`` indicating
                     the path to follow.  
    :type path:      an ``iterable`` over :py:class:`int`
    :param identifier: the identifier used in the header of the fasta formated sequence
    :type identifier:  :py:class:`bytes`
    :param minlink:  the minimum count of pair ended link to consider 
                     for asserting the relationship
    :type minlink:   :py:class:`int`
    :param nlength:  how many ``N`` must be added between two segment of sequences only connected
                     by pair ended links
    :type nlength:   :py:class:`int`
    :param back:     How many base pairs must be considered at the end of each edge
    :type back:      :py:class:`int`
    
    :returns: a string containing the fasta formated sequence
    :rtype: :py:class:`bytes`

    :raises: :py:class:`AssertionError`
    '''
    frglen,frglensd = estimateFragmentLength(self)
    
    alledges = dict((assgraph.getEdgeAttr(*e)['stemid'],e) 
                    for e in assgraph.edgeIterator(edgePredicate = lambda i: 'stemid' in assgraph.getEdgeAttr(*i)))
        
        
    seq=[]
    oldstem=None
    oldid=None
    
    rank = 1
    forceconnection=False

    for stemid in path:
        if stemid != 0:
            stem = alledges[stemid]
            attr = assgraph.getEdgeAttr(*stem)
            
            #print "@@>",stemid,attr['length'],stem,oldstem
    
            if oldstem is not None:
                connected,ml,sl = pairEndedConnected(self,assgraph,oldid,stemid,back)
                if oldstem[1]==stem[0]:
                    
                    if logger is None:
                        print("Both segments %d and %d are connected (paired-end=%d frg length=%f sd=%f)" % (oldid,stemid,connected,ml,sl),
                              file=sys.stderr)
                    else: 
                        logger.info("Both segments %d and %d are connected (paired-end=%d frg length=%f sd=%f)" % (oldid,stemid,connected,ml,sl))

                    label.append('{connection: %d - length: %d, sd: %d}' % (connected,int(ml),int(sl)))
                else:
                    glength = frglen - ml 
                    if logger is None:
                        print("Both segments %d and %d are disconnected" % (oldid,stemid),
                              file=sys.stderr)
                    else: 
                        logger.info("Both segments %d and %d are disconnected" % (oldid,stemid))
                    if connected >= minlink:
                        
                        if logger is None:
                            print("   But linked by %d pair ended links (gap length=%f sd=%f)" % (connected,glength,sl),
                                  file=sys.stderr)
                        else:
                            logger.info("   But linked by %d pair ended links (gap length=%f sd=%f)" % (connected,glength,sl))
                        if glength > 0:
                            seq.extend([0]*int(glength))
                        else:
                            seq.append([0]*self.index.getReadSize())

                    elif forceconnection:
                        if connected > 0:
                            
                            glength = int(frglen-ml) 

                            if logger is None:
                                print("Connection is forced with only %d pair ended links (gap length=%f sd=%f)" % (connected,glength,sl),
                                      file=sys.stderr)
                            else:
                                logger.info("Connection is forced with only %d pair ended links (gap length=%f sd=%f)" % (connected,glength,sl))
                                
                        else:
                            
                            if logger is None:
                                print("Connection is forced without pair ended links" % connected,
                                      file=sys.stderr)
                            else:
                                logger.info("Connection is forced without pair ended links" % connected)
                                
                            glength =  nlength+self.index.getReadSize()
                        
                        seq.extend([0]*glength)

                    else:
                        raise AssertionError('Disconnected path between stem '
                                             '%d and %d only %d pair ended links' % (oldid,stemid,connected))
                        
            rank+=1
    
            seq.extend(attr['path'])
            
            oldstem = stem
            oldid=stemid
            
            forceconnection=False
        else:
            forceconnection=True
        
    s1 = alledges[path[-1]]
    s2 = alledges[path[0]]
    sid1=assgraph.getEdgeAttr(*s1)['stemid']
    sid2=assgraph.getEdgeAttr(*s2)['stemid']
    connected,ml,sl = pairEndedConnected(self,assgraph,sid1,sid2,back)
    
    if s1[1]==s2[0]:
        
        if logger is None:
            print("Path is circular",file=sys.stderr)
        else:
            logger.info("Path is circular")
            
        circular=True
    else:
        if connected >= minlink:
            if logger is None:
                print("Path is circular but disconnected" ,file=sys.stderr)
                print("Linked by %d pair ended links" % connected,file=sys.stderr)
            else:
                logger.info("Path is circular but disconnected")
                logger.info("Linked by %d pair ended links" % connected)
               
            glength = frglen - ml 
            seq.extend([0]*glength)
            circular=True
        elif forceconnection:
            if logger is None:
                print("Circular connection forced",file=sys.stderr)
                print("Linked by %d pair ended links" % connected,file=sys.stderr)
            else:
                logger.info("Circular connection forced")
                logger.info("Linked by %d pair ended links" % connected)
                
            label.append('{F-connection: %d}' % connected)
            seq.extend([0]*nlength)
            circular=True
        else:
            if logger is None:
                print("Path is linear",file=sys.stderr)
            else:
                logger.info("Path is linear")
            circular=False
        ext = [0]*self.index.getReadSize()
        ext.extend(seq)
        seq=ext

    return seq
 

def run(config):

    logger=config['orgasm']['logger']
    output = config['orgasm']['outputfilename'] 

    r = getIndex(config)
    ecoverage,x = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)

    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300

    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    paths  = readPath(output+".path")

    for path in paths:
        for stemid in path:
            logger.info('stemid : %i' % stemid)
            
            

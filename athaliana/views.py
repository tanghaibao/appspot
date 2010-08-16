from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson as json

from bao.athaliana.models import Syntelog

outgroups = ["lyrata", "papaya", "peach", "grape"]

# Create your views here.
def index(request):
    params = {
            'outgroups': outgroups,
            }
    output = render_to_response('index.html', params)
    return output 


# the core query
def query(request):
    gid = request.GET.get('gid', '').strip()
    if gid:
        if gid.upper().startswith('AT'):
            query = Syntelog.objects.filter(athaliana__iexact=gid)
        else:
            query = Syntelog.objects.filter(description__istartswith=gid)
    else:
        query = Syntelog.objects.all()
        for o in outgroups:
            term = request.GET.get(o, 'A')
            if term=='A': continue
            query = query.filter(**{o+'_code': term})

    query = query.order_by('athaliana')[:10]

    params = {
            'gid': gid,
            'response': query,
            'outgroups': outgroups,
            }
    
    if query.count()==1:
        params.update(single=query[0])

    output = render_to_response('index.html', params)
    return output


# autocomplete for tha athaliana gene id
def autocomplete(request):
    term = request.GET.get('term', '').strip()
    query = Syntelog.objects.filter(athaliana__istartswith=term)\
            .order_by('athaliana')[:5] 
    suggestions = [q.athaliana for q in query]

    return HttpResponse(json.dumps(suggestions))


# plotting
def simple(request):
    gid = request.GET.get('gid', '').strip()
    query = Syntelog.objects.filter(athaliana=gid)
    q = query[0]

    import os
    os.environ['MPLCONFIGDIR'] = '/tmp'
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    #_ = lambda x: r"$\mathsf{%s}$" % (x.replace(" ", r"\ "))
    _ = lambda x: x 
    
    fig = Figure()
    root = fig.add_axes([0,0,1,1], axisbg='beige')

    # data
    species = ["athaliana"] + outgroups
    genes = [getattr(q, x) for x in species]
    codes = [getattr(q, x+'_code') for x in species[1:]]
    
    # plot params
    lw = 5
    ms = 12
    size = 15

    # taxa labels
    ytop = .9
    yinterval = .075
    nodes = []
    for s, g, code in zip(species, genes, ['S'] + codes):
        c = 'k' if code=='S' else 'lightgrey'
        root.text(.8, ytop, _(g), ha='center', color=c, size=size)
        root.text(.8, ytop-.01, _(s), ha='center', va='top', color=c, size=size,
                fontstyle='italic')
        nodes.append((.7, ytop))
        ytop -= 2 * yinterval
    
    # tree
    xstart = .7
    xinterval = .6 / 5
    labels = (("rosids", 108),
              ("rosid I+II", 104),
              ("Brassicales", 68),
              ("Arabidopsis", 5)
    )
    ytop = .9
        
    # scales
    xstart = .1
    xx = []
    for label, div in labels:
        xstart += xinterval
        xx.append(xstart)
        root.text(xstart, .2, _("%s (%dmya)" % (label, div)), color="g", 
                    rotation=20, ha='right', va='top', size=size)
    root.plot((.1,.7), (.2,.2), ':', color='gray', lw=lw)
    root.plot(xx, [.2] * len(xx), "go", mec="g", mfc="w", mew=lw, ms=ms)
            
    def draw_branches(n1, n2, height, c1='k', c2='grey', label=''):
        x1, y1 = n1
        x2, y2 = n2
        half_y = .5 * (y1 + y2)
        cnode = (height, half_y)
        root.plot((x1, height), (y1, y1), '-', color=c1, lw=lw)
        root.plot((x2, height), (y2, y2), '-', color=c2, lw=lw)       
        root.plot((height, height), (y1, half_y), '-', color=c1, lw=lw)
        root.plot((height, height), (y2, half_y), '-', color=c2, lw=lw)
        # the synteny code on the corner of branches
        root.text(height+.01, y2+.01, _(label), color=c2, size=size)
        return cnode
    
    # draw the tree branches recursively
    node = nodes[0]
    internal_nodes = []
    for i, (x, code) in enumerate(reversed(zip(xx, codes))):
        c = 'k' if code=='S' else 'lightgrey'
        node = draw_branches(node, nodes[i+1], x, c2=c, label=code)
        internal_nodes.append(node)
        
    # common ancestral branch
    x, y = node
    root.plot((.1, x), (y, y), 'k-', lw=lw)
    x, y = zip(*internal_nodes)
    root.plot(x, y, 'o', mfc='w', mec='k', mew=lw, ms=ms)
    
    # legends
    root.text(.5, .95, _("Positional history for gene %s" % q.athaliana), 
            ha="center", va="center", size=size)
    root.set_xlim((0,1))
    root.set_ylim((0,1))
    root.set_axis_off()
    
    # print out
    canvas = FigureCanvas(fig)
    response=HttpResponse(content_type='image/png')
    canvas.print_figure(response, format="png", dpi=80)

    return response


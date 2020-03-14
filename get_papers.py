import urllib.request
import json

memory = {}
papers = {}
refs = []

def GetReferences(semantic_id, arxiv, depth, top_n=10):
    if semantic_id in memory:
        data = memory[semantic_id]
    else:
        link = 'http://api.semanticscholar.org/v1/paper/{}'.format('arXiv:' + semantic_id if arxiv else semantic_id)

        with urllib.request.urlopen(link) as paper:
            data = json.loads(paper.read().decode())
        memory[data['paperId']] = data

    papers[data['paperId']] = {'title': data['title'],
                               'references': [{'paperId': reference['paperId'], 'title': reference['title']} for reference in data['references']] if depth > 2 else [],
                               'citations': len(data['citations'])}

    # Problem to fix. After going one layer down, you want to prune articles that don't fit the top_n. This will lead to top_n^depth time
    # Right now, we have ~avg_n^depth time, as we exhaustively search through every reference's reference.
    # Every depth%2==0 (Even), prune references not appearing above. Would have to be breadth wise

    if depth > 2:
        citations = {}
        for reference in papers[data['paperId']]['references']:
            citations[reference['paperId']] = GetCitations(reference['paperId'])

        citations = sorted(citations, key=lambda x: x[1], reverse=True)
        if top_n != -1:
            citations = citations[:top_n]

        papers[data['paperId']]['references'] = [reference for reference in papers[data['paperId']]['references'] if reference['paperId'] in citations]

        for reference in papers[data['paperId']]['references']:
            GetReferences(reference['paperId'], False, depth-1, top_n)
            reference['citations'] = papers[reference['paperId']]['citations']

   
def GetCitations(reference_id):
    if reference_id in memory:
        data = memory[reference_id]
    else:
        link = 'http://api.semanticscholar.org/v1/paper/{}'.format(reference_id)

        with urllib.request.urlopen(link) as paper:
            data = json.loads(paper.read().decode())
        memory[reference_id] = data

    return len(data['citations'])

def CleanTree(root): # Assuming that this works. Can not fully test, as depth 4 is too large as of yet
    for ref in papers[root]['references']:
        refs.append(ref['paperId'])
        CleanTree(ref['paperId'])

def MakeJson(paper_id="2001.09977"):
    global papers
    papers = {}
    global refs
    refs = []

    GetReferences(paper_id, True, 4, 4)
    root = next(iter(papers))

    CleanTree(root) # First element
    papers = dict(filter(lambda x: x[0] in refs or x[0] == root, papers.items()))

    output = {}
    output['nodes'] = [{'name': papers[id_]['title'], 'group': papers[id_]['citations']} for id_ in papers.keys()]
    output['links'] = [{'source': sum([i if output['nodes'][i]['name'] == papers[id_]['title'] else 0 for i in range(len(output['nodes']))]), 'target': sum([i if output['nodes'][i]['name'] == ref['title'] else 0 for i in range(len(output['nodes']))])} for id_ in papers.keys() for ref in papers[id_]['references']]

    with open('jsonfiles/graph.json', 'w') as f:
        json.dump(output, f)

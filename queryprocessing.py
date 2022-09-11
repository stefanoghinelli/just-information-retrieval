import os

from whoosh.qparser import MultifieldParser, OrGroup
from whoosh import scoring
from whoosh import index

OPENB_INDEX_PATH = os.path.curdir + os.path.sep + "preprocessing/indexdir/open-textbooks"
SPR_INDEX_PATH = os.path.curdir + os.path.sep + "preprocessing/indexdir/springer"


QUERY_NATURAL_PATH = os.path.curdir + os.path.sep + "query_natual_lang.txt"
QUERY_BENCH_PATH = os.path.curdir + os.path.sep + "query_benchmark.txt"


def submit_query(user_query, idx_path):
    ix = index.open_dir(idx_path)
    qp = MultifieldParser(["title",
                           "content"],  # all selected fields
                          schema=ix.schema,  # with my schema
                          group=OrGroup)  # OR instead AND
    user_query = user_query.lower()

    print("This is UNI: " + user_query)
    q = qp.parse(user_query)

    print("This is the parsed query: " + str(q))
    with ix.searcher(weighting=scoring.BM25F(B=0.75, content_B=1.0, K1=1.2)) as searcher:
        corrected = searcher.correct_query(q, user_query)
        if corrected.query != q:
            print("Did you mean:", corrected.string + " ?")
            exit(1)
        results = searcher.search(q)
        ret = []

        print(str(len(results)) + " results\n")
        for r in results:
            print(r.rank, ".", r["title"], " (Score: ", r.score, ")", )
            ret.append({"title": r["title"], 'score': r.score})

        print("\nRun time: " + "{:.5f}".format(results.runtime) + " s")
        return ret


def search_something(usr_query):

    # uni = input("Inserisci la query: ")

    # print("\nSubmitted OPB query -------")
    ris_opb = submit_query(usr_query, OPENB_INDEX_PATH)

    # print("\nSubmitted SPR query -------")
    ris_spr = submit_query(usr_query, SPR_INDEX_PATH)

    total_ris = [j for i in [ris_opb, ris_spr] for j in i]
    sorted_ris = sorted(total_ris, key=lambda x: x["score"], reverse=True)

    # print("\nFinal results -------")

    # for w in sorted_ris:
    #   print(w)

    return sorted_ris


def benchmark():
    tot_q = 10
    # ragionarci
    precisions = [1, 0.948, 1, 0.975, 0.218, 1, 1, 1, 1, 1]
    map_val = sum(precisions)/tot_q

    natural_queries = []
    with open(QUERY_NATURAL_PATH, 'r') as f:
        for line in f:
            # print(line, "-----")
            natural_queries.append(line[:-1])

    comp_queries = []
    with open(QUERY_BENCH_PATH, 'r') as f:
        for line in f:
            # print(line, "-----")
            comp_queries.append(line[:-1])

    final_res = []
    for cq in comp_queries:
        x = search_something(cq)[:11]
        final_res.append(x)

    for fs in final_res:
        print(f'{ natural_queries.pop(0) }')
        print(f'Executing query: { comp_queries.pop(0) }')
        print('Results number: ' + str(len(fs)))
        print(f'Average Precision for first 10 results: { precisions.pop(0) } \n\n')
    print(f'\nMean Average Precision: { map_val } \n')


benchmark()

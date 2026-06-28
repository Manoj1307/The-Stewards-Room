import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

retrieve_client= chromadb.PersistentClient("./chromadb")
retrieve_collection= retrieve_client.get_collection(name="the_stewards_room")

model= SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
reranker= CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def Retrieve(ques):
    ques_pairs =[]
    embeddings= model.encode(ques, normalize_embeddings=True)
    embeddings= embeddings.tolist()
    q_ans= retrieve_collection.query(query_embeddings=[embeddings], n_results=25)
    candidates = q_ans["documents"][0]
    ques_pairs = [[ques, chunk] for chunk in candidates]
    scores = reranker.predict(ques_pairs)
    cand_scores = zip(candidates, scores)
    cand_sorted = sorted(cand_scores, key=lambda x: x[1], reverse=True)
    retrieve_cand = cand_sorted[:5]
    return retrieve_cand

if __name__ == "__main__":
    ans= retrieve("What is the minimum amount of compound to be used in a race?")
    print(ans)
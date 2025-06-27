import json
import torch
import uuid
from datetime import datetime
from typing import List, Dict
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# === Load models ===
embedder = SentenceTransformer("all-MiniLM-L6-v2")
nli_pipe = pipeline("text-classification", model="microsoft/deberta-large-mnli")
qa_pipe = pipeline("question-answering", model="deepset/roberta-base-squad2")

# === Load knowledge base ===
with open("knowledge_base.json", "r") as f:
    category_knowledge_base = json.load(f)

# === Category descriptions ===
category_map = {
    "Login Problem": "The user is facing a login problem due to incorrect credentials.",
    "Password Reset Needed": "The user is requesting a password reset.",
    "Subscription Cancellation": "The user wants to cancel their subscription.",
    "Duplicate Charges": "The user is reporting that they have been charged twice.",
    "Refund Request": "The user is requesting a refund.",
    "Bug Report": "The user is reporting a bug in the application.",
    "API Access Request": "The user is requesting access to the platform's API."
}
reverse_map = {v: k for k, v in category_map.items()}

# === Normalize query ===
def normalize_query(query: str) -> str:
    return query if len(query.split()) > 4 else f"The user is facing an issue: {query}"

# === Step 1: SentenceTransformer classification ===
def classify_with_embeddings(query: str, descriptions: List[str]) -> Dict:
    query_emb = embedder.encode(query, convert_to_tensor=True)
    desc_emb = embedder.encode(descriptions, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(query_emb, desc_emb)[0]
    top_idx = int(torch.argmax(cosine_scores))
    return {
        "category": descriptions[top_idx],
        "score": float(cosine_scores[top_idx])
    }

# === Step 2: Refine with NLI ===
def refine_with_nli(query: str, top_descriptions: List[str]) -> Dict:
    results = []
    for desc in top_descriptions:
        out = nli_pipe(f"{query} </s></s> {desc}")[0]
        results.append({
            "category": desc,
            "label": out["label"],
            "score": out["score"]
        })
    entailments = [r for r in results if r["label"] == "ENTAILMENT"]
    best = max(entailments, key=lambda x: x["score"]) if entailments else max(results, key=lambda x: x["score"])
    return best

# === Main classification function ===
def classify_ticket(query: str) -> Dict:
    query = normalize_query(query)
    semantic_best = classify_with_embeddings(query, list(category_map.values()))
    refined = refine_with_nli(query, [semantic_best["category"]])
    category_name = reverse_map.get(refined["category"], "Unknown")
    return {
        "category_name": category_name,
        "semantic_score": semantic_best["score"],
        "nli_score": refined["score"],
        "nli_label": refined["label"],
        "description": refined["category"]
    }

# === Ticket creation ===
def create_ticket(user_query: str, category: str) -> Dict:
    ticket = {
        "ticket_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "query": user_query,
        "status": "open"
    }
    print("\n🎫 Ticket Created!")
    print(json.dumps(ticket, indent=2))

    # Save to file
    with open("tickets.json", "a") as f:
        f.write(json.dumps(ticket) + "\n")

    return ticket

# === Main interaction function ===
def handle_user_query():
    print("🤖 Hello! How can I help you today? (Describe your issue)")
    user_query = input("🧑 You: ")

    result = classify_ticket(user_query)
    category = result["category_name"]
    context = category_knowledge_base.get(category)

    print("\n🎯 Predicted Category:", category)
    print("🧠 Cosine Confidence:", round(result["semantic_score"] * 100, 2), "%")
    print("📐 NLI Confidence:", round(result["nli_score"] * 100, 2), "%")

    if context:
        if len(context.split()) > 50:
            answer = qa_pipe(question=user_query, context=context)
            print("📖 Extracted Answer:", answer["answer"])
        else:
            print("📖 Answer:", context.strip())
        print("📋 Full Category Description:", result["description"])
    else:
        print("ℹ️ Sorry, no info found for this category.")

    # === Ask for feedback ===
    feedback = input("\n❓Was this answer helpful? (yes/no): ").strip().lower()
    if feedback == "no":
        print("🙁 Sorry to hear that. Creating a support ticket...")
        create_ticket(user_query, category)

    print("\n🤖 Would you like to:")
    print("1. Talk to a support agent")
    print("2. Ask another question")
    print("3. Exit")

# === Run the bot ===
if __name__ == "__main__":
    while True:
        handle_user_query()
        choice = input("\n👉 Your choice (1/2/3): ").strip()
        if choice == "3":
            print("👋 Thank you! Have a great day!")
            break
        elif choice != "2":
            print("🔁 Redirecting you to an agent...\n")
            break

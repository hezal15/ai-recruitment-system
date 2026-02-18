from embeddings import compute_similarity
import numpy as np

def compute_skill_score(resume_text, job_skills):
    """
    Compute semantic similarity between resume and each job skill.
    Returns average similarity.
    """
    if not job_skills:
        return 0.0

    similarities = []

    for skill in job_skills:
        sim = compute_similarity(resume_text, skill)
        similarities.append(sim)

    return np.mean(similarities)


def compute_match_score(resume_text, job_description, job_skills=None):

    # 1️⃣ Overall semantic similarity
    semantic_score = compute_similarity(resume_text, job_description)

    # 2️⃣ Semantic skill similarity
    if job_skills:
        skill_score = compute_skill_score(resume_text, job_skills)
    else:
        skill_score = semantic_score

    # 3️⃣ Experience placeholder (can improve later)
    exp_score = semantic_score * 0.8

    # 4️⃣ Final hybrid score
    final_score = (
        0.5 * semantic_score +
        0.4 * skill_score +
        0.1 * exp_score
    )

    return (
        round(final_score * 100, 2),
        round(skill_score * 100, 2),
        round(exp_score * 100, 2)
       )

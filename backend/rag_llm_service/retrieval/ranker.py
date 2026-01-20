def rank_context(context_blocks):
    def score(block):
        score = 0
        if "ABC category: A" in block:
            score += 3
        if "VED category: V" in block:
            score += 3
        if "Cold storage required: Yes" in block:
            score += 1
        return score

    return sorted(context_blocks, key=score, reverse=True)

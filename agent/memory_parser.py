def prepare_historical_context(memory_records):
    """
    Convert Hindsight memory records into a clean context
    for the ResolveIQ AI agent.

    The agent depends primarily on the memory text and does
    not depend on Hindsight's complete raw response structure.
    """

    if not memory_records:
        return []

    historical_context = []

    for memory in memory_records:

        if not isinstance(memory, dict):
            continue

        text = memory.get("text", "")

        if not text:
            continue

        historical_context.append({
            "memory_id": memory.get("id"),
            "text": text,
            "type": memory.get("type", "unknown"),
            "context": memory.get("context", ""),
            "metadata": memory.get("metadata", {}),
            "entities": memory.get("entities", []),
            "mentioned_at": memory.get("mentioned_at")
        })

    return historical_context

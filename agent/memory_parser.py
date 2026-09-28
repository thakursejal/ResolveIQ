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
    
    def format_historical_context(memory_records):
    """
    Format prepared Hindsight memories into readable context
    for the AI agent.
    """

    if not memory_records:
        return "No relevant historical memories were recalled."

    formatted_memories = []

    for index, memory in enumerate(memory_records, start=1):

        text = memory.get("text", "No memory text available.")

        memory_type = memory.get(
            "type",
            "unknown"
        )

        context = memory.get(
            "context",
            ""
        )

        mentioned_at = memory.get(
            "mentioned_at",
            ""
        )

        formatted_memory = (
            f"HISTORICAL CASE {index}\n"
            f"Memory type: {memory_type}\n"
            f"Case details: {text}\n"
        )

        if context:
            formatted_memory += (
                f"Context: {context}\n"
            )

        if mentioned_at:
            formatted_memory += (
                f"Recorded at: {mentioned_at}\n"
            )

        formatted_memories.append(formatted_memory)

    return "\n".join(formatted_memories)

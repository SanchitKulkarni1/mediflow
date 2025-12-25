PRIORITY_RANK = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

def vertex_book_lab(resource: str, priority: str, hospital_state: dict):
    lab = hospital_state["labs"][resource]

    # Case 1: Slot available → book directly
    if lab["available_slots"] > 0:
        lab["available_slots"] -= 1
        lab["queue"].append({
            "priority": priority,
            "status": "BOOKED"
        })
        return {
            "status": "BOOKED",
            "remaining_slots": lab["available_slots"]
        }

    # Case 2: No slots → check for preemption
    # Find lowest-priority booking
    lowest = min(
        lab["queue"],
        key=lambda x: PRIORITY_RANK[x["priority"]],
        default=None
    )

    if lowest and PRIORITY_RANK[priority] > PRIORITY_RANK[lowest["priority"]]:
        # Preempt
        lab["queue"].remove(lowest)
        lab["queue"].append({
            "priority": priority,
            "status": "BOOKED"
        })
        return {
            "status": "PREEMPTED",
            "replaced": lowest["priority"]
        }

    # Case 3: Cannot preempt → queue
    lab["queue"].append({
        "priority": priority,
        "status": "QUEUED"
    })
    return {
        "status": "QUEUED",
        "reason": "Higher or equal priority already occupying slot"
    }

PRIORITY_RANK = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

def vertex_book_lab(resource: str, priority: str, hospital_state: dict):
    lab = hospital_state["labs"][resource]

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

    lowest = min(
        lab["queue"],
        key=lambda x: PRIORITY_RANK[x["priority"]],
        default=None
    )

    if lowest and PRIORITY_RANK[priority] > PRIORITY_RANK[lowest["priority"]]:
        lab["queue"].remove(lowest)
        lab["queue"].append({
            "priority": priority,
            "status": "BOOKED"
        })
        return {
            "status": "PREEMPTED",
            "replaced": lowest["priority"]
        }

    lab["queue"].append({
        "priority": priority,
        "status": "QUEUED"
    })
    return {
        "status": "QUEUED",
        "reason": "Higher or equal priority already occupying slot"
    }


def vertex_execute_plan(plan: dict, hospital_state: dict):
    results = []

    for action in plan["actions"]:
        if action["type"] == "BOOK_LAB":
            results.append(
                vertex_book_lab(
                    resource=action["resource"],
                    priority=plan["priority"],
                    hospital_state=hospital_state
                )
            )

    return results

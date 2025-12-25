# app/executor.py

from audit_log import log_event
import uuid

# -------------------------
# Priority definition
# -------------------------
PRIORITY_RANK = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

# -------------------------
# Core booking logic
# -------------------------
def vertex_book_lab(resource: str, priority: str, hospital_state: dict):
    lab = hospital_state["labs"][resource]

    # -------------------------
    # CASE 1: Slot available
    # -------------------------
    if lab["available_slots"] > 0:
        lab["available_slots"] -= 1

        lab["queue"].append({
            "priority": priority,
            "status": "BOOKED"
        })

        log_event("LAB_BOOKED", {
            "resource": resource,
            "priority": priority,
            "reason": "slot_available"
        })

        return {
            "status": "BOOKED",
            "reason": "slot_available",
            "remaining_slots": lab["available_slots"]
        }

    # -------------------------
    # CASE 2: Preemption candidate (NO execution)
    # -------------------------
    lowest = min(
        lab["queue"],
        key=lambda x: PRIORITY_RANK[x["priority"]],
        default=None
    )

    if lowest and PRIORITY_RANK[priority] > PRIORITY_RANK[lowest["priority"]]:
        request_id = str(uuid.uuid4())

        log_event("PREEMPTION_REQUESTED", {
            "request_id": request_id,
            "resource": resource,
            "incoming_priority": priority,
            "existing_priority": lowest["priority"],
            "reason": "higher_priority_patient_requires_resource"
        })

        return {
            "status": "PREEMPTION_REQUIRES_APPROVAL",
            "request_id": request_id,
            "resource": resource,
            "incoming_priority": priority,
            "existing_priority": lowest["priority"],
            "explainability": (
                "A higher-priority patient requires this resource. "
                "Doctor approval is required to reassign."
            )
        }

    # -------------------------
    # CASE 3: No preemption → queue
    # -------------------------
    lab["queue"].append({
        "priority": priority,
        "status": "QUEUED"
    })

    log_event("LAB_QUEUED", {
        "resource": resource,
        "priority": priority,
        "reason": "no_slots_and_no_lower_priority_case"
    })

    return {
        "status": "QUEUED",
        "reason": "no_slots_and_no_lower_priority_case"
    }


# -------------------------
# Doctor approval execution
# -------------------------
def approve_preemption(request_id: str, resource: str, incoming_priority: str, hospital_state: dict):
    lab = hospital_state["labs"][resource]

    lowest = min(
        lab["queue"],
        key=lambda x: PRIORITY_RANK[x["priority"]],
        default=None
    )

    if not lowest:
        log_event("PREEMPTION_FAILED", {
            "request_id": request_id,
            "resource": resource,
            "reason": "no_existing_booking"
        })
        return {
            "status": "FAILED",
            "reason": "no_existing_booking"
        }

    lab["queue"].remove(lowest)
    lab["queue"].append({
        "priority": incoming_priority,
        "status": "BOOKED"
    })

    log_event("PREEMPTION_APPROVED", {
        "request_id": request_id,
        "resource": resource,
        "incoming_priority": incoming_priority,
        "preempted_priority": lowest["priority"],
        "approved_by": "doctor"
    })

    return {
        "status": "PREEMPTED",
        "preempted_priority": lowest["priority"]
    }


# -------------------------
# Plan execution dispatcher
# -------------------------
def vertex_execute_plan(plan: dict, hospital_state: dict):
    results = []

    for action in plan.get("actions", []):
        if action["type"] == "BOOK_LAB":
            result = vertex_book_lab(
                resource=action["resource"],
                priority=plan["priority"],
                hospital_state=hospital_state
            )
            results.append(result)

    return results

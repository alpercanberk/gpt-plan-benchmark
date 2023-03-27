import pdb 

def parse_initial_conditions(initial_conditions_list):
    initial_conditions = []
    objects = set()

    for condition in initial_conditions_list:
        if condition.startswith("(:objects"):
            obj_str = condition.replace("(:objects", "").replace(")", "").strip()
            for obj in obj_str.split():
                objects.add(obj)
        elif condition.startswith("(") and condition.endswith(")"):
            initial_conditions.append(condition)

    return initial_conditions, objects


def evaluate_plan(initial_conditions_list, plan):
    initial_conditions, objects = parse_initial_conditions(initial_conditions_list)
    state = set(initial_conditions)

    for action in plan:
        action = action.replace("(", "").replace(")", "")
        action_parts = action.split()
        action_name = action_parts[0]
        action_obj1 = action_parts[1]
        action_obj2 = None

        if len(action_parts) > 2:
            action_obj2 = action_parts[2]

        if action_name == "unstack":
            if f"(handempty)" not in state or f"(on {action_obj1} {action_obj2})" not in state or f"(clear {action_obj1})" not in state:
                
                reason_1, explanation1 = f"(handempty)" not in state, "hand is not empty"
                reason_2, explanation2 = f"(on {action_obj1} {action_obj2})" not in state, f"object {action_obj1} is not on top of {action_obj2}"
                reason_3, explanation3 = f"(clear {action_obj1})" not in state, f"object {action_obj1} is not clear"
            
                out = f"Invalid action: {action} because"
                for reason, explanation in [(reason_1, explanation1), (reason_2, explanation2), (reason_3, explanation3)]:
                    if reason:
                        out += f" {explanation},"
                return False, out

            state.remove(f"(handempty)")
            state.add(f"(holding {action_obj1})")
            state.add(f"(clear {action_obj2})")
            state.remove(f"(on {action_obj1} {action_obj2})")
            state.remove(f"(clear {action_obj1})")
    
        elif action_name == "pick-up":
            if f"(handempty)" not in state or f"(ontable {action_obj1})" not in state or f"(clear {action_obj1})" not in state:
                reason_1, explanation1 = f"(handempty)" not in state, "hand is not empty"
                reason_2, explanation2 = f"(ontable {action_obj1})" not in state, f"object {action_obj1} is not on the table"
                reason_3, explanation3 = f"(clear {action_obj1})" not in state, f"object {action_obj1} is not clear"
                
                out = f"Invalid action: {action} because"
                for reason, explanation in [(reason_1, explanation1), (reason_2, explanation2), (reason_3, explanation3)]:
                    if reason:
                        out += f" {explanation},"
                return False, out
            
            state.remove(f"(handempty)")
            state.add(f"(holding {action_obj1})")
            state.remove(f"(ontable {action_obj1})")
            state.remove(f"(clear {action_obj1})")
        
        elif action_name == "put-down":
            if f"(holding {action_obj1})" not in state:
                reason_1, explanation1 = f"(holding {action_obj1})" not in state, f"object {action_obj1} is not in hand"

                out = f"Invalid action: {action} because"
                for reason, explanation in [(reason_1, explanation1)]:
                    if reason:
                        out += f" {explanation},"
                return False, out
            
            state.remove(f"(holding {action_obj1})")
            state.add(f"(handempty)")
            state.add(f"(ontable {action_obj1})")
            state.add(f"(clear {action_obj1})")
        
        elif action_name == "stack":
            if f"(holding {action_obj1})" not in state or f"(clear {action_obj2})" not in state:
                reason_1, explanation1 = f"(holding {action_obj1})" not in state, f"object {action_obj1} is not in hand"
                reason_2, explanation2 = f"(clear {action_obj2})" not in state, f"object {action_obj2} is not clear"
                
                out = f"Invalid action: {action} because"
                for reason, explanation in [(reason_1, explanation1), (reason_2, explanation2)]:
                    if reason:
                        out += f" {explanation},"
                return False, out
            
            state.remove(f"(holding {action_obj1})")
            state.add(f"(handempty)")
            state.remove(f"(clear {action_obj2})")
            state.add(f"(on {action_obj1} {action_obj2})")
            state.add(f"(clear {action_obj1})")

    return True, "All actions are valid."

if __name__ == "__main__":
    # initial_conditions_list = [
    # "(:objects a b c)",
    # "(:init",
    # "(handempty)",
    # "(ontable a)",
    # "(on b a)",
    # "(on c b)",
    # "(clear c)"
    # ]

    # plan = [
    # "(unstack c b)",
    # "(put-down c)",
    # "(pick-up a)",
    # "(stack a b)",
    # "(pick-up c)",
    # "(stack c a)"
    # ]

    # result = evaluate_plan(initial_conditions_list, plan)
    # print(result)

    initial_conditions1 = [
        "(:objects a b c)",
        "(:init",
        "(handempty)",
        "(ontable a)",
        "(ontable b)",
        "(ontable c)",
        "(clear a)",
        "(clear b)",
        "(clear c)",
        ")"
    ]

    plan1 = [
        "(pick-up a)",
        "(stack a b)",
        "(unstack a b)",
        "(put-down a)"
    ]

    assert evaluate_plan(initial_conditions1, plan1) == "All actions are valid."

    initial_conditions2 = [
        "(:objects a b c d)",
        "(:init",
        "(handempty)",
        "(ontable a)",
        "(ontable b)",
        "(ontable c)",
        "(on d a)",
        "(clear d)",
        "(clear b)",
        "(clear c)",
        ")"
    ]

    plan2 = [
        "(unstack d a)",
        "(stack d b)",
        "(unstack d a)",
        "(stack d a)"
    ]
 
    assert "Invalid action: unstack d a" in evaluate_plan(initial_conditions2, plan2)


    initial_conditions3 = [
    "(:objects a b)",
    "(:init",
    "(handempty)",
    "(ontable a)",
    "(ontable b)",
    "(on a b)",
    "(clear a)",
    ")"
    ]

    plan3 = [
        "(pick-up b)"
    ]

    assert "Invalid action: pick-up b" in evaluate_plan(initial_conditions3, plan3)

        

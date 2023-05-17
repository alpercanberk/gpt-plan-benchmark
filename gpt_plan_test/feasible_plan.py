import pdb 

def get_initial_conditions_and_objects(problem_file, config):
    parsed_init_conditions = []
    with open(problem_file, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('(:objects'):
                for j in range(i, len(lines)):
                    if lines[j].startswith('(:goal'):
                        break
                    
                    #split by spaces
                    chunked_line = lines[j].split(' ')
                    #iterate over chunks
                    #if the first element is a letter and the length of the string is at most 2, then it is an object
                    for k, chunk in enumerate(chunked_line):
                        if chunk[0].isalpha() and (len(chunk) <= 1 or chunk[1] == ')'):
                            #replace the chunk with the corresponding object
                            chunked_line[k] = config['encoded_objects'][chunk[0]].split(' ')[0] + chunk[1:]
                    #join the chunks back together
                    lines[j] = ' '.join(chunked_line)
                    parsed_init_conditions.append(lines[j])
    
        parsed_init_conditions = [line.strip() for line in parsed_init_conditions]
        parsed_init_conditions = [line for line in parsed_init_conditions if line != '']

    """
    This results in something in the form
    '(:objects red blue yellow )', '(:init', '(handempty)', '(on red blue)', '(on blue yellow)', '(ontable yellow)', '(clear red)', ')'
    """
    initial_conditions = []
    objects = set()

    for condition in parsed_init_conditions:
        if condition.startswith("(:objects"):
            obj_str = condition.replace("(:objects", "").replace(")", "").strip()
            for obj in obj_str.split():
                objects.add(obj)
        elif condition.startswith("(") and condition.endswith(")"):
            initial_conditions.append(condition)

    return initial_conditions, objects    

def evaluate_plan(plan, problem_file, config):
    initial_conditions, objects = get_initial_conditions_and_objects(problem_file, config)
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

        else:
            raise Exception(f"Action {action_name} is not supported")

    return True, "All actions are valid."

if __name__ == "__main__":
    initial_conditions_list = [
    "(:objects a b c)",
    "(:init",
    "(handempty)",
    "(ontable a)",
    "(on b a)",
    "(on c b)",
    "(clear c)"
    ]

    plan = [
    "(unstack c b)",
    "(put-down c)",
    "(pick-up a)",
    "(stack a b)",
    "(pick-up c)",
    "(stack c a)"
    ]

    result = evaluate_plan(initial_conditions_list, plan)
    print(result)

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

        

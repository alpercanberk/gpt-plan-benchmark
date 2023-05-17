import random
import re
import pdb

"""
PLANS COME IN THE FORM
   plan = [
    "(unstack c b)",
    "(put-down c)",
    "(pick-up a)",
    "(stack a b)",
    "(pick-up c)",
    "(stack c a)"
    ]
"""

def add_random_action(plan, n=1, len_plan=10):
    """
    gets a random action and then adds it to a random index in the plan
    """
    
    for i in range(n):
        random_action = get_random_action(plan)
        random_index = random.randint(0, len(plan))
        plan.insert(random_index, random_action)

    return plan

def get_random_action(plan=None, objects=None, possible_actions = ['unstack', 'put-down', 'pick-up', 'stack']):

    if objects is None:
        assert plan is not None
        objects = []
        for line in plan:
            #get rid of the parentheses
            line = line[1:-1]
            #split the line into words
            words = line.split()
            #take the last two words
            objects.append(words[1])
            if len(words) > 2:
                objects.append(words[2])

    objects = ['a', 'b', 'c']

    random_action = random.choice(possible_actions)
    #sample 2 random objects
    try:
        random_objects = random.sample(objects, 2)
    except ValueError:
        print("Not enough objects to sample from")
        random_objects = random.sample(objects, 1)

    #create the action
    # new_action = '(' + random_action + ' ' + random_objects[0] + ' ' + random_objects[1] + ')'
    if random_action == 'unstack' or random_action == 'stack':
        new_action = '(' + random_action + ' ' + random_objects[0] + ' ' + random_objects[1] + ')'
    else:
        new_action = '(' + random_action + ' ' + random_objects[0] + ')'

    return new_action



def repeat_random_step(plan, n=1):
    """
    Randomly choose a step in the plan and repeat it at the same position.
    """
    # Choose a random step in the plan
    random_step = random.choice(plan)
    # Repeat the random step at the position of the original step, n times
    for i in range(n):
        plan.insert(plan.index(random_step), random_step)
    return plan

def extend_plan(plan, n=1):
    """
    Randomly choose a step in the plan and repeat it at the end of the plan
    """
    # Choose a random step in the plan
    random_step = random.choice(plan)
    # Repeat the random step at the end of the plan, n times
    for i in range(n):
        plan.append(random_step)
    return plan

def remove_random_step(plan, n=1, len_plan=10):
    """
    Randomly choose a step in the plan and remove it from the plan
    """
    # Return an empty array if n is greater than the length of the plan
    if n > len(plan):
        return []
    # Choose a random step in the plan
    # Remove the random st
    # ep from the plan, n times
    for i in range(n):
        random_step = random.choice(plan)
        plan.remove(random_step)

    return plan

#opposite of pick-up and put-down, opposite of stack is unstack
def opposite(action):
    """
    Return the opposite action of the given action
    """
    if action.startswith("(pick-up"):
        return action.replace("pick-up", "put-down")
    elif action.startswith("(put-down"):
        return action.replace("put-down", "pick-up")
    elif action.startswith("(stack"):
        return action.replace("stack", "unstack")
    elif action.startswith("(unstack"):
        return action.replace("unstack", "stack")
    else:
        raise ValueError("Invalid action")

def cycle_once(plan, idx=-1):
    """
    Randomly choose a step, perform it's opposite and the step again
    """
    # Choose a random step in the plan
    if idx == -1:
        random_step = random.choice(plan)
    else:
        random_step = plan[idx]
    random_step_idx = plan.index(random_step)
    # Perform the opposite of the random step
    plan.insert(random_step_idx + 1, opposite(random_step))
    # Perform the random step again
    plan.insert(random_step_idx + 2, random_step)
    return plan

def cycle(plan, n=1):
    """
    Randomly choose a step, and cycle on that index n times
    """
    # Choose a random step in the plan
    random_step = random.choice(plan)
    random_step_idx = plan.index(random_step)
    # Cycle on the random step n times
    for i in range(n):
        cycle_once(plan, random_step_idx)
    return plan

def replace_step(plan, idx=-1):
    """
    Randomly choose a step, and replace it with a random action
    """
    
    # Choose a random step in the plan
    if idx == -1:
        random_step = random.choice(plan)
    else:
        random_step = plan[idx]
    random_step_idx = plan.index(random_step)
    # Replace the random step with a random action
    plan[random_step_idx] = get_random_action(plan)
    return plan

def replace_steps(plan, n=1):
    new_plan = plan.copy()
    for i in range(n):
        new_plan = replace_step(new_plan)
    return new_plan
    
        
if __name__ == "__main__":
    plan = [
        "(unstack c b)",
        "(put-down c)",
        "(pick-up a)",
        "(stack a b)",
        "(pick-up c)",
        "(stack c a)"
    ]
    # out = add_random_action(plan, 1)
    # print("Augmented Plan", out)
    # for i in range(10):
    #     print(get_random_action(plan))

    print(plan)
    plan = replace_step(plan)
    print(plan)




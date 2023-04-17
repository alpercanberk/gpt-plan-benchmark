def text_plan_to_natural_language(plan, data):
    out = []
    natural_language_plan = plan.split('\n')
    natural_language_plan = [x for x in natural_language_plan if x != '']
    natural_language_plan = [x.replace('(', '').replace(')', '') for x in natural_language_plan]
    
    for idx, step in enumerate(natural_language_plan):
        action, *objs = step.split(' ')
        if len(objs) == 2:
            obj1, obj2 = objs
            obj2 = obj2 + ' block'
            obj1 = obj1 + ' block'
            action_template = data['actions'][action]
            out.append(f"{idx + 1} " + action_template.format(obj1, obj2))
        elif len(objs) == 1:
            obj1 = objs[0]
            obj1 = obj1 + ' block'
            action_template = data['actions'][action]
            out.append(f"{idx + 1} " + action_template.format(obj1))
        else:
            action_template = data['actions'][action]
            out.append(f"{idx + 1} " + action_template)

    #join the elements of out using '\n'
    out =  '\n'.join(out)
    out += '\n[PLAN END]\n'
    out = '\n' + out
    return out
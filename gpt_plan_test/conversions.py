def text_plan_to_natural_language(plan, data):
            out = []
            natural_language_plan = plan.split('\n')
            natural_language_plan = [x for x in natural_language_plan if x != '']
            natural_language_plan = [x.replace('(', '').replace(')', '') for x in natural_language_plan]
            for step in natural_language_plan:
                action, obj1, *obj2 = step.split(' ')
                if obj2:
                    obj2 = obj2[0] + ' block'
                    obj1 = obj1 + ' block'
                    action_template = data['actions'][action]
                    out.append(action_template.format(obj1, obj2))
                else:
                    obj2 = None
                    obj1 = obj1 + ' block'
                    action_template = data['actions'][action]
                    out.append(action_template.format(obj1))

            #join the elements of out using '\n'
            out =  '\n'.join(out)
            out += '\n[PLAN END]'
            return out
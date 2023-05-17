# ========================================== TASKS ========================================== #
def t1_ablations(self, config_file, t1_or_t4="1_reasoning", augmentation=None, augmentation_n=1):
    self.read_config(config_file)

    # ---- Uncomment the below lines to generate problem instances ---- #
    # for f_name in self.data['callbacks']:
    #     callback_obj = Callbacks(self.data)
    #     getattr(callback_obj, f_name)()
    # ---- Uncomment the above lines to generate problem instances ---- #

    domain_name = self.data['domain']
    domain_pddl = f'./instances/{self.data["domain_file"]}'
    instance_folder = f'./instances/{domain_name}/'
    instance = f'./instances/{domain_name}/{self.data["instances_template"]}'
    n_files = min(self.data['n_instances'], len(os.listdir(instance_folder)))

    i_start = self.data['start']
    # i_end = self.data['end']
    i_end = 50
    n_files = i_end - i_start + 1  # min(self.data['n_instances'], len(os.listdir(instance_folder)))
    final_output = ""

    correct_plans = 0
    correct_feasibility = 0

    correct_perplexity = 0
    correct_perplexity_n = 0

    augmentations = {
        'add_random_action': add_random_action,
        'repeat_random_step': repeat_random_step,
        'cycle': cycle,
        'remove_random_step': remove_random_step,
        'extend_plan': extend_plan,
        'replace_steps':replace_steps
    }
    assert augmentation is None or augmentation in augmentations.keys(), f"Augmentation {augmentation} not supported"
    def augment_plan(text_plan, n, augmentation):
        #split text plan by \n
        text_plan = text_plan.split('\n')
        #get rid of the last line
        text_plan = text_plan[:-2]
        #augment text plan
        text_plan = augmentations[augmentation](text_plan, n)
        #join text plan by \n
        text_plan = '\n'.join(text_plan)
        return text_plan


    pbar = tqdm.tqdm(range(i_start, i_end + 2 - self.n_examples))
    for start in pbar:

        correct_success_percent = correct_plans / ((start - i_start) + 1e-6)
        correct_feasibility_percent = correct_feasibility / ((start - i_start) + 1e-6)
        correct_perplexity_percent = correct_perplexity / ((start - i_start) + 1e-6)
        
        pbar.set_description(f"n_examples={self.n_examples}, correct(%): {correct_success_percent:.2f}, "
                                f"correct_feasibility(%): {correct_feasibility_percent:.2f}, "
                                f"correct_perplexity(%): {correct_perplexity_percent:.2f}")

        query = ""
        for i in range(start, start + self.n_examples + 1):
            last_plan = True if i == start + self.n_examples else False
            get_plan = not last_plan
            cur_instance = instance.format(i)
            # --------------- Add to final output --------------- #
            final_output += f"\n Instance {cur_instance}\n"
            if self.verbose:
                print(f"Instance {cur_instance}")

            # --------------- Read Instance --------------- #
            problem = self.get_problem(cur_instance, domain_pddl)
            # --------------------------------------------- #

            # --------------- Read Instance to Python ---------------- #
            init_conditions_list = init_conditions_list_from_file(cur_instance, self.data)
            # --------------------------------------------- #

            # ------------ Put plan and instance into text ------------ #
            gt_plan_string = self.compute_plan(domain_pddl, cur_instance)
            gt_plan_string_with_objects = get_plan_as_text(self.data, len_plan=10)

            if i == start or INTERLEAVE_INSTRUCTIONS or last_plan:
                query += self.data["domain_intro"] 

            negative_example = False 
            if ((i-start) % 2 == 1) and NEGATIVE_EXAMPLE:
                negative_example = True
            query += fill_template(*instance_to_text_blocksworld(problem, get_plan, self.data, len_plan=10, negative_example=negative_example))
            # --------------------------------------------------------- #

        gt_plan_natural_language = text_plan_to_natural_language(gt_plan_string_with_objects, self.data)

        AUG = augmentation
        AUG_N = augmentation_n

        # gpt3_response = send_query(query, self.engine, self.max_gpt_response_length, model=self.model)  
        augmented_gt_plan_string = augment_plan(gt_plan_string, AUG_N, AUG)
        augmented_gt_plan_string_with_objects = get_plan_as_text(self.data, given_plan=augmented_gt_plan_string.split('\n'), len_plan=10)
        try:   
            augmented_gt_plan_natural_language = text_plan_to_natural_language(augmented_gt_plan_string_with_objects, self.data)  
        except Exception as e:
            print(e)
            assert augmentation == 'remove_random_step'
            augmented_gt_plan_natural_language = '\n[PLAN_END]\n' 
        
        gt_perplexity_query = query + gt_plan_natural_language
        gt_augmented_perplexity_query = query + augmented_gt_plan_natural_language

        gt_response_perplexity = perplexity_query(gt_perplexity_query, self.engine, self.max_gpt_response_length, model=self.model)
        gt_augmented_response_perplexity = perplexity_query(gt_augmented_perplexity_query, self.engine, self.max_gpt_response_length, model=self.model)

        # Do text_to_plan procedure
        gpt3_plan_string, gpt3_plan_string_with_objects = text_to_plan_blocksworld(augmented_gt_plan_natural_language, problem.actions, self.gpt3_plan_file, self.data)
        # --------------- Validate feasibility GPT-3's actions ---------------- #
        gpt3_plan_sequence = gpt3_plan_string_with_objects.split('\n') #split by \n
        gpt3_plan_sequence = [x[1:-1] for x in gpt3_plan_sequence if x != ''] #remove empty strings, and remove the parantheses around strings
        correct_f, feasibility_output = evaluate_feasible_plan(init_conditions_list, gpt3_plan_sequence)  #response in the form of a string
        correct_feasibility += correct_f
        # ------------------------------- #

        # --------------- Validate correctness of GPT-3's actions ---------------- #
        correct = int(validate_plan(domain_pddl, cur_instance, self.gpt3_plan_file))
        correct_plans += correct
        # ------------------------------- #
        
        correct_perplexity += gt_response_perplexity < gt_augmented_response_perplexity
        

        experiment_name = f"aug:{AUG}_aug_n:{AUG_N}"
        final_output += '='*5 + f" {experiment_name} " + '='*5 + '\n'
        #add perplexity
        final_output += "Ground Truth Perplexity: " + str(gt_response_perplexity) + '\n'
        final_output += "Augmented Ground Truth Perplexity: " + str(gt_augmented_response_perplexity) + '\n'
        final_output += "Correct Perplexity: " + str(gt_response_perplexity < gt_augmented_response_perplexity) + '\n'
        final_output += "Feasibility: " + feasibility_output + '\n' 
        final_output += f"[n_examples={self.n_examples}, correct: {correct_success_percent:.2f}, " \
                                f"correct_feasibility: {correct_feasibility_percent:.2f}, "\
                                f"correct_perplexity: {correct_perplexity_percent:.2f}]" + '\n'
        final_output += '='*15 + ("SUCCESS" if correct else "FAILURE")  + '='*15

        final_output += verbose_template.format(query, augmented_gt_plan_natural_language, \
                                                gpt3_plan_string_with_objects, gt_plan_string_with_objects, '='*77) if self.verbose else ""
        if self.verbose: print(final_output)

        self.save_output(experiment_name + "_" + t1_or_t4, final_output)
        self.save_output("task" + t1_or_t4, final_output)


    os.remove(self.plan_file)
    os.remove(self.gpt3_plan_file)

    # --------------- Add to final output --------------- #
    final_output += f"[+]: The number of correct plans is {correct_plans}/{n_files}={correct_plans / (n_files) * 100}%"
    print(f"[+]: The number of correct plans is {correct_plans}/{n_files}={correct_plans / (n_files) * 100}%")
    self.save_output("task" + t1_or_t4, final_output)





            ## CREATE AN AUGMENTED PLANS FOR TESTING

            # augmented_responses = []
            # N_AUGMENTED_RESPONSES = 3
            # for _ in range(N_AUGMENTED_RESPONSES):
            #     a = gt_plan
            #     for i in range(20):
            #         a = augment_plan(a, 1, "add_random_action", augmentations=AUGMENTATIONS, first_iteration=(i==0))
            #         a = augment_plan(a, 1, "remove_random_step", augmentations=AUGMENTATIONS, first_iteration=False)
            #         # print(a)
            #         # print("\n")

            #     augmented_gt_plan = a
            #     augmented_gt_plan_with_objects = get_plan_as_text(self.config, given_plan=augmented_gt_plan.split('\n'), len_plan=10)
            #     augmented_responses.append(text_plan_to_natural_language(augmented_gt_plan_with_objects, self.config))

            # pdb.set_trace()
            ########################################
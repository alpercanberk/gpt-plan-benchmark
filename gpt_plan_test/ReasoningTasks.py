import os

import yaml
from Executor import Executor
from utils import *
from pathlib import Path
from tarski.io import PDDLReader
import argparse
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
import tqdm
from feasible_plan import evaluate_plan as evaluate_feasible_plan
from plan_utils.conversions import text_plan_to_natural_language
from plan_utils.plan_augmentations import add_random_action, repeat_random_step, cycle, remove_random_step, extend_plan, replace_steps
from plan_utils.utils import init_conditions_list_from_file
import pandas as pd
import pickle
from typing import List
import time
import numpy as np
 
np.random.seed(42)

INTERLEAVE_INSTRUCTIONS = True
N_EXAMPLES = 2
NEGATIVE_EXAMPLE = False

success_template = "{} {} {} {}"
verbose_template="""
{}
--------- GPT3 response ---------
{}
--------- Extracted plan ---------
{}
-------- Ground truth plan ---------
{}
{}
"""
AUGMENTATIONS = {
            'add_random_action': add_random_action,
            'repeat_random_step': repeat_random_step,
            'cycle': cycle,
            'remove_random_step': remove_random_step,
            'extend_plan': extend_plan,
            'replace_steps':replace_steps
        }

def augment_plan(text_plan, n, augmentation, augmentations, first_iteration=True):
    #split text plan by \n
    text_plan = text_plan.split('\n')
    #get rid of the last line
    if first_iteration:
        text_plan = text_plan[:-2]
    #augment text plan
    text_plan = augmentations[augmentation](text_plan, n)
    #join text plan by \n
    text_plan = '\n'.join(text_plan)
    return text_plan


def extract_plan_begin_idx(sequence_tokens : List[str], plan_start_str : str = "[PLAN]") -> int:
    for i in range(len(sequence_tokens), 0, -1):
        if plan_start_str in "".join(sequence_tokens[i:]):
            return i

class ReasoningTasks():
    """
    Tasks:
    T1. Goal-directed reasoning
    T2. Paraphrasing of goals
    T3. Plan subset completion
    T4. Plan generalization
    T5. Optimality
    T6. Replanning
    T7. Plan execution
    """

    def __init__(self, engine, verbose=False):
        self.engine = engine
        self.verbose = verbose
        self.n_examples = N_EXAMPLES
        self.max_gpt_response_length = 500

        self.plan_file = "sas_plan"
        self.gpt3_plan_file = "gpt_sas_plan"
        if self.engine == 'bloom':
            self.model = self.get_bloom()
        else:
            self.model = None

    # ========================================== UTILS ========================================== #
    def compute_plan(self, domain, instance, timeout=30):
        fast_downward_path = os.getenv("FAST_DOWNWARD")
        # Remove > /dev/null to see the output of fast-downward
        assert os.path.exists(f"{fast_downward_path}/fast-downward.py")
        cmd = f"timeout {timeout}s {fast_downward_path}/fast-downward.py {domain} {instance} --search \"astar(lmcut())\" > /dev/null 2>&1"
        os.system(cmd)

        if not os.path.exists(self.plan_file):
            return ""
        return Path(self.plan_file).read_text()

    def read_config(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_problem(self, instance, domain):
        reader = PDDLReader(raise_on_error=True)
        reader.parse_domain(domain)
        return reader.parse_instance(instance)

    def get_executor(self, instance, domain):
        plan_executor = Executor(domain, instance)
        return plan_executor

    def get_bloom(self):
        max_memory_mapping = {0: "0GB", 1: "43GB", 2: "43GB", 3: "43GB", 4: "43GB", 5: "43GB"}
        tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom")
        model = AutoModelForCausalLM.from_pretrained("bigscience/bloom", cache_dir='/data/karthik/LLM_models/bloom/',
                                                     local_files_only=False, load_in_8bit=True, device_map='auto',
                                                     max_memory=max_memory_mapping)
        return {'model': model, 'tokenizer': tokenizer}

    def save_output(self, output_file, final_output):
        os.makedirs(f"outputs/{self.engine}/", exist_ok=True)
        with open(f"outputs/{self.engine}/" + output_file + ".txt", 'w+') as f:
            f.write(final_output)
    

    # ========================================== TASKS ========================================== #
    def t1_t4(self, config_file, t1_or_t4="1_reasoning"):
        self.read_config(config_file)

        # ---- Uncomment the below lines to generate problem instances ---- #
        # for f_name in self.config['callbacks']:
        #     callback_obj = Callbacks(self.config)
        #     getattr(callback_obj, f_name)()
        # ---- Uncomment the above lines to generate problem instances ---- #

        domain_name = self.config['domain']
        domain_pddl = f'./instances/{self.config["domain_file"]}'
        instance_folder = f'./instances/{domain_name}/'
        instance = f'./instances/{domain_name}/{self.config["instances_template"]}'
        n_files = min(self.config['n_instances'], len(os.listdir(instance_folder)))

        i_start = self.config['start']
        i_end = self.config['end']
        n_files = i_end - i_start + 1  # min(self.config['n_instances'], len(os.listdir(instance_folder)))
        final_output = ""

        correct_plans = 0
        correct_feasibility = 0
        correct_perplexity = 0

        gpt3_infos = []
        gt_infos = []
        aug_infos = []

        ### CREATE THE PROMPT ###
        EXAMPLES_SEED = 42
        #crate numpy state with seed
        g = np.random.RandomState(EXAMPLES_SEED)
        example_tasks_idx = g.choice(np.arange(self.config['start'], self.config['end']), 
                                                        size=self.n_examples, 
                                                        replace=False)  
        real_tasks_idx = np.setdiff1d(np.arange(self.config['start'], self.config['end']), example_tasks_idx)
        prompt = ""
        for i, example_task_idx in enumerate(example_tasks_idx):
            cur_instance = instance.format(example_task_idx)
            # --------------- Add to final output --------------- #
            print(f"Loading example instance {cur_instance}...")
            # --------------- Read Instance --------------- #
            problem = self.get_problem(cur_instance, domain_pddl)
            # ------------ Put plan and instance into text ------------ #
            gt_plan = self.compute_plan(domain_pddl, cur_instance)
            gt_plan_text = get_plan_as_text(self.config, len_plan=1)
            if i == 0 or INTERLEAVE_INSTRUCTIONS:
                prompt += self.config["domain_intro"] 
            # negative_example = False 
            # if ((i-start) % 2 == 1) and NEGATIVE_EXAMPLE:
            #     negative_example = True
            prompt += fill_template(*instance_to_text_blocksworld(problem, get_plan=True, data=self.config))
            prompt += "\n"

        ### STARTING THE MAIN LOOP ###
        prob_prev_pos = 0 #for caching the examples
        pbar = tqdm.tqdm(real_tasks_idx)
        for loop_idx, cur_task_idx in enumerate(pbar):
            output = ""

            correct_success_percent = correct_plans / (loop_idx + 1e-8)
            correct_feasibility_percent = correct_feasibility / (loop_idx + 1e-8)
            correct_perplexity_percent = correct_perplexity / (loop_idx + 1e-8)
            pbar.set_description(f"n_examples={self.n_examples}, correct(%): {correct_success_percent:.2f}, "
                                    f"correct_feasibility(%): {correct_feasibility_percent:.2f}, "
                                    f"correct_perplexity(%): {correct_perplexity_percent:.2f}")

            query = ""
            query += prompt

            last_plan = True

            ######
            cur_instance = instance.format(cur_task_idx)
            # --------------- Add to final output --------------- #
            output += f"Loading task instance {cur_instance}... \n"
            # --------------- Read Instance --------------- #
            problem = self.get_problem(cur_instance, domain_pddl)
            # ------------ Put plan and instance into text ------------ #
            gt_plan = self.compute_plan(domain_pddl, cur_instance)
            gt_plan_text = get_plan_as_text(self.config, len_plan=1)

            if INTERLEAVE_INSTRUCTIONS:
                query += self.config["domain_intro"] 
            query += fill_template(*instance_to_text_blocksworld(problem, get_plan=False, data=self.config))
            if not last_plan:
                query += "\n"
            #####
            
            # Querying LLM
            gpt3_response, response_tokens = send_query(query, 
                                        self.engine, 
                                        self.max_gpt_response_length,
                                         model=self.model, 
                                    )   
            if prob_prev_pos == 0:
                prob_prev_pos = extract_plan_begin_idx(response_tokens, plan_start_str = '[PLAN]') - 5

            gt_response = text_plan_to_natural_language(gt_plan_text, self.config)

            # pdb.set_trace()
            def response_to_list(response):
                response_list = response.split('\n')
                response_list = [x for x in response_list if x != '' and x != '[PLAN END]']
                return response_list

            gpt3_response_list = response_to_list(gpt3_response)
            gt_response_list = response_to_list(gt_response)

            gpt3_plan_length = len(gpt3_response_list)
            gt_plan_length = len(gt_response_list)

            # stats['gpt3_plan_length'].append(gpt3_plan_length)
            # stats['gt_plan_length'].append(gt_plan_length)

            gpt3_perplexity_query = query + gpt3_response
            gt_perplexity_query = query + gt_response

            #time it
            start = time.time()

            gpt3_response_perplexity, gpt3_info = perplexity_query(gpt3_perplexity_query, 
                                                                    self.engine,
                                                                    self.max_gpt_response_length, 
                                                                    model=self.model, 
                                                                    prob_prev_pos=prob_prev_pos)
            gt_response_perplexity, gt_info = perplexity_query(gt_perplexity_query, 
                                                                self.engine, 
                                                                self.max_gpt_response_length, 
                                                                model=self.model, 
                                                                prob_prev_pos=prob_prev_pos)

            end = time.time()
            print(f"Perplexity query took {end - start} seconds")
            # pdb.set_trace()

            # aug_info = {}
            # for i, augmented_response in enumerate(augmented_responses):
            #     augmented_query = query + augmented_response
            #     augmented_response_perplexity, augmented_info = perplexity_query(augmented_query, self.engine, self.max_gpt_response_length, model=self.model)
            #     augmented_info['response'] = augmented_response
            #     aug_info['aug_info' + str(i)] = augmented_info

            # gpt3_info['response'] = gpt3_response
            # gt_info['response'] = gt_response

            # gpt3_infos.append(gpt3_info)
            # gt_infos.append(gt_info)
            # aug_infos.append(aug_info)

            # stats['gpt3_perplexity'].append(gpt3_response_perplexity)
            # stats['gt_perplexity'].append(gt_response_perplexity)

            # stats['delta_perplexity'].append(gpt3_response_perplexity - gt_response_perplexity)
            # stats['delta_plan_length'].append(gpt3_plan_length - gt_plan_length)
            
            # Do text_to_plan procedure
            plan_written, gpt3_plan = text_to_plan_blocksworld(gpt3_response, problem.actions, self.gpt3_plan_file, self.config)

            # --------------- Validate feasibility GPT-3's actions ---------------- #
            gpt3_parsed_plan = gpt3_plan.split('\n')
            gpt3_parsed_plan = [x for x in gpt3_parsed_plan if x != '']
            correct_f, feasibility_output = evaluate_feasible_plan(gpt3_parsed_plan, problem_file=cur_instance, config=self.config)  #response in the form of a string
            correct_feasibility += correct_f
            # ------------------------------- #

            # --------------- Validate correctness of GPT-3's actions ---------------- #
            correct = int(validate_plan(domain_pddl, cur_instance, self.gpt3_plan_file))
            correct_plans += correct
            # ------------------------------- #

            correct_perplexity += (gt_response_perplexity <= gpt3_response_perplexity) or correct
            

            output += ('='*5) + f'success={correct}, feasibility=[{feasibility_output}],'\
                + f'NLL=[gt:{gt_response_perplexity:.4f},gpt3:{gpt3_response_perplexity:.4f}]' + ('='*5)
            
            output += verbose_template.format(query, gpt3_response, gpt3_plan, gt_plan_text, '='*77)
            if self.verbose: print(output)
            final_output += output

            self.save_output("task" + t1_or_t4, final_output)

            # save_path = os.path.join('/local/crv/acanberk/gpt-plan-benchmark', 'stats.csv')
            # stats_df = pd.DataFrame(stats)
            # stats_df.to_csv(save_path)

            # infos = {'gpt3':gpt3_infos, 'gt':gt_infos, 'aug':aug_infos}
            # save_path = os.path.join('/local/crv/acanberk/gpt-plan-benchmark', 'infos.pkl')
            # with open(save_path, 'wb') as f:
            #     pickle.dump(infos, f)
                


        os.remove(self.plan_file)
        os.remove(self.gpt3_plan_file)

        # --------------- Add to final output --------------- #
        final_output += f"[+]: The number of correct plans is {correct_plans}/{n_files}={correct_plans / (n_files) * 100}%"
        print(f"[+]: The number of correct plans is {correct_plans}/{n_files}={correct_plans / (n_files) * 100}%")
        self.save_output("task" + t1_or_t4, final_output)

if __name__ == '__main__':
    random.seed(10)
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default='t1', help='Task to run \
    \n t1 = Goal Directed Reasoning\
    \n t2 = Goal Reformulation \
    \n t3 = Plan Reuse \
    \n t4 = Plan Generalization\
    \n t5 = Optimal Planning \
    \n t6 = Replanning (easier) \
    \n t7 = Plan Execution \
    ')
    parser.add_argument('--engine', type=str, default='davinci', help='Engine to use')
    parser.add_argument('--verbose', type=str, default="False", help='Verbose')

    parser.add_argument('--augmentation', type=str, default="False", help='Augmentation') #for ablation task
    parser.add_argument('--aug_n', type=int, default=1, help='Number of augs') #for augmentations
    
    args = parser.parse_args()
    task = args.task
    engine = args.engine
    verbose = eval(args.verbose)
    tasks_obj = ReasoningTasks(engine, verbose)

    if task == 't1-a':
        config_file = './configs/t1_goal_directed_reasoning_easy.yaml'
        tasks_obj.t1_ablations(config_file, "1_reasoning", args.augmentation, args.aug_n)
    if task == 't1':
        config_file = './configs/t1_goal_directed_reasoning_easy.yaml'
        tasks_obj.t1_t4(config_file)
    elif task == 't2':
        config_file = './configs/t2_paraphrasing.yaml'
        tasks_obj.t2_paraphrasing(config_file)
    elif task == 't3':
        config_file = './configs/t3_plan_subset.yaml'
        tasks_obj.t3_plan_subset(config_file)
    elif task == 't4':
        config_file = './configs/t4_plan_generalization.yaml'
        tasks_obj.t1_t4(config_file, "4_generalization")
    elif task == 't5':
        config_file = './configs/t3_plan_subset.yaml'
        tasks_obj.t5_optimality(config_file)
    elif task == 't6':
        config_file = './configs/t3_plan_subset.yaml'
        tasks_obj.t6_replanning(config_file, harder=0)
    # tasks_obj.t6_replanning(config_file, harder=0)
    elif task == 't7':
        config_file = './configs/t3_plan_subset.yaml'
        tasks_obj.t7_plan_execution(config_file)


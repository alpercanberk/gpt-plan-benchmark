# March 27


### What if we repeat a random step of the ground truth plan n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| repeat_random_step   | 1       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 2       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 3       | 2        | 0.00    | 0.00                 | 1.00                 |

### What if we do/undo a move n times, keeping the solution valid?

| Augmentation  | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------|---------|----------|---------|----------------------|----------------------|
| cycle         | 1       | 2        | 1.00    | 1.00                 | 1.00                 |
| cycle         | 2       | 2        | 1.00    | 1.00                 | 1.00                 |
| cycle         | 3       | 2        | 1.00    | 1.00                 | 1.00                 |


### What if we add a random action to a random location

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| add_random_action   | 1       | 2        | 0.00    | 0.00                 | 0.92                 |
| add_random_action   | 2       | 2        | 0.00    | 0.00                 | 0.98                 |
| add_random_action   | 3       | 2        | 0.00    | 0.00                 | 0.99                 |

## What if we replace random steps with a random action that involves some other object in the ground truth plan?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| replace_steps       | 1       | 2        | 0.04    | 0.08                 | 0.72                 |
| replace_steps       | 2       | 2        | 0.03    | 0.05                 | 0.79                 |


## What if we remove a random step?
| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| remove_random_step  | 1       | 2        | 0.00    | 0.26                 | 0.65                 |
| remove_random_step  | 2       | 2        | 0.00    | 0.30                 | 0.58                 |
| remove_random_step  | 3       | 2        | 0.00    | 0.32                 | 0.51                 |


## Marc 30

### Todo
- [] Make sure the plan being evaluated contains the "PLAN END" token (15 )
- [] 
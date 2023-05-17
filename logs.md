# March 27

### Comparing perplexity of generated plans vs. ground truth plans
Out of 100 examples with 3 blocks
| n_shot | correct | correct_feasibility | correct_perplexity |
|------------|---------|-------------------|--------------------|
| 1          | 0.01    | 0.07              | 0.98               |
| 2          | 0.05    | 0.09              | 0.96               |
| 3          | 0.04    | 0.10              | 0.97               |


### What if we add a random action to the ground truth plan at a random location n times?

| Augmentation       | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|--------------------|---------|----------|---------|----------------------|----------------------|
| add_random_action  | 1       | 2        | 0.00    | 0.01                 | 0.91                 |
| add_random_action  | 2       | 2        | 0.00    | 0.00                 | 0.98                 |
| add_random_action  | 3       | 2        | 0.00    | 0.00                 | 1.00                 |


### What if we repeat a random step of the ground truth plan n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| repeat_random_step   | 1       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 2       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 3       | 2        | 0.00    | 0.00                 | 1.00                 |

### What if we remove a random step from a random location of the plan n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| remove_random_step   | 1       | 2        | 0.00    | 0.26                 | 0.65                 |

### What if we do/undo a move n times, keeping the solution valid?

| Augmentation  | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------|---------|----------|---------|----------------------|----------------------|
| cycle         | 1       | 2        | 1.00    | 1.00                 | 1.00                 |
| cycle         | 2       | 2        | 1.00    | 1.00                 | 1.00                 |
| cycle         | 3       | 2        | 1.00    | 1.00                 | 1.00                 |


# March 28

### What if we add a random action to the ground truth plan at a random location n times?
| Augmentation       | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|--------------------|---------|----------|---------|----------------------|----------------------|
| add_random_action  | 1       | 2        | 0.00    | 0.01                 | 0.96                 |
| add_random_action  | 2       | 2        | 0.00    | 0.00                 | 0.90                 |
| add_random_action  | 3       | 2        | 0.00    | 0.00                 | 1.00                 |


### What if we do/undo a move n times, keeping the solution valid?

| Augmentation  | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------|---------|----------|---------|----------------------|----------------------|
| cycle         | 1       | 2        | 1.00    | 1.00                 | 0.98                 |
| cycle         | 2       | 2        | 1.00    | 1.00                 | 0.98                 |
| cycle         | 3       | 2        | 1.00    | 1.00                 | 0.97                 |

### What if we repeat a random step of the ground truth plan n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| repeat_random_step   | 1       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 2       | 2        | 0.00    | 0.00                 | 1.00                 |
| repeat_random_step   | 3       | 2        | 0.00    | 0.00                 | 1.00                 |

### What if we remove a random step from a random location of the plan n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| remove_random_step   | 1       | 2        | 0.00    | 0.31                 | 0.71                 |
| remove_random_step   | 2       | 2        | 0.00    | 0.25                 | 0.73                 |
| remove_random_step   | 3       | 2        | 0.00    | 0.26                 | 0.65                 |

### What if we replace a random step with a random action n times?

| Augmentation        | `aug_n` | Examples | Correct | Correct (Feasibility) | Correct (Perplexity) |
|---------------------|---------|----------|---------|----------------------|----------------------|
| replace_step        | 1       | 2        | 0.02    | 0.04                 | 0.75                 |
| replace_step        | 1       | 2        | 0.00    | 0.04                 | 0.83                 |
| replace_step        | 1       | 2        | 0.00    | 0.04                 | 0.90                 |
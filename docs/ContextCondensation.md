# Token Optimization through Checkpoint-Based Context Condensation

## Overview

As part of improving the scalability and cost-efficiency of **CellCraft-AI's** Agentic AI system, we identified and resolved a key bottleneck related to **LLM prompt size and token consumption**.

Previously, each prompt sent to the language model (Gemini 2.5) included a **full linear history of all prior transformation steps** (`key_steps`) in order to maintain context. This led to rapid growth in prompt size, increased latency, higher costs, and in some cases, even model failure due to token limits.

To address this, we designed and implemented a **Checkpoint-Based Context Condensation** system.

---

## Key Challenges

1. **Prompt Size Explosion:** As users performed more transformations, the number of `key_steps` grew linearly, causing the prompt to exceed practical token limits.
2. **Unbounded Cost Growth:** More tokens meant higher inference costs with no effective cap.
3. **LLM Repetition:** Large histories diluted the LLM's focus, leading to less precise responses.

---

## Solution: Checkpoint + Condensed Context

### How It Works:

* The system introduces **Checkpoints**: synthetic commit summaries that condense all previous transformations into a concise, structured representation.
* Each checkpoint follows a strict **MDP-inspired format**:

  ```
  state: "<brief initial state>"
  action: "<transformation applied>"
  outcome: "<result or error>"
  ```
* Only the **latest checkpoint + the uncheckpointed recent commits** are passed to the LLM, keeping context short, meaningful, and consistent.

### Example

### Before: Verbose `key_steps` (Uncondensed)

```
Generating a data summary including data types, non-null counts, descriptive statistics, unique values for categorical columns, and identifying inconsistencies such as 'ERROR' in 'Total Spent' and 'UNKNOWN' in 'Payment Method' and 'Location'. Also checking for logical consistency between 'Quantity', 'Price Per Unit', and 'Total Spent'.
```

* **Approximate Token Count:** \~100 tokens

---

### After: Condensed Checkpoint (MDP-Style)

```
state: "inconsistent values in Total Spent"
action: "checked data types, fixed errors"
outcome: "errors removed, data summarized"
```

* **Approximate Token Count:** \~13 tokens

---

### Token Savings:

| Metric                 | Before       | After               |
| ---------------------- | ------------ | ------------------- |
| Token Count (per step) | \~100 tokens | \~13 tokens         |
| Reduction Achieved     | —            | **\~87% reduction** |

---

✅ By introducing this structured condensation:

* We reduced **prompt token usage per transformation step by \~85–90%**.
* This enables **longer-running sessions**, **lower LLM cost**, and **clearer context for downstream agents**.

---

> ⚠️ **Note:**  
> The token savings percentages provided above are **estimates based on typical tokenization patterns** observed in large language models such as Gemini and GPT.  
> 
> Exact token counts may vary depending on:  
> - The specific wording of transformation steps,  
> - The tokenizer behavior of the underlying model,  
> - Additional system metadata or formatting.  
> 
> For precise measurement, **benchmarking using actual token counts in the deployed environment is recommended**.

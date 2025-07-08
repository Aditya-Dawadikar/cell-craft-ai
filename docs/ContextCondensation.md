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

### Algorithm

![img](https://github.com/Aditya-Dawadikar/cell-craft-ai/blob/docs/docs/CheckpointBasedCondensation.png)

To optimize token usage and maintain efficient long-term memory, CellCraft-AI uses a **checkpoint-based context condensation system**. Here's how it works:

---

## Checkpoint-Based Context Management Algorithm (CellCraft-AI):

1. **Receive Data Transformation Request**

   * The system receives a user query or transformation instruction from the UI.

2. **Build Context**

   * Fetch the **latest checkpoint summary** from the `checkpoints` collection (MongoDB).
   * Fetch the **list of uncheckpointed commits** from the `commits` collection.
   * Merge both into a concise context for the LLM.

3. **Send Query to LLM and Receive Action**

   * The merged context and user query are sent to the **LangChain + Gemini agent**.
   * The model returns either Python code, a suggested action, or a response.

4. **Perform Action**

   * The suggested action (usually code) is executed inside the **Python Sandbox**.
   * Generated outputs (CSV, Markdown, visualizations) are created.

5. **Create New Commit**

   * A new **commit** is created containing the query, action, and key steps.
   * This commit is saved to the `commits` collection.

6. **Check Checkpoint Queue Size**

   * The system checks if the number of uncheckpointed commits exceeds a predefined threshold.

7. **Update or Create Checkpoint**

   * If the checkpoint queue is **not full**:

     * The new commit is simply **added to the latest checkpoint’s commit queue**.
   * If the queue **is full**:

     * A new **checkpoint summary** is generated using **LangChain summarization**.
     * The uncheckpointed commits are condensed into this summary.
     * A new **checkpoint document** is created, resetting the queue.

8. **Return Final Response**

   * The final response, including any generated files, is returned to the user interface.

---
### Example

### Before: Verbose `key_steps` (Uncondensed)

```
Generating a data summary including data types, non-null counts, descriptive statistics, unique values for categorical columns, and identifying inconsistencies such as 'ERROR' in 'Total Spent' and 'UNKNOWN' in 'Payment Method' and 'Location'. Also checking for logical consistency between 'Quantity', 'Price Per Unit', and 'Total Spent'.
```

* **Approximate Token Count:** \~100 tokens

For a context with 100 commits, the token count will be **10,000 Tokens**

---

### After: Condensed Checkpoint (MDP-Style)

```
state: "inconsistent values in Total Spent"
action: "checked data types, fixed errors"
outcome: "errors removed, data summarized"
```

* **Approximate Token Count:** \~30 tokens

For a context with 100 commits, the token count will be 3000 Tokens if we have linear growth.

Formula for generating context is:

```Context = Checkpoint Summary + last 10 commits with full detail```

:. Context Token Count ~ 30x90 + 100*10

:. Context Token Count ~ **3700**

:. Percentage Token Count Reduction = (10,000 - 3700)/10,000

:. Percentage Token Count Reduction ~ **63% reduction**


---

✅ By introducing this structured condensation:

* We reduced **prompt token usage per transformation step by \~60-65**.
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

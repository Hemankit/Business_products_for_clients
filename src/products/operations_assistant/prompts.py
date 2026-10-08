SYSTEM_PROMPT = """
You interpret employee requests as structured business operations.

Rules:
- Choose exactly one action from the allowed actions provided.
- Do not invent new actions.
- For the chosen action, use only the parameter names defined for that action.
- Populate a parameter when its value is explicitly stated or can be faithfully
  restated from information in the employee request.
- A short operational message may summarize the employee's stated instruction,
  but it must not introduce new facts, commitments, names, dates, amounts, or
  business details.
- Preserve relative dates and times as stated. For example, keep "tomorrow" or
  "next Monday" rather than converting them to an absolute date.
- If information for a parameter is not provided, omit that parameter rather
  than guessing, even when the parameter is marked as required.
- The target should identify the primary person, company, record, team, or
  business object the operation concerns when clearly stated.
- Keep the reason concise and describe the employee's stated purpose.
- Do not choose software platforms, integrations, APIs, or provider-specific
  tool names.
- Do not decide whether the operation is authorized.
"""


def build_operation_prompt(
    raw_text: str,
    operation_config: dict,
) -> str:

    action_lines = []

    for action, config in operation_config.items():
        action_lines.append(f"- {action}")

        parameters = config.get("parameters") or {}

        if not parameters:
            action_lines.append("  parameters: none")
            continue

        for name, details in parameters.items():
            requirement = (
                "required to execute"
                if details.get("required")
                else "optional"
            )

            description = details.get("description")

            if description:
                action_lines.append(
                    f"  - {name} [{requirement}]: {description}"
                )
            else:
                action_lines.append(
                    f"  - {name} [{requirement}]"
                )

    actions = "\n".join(action_lines)

    return f"""
Interpret the employee request as one structured business operation.

ALLOWED ACTIONS:

{actions}

Return parameters using only the parameter names defined for the chosen action.
If the employee has not supplied a value, leave that parameter absent rather
than inventing one.

EMPLOYEE REQUEST:

{raw_text}
""".strip()
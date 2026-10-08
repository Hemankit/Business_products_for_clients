SYSTEM_PROMPT = """
You interpret employee requests as structured business operations.

Rules:
- Choose exactly one action from the allowed actions provided by the user.
- Do not invent new actions.
- For the chosen action, populate "parameters" using the exact parameter names
  given for that action whenever the request contains the corresponding
  information, even if it is phrased as a relative date/time (e.g. "tomorrow")
  or needs to be summarized into a short message based on what was stated.
- Do not fabricate customer names, dates, amounts, messages, record IDs, or
  other information that is not stated or implied anywhere in the request.
- Preserve names, dates, amounts, and business details accurately.
- The target should identify the primary person, company, record, or business object the operation concerns when clearly stated.
- Keep the reason concise and describe why the employee requested the operation.
- Do not choose software platforms, integrations, APIs, or provider-specific tool names.
- Do not decide whether the operation is authorized; policy checks happen after interpretation.

Example:
Allowed actions: "schedule_meeting (parameters: attendees (required), time (required))"
Request: "Set up a meeting with the finance team for next Monday about the budget review."
Correct output: {"action": "schedule_meeting", "target": null, "parameters": {"attendees": "finance team", "time": "next Monday"}, "reason": "Employee requested a meeting with finance about the budget review"}
Note how "parameters" is filled in using the request's own wording (including relative
times like "next Monday") instead of being left empty.
"""


def build_operation_prompt(
    raw_text: str,
    operation_config: dict,
) -> str:
    action_lines = []

    for action, config in operation_config.items():
        parameters = config.get("parameters") or {}

        if parameters:
            param_descriptions = ", ".join(
                f"{name} (required)" if details.get("required") else name
                for name, details in parameters.items()
            )
            action_lines.append(
                f"- {action} (parameters: {param_descriptions})"
            )
        else:
            action_lines.append(f"- {action}")

    actions = "\n".join(action_lines)

    return f"""
Interpret the following employee request as a structured business operation.

ALLOWED ACTIONS AND THEIR PARAMETERS:
{actions}

For the action you choose, populate the "parameters" field using the parameter
names listed for that action whenever the corresponding information is present
in the employee request.

EMPLOYEE REQUEST:
{raw_text}
""".strip()  
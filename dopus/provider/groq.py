# def request(client, model, messages, tools=None, system_prompt=""):
#     messages = [{"role": "system", "content": system_prompt}] + messages
#     if tools is not None:
#         response = client.chat.completions.create(
#             messages=messages,
#             model=model,
#             tool_choice="required",
#             parallel_tool_calls=False,
#             n=1,
#             tools=tools
#         )
#     else:
#         response = client.chat.completions.create(
#             messages=messages,
#             model=model,
#             n=1,
#         )
#     return response

# def get_tool_calls(response):
#     return response.tool_calls
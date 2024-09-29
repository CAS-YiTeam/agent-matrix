from void_terminal.crazy_functions.json_fns.pydantic_io import GptJsonIO, JsonStringError

def structure_output(main_input, prompt, err_msg, run_gpt_fn, pydantic_cls):
    gpt_json_io = GptJsonIO(pydantic_cls)
    analyze_res = run_gpt_fn(
        main_input,
        sys_prompt=prompt + gpt_json_io.format_instructions
    )
    try:
        obj = gpt_json_io.generate_output_auto_repair(analyze_res, run_gpt_fn)
        err_msg = ""
    except JsonStringError as e:
        return None, err_msg
    return obj, err_msg

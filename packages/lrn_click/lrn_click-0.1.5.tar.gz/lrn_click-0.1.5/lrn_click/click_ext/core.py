import click


class OptionPicker(click.Option):
    def __init__(self, param_decls=None, show_default=False,
                 prompt=False, prompt_title=None, prompt_list_func=[],
                 prompt_pick_single=False, confirmation_prompt=False,
                 hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True,
                 type=None, help=None, foo=None, **attrs):

        click.Option.__init__(self, param_decls, show_default=show_default,
                              prompt=prompt,
                              confirmation_prompt=confirmation_prompt,
                              hide_input=hide_input, is_flag=is_flag,
                              flag_value=flag_value, multiple=multiple,
                              count=count,
                              allow_from_autoenv=allow_from_autoenv,
                              type=type, help=help, **attrs)

        self.prompt_list_func = prompt_list_func
        self.prompt_title = prompt_title
        self.prompt_pick_single = prompt_pick_single

    def prompt_for_value(self, ctx):
        from lrn_click.click_ext.ui import picker

        if self.default:
            self.process_value(ctx, self.default)
            return self.default

        choice = picker(
            self.prompt_list_func,
            prompt=self.prompt,
            title=self.prompt_title,
            pick_single=self.prompt_pick_single
        )
        self.process_value(ctx, choice)
        return choice

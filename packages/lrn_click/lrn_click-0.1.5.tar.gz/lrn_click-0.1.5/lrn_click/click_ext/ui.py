import click


def picker(options_func, title="", prompt="Enter choice", pick_single=False):
    "Prompt user for a selection from the list of options"
    options = options_func(click.get_current_context())

    # if pick single then return the one and only result without prompting
    if pick_single and len(options) == 1:
        return options[0]

    if title:
        click.echo("{} -".format(title))

    for i, name in enumerate(options):
        click.echo(
            "\t{}{}{} - {}".format(
                click.style("[", fg="magenta"),
                click.style(
                    str(i+1).rjust(len(str(len(options)))),
                    fg="white",
                    bold=True
                ),
                click.style("]", fg="magenta"),
                click.style(name, bold=True)
            )
        )

    choice_id = int(
        click.prompt(prompt, type=click.IntRange(1, len(options)))
    )

    choice_id = choice_id - 1  # zero based

    if isinstance(options, list):
        return options[choice_id]

    elif isinstance(options, dict):
        return options.get(list(options)[choice_id])

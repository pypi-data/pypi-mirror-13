import re


class StepInfo(object):
    def __init__(self, step_text, parsed_step_text, impl, file_name):
        self.__step_text = step_text
        self.__parsed_step_text = parsed_step_text
        self.__impl = impl
        self.__file_name = file_name

    @property
    def step_text(self):
        return self.__step_text

    @property
    def parsed_step_text(self):
        return self.__parsed_step_text

    @property
    def impl(self):
        return self.__impl

    @property
    def file_name(self):
        return self.__file_name


class Registry(object):
    def __init__(self):
        self.__steps_map = {}
        self.__before_step = []
        self.__after_step = []
        self.__before_scenario = []
        self.__after_scenario = []
        self.__before_spec = []
        self.__after_spec = []
        self.__before_suite = []
        self.__after_suite = []

    def before_step(self, tags=None):
        return _filter_hooks(tags, self.__before_step)

    def after_step(self, tags=None):
        return _filter_hooks(tags, self.__after_step)

    def before_scenario(self, tags=None):
        return _filter_hooks(tags, self.__before_scenario)

    def after_scenario(self, tags=None):
        return _filter_hooks(tags, self.__after_scenario)

    def before_spec(self, tags=None):
        return _filter_hooks(tags, self.__before_spec)

    def after_spec(self, tags=None):
        return _filter_hooks(tags, self.__after_spec)

    def before_suite(self):
        return self.__before_suite

    def after_suite(self):
        return self.__after_suite

    def all_steps(self):
        return [value.step_text for value in self.__steps_map.values()]

    def add_before_step(self, func, tags=None):
        self.__before_step.append({'tags': tags, 'func': func})

    def add_after_step(self, func, tags=None):
        self.__after_step.append({'tags': tags, 'func': func})

    def add_before_scenario(self, func, tags=None):
        self.__before_scenario.append({'tags': tags, 'func': func})

    def add_after_scenario(self, func, tags=None):
        self.__after_scenario.append({'tags': tags, 'func': func})

    def add_before_spec(self, func, tags=None):
        self.__before_spec.append({'tags': tags, 'func': func})

    def add_after_spec(self, func, tags=None):
        self.__after_spec.append({'tags': tags, 'func': func})

    def add_before_suite(self, func):
        self.__before_suite.append(func)

    def add_after_suite(self, func):
        self.__after_suite.append(func)

    def add_step_definition(self, step_text, func, file_name):
        parsed_step_text = re.sub('<[^<]+?>', '{}', step_text)
        self.__steps_map[parsed_step_text] = StepInfo(step_text, parsed_step_text, func, file_name)

    def is_step_implemented(self, step_text):
        return self.__steps_map.get(step_text) is not None

    def get_info(self, step_text):
        info = self.__steps_map.get(step_text)
        return info if info is not None else StepInfo(None, None, None, None)

    def clear(self):
        self.__steps_map = {}
        self.__before_step = []
        self.__after_step = []
        self.__before_scenario = []
        self.__after_scenario = []
        self.__before_spec = []
        self.__after_spec = []
        self.__before_suite = []
        self.__after_suite = []


registry = Registry()


def _filter_hooks(tags, hooks):
    filtered_hooks = []
    for hook in hooks:
        hook_tags = hook['tags']
        if hook_tags is None:
            filtered_hooks.append(hook['func'])
            continue
        for tag in tags:
            hook_tags = hook_tags.replace("<{}>".format(tag), "True")
        if eval(re.sub('<[^<]+?>', 'False', hook_tags)):
            filtered_hooks.append(hook['func'])
    return filtered_hooks

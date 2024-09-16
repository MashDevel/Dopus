import importlib

class LazyLoader:
    def __init__(self, module_name, class_name):
        self.module_name = module_name
        self.class_name = class_name
        self._module = None
        self._class = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        if self._class is None:
            self._class = getattr(self._module, self.class_name)
        return self._class

    def __call__(self, *args, **kwargs):
        class_ref = self._load()
        return class_ref(*args, **kwargs)

OpenAI = LazyLoader('dopus.provider.open_ai', 'OpenAI')
Anthropic = LazyLoader('dopus.provider.anthropic', 'Anthropic')

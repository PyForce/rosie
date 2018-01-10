class metaclass(type):
    instance = None

    def __call__(self, *args, **kwargs):
        if not self.instance:
            self.instance = super(metaclass, self).__call__(*args, **kwargs)
        return self.instance

Singleton = type.__new__(metaclass, '_temp', (), {})


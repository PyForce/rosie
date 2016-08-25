class Singleton(type):
    instance = None

    def __call__(self, *args, **kwargs):
        if not self.instance:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

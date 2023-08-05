class SingletonException(Exception):

    def __init__(self, classname):
        self.classname = classname

    def __str__(self):
        return repr(self.classname + " is a singleton. Cannot have more than one object of this class")

"""class PrivateMethodException(Exception):
    def __init__(self, method_name):
        self.method = method_name
        
    def __str__(self):
        return repr(self.method + " should not be called manually")"""
__author__ = 'karl.gong'


class TestListener(object):
    def on_test_suite_start(self, test_suite):
        pass

    def on_test_suite_finish(self, test_suite):
        pass

    def on_test_class_start(self, test_class):
        pass

    def on_test_class_finish(self, test_class):
        pass

    def on_test_group_start(self, test_group):
        pass

    def on_test_group_finish(self, test_group):
        pass

    def on_test_case_start(self, test_case):
        pass

    def on_test_case_finish(self, test_case):
        pass


class TestListenerGroup(object):
    def __init__(self):
        self.__test_listeners = []

    def append(self, test_listener):
        self.__test_listeners.append(test_listener)

    def on_test_suite_start(self, test_suite):
        for test_listener in self.__test_listeners:
            test_listener.on_test_suite_start(test_suite)

    def on_test_suite_finish(self, test_suite):
        for test_listener in self.__test_listeners:
            test_listener.on_test_suite_finish(test_suite)

    def on_test_class_start(self, test_class):
        for test_listener in self.__test_listeners:
            test_listener.on_test_class_start(test_class)

    def on_test_class_finish(self, test_class):
        for test_listener in self.__test_listeners:
            test_listener.on_test_class_finish(test_class)

    def on_test_group_start(self, test_group):
        for test_listener in self.__test_listeners:
            test_listener.on_test_group_start(test_group)

    def on_test_group_finish(self, test_group):
        for test_listener in self.__test_listeners:
            test_listener.on_test_group_finish(test_group)

    def on_test_case_start(self, test_case):
        for test_listener in self.__test_listeners:
            test_listener.on_test_case_start(test_case)

    def on_test_case_finish(self, test_case):
        for test_listener in self.__test_listeners:
            test_listener.on_test_case_finish(test_case)


test_listeners = TestListenerGroup()

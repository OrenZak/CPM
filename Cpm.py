import logging


class Activity:

    def __init__(self, name, duration):
        self._name = name
        self._duration = duration
        self._depending_activities = []

    def __str__(self):
        print("Activity %s with duration %s", self._name, self._duration)


class Project:

    def __init__(self, project):
        if project is not None:
            self._project = project
        else:
            self._project = {}
        self._project_duration = 0

    def add_activity(self, name, duration):
        self._project[name] = Activity(name, duration)
        logger.debug("%s added to the project", self._project[name])

    def remove_activity(self, activity):
        if activity in self._project:
            self._project.pop(activity)
            logger.debug("%s deleted from project", activity)

    def validate(self):
        # todo create the validation
        pass

    def find_isolated_activities(self):
        # todo find isolated activities (An activity without following or ascending another activity)
        pass

    def find_critical_path(self):
        # todo find critical path of the project (Showing the edges of the critical pass with their length
        pass

    def show_slacks(self):
        # todo Show slack's time for all activities in descending order.
        # Don’t show the critical activities in the list
        # (By definition, critical path has activities with a zero-slack time)
        pass

    def __str__(self):
        print("Project Details:\n")
        pass


if __name__ == "__main__":
    # create logger with
    logger = logging.getLogger('cpm_app')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)

    logger.debug("Start File: Model")
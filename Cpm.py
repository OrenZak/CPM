import logging


class Activity:

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.min_time_to_start = 0
        self.max_time_to_start = 0
        #self._depending_activities = []

    def __str__(self):
        print("Activity %s with duration %s", self.name, self.duration)

    def __eq__(self, other):
        return self.name == other.name and self.duration == other.duration

    def __ne__(self, other):
        return not self == other


class Project:

    def __init__(self, project):
        # this method initializes a project object if no dictionary or None is given, an empty dictionary will be used
        if project is not None:
            self.__project = project
        else:
            self.__project = {}

        self.__project_duration = 0

    def add_depending_activity(self, activity, depending_activity):
        # this method add depending activity to activity in the project
        if activity in self.__project:
            if depending_activity in self.__project[activity]:
                self._project[activity].append(depending_activity)
                logger.debug("%s added to the activity", depending_activity)
            else:
                logger.debug("%s already in the list of depending activities", depending_activity)
        else:
            logger.debug("%s isn`t at the project", activity)

    def add_activity(self, activity):
        # this method add activity to the project
        if activity not in self.__project:
            self._project[activity] = []
            logger.debug("%s added to the project", activity)
        else:
            logger.debug("%s already at the", activity)

    def remove_activity(self, activity):
        # this method removing activity from the project
        if activity in self.__project:
            self.__project.pop(activity)
            logger.debug("%s deleted from project", activity)

    def validate(self):
        # this method reveals a circle's activities in the project, and display them
        for key, depending_activities in self.__project.items():
            if key in depending_activities:
                print("Activity : %s contains a circle", key)
                logger.debug("Activity : %s contains a circle", key)
                return False
        return True  # No Circles!

    def find_isolated_activities(self):
        #  find isolated activities (An activity without following or ascending another activity)
        for key, depending_activities in self.__project.items():
            if len(depending_activities) == 0:
                print("Activity : %s is isolated activity", key)
                logger.debug("Activity : %s is isolated activity", key)
                return False
        return True  # No Circles!

    def calculate_activity_min_time_to_start(self):
        for activity, depending_activity in self._project.items():
            for dep_activity in depending_activity:
                if (dep_activity.min_time_to_start == 0 or
                        dep_activity.min_time_to_start > activity.duration + activity.min_time_to_start):
                    dep_activity.min_time_to_start = activity.duration + activity.min_time_to_start
                    dep_activity.max_time_to_start = dep_activity.min_time_to_start

    def calculate_activity_max_time_to_start(self):
        '''for activity, depending_activity in self._project.items():
            for dep_activity in depending_activity:
                if (dep_activity.max_time_to_start == 0 or
                        dep_activity.max_time_to_start < activity.duration + activity.min_time_to_start):
                    dep_activity.min_time_to_start = activity.duration + activity.min_time_to_start'''
        pass

    def find_critical_path(self):
        # find critical path of the project (Showing the edges of the critical pass with their length)
        for activity in self.__project.keys():
            if activity.min_time_to_start == activity.max_time_to_start:
                print("Activity : %s is a critical activity", activity)
                logger.debug("Activity : %s is a critical activity", activity)

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

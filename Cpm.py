import logging
import unittest

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


# The circles from the example
class Bullet:

    def __init__(self, bullet_id):
        self.bullet_id = bullet_id
        self.earliest_start = 0
        self.latest_start = 0

    def __str__(self):
        print("Bullet ID %s . Min start is : %s and Max start is : %s",
              self.bullet_id, self.earliest_start, self.latest_start)

    def __eq__(self, other):
        return self.bullet_id == other.bullet_id

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        key_tuple = (self.bullet_id, self.bullet_id)
        return hash(key_tuple)


# The arrows from the example
# duration represent by number as hours, 1 = one hour.
class Activity:

    def __init__(self, name, duration, from_bullet, to_bullet):
        self.name = name
        self.duration = duration
        self.from_bullet = from_bullet
        self.to_bullet = to_bullet

    def __str__(self):
        print("Activity %s with duration %s , from bullet : %s to bullet : %s",
              self.name, self.duration, self.from_bullet, self.to_bullet)

    def __eq__(self, other):
        return self.name == other.name and \
               self.duration == other.duration and \
               self.from_bullet == other.from_bullet and \
               self.to_bullet == other.to_bullet

    def __ne__(self, other):
        return not self == other


class Project:

    # prerequisites: Bullets name should be with some logic : like incremental id or something like that
    def __init__(self, structure, project_duration):
        # this method initializes a project object if no dictionary or None is given, an empty dictionary will be used
        if structure is not None:
            self.structure = structure
            self.project_duration = project_duration
        else:
            self.structure = {}
            self.project_duration = 0

    @classmethod
    def from_activities(cls, activities):
        structure = {}
        for activity in activities:
            if activity.from_bullet in structure.keys():
                activity_list = structure[activity.from_bullet]
                activity_list.append(activity)
            else:
                structure[activity.from_bullet] = [activity]

        # todo change to be calculated and not final
        project_duration = 20

        return cls(structure, project_duration)

    def calc_bullets_earliest_time(self):
        for bullet in self.structure.keys():
            if len(self.structure[bullet] == 0):  # this is the last bullet
                pass
            else:
                for activity in self.structure[bullet]:
                    if activity.to_bullet.earliest_start == 0 or \
                            activity.to_bullet.earliest_start > activity.duration + activity.from_bullet.ealiest_start:

                        # the activity points to a bullet that can start earlier.
                        activity.to_bullet.earliest_start = activity.duration + activity.from_bullet.ealiest_start
                    else:
                        # the activity points to a bullet that can't start earlier yet.
                        pass

    def calc_bullets_latest_time(self):
        last_bullet = self.find_isolated_activities()
        if last_bullet is None:
            logger.debug("Project does not have last bullet")
            return None
        last_bullet.latest_start = last_bullet.earliest_start
        self.project_duration = last_bullet.earliest_start
        activities_list = self.get_list_of_pointed_activities(last_bullet)
        while len(activities_list) > 0:
            # setting latest time for the current pointers
            for activity in activities_list:
                if activity.from_bullet.latest_time == 0 or activity.from_bullet.latest_time > activity.to_bullet.latest_start - activity.duration:
                    activity.from_bullet.latest_time = activity.to_bullet.latest_start - activity.duration
                # getting new pointers
                new_pointers = self.get_list_of_pointed_activities(activity.from_bullet)
                # adding pointers to the activities list
                activities_list.extend(new_pointers)
                # remove current activity
                activities_list.remove(activity)

    def get_list_of_pointed_activities(self, bullet):
        activities_to_last = []
        for key, activities in self.structure.items():
            for activity in activities:
                if activity.to_bullet == bullet:
                    activities_to_last.append(activity)
        return activities_to_last

    def add_activity_to_bullet(self, activity, bullet):
        # this method add activity to a bullet in the project
        if bullet in self.structure:
            if activity in self.structure[bullet]:
                logger.debug("%s already in the list of  activities", activity)
            else:
                self.structure[bullet].append(activity)
                logger.debug("added activity : %s to the list of activities", activity)
        else:
            self.structure[bullet] = []
            self.structure[bullet].append(activity)
            logger.debug("added bullet : %s and added activity : %s to the bullet list of activities.", bullet,
                         activity)

    def remove_activity_from_bullet(self, activity, bullet):
        # this method remove activity from a bullet in the project
        if bullet in self.structure:
            if activity in self.structure[bullet]:
                self.structure[bullet].pop(activity)
                logger.debug("activity %s removed from bullet : %s", activity, bullet)
            else:
                logger.debug("activity : %s is not in the bullet : %s list of activities ", activity, bullet)
        else:
            logger.debug(" bullet : %s is not in the project", bullet)

    def validate(self):
        # this method reveals a circle's activities in the project, and display them
        for bullet, activities in self.structure.items():
            for activity in activities:
                if activity.to_bullet == bullet:
                    print("Bullet : %s contains a circle to himself with activity : s", bullet, activity)
                    logger.debug("Bullet : %s contains a circle to himself with activity : s", bullet, activity)
                    return False
        return True  # No Circles!

    def find_isolated_activities(self):
        #  find isolated bullets (A bullet without following or ascending another activity)
        #  means last bullet
        for bullet, activities in self.structure.items():
            if len(activities) == 0:
                print("bullet  : %s is isolated bullet", bullet)
                logger.debug("bullet  : %s is isolated bullet", bullet)
                return bullet
        return None  # No Isolated bullet!

    def find_critical_path(self):
        # find critical path of the project (Showing the edges of the critical pass with their length)
        for bullet in self.structure.keys():
            if bullet.earliest_start == bullet.latest_start:
                print("Bullet : %s is a critical bullet", bullet)
                logger.debug("Bullet : %s is a critical bullet", bullet)

    def show_slacks(self):
        # todo Show slack's time for all activities in descending order.
        # Don’t show the critical activities in the list
        # (By definition, critical path has activities with a zero-slack time)
        pass

    def __str__(self):
        print("Project Details:\n")
        pass


class TestActivity(unittest.TestCase):
    test_bullets = [
        Bullet(1),  # first  bullet
        Bullet(2),  # middle bullet
        Bullet(3),  # middle bullet
        Bullet(4),  # middle bullet
        Bullet(5),  # latest bullet
    ]

    test_activities = [
        Activity("Create README.md", 1, test_bullets[0], test_bullets[1]),
        Activity("Implement validate", 2, test_bullets[0], test_bullets[2]),
        Activity("Implement Find Isolated Activities", 3, test_bullets[0], test_bullets[3]),
        Activity("Implement Find Critical Path", 4, test_bullets[1], test_bullets[4]),
        Activity("Implement Show Slacks", 5, test_bullets[2], test_bullets[4]),
        Activity("Implement UI View", 6, test_bullets[3], test_bullets[4]),
    ]

    test_project = Project.from_activities(test_activities)

    def setUp(self):
        pass

    def test_activity_creation(self):
        activity = TestActivity.test_activities[0]
        self.assertEqual("Create README.md", activity.name)
        self.assertEqual(1, activity.duration)
        self.assertEqual(TestActivity.test_bullets[0], activity.from_bullet)
        self.assertEqual(TestActivity.test_bullets[1], activity.to_bullet)


if __name__ == "__main__":
    unittest.main()

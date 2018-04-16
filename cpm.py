import logging
import operator
import unittest

# create logger with
logger = logging.getLogger('cpm_app')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('logs.log', mode='w')
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
        return "Bullet ID %s . Min start is : %s and Max start is : %s" % \
               (self.bullet_id, self.earliest_start, self.latest_start)

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
        return "Activity %s with duration %s , from bullet : %s to bullet : %s" % \
               (self.name, self.duration, self.from_bullet, self.to_bullet)

    def __eq__(self, other):
        return self.name == other.name and \
               self.duration == other.duration and \
               self.from_bullet == other.from_bullet and \
               self.to_bullet == other.to_bullet

    def __ne__(self, other):
        return not self == other


class Project:

    # prerequisites: Bullets name should be with some logic : like incremental id or something like that
    def __init__(self, structure=None):
        # this method initializes a project object if no dictionary or None is given, an empty dictionary will be used
        if structure is not None:
            self.structure = structure
            logger.debug("Project init with structure dictionary")
            if len(self.validate()) > 0:
                self.project_duration = 0
                logger.debug("Project validate is bad, thus project duration is 0")
            else:
                self.project_duration = self.calculate_project_duration()
                logger.debug("Project duration is: %s" % self.project_duration)
        else:
            logger.debug("Project init None structure, thus new structure initiated, duration 0")
            self.structure = {}
            self.project_duration = 0

    def calculate_project_duration(self):
        logger.debug("Start calculate project duration")
        self.calc_bullets_earliest_start()
        self.calc_bullets_latest_start()
        last_bullet = self.get_last_bullet()
        if last_bullet is not None:
            return last_bullet.latest_start
        else:
            return 0

    def calc_bullets_earliest_start(self):
        logger.debug("Start calculate bullets earliest start")
        activity_list = self.structure[self.get_first_bullet()][:]
        while len(activity_list) > 0:
            activity = activity_list[0]
            # check whether the ES is 0 or it greater than the activity duration and the parent ES.
            if activity.to_bullet.earliest_start == 0 or \
                    activity.to_bullet.earliest_start < activity.duration + activity.from_bullet.earliest_start:
                activity.to_bullet.earliest_start = activity.duration + activity.from_bullet.earliest_start

            activity_list.extend(self.structure[activity.to_bullet])  # add the next list of the next bullet
            activity_list = activity_list[1:]

    def calc_bullets_latest_start(self):
        logger.debug("Start calculate bullets latest start")
        last_bullet = self.get_last_bullet()
        if last_bullet is None:
            logger.debug("Project does not have last bullet")
            return None
        last_bullet.latest_start = last_bullet.earliest_start
        activity_list = self.get_list_of_pointed_activities(last_bullet)
        while len(activity_list) > 0:
            # setting latest time for the current pointers
            activity = activity_list[0]
            if not activity.from_bullet.bullet_id == "Start":
                if activity.from_bullet.latest_start == 0 or activity.from_bullet.latest_start > activity.to_bullet.latest_start - activity.duration:
                    activity.from_bullet.latest_start = activity.to_bullet.latest_start - activity.duration

            # getting new pointers
            new_pointers = self.get_list_of_pointed_activities(activity.from_bullet)
            # adding pointers to the activities list
            activity_list.extend(new_pointers)
            # remove current activity
            activity_list = activity_list[1:]

    def get_last_bullet(self):
        for bullet in self.structure.keys():
            if bullet.bullet_id == "End":
                return bullet
        return None

    def get_first_bullet(self):
        for bullet in self.structure.keys():
            if bullet.bullet_id == "Start":
                return bullet
        return None

    def get_list_of_pointed_activities(self, bullet):
        activities_to_last = []
        for key, activities in self.structure.items():
            for activity in activities:
                if activity.to_bullet == bullet:
                    activities_to_last.append(activity)
        return activities_to_last

    def add_activity_to_bullet(self, activity, bullet):
        # this method add activity to a bullet in the project
        logger.debug("Add activity %s to bullet %s" % (activity, bullet))
        if bullet in self.structure:
            if activity in self.structure[bullet]:
                logger.debug("%s already in the list of activities" % activity.name)
            else:
                self.structure[bullet].append(activity)
                logger.debug("added activity: %s to the list of activities" % activity.name)
        else:
            self.structure[bullet] = []
            self.structure[bullet].append(activity)
            logger.debug(
                "added bullet: %s with activity: %s to the project structure." % (bullet.bullet_id, activity.name))

    def remove_activity(self, activity):
        # this method remove activity
        if activity.from_bullet.bullet_id == "Start":
            if len(self.structure[activity.from_bullet]) == 1:
                logger.debug("cant remove the only activity from the start bullet")
                print("cant remove the only activity from the start bullet")
                return

        is_last_pointed_activity = False
        if len(self.get_list_of_pointed_activities(activity.to_bullet)) == 1:
            self.structure[activity.from_bullet].extend(self.structure[activity.to_bullet])
            for act in self.structure[activity.from_bullet]:
                act.from_bullet = activity.from_bullet
            logger.debug(
                "Make bullet %s points to the bullet %s activities." % (activity.from_bullet, activity.to_bullet))
            print("Make bullet %s points to the bullet %s activities." % (activity.from_bullet, activity.to_bullet))
            self.structure.pop(activity.to_bullet, None)
            logger.debug("removed bullet : %s from the project." % activity.to_bullet)
            print("removed bullet : %s from the project." % activity.to_bullet)
            is_last_pointed_activity = True

        if len(self.structure[activity.from_bullet]) == 1 and not is_last_pointed_activity:
            self.structure[activity.from_bullet].remove(activity)
            logger.debug("removed activity : %s from the project." % activity)
            print("removed activity : %s from the project." % activity)
            for bullet in self.structure.keys():
                if bullet.bullet_id == "End":
                    logger.debug("Make bullet %s points to the end." % activity.from_bullet)
                    print("Make bullet %s points to the end." % activity.from_bullet)
                    new_activity = Activity(activity.name, 0, activity.from_bullet, bullet)
                    self.structure[activity.from_bullet].append(new_activity)
                    return
        self.structure[activity.from_bullet].remove(activity)
        logger.debug("removed activity : %s from the project." % activity)
        print("removed activity : %s from the project." % activity)
        return

    def validate(self):
        # this method reveals a circle's activities in the project, and display them
        logger.debug("Start validate for the project")
        circle_bullets_list = []
        for bullet in self.structure.keys():
            activities = self.structure[bullet][:]
            if activities is not None and len(activities) > 0:
                while len(activities) > 0:
                    activity = activities[0]
                    if activity.to_bullet == bullet:
                        circle_bullets_list.append(bullet)
                        break
                    activities.extend(self.structure[activity.to_bullet])
                    activities = activities[1:]

        if len(circle_bullets_list) != 0:
            logger.debug("Circle bullets are:")
            i = 0
            for bullet in circle_bullets_list:
                logger.debug("%d. %s" % (i, bullet))
                i += 1
        else:
            logger.debug("There is not circle bullets")
        return circle_bullets_list

    def find_isolated_bullets(self):
        #  find isolated bullets (A bullet without following or ascending another activity)
        logger.debug("Start find isolated bullets")
        isolated_bullets = []
        for bullet, activities in self.structure.items():
            if len(self.get_list_of_pointed_activities(bullet)) == 0 or len(activities) == 0:
                isolated_bullets.append(bullet)
                print("bullet: %s is isolated bullet" % bullet.bullet_id)
                logger.debug("bullet: %s is isolated bullet" % bullet.bullet_id)

        return isolated_bullets

    def find_critical_path(self):
        # find critical path of the project (Showing the edges of the critical pass with their length)
        logger.debug("Start find critical path")
        critical_path = []
        for bullet in self.structure.keys():
            if bullet.earliest_start == bullet.latest_start:
                activities = self.get_list_of_pointed_activities(bullet)
                for activity in activities:
                    if activity.duration + activity.from_bullet.earliest_start == bullet.earliest_start:
                        critical_path.append(activity)
                        print("Activity : %s is a critical activity" % activity.name)
                        logger.debug("Activity : %s is a critical activity" % activity.name)

        return critical_path

    def show_slacks(self):
        logger.debug("Start show slacks")
        slack_list = {}
        for bullet in self.structure.keys():
            if not bullet.earliest_start == bullet.latest_start:
                slack_list[bullet] = bullet.latest_start - bullet.earliest_start

        slack_sorted_list = sorted(slack_list.items(), key=operator.itemgetter(1))

        for slack in slack_sorted_list:
            print("%s ### Slack value is : %s ###" % (slack[0], slack[1]))
            logger.debug("%s ### Slack value is : %s ###" % (slack[0], slack[1]))
        return slack_sorted_list

    def __str__(self):
        project_str = "Project Details:\n"
        for bullet, activities in self.structure.items():
            project_str += "Bullet %s with LS: %s and ES: %s -> " % (
                bullet.bullet_id, bullet.latest_start, bullet.earliest_start)
            if len(activities) == 0:
                project_str += "is isolated"
            else:
                for activity in activities:
                    project_str += "%s, " % activity.name
            project_str += "\n"

        return project_str


class TestCPM(unittest.TestCase):
    test_bullets = [
        Bullet("Start"),  # 0
        Bullet("A"),  # 1
        Bullet("B"),  # 2
        Bullet("C"),  # 3
        Bullet("D"),  # 4
        Bullet("E"),  # 5
        Bullet("F"),  # 6
        Bullet("G"),  # 7
        Bullet("End"),  # 8
    ]

    test_activities = [
        Activity("Task 1", 4, test_bullets[0], test_bullets[1]),
        Activity("Task 2", 2, test_bullets[2], test_bullets[4]),
        Activity("Task 3", 2, test_bullets[4], test_bullets[7]),
        Activity("Task 4", 5, test_bullets[6], test_bullets[8]),
        Activity("Task 5", 6, test_bullets[0], test_bullets[2]),
        Activity("Task 6", 4, test_bullets[3], test_bullets[5]),
        Activity("Task 7", 6, test_bullets[5], test_bullets[8]),
        Activity("Task 8", 5, test_bullets[4], test_bullets[6]),
        Activity("Task 9", 5, test_bullets[0], test_bullets[3]),
        Activity("Task 10", 5, test_bullets[4], test_bullets[8]),
        Activity("Task 11", 0, test_bullets[1], test_bullets[2]),
        Activity("Task 12", 0, test_bullets[4], test_bullets[3]),
        Activity("Task 13", 0, test_bullets[4], test_bullets[5]),
        Activity("Task 14", 0, test_bullets[6], test_bullets[5]),
        Activity("Task 15", 0, test_bullets[7], test_bullets[8]),
    ]

    test_structure = {
        test_bullets[0]: [test_activities[0], test_activities[4], test_activities[8]],
        test_bullets[1]: [test_activities[10]],
        test_bullets[2]: [test_activities[1]],
        test_bullets[3]: [test_activities[5]],
        test_bullets[4]: [test_activities[2], test_activities[9], test_activities[7], test_activities[11],
                          test_activities[12]],
        test_bullets[5]: [test_activities[6]],
        test_bullets[6]: [test_activities[3], test_activities[13]],
        test_bullets[7]: [test_activities[14]],
        test_bullets[8]: [],
    }

    test_circle_activities = [
        Activity("Task 1", 4, test_bullets[0], test_bullets[1]),
        Activity("Task 2", 2, test_bullets[1], test_bullets[2]),
        Activity("Task 3", 2, test_bullets[2], test_bullets[0]),
        Activity("Task 4", 2, test_bullets[2], test_bullets[8]),
    ]

    test_circle_structure = {
        test_bullets[0]: [test_circle_activities[0]],
        test_bullets[1]: [test_circle_activities[1]],
        test_bullets[2]: [test_circle_activities[2], test_circle_activities[3]],
        test_bullets[8]: [],
    }

    test_project = Project(test_structure)
    test_circle_project = Project(test_circle_structure)

    def setUp(self):
        pass

    def test_bullet_creation(self):
        start_bullet = TestCPM.test_bullets[0]
        end_bullet = TestCPM.test_bullets[-1]
        self.assertEqual("Start", start_bullet.bullet_id)
        self.assertEqual("End", end_bullet.bullet_id)

    def test_bullet_equals(self):
        bullet1 = TestCPM.test_bullets[0]
        bullet2 = TestCPM.test_bullets[0]
        self.assertEqual(bullet1, bullet2)

    def test_bullet_not_equals(self):
        bullet1 = TestCPM.test_bullets[0]
        bullet2 = TestCPM.test_bullets[1]
        self.assertNotEqual(bullet1, bullet2)

    #############################################################

    def test_activity_creation(self):
        activity = TestCPM.test_activities[0]
        self.assertEqual("Task 1", activity.name)
        self.assertEqual(4, activity.duration)
        self.assertEqual(TestCPM.test_bullets[0], activity.from_bullet)
        self.assertEqual(TestCPM.test_bullets[1], activity.to_bullet)

    def test_activity_equals(self):
        activity1 = TestCPM.test_activities[0]
        activity2 = TestCPM.test_activities[0]
        self.assertEqual(activity1, activity2)

    def test_activity_not_equals(self):
        activity1 = TestCPM.test_activities[0]
        activity2 = TestCPM.test_activities[1]
        self.assertNotEqual(activity1, activity2)

    #############################################################

    def test_project_creation_from_activities(self):
        project = TestCPM.test_project
        self.assertIsNotNone(project.structure)
        self.assertDictEqual(TestCPM.test_structure, project.structure)

    def test_find_isolated_bullets(self):
        isolated_bullets = TestCPM.test_project.find_isolated_bullets()
        bullet_end = TestCPM.test_bullets[8]
        bullet_start = TestCPM.test_bullets[0]
        self.assertEqual(2, len(isolated_bullets))
        self.assertTrue(bullet_end in isolated_bullets)
        self.assertTrue(bullet_start in isolated_bullets)

    def test_calc_bullets_earliest_start(self):
        self.assertEqual(0, TestCPM.test_bullets[0].earliest_start)
        self.assertEqual(4, TestCPM.test_bullets[1].earliest_start)
        self.assertEqual(6, TestCPM.test_bullets[2].earliest_start)
        self.assertEqual(8, TestCPM.test_bullets[3].earliest_start)
        self.assertEqual(8, TestCPM.test_bullets[4].earliest_start)
        self.assertEqual(13, TestCPM.test_bullets[5].earliest_start)
        self.assertEqual(13, TestCPM.test_bullets[6].earliest_start)
        self.assertEqual(10, TestCPM.test_bullets[7].earliest_start)
        self.assertEqual(19, TestCPM.test_bullets[8].earliest_start)

    def test_calc_bullets_latest_start(self):
        self.assertEqual(0, TestCPM.test_bullets[0].latest_start)
        self.assertEqual(6, TestCPM.test_bullets[1].latest_start)
        self.assertEqual(6, TestCPM.test_bullets[2].latest_start)
        self.assertEqual(9, TestCPM.test_bullets[3].latest_start)
        self.assertEqual(8, TestCPM.test_bullets[4].latest_start)
        self.assertEqual(13, TestCPM.test_bullets[5].latest_start)
        self.assertEqual(13, TestCPM.test_bullets[6].latest_start)
        self.assertEqual(19, TestCPM.test_bullets[7].latest_start)
        self.assertEqual(19, TestCPM.test_bullets[8].latest_start)

    def test_get_first_bullet(self):
        first_bullet = TestCPM.test_project.get_first_bullet()
        self.assertEqual("Start", first_bullet.bullet_id)

    def test_get_last_bullet(self):
        last_bullet = TestCPM.test_project.get_last_bullet()
        self.assertEqual("End", last_bullet.bullet_id)

    def test_critical_path(self):
        critical_path = TestCPM.test_project.find_critical_path()
        self.assertTrue(TestCPM.test_activities[4] in critical_path)
        self.assertTrue(TestCPM.test_activities[1] in critical_path)
        self.assertTrue(TestCPM.test_activities[7] in critical_path)
        self.assertTrue(TestCPM.test_activities[13] in critical_path)
        self.assertTrue(TestCPM.test_activities[6] in critical_path)

    def test_show_slack(self):
        slack_list = TestCPM.test_project.show_slacks()
        self.assertEqual(slack_list[0], (TestCPM.test_bullets[3], 1))
        self.assertEqual(slack_list[1], (TestCPM.test_bullets[1], 2))
        self.assertEqual(slack_list[2], (TestCPM.test_bullets[7], 9))

    def test_validate_not_circle(self):
        circle_list = self.test_project.validate()
        self.assertTrue(len(circle_list) == 0)

    def test_validate_is_circle(self):
        circle_list = self.test_circle_project.validate()
        self.assertTrue(len(circle_list) == 3)
        self.assertTrue(TestCPM.test_bullets[0] in circle_list)
        self.assertTrue(TestCPM.test_bullets[1] in circle_list)
        self.assertTrue(TestCPM.test_bullets[2] in circle_list)
        self.assertTrue(TestCPM.test_bullets[8] not in circle_list)

    def test_remove_activity(self):
        self.test_project.remove_activity(TestCPM.test_activities[14])
        self.assertEqual(TestCPM.test_project.structure[TestCPM.test_bullets[7]][0].to_bullet.bullet_id, "End")
        self.test_project.remove_activity(TestCPM.test_activities[7])
        self.assertEqual(len(TestCPM.test_project.structure[TestCPM.test_bullets[4]]), 6)
        self.assertTrue(TestCPM.test_bullets[6] not in TestCPM.test_project.structure.keys())
        self.test_project.remove_activity(TestCPM.test_activities[1])
        self.assertTrue(TestCPM.test_bullets[4] not in TestCPM.test_project.structure.keys())
        self.assertEqual(len(TestCPM.test_project.structure[TestCPM.test_bullets[2]]), 6)


if __name__ == "__main__":
    unittest.main()

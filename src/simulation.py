import salabim as sim
import itertools
import sys


"""
This is an elevator simulation which leverages the Salabim Python Package, developed with a similar take on 
simulation creation as the popular Simpy package.
I choose Salabim over Simpy for two main reasons:
1. Simpy has dropped support for its object oriented api as of Simpy 3
2. Salabim, while supporting the object oriented paradigm, comes with built in with animation through the Pillow python
   package and TKinter. I however, did not have time to implement this part of the library.
   
An Elevator Simulation -
This is an optimisation problem pon implementation you will note that the algorithm or logic for an elevator would 
produce different answers depending on the definition of best outcome. 
The reason for this is that a sequence of locally "optimal" choices don't always yield an optimal solution.

There is no way to tell which "best" will yield the more optimal solution.
You get an answer, but you don't always know weather it is the optimal solution.

Here I chose to focus on the length of stay or wait time that each person waited on there floor of origin, I could have
as easily chose to focus on the number of moves the elevator made to determine "optimal" solution. However, give this is 
simulation of real world events, it is perfectly conceivable to assume that customer wait time should supersede elevator
efficiency.   
  
"""
__author__ = "Thomas McDonnell"
__title__ = "Elevator Simulation"

# globals
requests = None
floors = None
elevators = None


class Building(sim.Component):
    """
    Factory class for generating people in a building with random selection of start position
    and destination
    """
    def __init__(self, num_floors, *args, **kwargs):
        sim.Component.__init__(self, *args, **kwargs)
        self.num_floors = num_floors
        self.choice = [x for x in range(self.num_floors)]

    def process(self):
        while True:
            start = sim.random.choice(self.choice)  # randomly select the start position
            dest_choice = [x for x in range(self.num_floors) if x != start]  # choice of levels excluding the start position
            dest = sim.random.choice(dest_choice)  # randomly select the destination level

            Person(start=start, dest=dest)  # init an instance of Person
            yield self.hold(5)  # yield control


class Person(sim.Component):
    """
    A class used to represent a Customer inherits from salabim built in component

    ...

    Attributes
    ----------
    id:             A unique id generated for each instance (itertools generator obj.next())
    start_position: The current floor occupied
    destination:    The floor the customer wishes to get to

    requests:       global -> to both People and Elevator dictionary obj ->
                    { key=tuple: (floor obj, direction): val=int: request time }
    levels:         global -> to both People and Elevator [floor obj.... n]
    """
    new_id = itertools.count()

    def __init__(self, start, dest, *args, **kwargs):
        sim.Component.__init__(self, *args, **kwargs)  # initialize sim component as normal
        # set custom obj state
        self.id = next(Person.new_id)  # unique id for each new instance of Person
        self.start = floors[start]
        self.dest = floors[dest]
        self.direction = Person.find_direction(self.start, self.dest)

    @staticmethod
    def find_direction(start, dest):
        """
        Utility function used to find the direction a Person is travelling.

        :param start:
        :param dest:
        :return: int: direction 1:up, -1:down, 0:None
        """
        if start.level_n < dest.level_n:
            return 1
        elif start.level_n > dest.level_n:
            return -1
        else:
            return 0

    def process(self):
        """
        Method is callable directly after the initialisation.
        This has the same behavior as def __call__()
        """
        self.enter(self.start.occupants)

        # priority logic for elevator
        # requests will store { (floor, direction): time }
        # elevator will work of a priority schedule
        if not (self.start, self.direction) in requests:
            requests[self.start, self.direction] = self.env.now()

        for elevator in elevators:
            if elevator.ispassive():  # if the elevator is stationary
                elevator.activate()  # activate the elevator

            yield self.passivate()  # wait for the elevator


class Floor:
    """
    A class used to represent a floor

    Attributes
    ----------
    occupants: salabim queue used to hold People obj on level

    Methods
    -------
    count_occ: checks the number of people currently in the queue for a give direction of travel,
               takes one argument *direction


    """
    def __init__(self, level_n):
        self.occupants = sim.Queue(name=f"People on floor: {level_n}")
        self.level_n = level_n

    def occ_for_direction(self, direction):
        people = 0
        for occ in self.occupants:
            if occ.direction == direction:
                people += 1
        return people


class Elevator(sim.Component):
    """
    A class used to represent an Elevator inherits from salabim built in component

    ...

    Attributes
    ----------
    MAX_LOAD:       static int maximum occupancy
    position:       floor currently being serviced
    direction:      integer value denominates direction 1:up, -1:down, 0:still default=0:still
    t_move:         time taken for elevator to move one level default=10
    t_open          time lapsed for elevator to open default=5
    t_close         time lapsed for elevator to close default=5
    t_enter         time allocated for occupants to enter default=5
    t_exit          time allocated for occupants to exit default=5
    occupants:      sim component queue of people currently occupying available slots
    occ_for_level:  number of occupants for a given level

    requests:       global -> to both People and Elevator
    levels:         global -> to both People and Elevator
    """
    MAX_LOAD: int = 8  # maximum slots allocated for people which people may take up
    LOGIC = ["standard", "priority"]

    def __init__(self, system, position=0, direction=0, t_move=10, t_open=2, t_close=2,
                 t_enter=2, t_exit=2, *args, **kwargs):
        sim.Component.__init__(self, *args, **kwargs)
        self.position = floors[position]  # starting position (level) of the elevator
        self.max_load = Elevator.MAX_LOAD
        self.occupants = sim.Queue(name=f"occupants in lift")
        self.system = Elevator.LOGIC[system]
        # simulation constants defaults given
        self.direction = direction
        self.t_move = t_move
        self.t_open = t_open
        self.t_close = t_close
        self.t_enter = t_enter
        self.t_exit = t_exit
        # elevator doors start off closed
        self.is_open = False

    @staticmethod
    def occ_for_level(occupants, position):
        """
        Utility function to determine if there are people for a given floor
        :param occupants:
        :param position:
        :return: int: number of people for a given floor
        """
        num_people = 0
        for person in occupants:
            if person.dest == position:
                num_people += 1
        return num_people

    @staticmethod
    def has_room(current_occupants, max_load):
        """
        Utility function used to determine if the elevator can except occupants

        :param current_occ:
        :param max_load:
        :return: boolean
        """
        if len(current_occupants) < max_load:
            return True
        return False

    @staticmethod
    def find_direction(current_position, destination):
        """
        Utility function used to find the direction between two positions.

        :param current_position:
        :param destination:
        :return: int: direction 1:up, -1:down, 0:None
        """
        if current_position.level_n < destination.level_n:
            return 1
        elif current_position.level_n > destination.level_n:
            return -1
        else:
            return 0

    def process(self):
        """
        The process function is called after initiation, much in the same way any java main run method would be called.
        This is not a very elegant way of switching between two different elevator strategies, however due to the call
        sequence of salabim setup and process methods it is not possible to use multiple inheritance in the form of a
        base class sim.Component. I had toyed with the idea of using a delegate design pattern but in truth this seems
        over kill and added complexity that would not read well.
        """
        if self.system == Elevator.LOGIC[0]:
            while True:
                if self.direction == 0:
                    if not requests:
                        # simulate passive state
                        yield self.passivate(mode=f"Stationary @ {self.position.level_n}")
                # if we have people for the current level
                if Elevator.occ_for_level(self.occupants, self.position) > 0:
                    yield self.hold(self.t_open, mode=f"Doors opening @ {self.position.level_n}")

                    for person in self.occupants:
                        if person.dest == self.position:
                            person.leave(self.occupants)
                            person.activate()
                    yield self.hold(self.t_exit, mode=f"People exiting @ {self.position.level_n}")

                if self.direction == 0:
                    self.direction = 1

                for self.direction in (self.direction, -self.direction):  # for both directions
                    # check the requests for the current position and directions
                    if (self.position, self.direction) in requests:
                        del requests[self.position, self.direction]  # delete if found in requests

                        if not self.is_open:  # if the door is closed simulate opening and set current state
                            yield self.hold(self.t_open, mode=f"Doors opening {self.position.level_n}")
                            self.is_open = True

                        for person in self.position.occupants:
                            if person.direction == self.direction and Elevator.has_room(self.occupants, self.max_load):
                                # import pdb; pdb.set_trace()
                                person.leave(self.position.occupants)
                                person.enter(self.occupants)
                            yield self.hold(self.t_enter, mode=f"Letting people in @ {self.position.level_n}")

                        if self.position.occ_for_direction(self.direction) > 0:
                            if not (self.position, self.direction) in requests:
                                requests[self.position, self.direction] = self.env.now()

                    if self.occupants:
                        break

                if self.is_open:
                    # if the elevator doors are open then simulate them closing
                    yield self.hold(self.t_close, mode=f"Door closing @ {self.position.level_n}")
                    self.is_open = False  # set state change
                # import pdb; pdb.set_trace()

                if self.direction != 0:  # are we in a moving state
                    # here we are no longer working with priority of requests and so may try to index a floor that does
                    # not exist. Catch the error (KeyError) and invert the direction with abs()
                    try:
                        _next = floors[self.position.level_n + self.direction]  # move up or down depending
                        yield self.hold(self.t_move, mode="Moving")  # simulate the move
                        self.position = _next  # set the current position
                    except KeyError:
                        self.direction == abs(self.direction)

        else:
            while True:
                # import pdb; pdb.set_trace()
                # if the elevator is stationary and has not been requested
                if self.direction == 0:
                    if not requests:
                        # simulate passive state (yield control)
                        yield self.passivate(mode=f"Stationary @ {self.position.level_n}")

                # if we currently have people for this floor
                if Elevator.occ_for_level(self.occupants, self.position) > 0:
                    # simulate opening the door
                    yield self.hold(self.t_open, mode=f"Doors opening @ {self.position.level_n}")
                    self.is_open = True

                    # occupants exit at their floor
                    for person in self.occupants:
                        if person.dest == self.position:
                            person.leave(self.occupants)
                            person.activate()  # the occupant object state is terminated
                            # {mode="") -> to be used in trace
                        # simulate the exit time
                    yield self.hold(self.t_exit, mode=f"People exiting @ {self.position.level_n}")

                if self.direction == 0:
                    self.direction = 1  # reset direction arbitrarily up or down

                for self.direction in (self.direction, -self.direction):  # for both directions
                    # check the requests for the current position and directions
                    if (self.position, self.direction) in requests:
                        del requests[self.position, self.direction]  # delete if found in requests

                        if not self.is_open:  # if the door is closed simulate opening and set current state
                            yield self.hold(self.t_open, mode=f"Doors opening {self.position.level_n}")
                            self.is_open = True

                        for person in self.position.occupants:
                            if person.direction == self.direction and Elevator.has_room(self.occupants, self.max_load):
                                # import pdb; pdb.set_trace()
                                person.leave(self.position.occupants)
                                person.enter(self.occupants)
                            yield self.hold(self.t_enter, mode=f"Letting people in @ {self.position.level_n}")

                        if self.position.occ_for_direction(self.direction) > 0:
                            if not (self.position, self.direction) in requests:
                                requests[self.position, self.direction] = self.env.now()

                    if self.occupants:
                        break
                else:
                    if requests:
                        first_req = sim.inf  # is essentially the same as scheduling for time=inf
                        for (position, direction) in requests:
                            if requests[position, direction] < first_req:  # check priority of the request
                                self.direction = Elevator.find_direction(self.position, position)  # adjust the direction
                                first_req = requests[position, direction]  # set the target request
                    else:
                        self.direction = 0  # if no requests elevator is stationary

                if self.is_open:
                    # if the elevator doors are open then simulate them closing
                    yield self.hold(self.t_close, mode=f"Door closing @ {self.position.level_n}")
                    self.is_open = False  # set state change

                if self.direction != 0:  # are we in a moving state
                    _next = floors[self.position.level_n + self.direction]  # move up or down depending
                    yield self.hold(self.t_move, mode="Moving")  # simulate the move
                    self.position = _next  # set the current position


def main(num_floors=10, num_elevators=1, logic=0, seed=123456):
    env = sim.Environment(random_seed=seed)

    Building(num_floors=num_floors)
    global floors, elevators, requests
    floors = {i: Floor(i) for i in range(num_floors)}
    elevators = [Elevator(system=logic) for _ in range(num_elevators)]
    requests = {}

    env.trace(True)
    env.run(1000)
    env.trace(False)
    for floor in floors.values():
        floor.occupants.reset_monitors()
    env.run(50000)

    with open("db.txt", "w") as f:
        with open('trace.txt', "w") as f_t:
            f_t.write("floor\tpeople\taverage length of stay\n")
            for floor in floors.values():
                f.write(f"{floor.level_n},{floor.occupants.length_of_stay.mean()}\r\n")
                f_t.write(f"{floor.level_n}\t"
                          f"{floor.occupants.length_of_stay.number_of_entries()}"
                          f"{floor.occupants.length.mean():15.3f}"
                          f"{floor.occupants.length_of_stay.mean():15.3f}\r\n")


if __name__ == "__main__":
    """
    Run the script with sys.argv arguments or defaults. Could have used argparse library here which allows to to set 
    flags for argument values. I've used this before but I dont think it is necessary here given this script will only
    ever be run by the controller, error checking from the view will ensure that this script is never run outside of the 
    params defined below. 
    """
    if len(sys.argv) == 5:
        main(num_floors=int(sys.argv[1]), num_elevators=int(sys.argv[2]), logic=int(sys.argv[3]), seed=int(sys.argv[4]))
    else:
        main()

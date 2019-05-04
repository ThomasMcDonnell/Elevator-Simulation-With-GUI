import os


class Controller:

    @staticmethod
    def run_simulation(num_floors=10, num_elevators=1, seed=1234567, logic=0):
        os.system(f"python simulation.py {num_floors} {num_elevators} {logic} {seed}")


if __name__ == "__main__":
    main()

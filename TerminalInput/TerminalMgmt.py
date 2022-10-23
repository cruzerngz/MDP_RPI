import time


class TerminalMgmt:
    def __init__(self, push_to_q):
        self.push_to_q = push_to_q

    def io_android(self):
        print("IN ANDROID :: write 'exit' to go back to main menu.")
        while True:
            message = input("enter message: ")
            if message == 'exit':
                break
            self.push_to_q(f'AND:ALG:{message}')

    def io_car(self):
        print("IN CAR :: write 'exit' to go back to main menu.")
        while True:
            message = input("enter message")
            if message == 'exit':
                break
            self.push_to_q(f'USR:STM:{message}')

    def startIO(self):
        time.sleep(0.1)
        while True:
            print("choose:")
            print("0: exit program")
            print("1: send message to android")
            print("2: send message to car")
            choice = int(input("choose: "))
            if choice == 0:
                break
            elif choice == 1:
                self.io_android()
            elif choice == 2:
                self.io_car()
            else:
                print("input not valid")

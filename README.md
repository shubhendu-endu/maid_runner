# maid_runner

This package is aimed to provide a seamless thread accumulator,
that can execute accumulated threads in three manners, Queue, Pool and Simultaneous Pool.

Once execution has started, it provides with a handle by which the progress
of the accumulator can be tracked live in terms of percentage of work done.

Test PyPI: https://test.pypi.org/project/maid-runner/


Usage:
######

from maid_runner import chorus
from maid_runner import Maid


class Dummy:

    @chorus
    def func1(self):
        print('Thread 1 executed')

    @chorus
    def func2(self):
        print('Thread 2 executed')

    def func3(self):
        print('Thread 3 executed')

    @chorus
    def func4(self):
        print('Thread 4 executed')

    @chorus
    def func5(self):
        print('Thread 5 executed')

    @chorus
    def func6(self):
        print('Thread 6 executed')

    def STAGE_1(self):
        self.func1()
        self.func2()
        self.func3()
        return Maid.start_working()

    def STAGE_2(self):
        self.func4()
        self.func5()
        self.func6()
        return Maid.start_working()


if __name__ == '__main__':
    import time
    obj = Dummy()
    for progress in obj.STAGE_1():
        time.sleep(0.5)
        print('STAGE 1: Progress {}'.format(progress))

    for progress in obj.STAGE_2():
        time.sleep(0.5)
        print('STAGE 2: Progress {}'.format(progress))
       
####
Any method that is supposed to be queued under maid_runner, needs to be decorated with 'chorus'. So whenever that particular method is called, it won't actually execute right and then. It will add it to maid_runner thread accumulator.
Once the request has been assigned to maid_runner via Maid.start_working(), the accumulator will start firing up the thread in designated system ( Queue, Pool, Simultaneous Pool) will provide with a handle to track the work progress.

NOTE: Currently only Queue accumulator system is up and running.
      Pool and Simultaneous Pool are yet to come.

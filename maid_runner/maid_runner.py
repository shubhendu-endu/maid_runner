"""
Created on: 29-May-2020
Author: shubhendu
"""
import threading
# Following are the systems supported
QUEUE = 0
SIMULTANEOUS = 1
SIMULTANEOUS_POOL = 2


def chorus(function):
    def execute(*args, **kwargs):
        Maid.push_thread(function, *args, **kwargs)
        OverAllThreadData.increase_thread_count()
    return execute


class PropagatingThread(threading.Thread):
    def run(self):
        self.exc = None
        try:
            if hasattr(self, '_Thread__target'):
                # Thread uses name mangling prior to Python 3.
                self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            else:
                self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self):
        super(PropagatingThread, self).join()
        if self.exc:
            raise self.exc
        return self.ret


class OverAllThreadData:
    __thread_count = 0

    @staticmethod
    def increase_thread_count():
        OverAllThreadData.__thread_count += 1

    @staticmethod
    def get_overall_count():
        return OverAllThreadData.__thread_count

    @staticmethod
    def clear_data():
        OverAllThreadData.__thread_count = 0


class CurrentThreadData:
    __data_dict = dict()

    @staticmethod
    def set_data(data_dict):
        CurrentThreadData.__data_dict.update(**data_dict)

    @staticmethod
    def get_data():
        return CurrentThreadData.__data_dict

    @staticmethod
    def clear_data():
        CurrentThreadData.__data_dict = dict()


class LastThreadData:
    __thread_id = None

    @staticmethod
    def set_thread_id(thread_id):
        LastThreadData.__thread_id = thread_id

    @staticmethod
    def get_thread_id():
        return LastThreadData.__thread_id


class Maid:
    __thread_queue = dict()
    __thread_pool = dict()
    __thread_system = 0
    __response_handlers = dict()  # Mapped with thread id in thread_queue/thread_pool

    threads = {
                0: __thread_queue,
                1: __thread_pool,
                2: __thread_pool
              }

    @staticmethod
    def __reset_data():
        for key in Maid.threads:
            Maid.threads[key] = dict()

        LastThreadData.set_thread_id(None)
        CurrentThreadData.clear_data()
        OverAllThreadData.clear_data()

    @staticmethod
    def __get_storage():
        return Maid.threads[Maid.__thread_system]

    @staticmethod
    def __set_thread(thread_function):
        storage = Maid.__get_storage()
        current_length = len(storage)
        storage[current_length] = thread_function
        return current_length

    @staticmethod
    def __get_thread(thread_id):
        storage = Maid.__get_storage()
        return storage[thread_id]

    @staticmethod
    def __get_next_thread_id():
        all_thread_id = Maid.__get_all_thread_id()
        if all_thread_id:
            return min(all_thread_id)
        else:
            return -1

    @staticmethod
    def __get_all_thread_count():
        all_thread_id = Maid.__get_all_thread_id()
        return len(all_thread_id)

    @staticmethod
    def __get_all_thread_id():
        storage = Maid.__get_storage()
        all_thread_id = list(storage.keys())
        return all_thread_id

    @staticmethod
    def __get_response_handler(thread_id):
        if thread_id in Maid.__response_handlers:
            return Maid.__response_handlers[thread_id]
        else:
            return False

    @staticmethod
    def __set_response_handler(thread_id, resp_handler):
        Maid.__response_handlers[thread_id] = resp_handler
        return True

    @staticmethod
    def __remove_thread(thread_id):
        storage = Maid.__get_storage()
        if not storage[thread_id].isAlive():
            try:
                storage[thread_id].join()
            except BaseException as e_excp:
                Maid.__reset_data()
                raise e_excp
            del storage[thread_id]
            return True
        else:
            return False

    @staticmethod
    def __set_thread_system(system):
        Maid.__thread_system = system

    @staticmethod
    def __get_thread_system():
        return Maid.__thread_system

    @staticmethod
    def __kick_off_thread():
        thread_id = LastThreadData.get_thread_id()
        thread_func = Maid.__get_thread(thread_id)
        thread_func.start()

    @staticmethod
    def push_thread(func, *args, **kwargs):
        thread_function = PropagatingThread(target=func, args=(*args,), kwargs=kwargs)
        thread_id = Maid.__set_thread(thread_function)
        return thread_id

    @staticmethod
    def __pop_thread(thread_id):
        return Maid.__remove_thread(thread_id)

    @staticmethod
    def __assign_response_handler(thread_id, resp_handler):
        if thread_id in Maid.__get_all_thread_id():
            if not Maid.__get_response_handler(thread_id):
                Maid.__set_response_handler(thread_id, resp_handler)
                return True
            else:
                print('Response handler already assigned for given thread id: {}'.format(thread_id))
        else:
            print('Thread Id: {} not found for Response Handler assignment')
        return False

    @staticmethod
    def __check_thread_status(thread_id):
        if thread_id in Maid.__get_all_thread_id():
            return Maid.__get_thread(thread_id).isAlive()

    @staticmethod
    def __stop_thread_execution():
        # Will be better suited only for QUEUE system
        pass

    @staticmethod
    def start_working():
        if Maid.__get_thread_system() == QUEUE:
            return Maid.__start_thread_execution_queue()

    @staticmethod
    def __get_progress_percentage():
        threads_in_storage = Maid.__get_all_thread_count()
        threads_added_overall = OverAllThreadData.get_overall_count()

        try:
            # When no thread has been added in the queue we expect ZeroDivisionError
            progress_percentage = ((threads_added_overall - threads_in_storage) / (threads_added_overall)) * 100
        except ZeroDivisionError:
            progress_percentage = 100
        return progress_percentage

    @staticmethod
    def __allocate_new_thread_for_kickoff():
        storage_free = True
        thread_allocated = False

        last_thread_id = LastThreadData.get_thread_id()

        if last_thread_id is not None:
            if Maid.__check_thread_status(last_thread_id):  # Not to proceed in this case
                storage_free = False
            else:
                Maid.__pop_thread(last_thread_id)

        next_thread_id = Maid.__get_next_thread_id()  # Get the id of next thread in Queue

        if storage_free:
            if next_thread_id != -1:
                LastThreadData.set_thread_id(next_thread_id)
                thread_allocated = True
        return thread_allocated

    @staticmethod
    def __start_thread_execution_queue():
        break_execution = False
        while not break_execution:
            if Maid.__allocate_new_thread_for_kickoff():
                Maid.__kick_off_thread()
            progress_percentage = Maid.__get_progress_percentage()

            if progress_percentage == 100:
                Maid.__reset_data()
                break_execution = True
            yield progress_percentage

    @staticmethod
    def __pause_thread_execution():
        pass

    @staticmethod
    def __set_thread_execution_system(system_value: int):
        if type(system_value) != int:
            raise NotImplementedError('Enter a valid system_value')
        else:
            if system_value not in [QUEUE, SIMULTANEOUS, SIMULTANEOUS_POOL]:
                raise ValueError('Please check the valid thread execution system-> 0: Queue, 1: Simultaneous, '
                                 '2: Simultaneous Pool')
            else:
                Maid.__set_thread_system(system_value)
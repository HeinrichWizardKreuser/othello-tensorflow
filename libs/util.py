import sys, datetime, time

class ProgressBar(object):
    def __init__(self, to_complete, time_start=None):
        self.completed = 0
        self.to_complete = to_complete
        if time_start == None:
            self.time_start = time.time()
        else:
            self.time_start = time_start
        update_progress(self.completed, self.to_complete, self.time_start)
    def update(self):
        self.completed += 1
        update_progress(self.completed, self.to_complete, self.time_start)
    def finish(self):
        update_progress(self.to_complete, self.to_complete, self.time_start)
        


def update_progress(completed: int, to_complete: int, time_start=None):
    ''' Displays a progress bar using the given amount already finished and the
        total amount to complete

    @param completed the amount that has already been completed
    @param to_complete the total amount that must be completed
    '''
    total_bars = 20
    sys.stdout.write('\r')
    if to_complete == 0:
        percentage = 1
    else:
        percentage = completed/to_complete
    bars = round(percentage * total_bars)
    notbars = total_bars - bars
    s = f"|{chr(9608)*bars}{' '*notbars}| {round(percentage*100, 2):<5}%"
    if time_start != None and completed != 0 and completed != to_complete:
        time_so_far = time.time() - time_start
        rate = time_so_far / completed
        time_left = rate * (to_complete - completed)
        s += datetime.datetime.utcfromtimestamp(time_left).strftime(" | eta %X") 
    sys.stdout.write(s)
    sys.stdout.flush()
    if completed == to_complete:
        print()


class TimeLeftEstimator(object):
    """ Helps with estimating the time left for running processes"""
    def __init__(self, curr_gen, max_gens):
        self.curr_gen = curr_gen
        self.init_gen = curr_gen
        self.max_gens = max_gens + 1
        self.alpha = time.time() # the time this process was started
        self.gen_time = time.time()
    def update(self):
        self.curr_gen += 1
        if self.curr_gen > self.max_gens:
            print(f"ETA: Finished")
            return
        # report how long the previous gen took
        self._report_prev_time()
        # get the time left
        seconds_left = self._calc_time_left()
        # report estimations
        finish_date = (datetime.datetime.now() + \
                       datetime.timedelta(seconds=seconds_left))
        print(f"Estimated to finish at:", 
            finish_date.strftime('%Y-%m-%d %X.%f'))
        print(f"ETA:", finish_date - datetime.datetime.now())
    
    def _report_prev_time(self):
        prev_gen_time = time.time() - self.gen_time
        self.gen_time = time.time() # reset for next time
        print(f"time elapsed:", 
            datetime.datetime.utcfromtimestamp(prev_gen_time).strftime('%X'))

    def _calc_time_left(self):
        # calc ave time
        total_num = self.curr_gen - self.init_gen
        total_time = time.time() - self.alpha
        ave_time = total_time / total_num
        # calc estimated time to finishing
        return ave_time * (self.max_gens - self.curr_gen)


# class TimeLeftEstimator(object):
#     def __init__(self, cycle_num, max_cycles):
#         self.session_cycles = 0
#         self.session_time = 0
#         self.max_cycles = max_cycles
#         self.cycle_num = cycle_num
#         self.alpha = time.time()
#     def update(self):
#         self.cycle_num += 1
#         self.session_cycles += 1
#         generation_time = time.time() - self.alpha
#         self.session_time += generation_time
#         print(f"~ {generation_time}s")
#         ave_generation_time = self.session_time/self.session_cycles
#         print(f"average time: {ave_generation_time}s")
#         if self.cycle_num <= self.max_cycles:
#             seconds_left = ave_generation_time * (self.max_cycles - self.cycle_num)
#             seconds = seconds_left
#             if seconds_left < 60 * 60 * 24:
#                 fmt = '%X'
#             else:
#                 seconds -= 60 * 60 * 24
#                 fmt = '%d days %X'
#             s = datetime.datetime.utcfromtimestamp(seconds).strftime(fmt)
#             print(f"ETA to {self.max_cycles}: {s}")
#             finish_date = (datetime.datetime.now() + \
#                            datetime.timedelta(seconds=seconds_left))
#             s = finish_date.strftime('%Y-%m-%d %X.%f')
#             print(f"Estimated to finish at: {s}")
#         self.alpha = time.time()


def distributed_elements(seq, num):
    ''' returns a list of num elements from list seq
    e.g.:
    >>> lis = [0, 1, 2, 3, 4, 5, 6]
    >>> distributed_elements(lis, 3)
    [0, 3, 6]
    Mainly used to distribute colors from a palette (list of colors)
    '''
    seq, z = seq[:-1], seq[-1]
    num -= 1
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last)])
        last += avg
    return out + [z]


color_codes = {
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'BLUE': '\033[34m',
    'ENDC': '\033[0m',
    'UNDERLINE': '\033[4m',
}

# GREEN_ARROW = color_text(chr(0x25b2), 'GREEN')
# RED_ARROW = color_text(chr(0x25bc), 'RED')
# BLUE_ARROW = color_text(chr(0x25b6), 'BLUE')

def color_text(s: str, color_str: str):
    """ colors the given string in the given color """
    return f"{color_codes[color_str]}{s}\033[0m"


import pickle
def pickle_dump(data, filename):
    file = open(filename, 'wb')
    pickle.dump(data, file)
    file.close()
def pickle_load(filename):
    file = open(filename, 'rb')
    data = pickle.load(file)
    file.close()
    return data
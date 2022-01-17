import numpy
import time

MIN_TEMPO_TAPS = 4 # how many taps are needed (within 2 stdev) to calc tempo

class Tempo:
    def __init__(self, bpm, info=lambda _: None):
        self.bpm = bpm
        self.reset()
        self.info = info

    def reset(self):
        self.tap_times = []
    
    def tap(self):
        # mark the time
        self.tap_times.append(time.time())
        
        if len(self.tap_times) > 2:
            # calculate deltas
            tap_deltas = numpy.array([stop-start for start, stop in zip(self.tap_times[:-1], self.tap_times[1:])])
            avg = numpy.average(tap_deltas)
            
            # filter out outliers
            boundary = tap_deltas.std() * 2
            tap_deltas = numpy.array(list(filter(lambda d: (d<avg+boundary and d>avg-boundary), tap_deltas)))

            # update the tempo
            if len(tap_deltas) >= MIN_TEMPO_TAPS:
                # avg tempo
                avg_delta = numpy.average(tap_deltas)

                # median tempo
                median_delta = numpy.median(tap_deltas)

                # selected tempo
                target_delta = (avg_delta + median_delta) / 2
                
                self.bpm = round(60/target_delta) # delta to bpm
                self.info(f"tempo set to {self.bpm} bpm")

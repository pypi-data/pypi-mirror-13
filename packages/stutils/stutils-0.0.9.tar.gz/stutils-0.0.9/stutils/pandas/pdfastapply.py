import pandas as pd
import numpy as np
import multiprocessing as mp

class PdFastApply:
    def __init__(self):
        self.mgr = mp.Manager()
        self.ns = self.mgr.Namespace()
        self.ns.df = pd.DataFrame()
        self.process_number_max = mp.cpu_count()
        self.process_list = []
        self.df_list = []
        self.flag = mp.Semaphore(1)

    def rep(self):
        print "Number max process: {}".format(self.process_number_max)
        print "Number splits: {}".format(str(len(self.df_list)))
        print "Number current process: {}".format(self.count_running_process())

    def run_processing(self, df, f, name):
        df[name] = df.apply(f, axis=1)
        with self.flag:
            self.ns.df = self.ns.df.append(df)

    def df_split(self, df):
        for a in np.array_split(df, self.process_number_max):
            self.df_list.append(a)

    def df_apply(self, f, name):
        process_number = 0
        while process_number < self.process_number_max:
            p = mp.Process(target=self.run_processing, args=(self.df_list[process_number], f, name))
            self.process_list.append(p)
            p.start()
            process_number += 1

    def df_get(self):
        if len(self.process_list) != 0:
            print "Current process: {}".format(self.count_running_process())
        else:
            return self.ns.df

    def count_running_process(self):
        if len(self.process_list) != 0:
            count = 0
            for p in self.process_list:
                if p.is_alive():
                    count += 1
            return count
        return 0

    def kill_process(self):
        for p in self.process_list:
            p.terminate()

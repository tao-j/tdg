import multiprocessing as mp
from tqdm import tqdm
from evolve import *
import h5py

periods = [1]
n_period = 3
root_len = 10

n_dist = 4096  # num of dists
n_sample = 16  # num of samples per dist
# n_dataset = 10 # num of dataset being generated
data_len = range(1024, 1025, 32)


n_requesters = 1
n_workers = 1
n_workers = max(1, mp.cpu_count() - n_requesters - 1)
# SequenceClass = SequenceDup
SequenceClass = SequenceDupDel
seq_name = SequenceClass.__name__
filename = f"up{','.join(periods)}{seq_name}.train"


def gen_requests(request, target_len):
    for pi, period in enumerate(periods):
        output_size = period * n_period + 2
        for di in range(n_dist):
            p = SequenceClass.gen_dist(period, n_period, output_size)
            request.put([p, target_len])


def gen_samples(requests, output):
    # P = randdist_period_size_del(period, n_period, output_size)
    # s = SequenceDup(np.random.randint(4, size=root_len), target_len, P[0:output_size])
    for args in iter(requests.get, None):
        p, target_len = args
        for _ in range(n_sample):
            s = SequenceClass(np.random.randint(4, size=root_len), target_len, p)
            x = s.evolve()
            output.put([x, p])


def main():
    print("filename:", filename)
    f_trainX = h5py.File("data/" + filename + "X", "w")
    f_trainY = h5py.File("data/" + filename + "Y", "w")

    for target_len in data_len:
        print(f"n_dist {n_dist} len: {target_len} np: {n_period} times: {n_sample}")
        in_queue = mp.Queue()
        out_queue = mp.Queue()
        jobs = []

        requester = mp.Process(target=gen_requests, args=(in_queue, target_len))
        requester.start()

        for _ in range(n_workers):
            pw = mp.Process(target=gen_samples, args=(in_queue, out_queue))
            jobs.append(pw)
            pw.start()

        n_data = n_sample * n_dist * len(periods)
        X = np.empty(shape=(n_data, target_len, 4), dtype=np.int8)
        Y = np.empty(shape=(n_data, max(periods) * n_period + 2), dtype=np.float16)
        for k in tqdm(range(n_data)):
            x, P = out_queue.get()
            if x is not None:
                X[k] = seqto4rowmx(x)
                Y[k] = P
            else:
                break

        requester.join()
        for _ in range(n_workers):
            in_queue.put(None)
        for pw in jobs:
            pw.join()
        f_trainX.create_dataset("X_" + str(target_len), data=X)
        f_trainY.create_dataset("Y_" + str(target_len), data=Y)
        print("dataset_length", target_len, "stored")

    f_trainX.close()
    f_trainY.close()

    # %%
    log = open(f"data/{filename}.txt", 'w')
    log.write("Dataset Name: " + filename + "\n")
    # if deletion == True:
    #    log.write(" del prob = " + str(alpha) + " ")
    log.write("Ndist = " + str(n_dist) + "\n")
    log.write("Nsample = " + str(n_sample) + "\n")
    log.write("dataset length=" + str(data_len) + "\n")
    log.write("period=" + str(periods) + "\n")
    log.write("\n")
    log.close()


if __name__ == "__main__":
    main()

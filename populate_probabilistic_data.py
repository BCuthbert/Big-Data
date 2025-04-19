import simpy
import random
import pandas as pd
from multiprocessing import Pool

# === Simulation parameters ===
NUM_SENSORS   = 1000
UNCERTAINTY_RATE = 0.1
QUERY_SUBSET_SIZE = 100
TARGET_QUALITY   = 0.9
BANDWIDTHS       = [200, 350, 500]
ARRIVAL_RATES    = [5, 20, 45]
POLICIES         = ['Glb_RR', 'Loc_RR', 'MinMin', 'MaxUnc', 'MinExpEntropy']
NUM_TRIALS       = 5

def run_simulation(policy, bandwidth, arrival_rate, trial):
    """Run one SimPy trial and return a list of metric dicts."""
    env = simpy.Environment()
    # Initialize uncertainties and last_update arrays...
    # This is shown in the '03 paper using baseline values.
    uncertainties = [(0.0, 0.0)] * NUM_SENSORS
    last_update  = [0.0] * NUM_SENSORS
    metrics = []

    def generate_queries():
        while True:
            yield env.timeout(random.expovariate(arrival_rate))
            env.process(handle_query())

    def handle_query():
        start = env.now
        subset = random.sample(range(NUM_SENSORS), QUERY_SUBSET_SIZE)
        updates = 0
        while True:
            # Placeholder for actual quality computation
            quality = random.random()
            avg_unc = sum(u[1]-u[0] for u in uncertainties) / NUM_SENSORS
            if quality >= TARGET_QUALITY or updates >= 5:
                metrics.append({
                    'policy': policy,
                    'bandwidth': bandwidth,
                    'arrival_rate': arrival_rate,
                    'trial': trial,
                    'run_time': env.now - start,
                    'quality': quality,
                    'avg_uncertainty': avg_unc
                })
                return
            # Select and update sensor based on policy...
            if policy == 'MinMin':
                idx = min(range(NUM_SENSORS), key=lambda i: uncertainties[i][0])
            elif policy == 'MaxUnc':
                idx = max(range(NUM_SENSORS), key=lambda i: uncertainties[i][1] - uncertainties[i][0])
            elif policy == 'Glb_RR':
                idx = (updates) % NUM_SENSORS
            elif policy == 'Loc_RR':
                idx = subset[updates % len(subset)]
            else:
                idx = random.choice(subset)

            uncertainties[idx] = (0.0, 0.0)
            last_update[idx] = env.now
            updates += 1
            yield env.timeout(1.0 / bandwidth)

    env.process(generate_queries())
    env.run(until=1000)
    return metrics

def simulate_setting(args):
    """Unpack args tuple and run simulation, returning its metrics."""
    return run_simulation(*args)

def main():
    # Build list of all parameter tuples
    params = [
        (policy, bw, ar, trial)
        for bw in BANDWIDTHS
        for ar in ARRIVAL_RATES
        for policy in POLICIES
        for trial in range(NUM_TRIALS)
    ]

    # runs very slow without using CPU pool => separates program into processes to run quicker. 
    with Pool() as pool:
        all_results = pool.map(simulate_setting, params)

    # Flatten metrics lists and save
    flat_results = [m for sublist in all_results for m in sublist]
    df = pd.DataFrame(flat_results)
    df.to_csv('simulation_results.csv', index=False)
    print("Done. CSV contains", len(df), "rows.")

if __name__ == '__main__':
    main()


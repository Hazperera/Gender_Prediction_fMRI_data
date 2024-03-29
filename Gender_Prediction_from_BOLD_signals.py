#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: Gender_Prediction_from_BOLD_signals.py
# Authors: Hasani Perera, Ricardo Luévano
# Contact: heperera826@gmail.com
# Date created: 25/07/2021
# Date last modified: 25/10/2021
# Python Version: 3.9
# Project: Predicting gender from task-based BOLD signal using logistic regression
# Dataset: The HCP/NMA-curated dataset comprises task-based fMRI from a sample of 339 human subjects

# import libraries
import os
import re
import cmd
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#@title Figure settings
# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'
plt.style.use("https://raw.githubusercontent.com/NeuromatchAcademy/course-content/master/nma.mplstyle")

## Basic parameters

# Load HCP parcellated task data

HCP_DIR = "./hcp"
if not os.path.isdir(HCP_DIR):
  os.mkdir(HCP_DIR)

# The data have already been aggregated into ROIs from the Glasser parcellation
N_PARCELS = 360

# The acquisition parameters for all tasks were identical
TR = 0.72  # Time resolution, in seconds

# The parcels are matched across hemispheres with the same order
HEMIS = ["Right", "Left"]

# Each experiment was repeated twice in each subject
RUNS   = ['LR','RL']
N_RUNS = 2

# The dataset for the SOCIAL experiment also includes mental_resp and other_resp
CONDITIONS = ['mental','rnd']

# All these names are needed to get the right index for the timeseries.
BOLD_NAMES = [
  "rfMRI_REST1_LR", "rfMRI_REST1_RL",
  "rfMRI_REST2_LR", "rfMRI_REST2_RL",
  "tfMRI_MOTOR_RL", "tfMRI_MOTOR_LR",
  "tfMRI_WM_RL", "tfMRI_WM_LR",
  "tfMRI_EMOTION_RL", "tfMRI_EMOTION_LR",
  "tfMRI_GAMBLING_RL", "tfMRI_GAMBLING_LR",
  "tfMRI_LANGUAGE_RL", "tfMRI_LANGUAGE_LR",
  "tfMRI_RELATIONAL_RL", "tfMRI_RELATIONAL_LR",
  "tfMRI_SOCIAL_RL", "tfMRI_SOCIAL_LR"
]

# Downloading data

fname = "hcp_task.tgz"
if not os.path.exists(fname):
  !wget -qO $fname https://osf.io/s4h8j/download/
  !tar -xzf $fname -C $HCP_DIR --strip-components=1

#List with IDs for the 339 subjects

str_ids_339 = """
              199453  517239  118124  898176  107321  816653  110411  110007  955465  203923
              580751  154734  146937  414229  833249  182436  150625  178950  152831  744553
              173435  957974  966975  930449  194645  310621  188549  663755  130316  133019
              919966  116524  198855  298051  144731  459453  139839  587664  100206  679568
              181636  297655  188751  149842  154835  679770  576255  112314  181131  380036
              192843  109830  139233  173940  186141  110613  465852  618952  106016  377451
              894067  432332  567052  108222  123117  135730  176037  449753  656253  200008
              174437  134728  134223  175035  825048  907656  154229  479762  101006  191033
              159138  656657  529549  371843  173536  877269  257845  994273  849971  204622
              144125  105115  849264  209228  599671  559053  128632  397760  611938  645450
              162329  729557  163836  141119  149539  200311  100610  393247  627549  792867
              667056  604537  657659  200614  633847  127630  205119  638049  149236  510326
              183034  137633  580044  361941  189450  865363  201515  984472  132017  155635
              300618  947668  660951  124422  140117  101915  597869  159441  214423  303119
              159340  202719  169949  124826  158035  163331  293748  499566  318637  211316
              561444  103818  161731  146533  133827  155938  173839  112112  194746  175439
              212419  198249  749058  137229  192035  386250  138231  164030  835657  894774
              812746  162733  524135  952863  352132  211922  433839  598568  397154  248339
              135528  151627  131823  221319  150928  695768  837560  562345  803240  153227
              170631  130013  130417  295146  192136  702133  530635  725751  304727  118528
              250427  555651  201111  316835  103515  753150  164939  671855  268850  581349
              257542  923755  495255  214221  833148  208327  255639  112920  175237  195445
              131217  102311  899885  179346  188448  214019  585256  901442  175742  175338
              171633  154532  285446  108121  134021  211215  207123  122822  770352  146129
              129028  206222  103414  622236  113619  800941  172938  149337  664757  113922
              146432  573249  316633  168240  912447  136833  748258  102513  159239  756055
              789373  654754  107422  220721  769064  987983  529953  203418  195849  186444
              250932  889579  724446  553344  654350  208125  148133  872562  690152  715950
              616645  141826  782561  180129  173738  993675  121416  181232  387959  147030
              213421  672756  204521  160830  129634  599065  395756  393550  195950  210415
              381038  233326  185139  167238  299154  735148  731140  309636  308331  139637
              555348  228434  135932  157942  136732  520228  820745  204319  567961  134425
              119126  395251  187345  922854  197348  412528  436845  525541  568963  101309
              185442  154936  227432  336841  214524  571144  212015  199958  129129
              """

# List of subjects's ID (str type), used to access the DataFrame's rows.
subjects_str = re.findall(r"[\w']+", str_ids_339)

# List of subjects's ID (int type), used for everything else.
SUBJECTS   = [int(i) for i in subjects_str]
N_SUBJECTS = len(SUBJECTS)

# Loading subjects's behavior information

# Retrieved from http://www.humanconnectomeproject.org/ and uploaded to a public repository for easy access.
url = "https://raw.githubusercontent.com/Luevateros/neuromatch_neuroscience/main/projects/resources/Demographics_HCP_7_7_2021_0_3_48.csv"
all_subjects = pd.read_csv(url)

# Retrieve only the subjects of interest
unsorted_subjects = all_subjects.loc[all_subjects['Subject'].isin(subjects_str)]


subjects_in_order = []
# Subjects in the same order as in ids
for id in SUBJECTS:
  subjects_in_order.append(unsorted_subjects.loc[unsorted_subjects['Subject'] == id])

# The subjects of interest are in the same order as in the NMA-curated dataset
SUBJECTS_BEHAVIOR = pd.concat(subjects_in_order, keys=list(range(N_SUBJECTS+1)))

# Remove index column that remained from the original dataframe
SUBJECTS_BEHAVIOR.index = SUBJECTS_BEHAVIOR.index.droplevel(-1)

# Find columns with NaN values
columns_with_nans = []
for column, columnData in SUBJECTS_BEHAVIOR.iteritems():
  if SUBJECTS_BEHAVIOR[column].isnull().values.any():
    columns_with_nans.append(column)

# Remove columns with NaN values (before 582, after 489 columns)
for column in columns_with_nans:
  del(SUBJECTS_BEHAVIOR[column])

# See all the features available in SUBJECTS_BEHAVIOR
features = list(SUBJECTS_BEHAVIOR.columns)
# cmd.Cmd().columnize(features, displaywidth=80)  # <-- Uncomment to see all features !!!

# Loading region information
#This dataset contains region name and network assignment for each parcel.
#Detailed information about the name used for each region is provided [in the Supplement]
#(https://static-content.springer.com/esm/art%3A10.1038%2Fnature18933/MediaObjects/41586_2016_BFnature18933_MOESM330_ESM.pdf) to [Glasser et al. 2016](https://www.nature.com/articles/nature18933).
#Information about the network parcellation is provided in [Ji et al, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6289683/).

regions = np.load(f"{HCP_DIR}/regions.npy").T
region_info = dict(
    name=regions[0].tolist(),
    network=regions[1],
    hemi=['Right']*int(N_PARCELS/2) + ['Left']*int(N_PARCELS/2),
)

NETWORKS = set(region_info['network'])
ROIs     = region_info['name']

# Help functions

# Data loading functions

# Function: Get the 1-based image indices for runs in a given experiment

def get_image_ids(experiment):
  """
  Get the 1-based image indices for runs in a given experiment.

    Args:
      experiment (str) : Name of experiment to load

    Returns:
      run_ids (list of int) : Numeric ID for experiment image files
  """

  run_ids = [ i for i, code in enumerate(BOLD_NAMES, 1) if experiment.upper() in code ]
  if not run_ids:
    raise ValueError(f"Found no data for '{experiment}''")
  return run_ids

#Function: Load timeseries data for a single subject

def load_timeseries(subject, experiment, runs=None, concat=True, remove_mean=True):
  """
  Load timeseries data for a single subject.
  
  Args:
    subject (int): 0-based subject ID to load
    experiment (str) : Name of experiment to load
    run (None or int or list of ints): 0-based run(s) of the task to load,
      or None to load all runs.
    concat (bool) : If True, concatenate multiple runs in time
    remove_mean (bool) : If True, subtract the parcel-wise mean

  Returns
    ts (n_parcel x n_tp array): Array of BOLD data values

  """
  # Get the list relative 0-based index of runs to use
  if runs is None:
    runs = range(N_RUNS)
  elif isinstance(runs, int):
    runs = [runs]


  # Get the first (1-based) run id for this experiment 
  offset = get_image_ids(experiment)[0]

  # Load each run's data
  bold_data = [
      load_single_timeseries(subject, offset + run, remove_mean) for run in runs
  ]

  # Optionally concatenate in time
  if concat:
    bold_data = np.concatenate(bold_data, axis=-1)

  return bold_data

#Function: Load timeseries data for a single subject and single run

def load_single_timeseries(subject, bold_run, remove_mean=True):
  """
  Load timeseries data for a single subject and single run.
  
  Args:
    subject (int): 0-based subject ID to load
    bold_run (int): 1-based run index, across all tasks
    remove_mean (bool): If True, subtract the parcel-wise mean

  Returns
    ts (n_parcel x n_timepoint array): Array of BOLD data values

  """

  bold_path = f"{HCP_DIR}/subjects/{subject}/timeseries"
  bold_file = f"bold{bold_run}_Atlas_MSMAll_Glasser360Cortical.npy"
  ts = np.load(f"{bold_path}/{bold_file}")
  
  # # Compute z-score
  # for parcel in range(ts.shape[0]):
  #   parcel_mean = np.mean(ts[parcel])
  #   parcel_std  = np.std(ts[parcel])
  #   # For each entry
  #   for tp in range(ts.shape[1]):
  #     ts[parcel][tp] = (ts[parcel][tp] - parcel_mean)/parcel_std

  if remove_mean:
    ts -= ts.mean(axis=1, keepdims=True)

  return ts

#Function: Load EV (explanatory variable) data for one task condition

def load_evs(subject, experiment, condition):
  """
  Load EV (explanatory variable) data for one task condition.

  Args:
    subject (int): 0-based subject ID to load
    experiment (str) : Name of experiment
    condition (str) : Name of condition

  Returns
    evs (list of dicts): A dictionary with the onset, duration, and amplitude
      of the condition for each run.

  """
  evs = []
  for id in get_image_ids(experiment):
    task_key = BOLD_NAMES[id - 1]
    ev_file = f"{HCP_DIR}/subjects/{subject}/EVs/{task_key}/{condition}.txt"
    ev_array = np.loadtxt(ev_file, ndmin=2, unpack=True)
    ev = dict(zip(["onset", "duration", "amplitude"], ev_array))
    evs.append(ev)
  return evs

#Function: Get the indexes of all regions (parcels) of a network

def network_indexes(net):

  index_list = []
  networks   = region_info['network']

  if net not in networks:
    raise ValueError(f"There's no network named '{net}'")

  for i, network in enumerate(region_info['network']):
    if net == network:
      index_list.append(i)

  return index_list

#Function: Get regions (parcels) names of a network

def get_regions_names(indexes):
  names = region_info['name']
  return [names[i] for i in indexes]

#Task-based analysis

#Function: Identify timepoints corresponding to a given condition in each run

def condition_frames(run_evs):
  """
  Identify timepoints corresponding to a given condition in each run.

  Args:
    run_evs (list of dicts) : Onset and duration of the event, per run

  Returns:
    frames_list (list of 1D arrays): Flat arrays of frame indices, per run

  """
  frames_list = []
  for ev in run_evs:

    # Determine when trial starts, rounded down
    start = np.floor(ev["onset"] / TR).astype(int)

    # Use trial duration to determine how many frames to include for trial
    duration = np.ceil(ev["duration"] / TR).astype(int)

    # Take the range of frames that correspond to this specific trial
    frames = [s + np.arange(0, d) for s, d in zip(start, duration)]

    frames_list.append(np.concatenate(frames))

  return frames_list

#Function: Select the frames from each image. 
#Returns a list with two numpy arrays, one for each condition. Each entry of any numpy array corresponds to a matrix (360, 274) of 360 parcels, 274 time points.


def select_frames(timeseries_data, ev):
  """
  Select the frames from each image.

  Args:
    timeseries_data (array or list of arrays): n_parcel x n_tp arrays
    ev (dict or list of dicts): Condition timing information

  Returns:
    selected_data (1D array): Selected image frames based on condition timing.


  Structure:  
    selected_data[condition][roi][time_point]
              ^       ^       ^       ^
    type:   list   (360,c)   (c, )   float   


  Important for SOCIAL:   
    selected_data[0]    NumPy matrix for 'mental'   run_0: 64 tp, run_1: 96 tp
    selected_data[1]    NumPy matrix for 'rnd'      run_0: 96 tp, run_1: 64 tp

  To compare different conditions (with same tp):
  >>> two_runs = [select_frames(timeseries_social[subject], ev) for ev in evs]
  >>> compare(two_runs[0][0], two_runs[1][1])
                        ^                ^
                   run_0/mental     run_1/rnd     <--- Same # of tp

  Beware:
    Subject 3 and 98 show the following   run_0:  96 tp (both conditions)
                                          run_1:  64 tp (both conditions)
  Exclude them before
  """

  # Ensure that we have lists of the same length
  if not isinstance(timeseries_data, list):
    timeseries_data = [timeseries_data]
  if not isinstance(ev, list):
    ev = [ev]
  if len(timeseries_data) != len(ev):
    raise ValueError("Length of `timeseries_data` and `ev` must match.")

  # Identify the indices of relevant frames
  frames = condition_frames(ev)

  # Select the frames from each image
  selected_data = []
  for run_data, run_frames in zip(timeseries_data, frames):
    run_frames = run_frames[run_frames < run_data.shape[1]]
    selected_data.append(run_data[:, run_frames])

  return selected_data

#Function: Load a concatenated timeseries
#For an experiment (using all runs' data) for each subject.


def get_timeseries(experiment, concat=False):
  
  timeseries = []

  for subject in range(N_SUBJECTS):
    ts_concat = load_timeseries(subject, experiment, concat=concat)
    timeseries.append(ts_concat)  

  return timeseries

#Function: Gets BOLD signal in each region/condition/subject

def get_BOLD(time_series, experiment):
  
  all_BOLDs = []
  for subject in range(N_SUBJECTS):
    evs  = [load_evs(subject, experiment, cond) for cond in CONDITIONS]
    data = [select_frames(time_series[subject], ev) for ev in evs]
    all_BOLDs.append(data)

  return all_BOLDs

#Function:Reduces the excess of BOLD signals timepoints for conditions with different size.

def remove_excess(data, run):

  new_data = []

  # Get the number of timepoints per condition
  tps_c_0 = data[0][run][0].shape[1]
  tps_c_1 = data[0][run][1].shape[1]

  # Stop when both conditions have same number of timepoints
  if tps_c_0 == tps_c_1:
      return data

  # Get the number of timepoints to reduce and in which
  # 'condition' should be reduced.
  if tps_c_0 < tps_c_1:
    tps_to_reduce = tps_c_1 - tps_c_0
    remove_condition = True
  else: 
    tps_to_reduce = tps_c_0 - tps_c_1
    remove_condition = False

  # Start reduction.
  for subject in range(N_SUBJECTS):

    parcel_tps_cond_0 = data[subject][run][0]
    parcel_tps_cond_1 = data[subject][run][1]

    for _ in range(tps_to_reduce):

      if remove_condition:
        parcel_tps_cond_1 = np.delete(parcel_tps_cond_1, -1, 1)
      else:
        parcel_tps_cond_0 = np.delete(parcel_tps_cond_0, -1, 1)

    # New data has only the two conditions for the given run
    new_data.append([parcel_tps_cond_0, parcel_tps_cond_1])

  return new_data

#Function:Get vertical average (regions across subjects)

def get_average_all_subjects(data):

  avg_subjects_cond_0 = []
  avg_subjects_cond_1 = []

  for subject in range(len(data)):
    avg_subjects_cond_0.append(data[subject][0])
    avg_subjects_cond_1.append(data[subject][1])

  np_avg_subjects_c0 = np.mean(np.array(avg_subjects_cond_0), axis=0)
  np_avg_subjects_c1 = np.mean(np.array(avg_subjects_cond_1), axis=0)

  return [np_avg_subjects_c0, np_avg_subjects_c1]

#Function:Get horizontal average (timepoints for each region/subject)

def get_average_by_region(data):
  
  averages = []

  for subject in range(len(data)):
    avg_cond_0 = np.mean(data[subject][0], axis=1)
    avg_cond_1 = np.mean(data[subject][1], axis=1)
    averages.append([avg_cond_0, avg_cond_1])

  return averages

#Function: Get difference between conditions

def get_difference(averages):
  
  difference = []
  for subject in range(len(averages)):
    difference.append(averages[subject][0] - averages[subject][1])

  return difference

# Subjects' information

#Function: Get behavior of a single subject

def subject_behavior(subject, feature=None):
  """
  Get subject's info using the index in the NMA-curated dataset

    Args:
      subject (int or numpy.str_): 
            - int corresponds to subject's index in the NMA-curated dataset
            - numpy.str_ corresponds to subject's ID
      feature (None or string or list of strings): 
            - None returns all subject's info as a pandas.Series
            - string returns only one column as a value
            - list of strings returns all requested columns as a list of values
    
    Returns:
      SUBJECTS_BEHAVIOR.iloc[subject] : pandas.Series
      SUBJECTS_BEHAVIOR.iloc[subject][feature] : value
      SUBJECTS_BEHAVIOR.iloc[subject][feature].values.tolist() : list of values

    Raises:
      IndexError for invalid index.
      NameError for invalid column's experiment
    
    Examples:

    >>> subject_behavior(SUBJECTS[0], feature='Age')
    '26-30'

    >>> subject_behavior(SUBJECTS[0], feature=['Age', 'Gender'])
    ['26-30', 'F']

    >>> subject_behavior(0, feature=['Age', 'Gender'])
    ['26-30', 'F'] 

  """

  # If a string is passed as the subject, retrieve subject's index
  if type(subject) == str:
    subject = ids_int.index(int(subject))

  # All of subject's behavior information.
  subject_series = SUBJECTS_BEHAVIOR.iloc[subject]

  if feature is None:
    return subject_series

  if type(feature) == str:
    if feature in features:
      return subject_series[feature]
    else:
      raise NameError(f'Feature "{feature}" is not a valid column.')

  if type(feature) == list:
    for f in feature:
      if f not in features:
        raise NameError(f"Feature '{feature}' is not a valid column.")
    return subject_series[feature].values.tolist()

  raise TypeError(f"Invalid type for 'feature', it should be str or list")

#Function: Get behavior of all subjects

def all_subjects_behavior(subjects, behaviors, use_index=False):

  all_behaviors = []

  if use_index:
    for i in subjects:
      all_behaviors.append(subject_behavior(i, behaviors))
      
  else:
    for i in range(len(subjects)):
      all_behaviors.append(subject_behavior(i, behaviors))

  return all_behaviors

#Function: Get the indexes for female and male subjects.

def gender_indexes():

  females = [] 
  males   = []
  
  for i, gender in enumerate(all_subjects_behavior(SUBJECTS, 'Gender')):
    if gender == 'F':
      females.append(i)
    else:
      males.append(i)

  return females, males

#Function: Get a random selection of indexes for each gender
#We need subsets of 150 females and males.

def get_random_indexes():
  
  females, males = gender_indexes()

  # There are two male subjects with wrong BOLD readouts
  males.remove(3)
  males.remove(98)

  females_150 = random.sample(females, 150)
  males_150   = random.sample(males, 150)

  return females_150, males_150

#Function: Divide the whole BOLD data into two groups by gender

def divide_by_gender(data, female_indexes, male_indexes):

  females = []
  for f in female_indexes:
    females.append(data[f])

  males = []
  for m in male_indexes:
    males.append(data[m])

  return females, males

# Processing data

# Initialize data
#experiment = "SOCIAL"
#ts_social  = get_timeseries(experiment)
#bold_data  = get_BOLD(ts_social, experiment)

# print("Original data . . . . . . . . . . . . . . . . . . . . . . . .\n")  # <--- Uncomment whole block to
# print(f"bold_data has:   {len(bold_data)} subjects")                      #      understand the structure
# print(f"subject_0 has:   {len(bold_data[0])} runs")
# print(f"s0, 1st_run has: {len(bold_data[0][0])} conditions")
# print(f"s0, 2nd_run has: {len(bold_data[0][1])} conditions")
# print(f"s0r0, 'mental':  {bold_data[0][0][0].shape} (ROIs, timepoints)")
# print(f"s0r0, 'rnd':     {bold_data[0][0][1].shape}")
# print(f"s0r1, 'mental':  {bold_data[0][1][0].shape}")
# print(f"s0r1, 'rnd':     {bold_data[0][1][1].shape}\n\n")

#Data processed

# Removing excess of timepoints in 'condition' with bigger size.
# Also, returns only the data for the run that was reduced.
reduced_data = remove_excess(bold_data, 0)

# print("After removing the excess . . . . . . . . . . . . . . . . . . .\n")  # <--- Uncomment whole block to
# print(f"reduced_data has: {len(reduced_data)} subjects")                    #      understand the structure
# print(f"subject_0 has:    {len(reduced_data[2])} conditions")
# print(f"s0, 'mental':     {reduced_data[2][0].shape} (ROIs, timepoints)")
# print(f"s0, 'rnb:         {reduced_data[2][1].shape}\n")

# Calculating BOLD signal's average for each region/subject, run 0
average_BOLD = get_average_by_region(reduced_data)

# print("BOLD signal's average for each region/subject, run 0 . . . . . .\n")  # <--- Uncomment whole block to
# print(f"average_BOLD has: {len(average_BOLD)} subjects")                     #      understand the structure
# print(f"subject_0 has:    {len(average_BOLD[0])} conditions")
# print(f"s0, 'mental' has: {len(average_BOLD[0][0])} regions")
# print(f"s0c0, 1st region: {average_BOLD[0][0][0]}")
# print(f"s0c0,last region: {average_BOLD[0][0][359]}\n")

# Dividing subjects by gender.
female_indexes, male_indexes = get_random_indexes()
F_AVERAGE_BOLD, M_AVERAGE_BOLD = divide_by_gender(average_BOLD, female_indexes, male_indexes)

# print("Dividing subjects by gender, run 0 . . . . . . . . . . . . . . . .\n")  # <--- Uncomment whole block to
# print("Female's average for each region/subject")                              #      understand the structure
# print(f"F_AVERAGE_BOLD has: {len(F_AVERAGE_BOLD)} subjects")
# print(f"female_0 has:       {len(F_AVERAGE_BOLD[0])} conditions")
# print(f"f0, 'mental' has:   {len(F_AVERAGE_BOLD[0][0])} regions")
# print(f"f0c0,last region:   {F_AVERAGE_BOLD[0][0][359]}\n")

# Region's average for all subjects, by gender, run 0 
F_AVERAGE_REGN = get_average_all_subjects(F_AVERAGE_BOLD)
M_AVERAGE_REGN = get_average_all_subjects(M_AVERAGE_BOLD)

# print("Region's average for females, run 0 . . . . . . . . . . . . . . . .\n")  # <--- Uncomment whole block to
# print(f"F_AVERAGE_REGN has: {len(F_AVERAGE_REGN)} conditions")                  #      understand the structure
# print(f"condition_0 has:    {len(F_AVERAGE_REGN[0])} averages for each region")
# print(f"c0, last region:    {F_AVERAGE_REGN[0][359]}")

# Difference between conditions
F_MENTAL_RND_DIFF = get_difference(F_AVERAGE_BOLD)
M_MENTAL_RND_DIFF = get_difference(M_AVERAGE_BOLD)

print(f"F_MENTAL_RND_DIFF has: {len(F_MENTAL_RND_DIFF)} subjects")                  #      understand the structure
print(f"female_0 has:          {len(F_MENTAL_RND_DIFF[0])} mental-rnd differences")

# Key lists from previous cell

#F_AVERAGE_BOLD has the BOLD signal average for each female/region.

#F_AVERAGE_BOLD[females]                              <-- 150 females
#F_AVERAGE_BOLD[females][condition]                   <-- 2 conditions
#F_AVERAGE_BOLD[females][condition][average_region]   <-- 360 regions averaged

#Example

print("Female 1,   'mental', region 360 = ", F_AVERAGE_BOLD[0][0][359])
print("Female 150, 'rnd',    region 1   = ", F_AVERAGE_BOLD[149][1][0], "\n")

# Same for M_AVERAGE_BOLD:
# M_AVERAGE_BOLD[males][condition][average_region]
#F_MENTAL_RND_DIFF has the 'mental' and 'rnd' difference (BOLD signal average per region/subject).
#F_MENTAL_RND_DIFF[subject]                    <-- 150 females
#F_MENTAL_RND_DIFF[subject][region_difference] <-- 360 regions averaged

#Example:

print("Female 1,   region 360 = ", F_MENTAL_RND_DIFF[0][359])
print("Female 150, region 1   = ", F_MENTAL_RND_DIFF[1][0], "\n")
print(type(F_MENTAL_RND_DIFF))
print(type(F_MENTAL_RND_DIFF[0]))
print(type(F_MENTAL_RND_DIFF[0][0]), "\n")

np_F_MENTAL_RND_DIFF = np.array(F_MENTAL_RND_DIFF)
np_M_MENTAL_RND_DIFF = np.array(M_MENTAL_RND_DIFF)

print(type(np_F_MENTAL_RND_DIFF))
print(type(np_F_MENTAL_RND_DIFF[0]))
print(type(np_F_MENTAL_RND_DIFF[0][0]))

# Same for M_MENTAL_RND_DIFF

#List with original genders

# From a previous cell, you have the lists female_indexes and male_indexes
# these two have the index for each female and male in the original list.
# Let's combine female_indexes and male_indexes so you have one list. 
# NOTE: these indexes were selected randomly.

both_indexes = female_indexes + male_indexes
both_indexes.sort()
print(both_indexes)

# Now we're going to look for their gender.
current_subjects_gender = all_subjects_behavior(both_indexes, 'Gender', use_index=True)
print(current_subjects_gender)

# Model

#@title PyCaret
!pip install pycaret

#@title Libraries
from pycaret.classification import *
from xgboost import XGBClassifier
from sklearn import datasets, svm
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.model_selection import train_test_split, cross_validate, cross_val_score
from sklearn.linear_model import LogisticRegression

# Prepare data

# Initial input data.

# X_vector should be the data (BOLD averages) of both genders.
BOLD_DATA = np.vstack((np_F_MENTAL_RND_DIFF, np_M_MENTAL_RND_DIFF))

# Y_vector should be the gender labels.
LABELS = np.array(['F'] * 150 + ['M'] * 150)

# Split the data into training and test sets

X_train, X_test, y_train, y_test = train_test_split(BOLD_DATA,
                                                    LABELS, 
                                                    test_size = 0.1, 
                                                    random_state=0)
print(X_train.shape, X_test.shape)
print(y_train.shape, "\t  ", y_test.shape)

# Scale and normalize the data

normal = Normalizer()
scaler = StandardScaler()

X_train = normal.fit_transform(X_train)
X_train = scaler.fit_transform(X_train)

X_test = normal.fit_transform(X_test)
X_test = scaler.fit_transform(X_test)

print(X_train.shape, X_test.shape)

# Frame with the training data and label

DF_TRAINING = pd.DataFrame(X_train)
DF_TRAINING['Label'] = y_train
DF_TRAINING.head()

# Identifying most relevant ROI for the experiment.

#Since we have more features (360 regions) than variables (300 subjects) we need to select the most relevant ones. We do this by computing the ANOVA F-value for the provided sample.

# Computing the ANOVA F-value
relevant = f_classif(X_train, y_train)
relevant_feat = pd.Series(relevant[0], DF_TRAINING.columns[:len(DF_TRAINING.columns)-1])


# Codes for the relevant regions with a F-value above 2
roi_index_2 = [i for i,f in enumerate(relevant_feat) if f > 2]
roi_above_2 = [ROIs[i] for i in roi_index_2]

print(f"There are {len(roi_above_2)} regions with " +
      f"a F-value higher than 2:\n{roi_above_2}\n")


# Codes for the relevant regions with a F-value above 3
roi_index_3 = [i for i,f in enumerate(relevant_feat) if f > 3]
roi_above_3 = [ROIs[i] for i in roi_index_3]

print(f"There are {len(roi_above_3)} regions with " +
      f"a F-value higher than 3:\n{roi_above_3}\n")


# Codes for the relevant regions with a F-value above 4
roi_index_4 = [i for i,f in enumerate(relevant_feat) if f > 4]
roi_above_4 = [ROIs[i] for i in roi_index_4]

print(f"There are {len(roi_above_4)} regions with " +
      f"a F-value higher than 4:\n{roi_above_4}\n")


# Codes for the relevant regions with a F-value above 5
roi_index_5 = [i for i,f in enumerate(relevant_feat) if f > 5]
roi_above_5 = [ROIs[i] for i in roi_index_5]

print(f"There are {len(roi_above_5)} regions with " +
      f"a F-value higher than 5:\n{roi_above_5}\n")

# Select relevant features from the data

TRAINING_ABOVE_2 = DF_TRAINING.filter(roi_index_2, axis=1)
TRAINING_ABOVE_2['Label']= DF_TRAINING['Label']

TRAINING_ABOVE_3 = DF_TRAINING.filter(roi_index_3, axis=1)
TRAINING_ABOVE_3['Label']= DF_TRAINING['Label']

TRAINING_ABOVE_4 = DF_TRAINING.filter(roi_index_4, axis=1)
TRAINING_ABOVE_4['Label']= DF_TRAINING['Label']

TRAINING_ABOVE_5 = DF_TRAINING.filter(roi_index_5, axis=1)
TRAINING_ABOVE_5['Label']= DF_TRAINING['Label']

# Finding the best model for our data

# Data with F-value > 2.
#setup(data = TRAINING_ABOVE_2, target = 'Label')
#compare_models()
#model = create_model('et')
#tune_model(model)

# Data with F-value > 3

setup(data = TRAINING_ABOVE_3, target = 'Label')

compare_models()

model = create_model('et')
tune_model(model)

# Data with F-value > 4

setup(data = TRAINING_ABOVE_4, target = 'Label')

compare_models()

model = create_model('et')
tune_model(model)

# Data with F-value > 5

setup(data = TRAINING_ABOVE_5, target = 'Label')

compare_models()

model = create_model('rf')
tune_model(model)

# Cross-validation to check model's accuracy

# Remove less relevant features from train and test data **(run just once)

#delete_columns = [i for i in range(360) if i not in roi_index_4]
#X_train = np.delete(X_train, delete_columns, 1)
#X_test  = np.delete(X_test,  delete_columns, 1)

# Cross-validation: Extra Trees Classifier

model  = ExtraTreesClassifier(n_estimators=100, random_state=0)
scores = cross_val_score(model, X_train, y_train, cv=5)

print(scores.mean(), scores.std())

# Test the data

model = ExtraTreesClassifier(n_estimators=100, random_state=0).fit(X_train, y_train)
model.score(X_test, y_test)

# Permutation test

# # PERMUTATION TESTING

# generate some random feature data that are uncorrelated with the 
# class labels in the dataset

# import numpy as np
# from sklearn.model_selection import permutation_test_score
# from sklearn.model_selection import StratifiedKFold

# n_uncorrelated_features = 2200
# rng = np.random.RandomState(seed=0)
# # use same number of samples as in the dataset and 2200 features
# X_rand = rng.normal(size=(X.shape[0], n_uncorrelated_features))

# clf_lr = LogisticRegression(penalty='l2', max_iter=1000)

# score_iris, perm_scores_iris, pvalue_iris = permutation_test_score(
#     clf_lr, X, y, n_permutations=100)

# score_rand, perm_scores_rand, pvalue_rand = permutation_test_score(
#     clf_lr, X_rand, y, scoring="accuracy", cv=cv, n_permutations=100)

# import matplotlib.pyplot as plt

# fig, ax = plt.subplots()

# ax.hist(perm_scores_iris, bins=20, density=True)
# ax.axvline(score_iris, ls='--', color='r')
# score_label = (f"Score on original\ndata: {score_iris:.2f}\n"
#                f"(p-value: {pvalue_iris:.3f})")
# ax.text(0.7, 260, score_label, fontsize=12)
# ax.set_xlabel("Accuracy score")
# _ = ax.set_ylabel("Probability")

#Visualising Brain Regions

# This uses the nilearn package
!pip install nilearn --quiet
from nilearn import plotting, datasets

# NMA provides an atlas 
fname = f"{HCP_DIR}/atlas.npz"
if not os.path.exists(fname):
  !wget -qO $fname https://osf.io/j5kuc/download
with np.load(fname) as dobj:
  atlas = dict(**dobj)

# Try both hemispheres (L->R and left->right)
fsaverage = datasets.fetch_surf_fsaverage()
surf_contrast = group_contrast[atlas["labels_L"]]
plotting.view_surf(fsaverage['infl_left'],
                   surf_contrast,
                   vmax=20)

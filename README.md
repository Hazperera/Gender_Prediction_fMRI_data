# Predicting Gender from task-fMRI BOLD signals
### Can task-based BOLD signal from a social cognition task be used to predict gender?

#### Background:
- A rich collection of previous studies have probed the question of whether differences attributable to gender exist across a wide range of brain-relevant parameters. It remains unclear to what extent the brain is classifiable on this basis. 
- Previous work exploring functional connectivity using resting-state fMRI and task-fMRI BOLD signals have found discrepancies across genders (operationalized as “male” and “female”) in various functional networks and across several cognitive tasks. 
- Analyses centred on comparing BOLD signals from local intrinsic spontaneous activity have been generally neglected in computational modeling research on gender differences in brain activity. 
- While functional connectivity offers a robust measure for tracking these differences, the question of whether accounting for regional correlations in activity levels, as opposed to simply focusing on spontaneous activity, is necessary to generate an efficient predictive model remains. 

#### Objective:
This project aims to build a parsimonious computational model that predicts categorized gender from local BOLD signal patterns in a social cognition task-fMRI dataset. 

#### Model:
Preprocessed version of [Human Connectome Project (HCP)](https://www.humanconnectome.org/study/hcp-young-adult/overview) social cognition task BOLD signal data was used to construct a Generalized Linear Model that classifies BOLD signal activity into discrete gender categories. 

As for our expectations for the model’s performance, we hypothesize that our model will predict gender better than chance, but also that it will not perform as well as previous functional connectivity-based models due to the value-added information of functional connectivity. 

#### Dataset Description: [Human Connectome Project Reference Manual](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjQuNG1psXzAhUKAcAKHRk3CE4QFnoECAkQAQ&url=https%3A%2F%2Fwww.humanconnectome.org%2Fstorage%2Fapp%2Fmedia%2Fdocumentation%2Fs1200%2FHCP_S1200_Release_Reference_Manual.pdf&usg=AOvVaw21GMrvh_Ri0whYIlc6qMPK)
#### References: *[Barch, Deanna M., et al. “Function in the human connectome: task-fMRI and individual differences in behavior.” Neuroimage 80 (2013): 169-189.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4011498/)*


<p align="center">
  <img width="300" height="300" src="https://cdn5.vectorstock.com/i/thumb-large/00/79/brain-logo-silhouette-design-template-line-art-vector-29510079.jpg">
</p>

<p align="center">
<a href="https://www.vectorstock.com/royalty-free-vector/brain-logo-silhouette-design-template-line-art-vector-29510079">Vector image by VectorStock / LuckyCreative</a>
</p>

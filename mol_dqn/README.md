
Latest successful script "multi_obj_opt_w-PI.py"

Key References
MOL_DQN 
Zhou, Z., Kearnes, S., Li, L. et al. Optimization of Molecules via Deep Reinforcement Learning. Sci Rep 9, 10752 (2019). https://doi.org/10.1038/s41598-019-47148-x

Persistance images framework
Townsend, J., Micucci, C.P., Hymel, J.H. et al. Representation of molecular structures with persistent homology for machine learning applications in chemistry. Nat Commun 11, 3230 (2020). https://doi.org/10.1038/s41467-020-17035-5

Phenothiazines

Biphasic, Membrane-Free Zn/Phenothiazine Battery: Effects of Hydrophobicity of Redox Materials on Cyclability
Jingchao Chai, Amir Lashgari, Andrew E. Eisenhart, Xiao Wang, Thomas L. Beck, and Jianbing “Jimmy” Jiang
ACS Materials Letters 2021 3 (4), 337-343
DOI: 10.1021/acsmaterialslett.1c00061


Abstract:
In this work Mol_DQN reinforcement leaning framework was used to generate novel Phenothiazine derivatives. These Phenothiazene derivative potentials were evaluated using a TPOT generated ML model (random forest regressor) trained from data generated from pre-generated 218 phenothiazine derivatives, each of which has its target "HOMO-LUMO" gap calculated using the Gaussian software (g16c01).

Results:
The resulting MOL_DQN workflow generated ~50 candidate molecules with high stability. The next part of this project should evaulate thses molecules for solubility either using the pre-trained logp predictor or another chemical method.

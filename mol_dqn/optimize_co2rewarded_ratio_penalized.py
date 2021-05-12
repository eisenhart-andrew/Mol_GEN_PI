# coding=utf-8
# Copyright 2020 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python2, python3
"""Optimize the logP of a molecule."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import json
import os
from absl import app
from absl import flags
from rdkit import Chem

from mol_dqn.chemgraph.dqn import deep_q_networks
from mol_dqn.chemgraph.dqn import molecules as molecules_mdp
from mol_dqn.chemgraph.dqn import run_dqn
from mol_dqn.chemgraph.dqn.py import molecules
from mol_dqn.chemgraph.dqn.tensorflow_core import core

from Element_PI import VariancePersist
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.kernel_ridge import KernelRidge
from joblib import dump, load
from rdkit.Chem import AllChem
import subprocess
from rdkit.Chem import rdqueries


flags.DEFINE_float('gamma', 0.999, 'discount')
FLAGS = flags.FLAGS

def PI_reward(molecule):
  """uses persistance image trained krr to predict CO2 bindin of molecules.

  Args:
    molecule: Chem.Mol. A molecule.

  Returns:
    Float. The CO2 binding affinity value.

  """
  pixelsx=150
  pixelsy=150
  spread=.08
  Max=2.5
  m = molecule
  AllChem.EmbedMolecule(m,useRandomCoords=True,maxAttempts=15000)
  
  try:
    AllChem.MMFFOptimizeMolecule(m,maxIters=15000)
  except ValueError:
    print('ValueError on mol:',Chem.MolToSmiles(m))
    pass
  mH = Chem.AddHs(molecule)
  try:
    AllChem.EmbedMolecule(mH,useRandomCoords=True,maxAttempts=15000)
    AllChem.MMFFOptimizeMolecule(mH,maxIters=15000)
  except ValueError:
    print('ValueError on mol:',Chem.MolToSmiles(mH))
    pass
  print(Chem.MolToMolBlock(mH),file=open('./database/mol.mol','w+'))
  cmd = "obabel ./database/mol.mol -O ./database/mol.xyz"
  subprocess.call(cmd, shell=True)
  
  try:
    X=VariancePersist('./database/mol.xyz', pixelx=pixelsx, pixely=pixelsy, myspread=spread, myspecs={"maxBD": Max, "minBD":-.10}, showplot=False)
    modelco2 = load('saved_PI_CO.joblib')
    co2reward = modelco2.predict(X.reshape(1, -1))
    print(f'predicted co2 binding affinity = {co2reward[0][0] * -1}')  
  except TypeError:
    print(f'TypeError on mol: {Chem.MolToSmiles(mH)} -- co2 prediction')
    co2reward = [[0]]
    pass
  
  try:
    q = rdqueries.AtomNumEqualsQueryAtom(6)
    carbons = len(mH.GetAtomsMatchingQuery(q))
    q = rdqueries.AtomNumEqualsQueryAtom(7)
    nitrogens = len(mH.GetAtomsMatchingQuery(q))
    q = rdqueries.AtomNumEqualsQueryAtom(8)
    oxygens = len(mH.GetAtomsMatchingQuery(q))

    ratioreward = carbons / (nitrogens + oxygens)
    print(f'ratio reward  = {ratioreward}')

  except ZeroDivisionError:
    print(f'TypeError on mol: {Chem.MolToSmiles(mH)} -- gap prediction')
    ratioreward = [[0]]
  PIreward = (co2reward[0][0] * -1) + ratioreward
  return PIreward 

class Molecule(molecules_mdp.Molecule):

  def _reward(self):
    molecule = Chem.MolFromSmiles(self._state)
    if molecule is None:
      return 0.0
    return PI_reward(molecule)


def main(argv):
  del argv
  if FLAGS.hparams is not None:
    with open(FLAGS.hparams, 'r') as f:
      hparams = deep_q_networks.get_hparams(**json.load(f))
  else:
    hparams = deep_q_networks.get_hparams()

  environment = Molecule(
      atom_types=set(hparams.atom_types),
      init_mol=FLAGS.start_molecule,
      allow_removal=hparams.allow_removal,
      allow_no_modification=hparams.allow_no_modification,
      allow_bonds_between_rings=hparams.allow_bonds_between_rings,
      allowed_ring_sizes=set(hparams.allowed_ring_sizes),
      max_steps=hparams.max_steps_per_episode)

  dqn = deep_q_networks.DeepQNetwork(
      input_shape=(hparams.batch_size, hparams.fingerprint_length + 1),
      q_fn=functools.partial(
          deep_q_networks.multi_layer_model, hparams=hparams),
      optimizer=hparams.optimizer,
      grad_clipping=hparams.grad_clipping,
      num_bootstrap_heads=hparams.num_bootstrap_heads,
      gamma=hparams.gamma,
      epsilon=1.0)

  run_dqn.run_training(
      hparams=hparams,
      environment=environment,
      dqn=dqn,
  )

  core.write_hparams(hparams, os.path.join(FLAGS.model_dir, 'config.json'))


if __name__ == '__main__':
  app.run(main)

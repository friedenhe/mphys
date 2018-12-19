"""
Mass minimization of uCRM wingbox subject to a constant vertical force

"""
from __future__ import division, print_function
import numpy as np

from openmdao.api import Problem, ScipyOptimizeDriver
from openmdao.api import ExplicitComponent, ExecComp, IndepVarComp, Group
from openmdao.api import NonlinearRunOnce, LinearRunOnce
from openmdao.api import SqliteRecorder

from tacs import elements, constitutive
from assemble_dummy_aero import FsiComps

################################################################################
# Tacs solver pieces
################################################################################
def add_elements(mesh):
    rho = 2500.0  # density, kg/m^3
    E = 70.0e9 # elastic modulus, Pa
    nu = 0.3 # poisson's ratio
    kcorr = 5.0 / 6.0 # shear correction factor
    ys = 350e6  # yield stress, Pa
    t= 0.010
    min_thickness = 0.00
    max_thickness = 1.00

    num_components = mesh.getNumComponents()
    for i in xrange(num_components):
        descript = mesh.getElementDescript(i)
        stiff = constitutive.isoFSDT(rho, E, nu, kcorr, ys, t, i,
                                     min_thickness, max_thickness)
        element = None
        if descript in ["CQUAD", "CQUADR", "CQUAD4"]:
            element = elements.MITCShell(2,stiff,component_num=i)
        mesh.setElement(i, element)

    ndof = 6
    ndv = num_components

    return ndof, ndv

func_list = ['ks_failure','mass']
tacs_setup = {'add_elements': add_elements,
              'nprocs'      : 4,
              'mesh_file'   : 'CRM_box_2nd.bdf',
              'func_list'   : func_list}
meld_setup = {'isym': 1,
              'n': 200,
              'beta': 0.5}
flow_setup = {}

setup = {'tacs': tacs_setup, 'meld': meld_setup, 'flow': flow_setup}

fsi_comps = FsiComps()

################################################################################
# OpenMDAO setup
################################################################################
prob = Problem()
model = prob.model

indeps = IndepVarComp()
indeps.add_output('dv_struct',np.array(240*[0.0031]))
indeps.add_output('dv_aero',1.0)
model.add_subsystem('indeps',indeps,promotes=['dv_struct','dv_aero'])

fsi_comps.add_fsi_subsystems(model,setup)

prob.driver = ScipyOptimizeDriver(debug_print=['objs','nl_cons'],maxiter=1000)
prob.driver.options['optimizer'] = 'SLSQP'

#recorder = SqliteRecorder('crm.sql')
#prob.driver.add_recorder(recorder)
#prob.driver.recording_options['includes'] = ['*']

model.add_design_var('dv_struct',lower=0.001,upper=0.075,scaler=1.0/1.0)

model.add_objective('mass',scaler=1.0/100000.0)
model.add_constraint('f_struct',lower = 0.0, upper = 2.0/3.0,scaler=100.0/100.0)

prob.setup()

#prob.run_model()
#prob.check_partials()

prob.run_driver()

for i in range(240):
    print('final dvs',i,prob['dv_struct'][i])
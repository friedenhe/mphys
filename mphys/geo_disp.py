import numpy as np
import openmdao.api as om

class GeoDisp(om.ExplicitComponent):
    """
    This component adds the aerodynamic
    displacements to the geometry-changed aerodynamic surface
    """
    def initialize(self):
        self.options['distributed'] = True
        self.options.declare('number_of_surface_nodes')

    def setup(self):
        nnodes = self.options['number_of_surface_nodes']
        local_size = nnodes * 3
        n_list = self.comm.allgather(local_size)
        irank  = self.comm.rank

        n1 = np.sum(n_list[:irank])
        n2 = np.sum(n_list[:irank+1])

        self.add_input('x_aero0', shape_by_conn=True,
                                  desc='aerodynamic surface with geom changes')
        self.add_input('u_aero',  shape_by_conn=True,
                                  desc='aerodynamic surface displacements')

        self.add_output('x_aero', shape=local_size, desc='deformed aerodynamic surface')

    def compute(self,inputs,outputs):
        outputs['x_aero'] = inputs['x_aero0'] + inputs['u_aero']

    def compute_jacvec_product(self,inputs,d_inputs,d_outputs,mode):
        if mode == 'fwd':
            if 'x_aero' in d_outputs:
                if 'x_aero0' in d_inputs:
                    d_outputs['x_aero'] += d_inputs['x_aero0']
                if 'u_aero' in d_inputs:
                    d_outputs['x_aero'] += d_inputs['u_aero']
        if mode == 'rev':
            if 'x_aero' in d_outputs:
                if 'x_aero0' in d_inputs:
                    d_inputs['x_aero0'] += d_outputs['x_aero']
                if 'u_aero' in d_inputs:
                    d_inputs['u_aero']  += d_outputs['x_aero']

from mphys.time_domain.integrator import Integrator

from .timestep_aerodynamic import TimeStepAerodynamic


class IntegratorAerodynamic(Integrator):
    def initialize(self):
        self.options.declare("aero_builder")
        self.options.declare("geometry_builder")
        return super().initialize()

    def _get_timestep_group(self):
        return TimeStepAerodynamic(
            aero_builder=self.options["aero_builder"],
            geometry_builder=self.options["geometry_builder"],
        )

    def _get_builder_list(self):
        return [
            self.options["aero_builder"],
            self.options["geometry_builder"],
        ]

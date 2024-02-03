from .timestep import TimeStep


class TimeStepAerodynamic(TimeStep):
    def initialize(self):
        """
        A class to perform a single discipline aerodynamic case.
        The Scenario will add the aerodynamic builder's precoupling subsystem,
        the coupling subsystem, and the postcoupling subsystem.
        """
        super().initialize()

        self.options.declare(
            "aero_builder",
            recordable=False,
            desc="The MPhys builder for the aerodynamic solver",
        )
        self.options.declare(
            "geometry_builder", default=None, recordable=False, desc="The optional MPhys builder for the geometry"
        )

    def _mphys_timestep_setup(self):
        aero_builder = self.options["aero_builder"]
        geometry_builder = self.options["geometry_builder"]
        builders = [aero_builder, geometry_builder]

        self._add_ivc_with_mphys_inputs(builders, self.options["user_input_variables"])
        self._add_ivc_with_state_backplanes(builders)
        self._add_ivc_with_time_information()

        self._mphys_add_pre_coupling_subsystem_from_builder("aero", aero_builder, self.name)
        self.mphys_add_subsystem("coupling", aero_builder.get_coupling_group_subsystem(self.name))
        self._mphys_add_post_coupling_subsystem_from_builder("aero", aero_builder, self.name)

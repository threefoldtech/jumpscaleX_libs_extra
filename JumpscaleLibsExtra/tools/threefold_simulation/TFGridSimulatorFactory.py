from Jumpscale import j

from .TFGridSimulator import TFGridSimulator
from .BillOfMaterial import Environment, BillOfMaterial
import sys


class TFGridSimulatorFactory(j.baseclasses.testtools, j.baseclasses.object):

    __jslocation__ = "j.tools.tfgrid_simulator"

    def _init(self, **kwargs):
        j.application.start("simulator")
        self._instances = j.baseclasses.dict()
        self._environments = j.baseclasses.dict()
        self._bom = j.baseclasses.dict()

        notebookpath = j.core.tools.text_replace(
            "{DIR_CODE}/github/threefoldtech/jumpscaleX_libs_extra/JumpscaleLibsExtra/tools/threefold_simulation/notebooks"
        )
        if notebookpath not in sys.path:
            sys.path.append(notebookpath)

    @property
    def default(self):
        s = self.simulation_get("default")
        return s

    def simulation_get(
        self,
        name="default",
        tokencreator_name="optimized",
        hardware_config_name="amd",
        node_growth=None,
        tft_growth=None,
        reload=True,
        calc=True,
    ):
        """
        example how to use

        ```
        simulation = j.tools.tfgrid_simulator.simulation_get()
        ```

        @param node_growth: if empty will be whatever was defined in the simlator name see notebooks/simulators
            default: "0:5,6:150,12:1000,18:2000,24:8000,36:12000,48:20000,60:20000"
        @param tft_growth: if empty will be whatever was defined in the simlator name see notebooks/simulators
            default: "0:0.15,60:3"

        ## meaning of the interpolation values
        # 0:0 means month 0 we have value 0
        # 60:3 means month 60: value is 3
        # interpolation will happen between the values
        # above: the price go from 0.15 first month to 3 over 60 months


        """

        if reload or name not in self._instances:
            simulation = TFGridSimulator(name=name)
            # choose your token simulation !!!
            environment = self.environment_get(hardware_config_name, reload=reload)
            assert environment.nr_devices > 0

            exec(f"from token_creators.{tokencreator_name} import TokenCreator", globals())
            simulation.token_creator = TokenCreator(simulation=simulation, environment=environment)

            exec(f"from simulations.{name} import simulation_calc", globals())
            simulation, environment = simulation_calc(simulation, environment)

            if tft_growth:
                simulation.tokenprice_set(tft_growth)

            if node_growth:
                simulation.nrnodes_new_set(node_growth)

            # put the default bom's
            simulation.environment = environment
            simulation.bom = environment.bom

            self._instances[name] = simulation

        simulation = self._instances[name]

        # simulation.calc()

        if calc and simulation.simulated == False:
            key = f"{name}_{tokencreator_name}_{hardware_config_name}_{node_growth}_{tft_growth}"
            simulation.import_redis(key=key, autocacl=True, reset=reload)

        return simulation

    def calc_custom_environment(self, reload=False):
        """
        kosmos 'j.tools.tfgrid_simulator.calc_custom_environment()'
        kosmos 'j.tools.tfgrid_simulator.calc_custom_environment(reload=True)'
        """

        startmonth = 1

        # define how the nodes will grow
        node_growth = "0:5,6:150,12:1000,18:2000,24:8000,36:12000,48:20000,60:20000"
        # node_growth="0:5,6:150,12:1000,24:5000"
        # node_growth="0:1000"

        # tft price in 5 years, has impact on return
        tft_price = 3

        simulation = j.tools.tfgrid_simulator.simulation_get(
            name="default",
            tokencreator_name="optimized",
            hardware_config_name="amd",  # dont change here, this is the growth calc
            node_growth=node_growth,
            tft_growth=tft_price,
            reload=True,
        )

        ###################################################
        ## NOW THE NODES BATCH WE WANT TO SIMULATE FOR

        # bill of material name
        # hardware_config_name = "CH_archive"
        hardware_config_name = "A_dc_rack"
        # hardware_config_name = "hpe_dl385_amd"
        # hardware_config_name = "amd"

        # parameters for simulation
        # choose your hardware profile (other choices in stead of amd or supermicro or hpe)
        nb = simulation.nodesbatch_simulate(month=startmonth, hardware_config_name=hardware_config_name)

        print(nb)

        # print(nb.normalized)

        j.shell()

        # nb._values_usd_get()

        nb.graph_tft(single=True)

        print(nb.roi_end)

    def environment_get(self, name="amd", reload=False):
        """
        name is name of file in notebooks/params/hardware

        ```
        simulation = j.tools.tfgrid_simulator.bom_get()
        ```

        return (bom,environment)

        """
        if not reload or name not in self._environments:
            # if reload or name not in self._bom:
            environment = Environment(name=name)
            self._environments[name] = environment
        return self._environments[name]

    def calc(self, batches_simulation=False, reload=False):
        """
        kosmos 'j.tools.tfgrid_simulator.calc()'
        kosmos 'j.tools.tfgrid_simulator.calc(reload=True)'
        :return:
        """
        simulation = self.simulation_get(
            name="default",
            tokencreator_name="optimized",
            hardware_config_name="amd",
            node_growth=None,
            tft_growth="auto100",
            reload=reload,
        )

        if batches_simulation:
            # nrnodes is 2nd
            nb0 = simulation.nodesbatch_get(0)
            nb0.graph_tft(cumul=True)
            nb0.graph_usd(cumul=True)
            nb = simulation.nodesbatch_get(20)
            nb.graph_tft(single=True)
            # nb.graph_usd(cumul=True,single=True)
            for month in [1, 10, 30, 50]:
                simulation.nodesbatch_get(month).graph_usd(cumul=True, single=True)

        # simulation.graph_tft_simulation()

        return

    def get_path_dest(self, name=None, reset=False):
        path_source = "{DIR_CODE}/github/threefoldtech/jumpscaleX_libs_extra/JumpscaleLibsExtra/tools/threefold_simulation/notebooks/home.ipynb"
        path_source = j.core.tools.text_replace(path_source)
        if name:
            path_dest = j.core.tools.text_replace("{DIR_VAR}/notebooks/%s" % name)
            if reset:
                j.core.tools.remove(path_dest)
            j.sal.fs.copyDirTree(path_source, path_dest, overwriteFiles=False)
        else:
            path_dest = path_source
        return path_dest

    def start(self, voila=False, background=False, base_url=None, name=None, port=8888, pname="notebook", reset=False):
        """
        to run:

        kosmos -p 'j.tools.tfgrid_simulator.start()'

        #means we run the notebook in the code env (careful)
        kosmos -p 'j.tools.tfgrid_simulator.start(name=None)'
        """

        j.application.start("tfsimulation")

        j.core.myenv.log_includes = []
        # e = self.calc()
        path_dest = self.get_path_dest(name=name, reset=reset)
        self._log_info("start notebook on:%s" % path_dest)

        j.servers.notebook.start(
            path=path_dest, voila=voila, background=background, base_url=base_url, port=port, pname=pname
        )  # it will open a browser with access to the right output
        j.application.reset_context()

    def stop(self, voila=False, background=False, base_url=None, name=None, pname="notebook"):
        path_dest = self.get_path_dest(name=name)
        j.servers.notebook.stop(path=path_dest, voila=voila, background=background, base_url=base_url, pname=pname)

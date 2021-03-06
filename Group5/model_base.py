from darts.models.reservoirs.struct_reservoir import StructReservoir
from darts.models.physics.dead_oil import DeadOil
from darts.models.darts_model import DartsModel
from darts.engines import value_vector, sim_params
import numpy as np
from darts.tools.keyword_file_tools import load_single_keyword, save_few_keywords
import os

class BaseModel(DartsModel):
    def __init__(self, n_points=100):
        # call base class constructor
        super().__init__()
        self.n_points = n_points
        # measure time spend on reading/initialization
        self.timer.node["initialization"].start()

        # create reservoir from UNISIM - 20 layers (81*58*20, Corner-point grid)
        self.permx = load_single_keyword('Permeability_(Eff_Por).GRDECL', 'PERMEABILITY')
        self.permy = load_single_keyword('Permeability_(Eff_Por).GRDECL', 'PERMEABILITY')
        self.permz = load_single_keyword('Perm_v.GRDECL', 'PERMZ')
        self.poro = load_single_keyword('Effective_Porosity.GRDECL', 'POROSITY-EFFECTIVE')
        self.depth = load_single_keyword('ZZ.GRDECL', 'ZZ')

        # thresholds to avoid 0 porosity & permeability
        poro_t = 1e-4
        perm_t = 1e-5
        self.poro[self.poro < poro_t] = poro_t
        self.permx[self.permx < perm_t] = perm_t
        self.permy[self.permy < perm_t] = perm_t
        self.permz[self.permz < perm_t] = perm_t

        nx, ny, nz = 49, 285, 49
        
        if os.path.exists(('width.in')):
            print('Reading dx, dy and dz specifications...')
            self.dx = load_single_keyword('width.in', 'DX')
            self.dy = load_single_keyword('width.in', 'DY')
            self.dz = load_single_keyword('width.in', 'DZ')
        else:
            self.dx = np.zeros(nx*ny*nz)
            self.dy = np.zeros(nx*ny*nz)
            self.dz = np.zeros(nx*ny*nz)
        
        # Import other properties from files
        filename = '3D_Grid_V2.GRDECL'
        self.actnum = load_single_keyword(filename, 'ACTNUM')
        self.coord = load_single_keyword(filename, 'COORD')
        self.zcorn = load_single_keyword(filename, 'ZCORN')

        is_CPG = True  # True for re-calculation of dx, dy and dz from CPG grid

        self.reservoir = StructReservoir(self.timer, nx=nx, ny=ny, nz=nz, dx=self.dx, dy=self.dy, dz=self.dz,
                                         permx=self.permx, permy=self.permy, permz=self.permz, poro=self.poro,
                                         depth=self.depth, actnum=self.actnum, coord=self.coord, zcorn=self.zcorn,
                                         is_cpg=is_CPG)
        print("self.reservoir")
        
        if is_CPG:
            dx, dy, dz = self.reservoir.get_cell_cpg_widths()
            save_few_keywords('width.in', ['DX', 'DY', 'DZ'], [dx, dy, dz])

        print("dx,dy,dz should be saved")
        well_dia = 0.152
        well_rad = well_dia / 2

        nx, ny, nz = 49, 285, 49
        self.reservoir.add_well("I1", wellbore_diameter=well_dia)
        for i in range(nz):
            self.reservoir.add_perforation(self.reservoir.wells[-1], 24, 150, i + 1, well_radius=well_rad, multi_segment=False)

        self.reservoir.add_well("P1", wellbore_diameter=well_dia)
        for i in range(nz):
            self.reservoir.add_perforation(self.reservoir.wells[-1], 24, 170, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("NA3D", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 44, 43, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("RJS19", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 17, 18, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 31, 27, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD005", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [1, 4, 5, 10, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 33, 18, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD008", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 19, 30, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD009", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 15, 40, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD010", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 9, 14, 18, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 36, 42, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD012", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 46, 23, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD014", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 50, 18, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD021", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 27, 41, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD023A", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 65, 23, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD024A", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 13, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 61, 35, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("PROD025A", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 57, 23, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ003", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 49, 23, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ005", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 31, 19, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ006", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 48, 34, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ007", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 9, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 59, 17, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ010", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 55, 30, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ015", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 36, 28, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ017", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 33, 39, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ019", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 13, 14, 19, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 29, 41, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ021", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 24, 28, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ022", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 48, 11, i + 1, well_radius=well_rad, multi_segment=False)

        #self.reservoir.add_well("INJ023", wellbore_diameter=well_dia)
        #for i in range(20):
        #    if (i + 1) not in [4, 5, 9, 14, 20]:
        #        self.reservoir.add_perforation(self.reservoir.wells[-1], 42, 18, i + 1, well_radius=well_rad, multi_segment=False)

        self.timer.node["initialization"].stop()


    def set_op_list(self):
        self.op_num = np.array(self.reservoir.mesh.op_num, copy=False)
        n_res = self.reservoir.mesh.n_res_blocks
        self.op_num[n_res:] = 1
        self.op_list = [self.physics.acc_flux_itor, self.physics.acc_flux_itor_well]

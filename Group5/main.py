from darts.engines import value_vector, redirect_darts_output, sim_params
from model_geo import Model
import pandas as pd

import matplotlib.pyplot as plt

redirect_darts_output('out.log')
m = Model()
m.init()
m.export_vtk()
for a in range(2):
    m.run_python(365) #time in days
    m.export_vtk()
m.print_timers()
m.print_stat()

time_data = pd.DataFrame.from_dict(m.physics.engine.time_data)
time_data.to_pickle("darts_time_data.pkl")

writer = pd.ExcelWriter('time_data.xlsx')
time_data.to_excel(writer, 'Sheet1')
writer.save()


from darts.tools.plot_darts import *
w = m.reservoir.wells[1]
ax1 = plot_temp_darts(w.name, time_data)

ax2 = plot_water_rate_darts(w.name, time_data)

plt.show()
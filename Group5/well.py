from paraview.simple import *
well_list = ['I01','I01'];
well_type = ['INJECTOR','PRODUCER'];
well_x = [24,24];
well_y = [150,170];
DX = 50;
DY = 50;
 
X0 = 65488.38
Y0 = 441207.15
well_cyl = Cylinder();
SetProperties(well_cyl,Height=1000,Radius=30);
for idx, val in enumerate(well_list):
	t = Transform(well_cyl);
	t.Transform.Translate=[X0 + well_x[idx]*DX, Y0 + well_y[idx]*DY,3100];
	t.Transform.Rotate = [90,0,0];
	dp = GetDisplayProperties(t);
	if (well_type[idx] == 'PRODUCER'):
		dp.DiffuseColor=[1,0,0];
	else:	
		dp.DiffuseColor=[0,0,1];
	Show(t);
Render();

	
	






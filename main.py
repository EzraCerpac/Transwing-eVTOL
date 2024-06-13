from aircraft_models import rot_wing
from sizing_tools.wing_planform import WingModel

if __name__ == '__main__':
    # rot_wing.display_data(True, True)
    print(rot_wing.parametric.wings[0].xsecs[-1].chord)
    print(rot_wing.parametric.wings[0].xsecs[0].chord)
    print(WingModel(rot_wing.data).le_sweep)
    print(rot_wing.parametric.fuselages[0].xsecs[-1].xyz_c[0] -
          rot_wing.parametric.fuselages[0].xsecs[0].xyz_c[0])

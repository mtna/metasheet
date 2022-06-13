import pandas as pd

data=pd.read_fwf(''
,colspecs=[(0, 2), (2, 8), (8, 12), (12, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 28), (28, 30), (30, 32), (32, 34), (34, 36), (36, 38), (38, 40), (40, 42), (42, 44), (44, 45), (45, 46), (46, 48), (48, 49), (49, 50), (50, 52), (52, 54), (54, 55), (55, 56), (56, 58), (58, 60), (60, 61), (61, 62), (62, 63), (63, 65), (65, 66), (66, 68), (68, 70), (70, 72), (72, 74), (74, 76), (76, 78), (78, 80), (80, 82), (82, 84), (84, 86), (86, 88), (88, 90), (90, 92), (92, 94), (94, 95), (95, 96), (96, 97), (97, 98), (98, 99), (99, 100), (100, 101), (101, 102), (102, 103), (103, 104), (104, 105), (105, 106), (106, 107), (107, 108)]
,names=['VVERSION', 'VDSETNO', 'V480001', 'V480002', 'V480003', 'V480004', 'V480005', 'V480006', 'V480007', 'V480008', 'V480009', 'V480010', 'V480011', 'V480012', 'V480013', 'V480014a', 'V480014b', 'V480015a', 'V480015b', 'V480016a', 'V480016b', 'V480017a', 'V480017b', 'V480018', 'V480019', 'V480020', 'V480021a', 'V480021b', 'V480022a', 'V480022b', 'V480023', 'V480024', 'V480025a', 'V480025b', 'V480026', 'V480027', 'V480028', 'V480029', 'V480030', 'V480031a', 'V480031b', 'V480031c', 'V480032a', 'V480032b', 'V480032c', 'V480033a', 'V480033b', 'V480034a', 'V480034b', 'V480035a', 'V480035b', 'V480036a', 'V480036b', 'V480037', 'V480038', 'V480039', 'V480040', 'V480041', 'V480042', 'V480043', 'V480044', 'V480045', 'V480046', 'V480047', 'V480048', 'V480049', 'V480050']
,converters={0:float,1:str,2:float,3:float,4:float,5:float,6:float,7:float,8:float,9:float,10:float,11:float,12:float,13:float,14:float,15:float,16:float,17:float,18:float,19:float,20:float,21:float,22:float,23:float,24:float,25:float,26:float,27:float,28:float,29:float,30:float,31:float,32:float,33:float,34:float,35:float,36:float,37:float,38:float,39:float,40:float,41:float,42:float,43:float,44:float,45:float,46:float,47:float,48:float,49:float,50:float,51:float,52:float,53:float,54:float,55:float,56:float,57:float,58:float,59:float,60:float,61:float,62:float,63:float,64:float,65:float,66:float}
)

print(data.head())
print(data.describe())
import torchio as tio

blur = tio.RandomBlur()
to_ras = tio.ToCanonical()
fpg = tio.datasets.FPG()
fpg_ras = to_ras(fpg)

blurred = blur(fpg_ras)
